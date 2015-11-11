# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Account module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import netsvc
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv.osv import except_osv
from openerp.osv.orm import Model
from openerp.tools.translate import _


class AccountInvoice(Model):
    _inherit = 'account.invoice'

    # Fields Function Section
    def _get_intercompany_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for ai in self.browse(cr, uid, ids, context=context):
            res[ai.id] = ai.partner_id.intercompany_trade
        return res

    # Columns Section
    _columns = {
        'intercompany_trade': fields.function(
            _get_intercompany_trade, type='boolean',
            string='Intercompany Trade',
            store={'account.invoice': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'intercompany_trade_account_invoice_id': fields.many2one(
            'account.invoice', string='Intercompany Trade Account Invoice',
            readonly=True,
        ),
    }

#    # TODO Move this
#    def wkf_verify_invoice(self, cr, uid, ids, context=None):
#        context = context and context or {}
#        for invoice in self.browse(cr, uid, ids, context=context):
#            if invoice.intercompany_trade and\
#                    invoice.type in ('in_invoice', 'in_refund') and\
#                    not self.pool['res.users'].has_group(
#                    cr, uid, 'account.group_account_manager'):
#                raise except_osv(
#                    _("Forbidden Operation!"),
#                    _("You're not allowed to verify the Invoice."
#                        " Please ask your supplier or your accountant to do"
#                        " it."))
#        return super(AccountInvoice, self).wkf_verify_invoice(
#            cr, uid, ids, context=context)

#    def invoice_validate(self, cr, uid, ids, context=None):
#        context = context and context or {}
#        for invoice in self.browse(cr, uid, ids, context=context):
#            if invoice.intercompany_trade and\
#                    invoice.type in ('in_invoice', 'in_refund') and\
#                    not self.pool['res.users'].has_group(
#                    cr, uid, 'account.group_account_manager'):
#                raise except_osv(
#                    _("Forbidden Operation!"),
#                    _("You're not allowed to validate the Invoice."
#                        " Please ask your supplier or your accountant to do"
#                        " it."))
#        return super(AccountInvoice, self).invoice_validate(
#            cr, uid, ids, context=context)

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        rp_obj = self.pool['res.partner']

        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_account_invoice = (
            not context.get('intercompany_trade_do_not_propagate', False) and
            rp.intercompany_trade)

        if create_account_invoice:
            line_ids = vals.get('invoice_line', False)
            vals.pop('invoice_line', None)

        res = super(AccountInvoice, self).create(
            cr, uid, vals, context=context)

        if create_account_invoice:
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            ctx.pop('type', None)
            ctx.pop('journal_type', None)
            ctx.pop('default_type', None)

            # Create associated Invoice
            ai = self.browse(cr, uid, res, context=context)

            rit = self._get_intercompany_trade_by_partner_company_type(
                cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                context=context)

            ai_other_vals, other_user_id =\
                self.prepare_intercompany_invoice(
                    cr, uid, ai, rit, 'create', context=context)

            ai_other_id = self.create(
                cr, other_user_id, ai_other_vals, context=ctx)

            # Update Proper Account Invoice
            self.write(cr, uid, [ai.id], {
                'intercompany_trade_account_invoice_id': ai_other_id,
                'invoice_line': line_ids,
            }, context=context)
        return res

    # TODO: TESTME
    def write(self, cr, uid, ids, vals, context=None):
        context = context if context else {}
        res = super(AccountInvoice, self).write(
            cr, uid, ids, vals, context=context)

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            for ai in self.browse(cr, uid, ids, context=context):
                if ai.intercompany_trade:
                    rit = self._get_intercompany_trade_by_partner_company_type(
                        cr, uid, ai.partner_id.id, ai.company_id.id,
                        ai.type, context=context)
                    # Disable possibility to change the supplier
                    if 'partner_id' in vals:
                        raise except_osv(
                            _("Error!"),
                            _("You can not change the partner because of"
                                " Intercompany Trade Rules. Please create"
                                " a new Invoice."))

                    # Update changes for according invoice
                    ai_vals, other_user_id = self.prepare_intercompany_invoice(
                        cr, uid, ai, rit, 'update', context=context)

                    self.write(
                        cr, other_user_id,
                        [ai.intercompany_trade_account_invoice_id.id], ai_vals,
                        context=ctx)

                    # TODO FORBID state change for customer
                    if ai.type == 'out_invoice' and\
                            vals.get('state', False) == 'open':
                        ai_other_super = self.browse(
                            cr, SUPERUSER_ID,
                            ai.intercompany_trade_account_invoice_id.id,
                            context=context)
                        if ai_other_super.amount_untaxed != ai.amount_untaxed\
                                    or ai_other_super.amount_tax !=\
                                    ai.amount_tax:
                            raise except_osv(_("Error!"),_(
                                "You can not validate this invoice"
                                " because the according customer invoice"
                                " don't have the same total amount."
                                " Please fix the problem first."))
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(
                            other_user_id, 'account.invoice',
                            ai.intercompany_trade_account_invoice_id.id,
                            'invoice_verify', cr)

                        wf_service.trg_validate(
                            other_user_id, 'account.invoice',
                            ai.intercompany_trade_account_invoice_id.id,
                            'invoice_open', cr)

        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Invoice."""
        context = context and context or {}

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for ai in self.browse(
                    cr, uid, ids, context=context):
                if ai.intercompany_trade:
                    rit = self._get_intercompany_trade_by_partner_company_type(
                        cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                        context=context)
                    if ai.type in ('in_invoice', 'in_refund'):
                        other_uid = rit.supplier_user_id.id
                    else:
                        other_uid = rit.customer_user_id.id
                    self.unlink(
                        cr, other_uid,
                        [ai.intercompany_trade_account_invoice_id.id],
                        context=ctx)
        res = super(AccountInvoice, self).unlink(
            cr, uid, ids, context=context)
        return res

    # Custom Section
    def _get_intercompany_trade_by_partner_company_type(
            self, cr, uid, partner_id, company_id, type, context=None):
        rit_obj = self.pool['intercompany.trade.config']

        if type in ('in', 'in_invoice', 'in_refund'):
            regular_type = 'in'
        else:
            regular_type = 'out'

        return rit_obj._get_intercompany_trade_by_partner_company(
            cr, uid, partner_id, company_id, regular_type,
            context=context)

    def prepare_intercompany_invoice(
            self, cr, uid, ai, rit, operation, context=None):
        if ai.type == 'out_invoice':
            # A Purchase Invoice Create a Sale Invoice
            other_type = 'in_invoice'
            other_user_id = rit.customer_user_id.id
            other_company_id = rit.customer_company_id.id
            other_partner_id = rit.supplier_partner_id.id
        elif ai.type == 'in_invoice':
            # A Sale Invoice Create a Purchase Invoice
            other_type = 'out_invoice'
            other_user_id = rit.supplier_user_id.id
            other_company_id = rit.supplier_company_id.id
            other_partner_id = rit.customer_partner_id.id
        else:
            raise except_osv(
                _("Unimplemented Feature!"),
                _("You can not create an invoice %s with a"
                    " partner flagged as Intercompany Trade." % (ai.type)))

        account_info = self.onchange_partner_id(
            cr, other_user_id, [], other_type, other_partner_id,
            company_id=other_company_id)['value']

        account_journal_id = self._get_journal(cr, other_user_id, {
            'type': other_type, 'company_id': other_company_id})

        values = {
            'intercompany_trade_account_invoice_id': ai.id,
            'type': other_type,
            'company_id': other_company_id,
            'date_invoice': ai.date_invoice,
            'date_due': ai.date_due,
            'currency_id': ai.currency_id.id,
            'comment': ai.comment,
        }
        if ai.type == 'out_invoice':
            print 'out_invoice'
            values['supplier_invoice_number'] = ai.number and ai.number or\
                _('Intercompany Trade')
        if operation == 'create':
            values.update({
                'partner_id': other_partner_id,
                'account_id': account_info['account_id'],
                'journal_id': account_journal_id,
            })

        return values, other_user_id
