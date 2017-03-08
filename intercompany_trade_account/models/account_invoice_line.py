# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

from openerp.addons.intercompany_trade_product.models.custom_tools\
    import _get_other_product_info


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # Columns Section
    intercompany_trade = fields.Boolean(
        string='Intercompany Trade', default=True,
        related='invoice_id.intercompany_trade')

    intercompany_trade_account_invoice_line_id = fields.Many2one(
        string='Intercompany Trade Account Invoice Line',
        comodel_name='account.invoice.line', readonly=True, _prefetch=False)

    price_subtotal = fields.Float(compute_sudo=True)

    # Overload Section
    @api.model
    def create(self, vals):
        """Create the according Account Invoice Line."""
        invoice_obj = self.env['account.invoice']

        # Call Super
        line = super(AccountInvoiceLine, self).create(vals)

        if not self.env.context.get(
                'intercompany_trade_do_not_propagate', False) and\
                line.intercompany_trade:

            config =\
                invoice_obj._get_intercompany_trade_by_partner_company_type(
                    line.invoice_id.partner_id.id,
                    line.invoice_id.company_id.id,
                    line.invoice_id.type)

            # Prepare and create associated Account Invoice Line
            line_other_vals, other_user = \
                line.prepare_intercompany_account_invoice_line(config)

            line_other = self.sudo(user=other_user).with_context(
                intercompany_trade_do_not_propagate=True).create(
                    line_other_vals)

            # if this is a supplier invoice and an intercompany trade, the user
            # doesn't have the right to change the unit price, so we will
            # erase the unit price, and recover the good one.
            if line.invoice_id.type in ('in_invoice', 'in_refund'):
                price_unit = line_other_vals['price_unit']
            else:
                price_unit = vals['price_unit']

            # Update Original Account Invoice Line
            line.with_context(
                intercompany_trade_do_not_propagate=True).write({
                    'intercompany_trade_account_invoice_line_id':
                    line_other.id,
                    'price_unit': price_unit})

            # Update Other Account Invoice Line
            line_other.sudo(user=other_user).with_context(
                intercompany_trade_do_not_propagate=True).write({
                    'intercompany_trade_account_invoice_line_id': line.id,
                    'price_unit': price_unit})

        return line

    @api.multi
    def write(self, vals):
        """"- Update the according Invoice Line with new data.
            - Block any changes of product.
            - the function will propagate only to according invoice line
              price or quantity changes. All others are ignored. Most of
              the important fields ignored will generated an error.
              (product / discount / UoM changes)    """
        invoice_obj = self.env['account.invoice']

        res = super(AccountInvoiceLine, self).write(vals)

        if 'intercompany_trade_do_not_propagate' not in\
                self.env.context.keys():

            for line in self:
                if line.intercompany_trade:
                    # Get Intercompany Trade
                        config = invoice_obj.\
                            _get_intercompany_trade_by_partner_company_type(
                                line.invoice_id.partner_id.id,
                                line.invoice_id.company_id.id,
                                line.invoice_id.type)

                    # Block some changes of product
                if 'product_id' in vals.keys():
                    raise UserError(_(
                        "Error!\nYou can not change the product %s."
                        "Please remove this line and create a"
                        " new one." % (line.product_id.name)))
                if 'uos_id' in vals.keys():
                    raise UserError(_(
                        "Error!\nYou can not change the UoM of the Product"
                        " %s." % (line.product_id.name)))
                if 'price_unit' in vals.keys() and line.invoice_id.type\
                        in ('in_invoice', 'in_refund'):
                    raise UserError(_(
                        "Error!\nYou can not change the Unit Price of"
                        " '%s'. Please ask to your supplier." % (
                            line.product_id.name)))

                # Prepare and update associated Sale Order line
                line_other_vals, other_user = \
                    line.prepare_intercompany_account_invoice_line(
                        config)

                if 'price_unit' in vals.keys():
                    line_other_vals['price_unit'] = vals['price_unit']
                line.intercompany_trade_account_invoice_line_id.sudo(
                    user=other_user).with_context(
                        intercompany_trade_do_not_propagate=True).write(
                            line_other_vals)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Invoice Line."""
        ai_obj = self.pool['account.invoice']
        context = context and context or {}

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for ail in self.browse(
                    cr, uid, ids, context=context):
                if ail.intercompany_trade:
                    rit = ai_obj.\
                        _get_intercompany_trade_by_partner_company_type(
                            cr, uid, ail.invoice_id.partner_id.id,
                            ail.invoice_id.company_id.id, ail.invoice_id.type,
                            context=context)
                    if ail.invoice_id.type in ('in_invoice', 'in_refund'):
                        other_uid = rit.supplier_user_id.id
                    else:
                        other_uid = rit.customer_user_id.id
                    self.unlink(
                        cr, other_uid,
                        [ail.intercompany_trade_account_invoice_line_id.id],
                        context=ctx)
        res = super(AccountInvoiceLine, self).unlink(
            cr, uid, ids, context=context)
        return res

    # Custom Section
    @api.multi
    def prepare_intercompany_account_invoice_line(self, config):
        self.ensure_one()
        invoice = self.invoice_id
        if invoice.type == 'out_invoice':
            # A Purchase Invoice Create a Sale Invoice
            direction = 'out'
            other_type = 'in_invoice'
            other_user = config.customer_user_id
            other_company_id = config.customer_company_id.id
            other_partner_id = config.supplier_partner_id.id
        elif invoice.type == 'in_invoice':
            # A Sale Invoice Create a Purchase Invoice
            direction = 'in'
            other_type = 'out_invoice'
            other_user = config.supplier_user_id
            other_company_id = config.supplier_company_id.id
            other_partner_id = config.customer_partner_id.id
        else:
            raise UserError(_(
                "Unimplemented Feature!\n"
                "You can not create an invoice Line %s with a"
                " partner flagged as Intercompany Trade." % (invoice.type)))

        # Create according account invoice line
        other_product_info = _get_other_product_info(
            self.pool, self.env.cr, self.env.user.id, config,
            self.product_id.id, direction, context=self.env.context)

        values = self.sudo(user=other_user).product_id_change(
            other_product_info['product_id'],
            False, type=other_type, company_id=other_company_id,
            partner_id=other_partner_id)['value']

        values.update({
            'invoice_id': invoice.intercompany_trade_account_invoice_id.id,
            'product_id': other_product_info['product_id'],
            'company_id': other_company_id,
            'partner_id': other_partner_id,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'uos_id': self.uos_id.id,
            'invoice_line_tax_id': (
                values.get('invoice_line_tax_id', False) and
                [[6, False, values['invoice_line_tax_id']]] or False),
            })

        return values, other_user
