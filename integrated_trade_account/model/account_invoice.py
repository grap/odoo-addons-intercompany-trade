# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Account module for Odoo
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

from openerp.osv import fields
from openerp.osv.osv import except_osv
from openerp.osv.orm import Model
from openerp.tools.translate import _


class AccountInvoice(Model):
    _inherit = 'account.invoice'

    # Fields Function Section
    def _get_integrated_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for ai in self.browse(cr, uid, ids, context=context):
            res[ai.id] = ai.partner_id.integrated_trade
        return res

    # Columns Section
    _columns = {
        'integrated_trade': fields.function(
            _get_integrated_trade, type='boolean', string='Integrated Trade',
            store={'account.invoice': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'integrated_trade_account_invoice_id': fields.many2one(
            'account.invoice', string='Integrated Trade Account Invoice',
            readonly=True,
        ),
    }

    # Private Function
    def _get_res_integrated_trade(
            self, cr, uid, partner_id, company_id, type,
            context=None):
        rit_obj = self.pool['res.integrated.trade']
        if type == 'in_invoice':
            rit_id = rit_obj.search(cr, uid, [
                ('supplier_partner_id', '=', partner_id),
                ('customer_company_id', '=', company_id),
            ], context=context)[0]
        else:
            rit_id = rit_obj.search(cr, uid, [
                ('customer_partner_id', '=', partner_id),
                ('supplier_company_id', '=', company_id),
            ], context=context)[0]
        return rit_obj.browse(cr, uid, rit_id, context=context)

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        rp_obj = self.pool['res.partner']

        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_account_invoice = (
            not context.get('integrated_trade_do_not_propagate', False) and
            rp.integrated_trade)

        if create_account_invoice:
            line_ids = vals['invoice_line']
            vals.pop('invoice_line')

        res = super(AccountInvoice, self).create(
            cr, uid, vals, context=context)

        if create_account_invoice:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            ctx.pop('type')
            ctx.pop('journal_type')
            ctx.pop('default_type')

            # Create associated Invoice
            ai = self.browse(cr, uid, res, context=context)
            if ai.type == 'out_invoice':
                create_type = 'in_invoice'
            elif ai.type == 'in_invoice':
                create_type = 'out_invoice'
            else:
                raise except_osv(
                    _("Unimplemented Feature!"),
                    _("""You can not change create an invoice %s with a"""
                        """ partner flagged as 'Integratedd Trade'. """ % (
                            ai.type)))
            rit = self._get_res_integrated_trade(
                cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                context=context)

            if create_type == 'out_invoice':
                # A Purchase Invoice Create a Sale Invoice
                other_user_id = rit.supplier_user_id.id
                other_company_id = rit.supplier_company_id.id
                other_partner_id = rit.customer_partner_id.id
            else:
                # A Sale Invoice Create a Purchase Invoice
                other_user_id = rit.customer_user_id.id
                other_company_id = rit.customer_company_id.id
                other_partner_id = rit.supplier_partner_id.id

            # Update ctx['uid'] due to an incompatibility with
            # account_invoice_pricelist
            ctx['uid'] = other_user_id

            account_info = self.onchange_partner_id(
                cr, other_user_id, [], create_type, other_partner_id,
                company_id=other_company_id)['value']

            account_journal_id = self._get_journal(cr, other_user_id, {
                'type': create_type, 'company_id': other_company_id})

            ai_other_vals = {
                'integrated_trade_account_invoice_id': ai.id,
                'type': create_type,
                'company_id': other_company_id,
                'partner_id': other_partner_id,
                'account_id': account_info['account_id'],
                'journal_id': account_journal_id,
            }

            ai_other_id = self.create(
                cr, other_user_id, ai_other_vals, context=ctx)
            ai_other = self.browse(
                cr, other_user_id, ai_other_id, context=context)

            # Update Proper Account Invoice
            self.write(cr, uid, [ai.id], {
                'integrated_trade_account_invoice_id': ai_other.id,
                'order_line': line_ids,
            }, context=context)
        return res
