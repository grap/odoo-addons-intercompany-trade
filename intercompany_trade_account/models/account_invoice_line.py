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

from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from openerp.osv import fields
from openerp.osv.orm import Model

from openerp.addons.intercompany_trade_product.models.custom_tools\
    import _get_other_product_info


class AccountInvoiceLine(Model):
    _inherit = 'account.invoice.line'

    # Columns Section
    _columns = {
        'intercompany_trade': fields.related(
            'invoice_id', 'intercompany_trade', type='boolean',
            string='Intercompany Trade'),
        'intercompany_trade_account_invoice_line_id': fields.many2one(
            'account.invoice.line',
            string='Intercompany Trade Account Invoice Line',
            readonly=True,
        ),
    }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create the according Account Invoice Line."""
        context = context and context or {}
        ai_obj = self.pool['account.invoice']

        if vals.get('invoice_id', False):
            ai = ai_obj.browse(cr, uid, vals['invoice_id'], context=context)
            create_account_invoice_line = (not context.get(
                'intercompany_trade_do_not_propagate', False) and
                ai.intercompany_trade)
        else:
            create_account_invoice_line = False

        # Call Super: Create
        res = super(AccountInvoiceLine, self).create(
            cr, uid, vals, context=context)

        if create_account_invoice_line:
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            # Get Created Account Invoice Line
            ail = self.browse(cr, uid, res, context=context)

            # Get Intercompany Trade
            rit = ai_obj._get_intercompany_trade_by_partner_company_type(
                cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                context=context)

            # Prepare and create associated Account Invoice Line
            ail_other_vals, other_user_id = \
                self.prepare_intercompany_account_invoice_line(
                    cr, uid, ail, rit, context=context)

            ail_other_id = self.create(
                cr, other_user_id, ail_other_vals, context=ctx)

            # if this is a supplier invoice and an intercompany trade, the user
            # doesn't have the right to change the unit price, so we will
            # erase the unit price, and recover the good one.
            if ai.type in ('in_invoice', 'in_refund'):
                price_unit = ail_other_vals['price_unit']
            else:
                price_unit = vals['price_unit']

            # Update Original Account Invoice Line
            self.write(cr, uid, res, {
                'intercompany_trade_account_invoice_line_id': ail_other_id,
                'price_unit': price_unit,
            }, context=ctx)

            # Update Other Account Invoice Line
            self.write(
                cr, other_user_id, ail_other_id, {
                    'intercompany_trade_account_invoice_line_id': res,
                    'price_unit': price_unit,
                }, context=ctx)

            # Recompute All Invoice
            ai_obj.button_reset_taxes(
                cr, uid, [ai.id], context=ctx)
            # PUTE FIXME PAS SUR
#            ai_obj.button_reset_taxes(
#                cr, other_user_id,
#                [ai.intercompany_trade_account_invoice_id.id],
#                context=ctx)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Invoice Line with new data.
            - Block any changes of product.
            - the function will propagate only to according invoice line
              price or quantity changes. All others are ignored. Most of
              the important fields ignored will generated an error.
              (product / discount / UoM changes)    """
        context = context and context or {}
        ai_obj = self.pool['account.invoice']

        res = super(AccountInvoiceLine, self).write(
            cr, uid, ids, vals, context=context)

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for ail in self.browse(cr, uid, ids, context=context):
                if ail.intercompany_trade_account_invoice_line_id:
                    # Block some changes of product
                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product %s."""
                                """Please remove this line and create a"""
                                """ new one.""" % (ail.product_id.name)))
                    if 'uos_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the UoM of the Product"""
                                """ %s.""" % (ail.product_id.name)))
                    if 'price_unit' in vals.keys() and ail.invoice_id.type\
                            in ('in_invoice', 'in_refund'):
                        raise except_osv(
                            _("Error!"),
                            _("You can not change the Unit Price of"
                                " '%s'. Please ask to your supplier." % (
                                    ail.product_id.name)))

                    # Get Intercompany Trade
                    rit = ai_obj.\
                        _get_intercompany_trade_by_partner_company_type(
                            cr, uid, ail.invoice_id.partner_id.id,
                            ail.invoice_id.company_id.id,
                            ail.invoice_id.type, context=context)

                    # Prepare and update associated Sale Order line
                    ail_other_vals, other_user_id = \
                        self.prepare_intercompany_account_invoice_line(
                            cr, uid, ail, rit, context=context)

                    if 'price_unit' in vals.keys():
                        ail_other_vals['price_unit'] = vals['price_unit']
                    self.write(
                        cr, other_user_id,
                        [ail.intercompany_trade_account_invoice_line_id.id],
                        ail_other_vals, context=ctx)
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
    def prepare_intercompany_account_invoice_line(
            self, cr, uid, ail, rit, context=None):
        ai = ail.invoice_id
        if ai.type == 'out_invoice':
            # A Purchase Invoice Create a Sale Invoice
            direction = 'out'
            other_type = 'in_invoice'
            other_user_id = rit.customer_user_id.id
            other_company_id = rit.customer_company_id.id
            other_partner_id = rit.supplier_partner_id.id
        elif ai.type == 'in_invoice':
            # A Sale Invoice Create a Purchase Invoice
            direction = 'in'
            other_type = 'out_invoice'
            other_user_id = rit.supplier_user_id.id
            other_company_id = rit.supplier_company_id.id
            other_partner_id = rit.customer_partner_id.id
        else:
            raise except_osv(
                _("Unimplemented Feature!"),
                _("You can not create an invoice Line %s with a"
                    " partner flagged as Intercompany Trade." % (ai.type)))

        # Create according account invoice line
        other_product_info = _get_other_product_info(
            self.pool, cr, uid, rit, ail.product_id.id, direction,
            context=context)

        values = self.product_id_change(
            cr, other_user_id, False, other_product_info['product_id'],
            False, type=other_type, company_id=other_company_id,
            partner_id=other_partner_id)['value']

        values.update({
            'invoice_id': ai.intercompany_trade_account_invoice_id.id,
            'product_id': other_product_info['product_id'],
            'company_id': other_company_id,
            'partner_id': other_partner_id,
            'quantity': ail.quantity,
            'price_unit': ail.price_unit,
            'discount': ail.discount,
            'uos_id': ail.uos_id.id,
            'invoice_line_tax_id': (
                values['invoice_line_tax_id'] and
                [[6, False, values['invoice_line_tax_id']]] or False),
            })

        return values, other_user_id
