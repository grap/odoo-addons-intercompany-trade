# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models, netsvc
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # ACL Changes
    # TODO investigate why compute_amount is launched with the same
    # user for the two invoices, raising ACL Error
    @api.one
    def _compute_amount(self):
        return super(AccountInvoice, self.sudo())._compute_amount()

    # Columns Section
    intercompany_trade_account_invoice_id = fields.Many2one(
        comodel_name='account.invoice', readonly=True, _prefetch=False,
        string='Intercompany Trade Account Invoice')

    intercompany_trade = fields.Boolean(
        string='Intercompany Trade', related='partner_id.intercompany_trade')

    # Overload Section
    @api.model
    def create(self, vals):
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(vals['partner_id'])

        create_account_invoice = (not self.env.context.get(
            'intercompany_trade_do_not_propagate', False) and
            partner.intercompany_trade)

        if create_account_invoice:
            line_ids = vals.get('invoice_line', False)
            vals.pop('invoice_line', None)

        invoice = super(AccountInvoice, self).create(vals)

        if create_account_invoice:
            # Get config
            config = self._get_intercompany_trade_by_partner_company_type(
                invoice.partner_id.id, invoice.company_id.id, invoice.type)

            # Create associated Invoice
            invoice_other_vals, other_user =\
                invoice.prepare_intercompany_invoice(config, 'create')

            invoice_other = self.sudo(user=other_user).with_context(
                intercompany_trade_do_not_propagate=True,
                type=None, journal_type=None, default_type=None).create(
                invoice_other_vals)

            # Update Proper Account Invoice
            invoice.write({
                'intercompany_trade_account_invoice_id': invoice_other.id,
                'invoice_line': line_ids})
        return invoice

    # TODO FORBID state change for customer
    # TODO refactor state management (verify state) or wait for V10
    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)

        if 'intercompany_trade_do_not_propagate' not in self.env.context:
            for invoice in self:
                if invoice.intercompany_trade:
                    config =\
                        self._get_intercompany_trade_by_partner_company_type(
                            invoice.partner_id.id, invoice.company_id.id,
                            invoice.type)
                    # Disable possibility to change the supplier
                    if 'partner_id' in vals and\
                            vals.get('partner_id') != invoice.partner_id.id:
                        raise UserError(_(
                            "Error!\nYou can not change the partner because of"
                            " Intercompany Trade Rules. Please create"
                            " a new Invoice."))

                    # Update changes for according invoice
                    invoice_vals, other_user =\
                        invoice.prepare_intercompany_invoice(config, 'update')

                    invoice.intercompany_trade_account_invoice_id.sudo(
                        user=other_user).with_context(
                            intercompany_trade_do_not_propagate=True).write(
                                invoice_vals)

                    if invoice.type == 'out_invoice' and\
                            vals.get('state', False) == 'open':
                        invoice_other = self.sudo(other_user).browse(
                            invoice.intercompany_trade_account_invoice_id.id)
                        if invoice_other.amount_untaxed !=\
                                invoice.amount_untaxed\
                                or invoice_other.amount_tax !=\
                                invoice.amount_tax:
                            raise UserError(_(
                                "Error!\nYou can not validate this invoice"
                                " because the according customer invoice"
                                " don't have the same total amount."
                                " Please fix the problem first."))
                        wf_service = netsvc.LocalService("workflow")

                        wf_service.trg_validate(
                            other_user.id, 'account.invoice',
                            invoice_other.id, 'invoice_verify', self.env.cr)

                        wf_service.trg_validate(
                            other_user.id, 'account.invoice',
                            invoice_other.id, 'invoice_open', self.env.cr)

        return res

    @api.multi
    def unlink(self):
        """" Unlink the according Invoices"""
        if 'intercompany_trade_do_not_propagate' not in self.env.context:
            for invoice in self:
                if invoice.intercompany_trade:
                    config =\
                        self._get_intercompany_trade_by_partner_company_type(
                            invoice.partner_id.id, invoice.company_id.id,
                            invoice.type)
                    if invoice.type in ('in_invoice', 'in_refund'):
                        other_uid = config.supplier_user_id
                    else:
                        other_uid = config.customer_user_id
                    invoice.intercompany_trade_account_invoice_id.sudo(
                        user=other_uid).with_context(
                            intercompany_trade_do_not_propagate=True).unlink()
        return super(AccountInvoice, self).unlink()

    # Custom Section
    @api.model
    def _get_intercompany_trade_by_partner_company_type(
            self, partner_id, company_id, type):
        config_obj = self.env['intercompany.trade.config']

        if type in ('in', 'in_invoice', 'in_refund'):
            regular_type = 'in'
        else:
            regular_type = 'out'

        return config_obj._get_intercompany_trade_by_partner_company(
            partner_id, company_id, regular_type)

    @api.multi
    def prepare_intercompany_invoice(self, config, operation):
        self.ensure_one()
        if self.type == 'out_invoice':
            # A Purchase Invoice Create a Sale Invoice
            other_type = 'in_invoice'
            other_user = config.customer_user_id
            other_company_id = config.customer_company_id.id
            other_partner_id = config.supplier_partner_id.id
        elif self.type == 'in_invoice':
            # A Sale Invoice Create a Purchase Invoice
            other_type = 'out_invoice'
            other_user = config.supplier_user_id
            other_company_id = config.supplier_company_id.id
            other_partner_id = config.customer_partner_id.id
        else:
            raise UserError(_(
                "Unimplemented Feature!\n You can not create an invoice %s"
                " with a partner flagged as Intercompany Trade." % (
                    self.type)))

        account_info = self.sudo(user=other_user).onchange_partner_id(
            other_type, other_partner_id, company_id=other_company_id)['value']

        account_journal = self.sudo(user=other_user).with_context(
            type=other_type, company_id=other_company_id)._default_journal()

        values = {
            'intercompany_trade_account_invoice_id': self.id,
            'type': other_type,
            'company_id': other_company_id,
            'date_invoice': self.date_invoice,
            'date_due': self.date_due,
            'currency_id': self.currency_id.id,
            'comment': self.comment,
        }
        if self.type == 'out_invoice':
            values['supplier_invoice_number'] = self.number and self.number or\
                _('Intercompany Trade')
        if operation == 'create':
            values.update({
                'partner_id': other_partner_id,
                'account_id': account_info['account_id'],
                'journal_id': account_journal.id,
            })

        return values, other_user
