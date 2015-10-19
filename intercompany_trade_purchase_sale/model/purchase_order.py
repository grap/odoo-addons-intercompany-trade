# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase / Sale module for OpenERP
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
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class purchase_order(Model):
    _inherit = 'purchase.order'

    # Fields Function Section
    def _get_intercompany_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for po in self.browse(cr, uid, ids, context=context):
            res[po.id] = po.partner_id.intercompany_trade
        return res

    # Columns Section
    _columns = {
        'intercompany_trade': fields.function(
            _get_intercompany_trade, type='boolean',
            string='Intercompany Trade',
            store={'purchase.order': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'intercompany_trade_sale_order_id': fields.many2one(
            'sale.order', string='Intercompany Trade Sale Order',
            readonly=True,
        ),
    }

    # Constraint Section
    def _check_intercompany_trade_invoice_method(
            self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            if po.intercompany_trade and po.invoice_method != 'picking':
                return False
        return True

    _constraints = [
        (
            _check_intercompany_trade_invoice_method,
            """Error: The module 'Intercompany Trade' Only works with"""
            """ 'Invoice Method' set to 'Picking'.""",
            ['intercompany_trade', 'invoice_method']),
    ]

    # View Section
    def intercompany_trade_request(self, cr, uid, ids, context=None):
        rit_obj = self.pool['intercompany.trade.config']
        so_obj = self.pool['sale.order']

        # Check if Total of the PO and SO are identical
        for po in self.browse(cr, uid, ids, context=context):
            if po.intercompany_trade:
                # Get Intercompany Trade
                rit = rit_obj._get_intercompany_trade_by_partner_company(
                    cr, uid, po.partner_id.id, po.company_id.id, 'in',
                    context=context)
                so = so_obj.browse(
                    cr, rit.supplier_user_id.id,
                    po.intercompany_trade_sale_order_id.id, context=context)
                if po.amount_untaxed != so.amount_untaxed or\
                        po.amount_tax != so.amount_tax:
                    raise except_osv(
                        _("Error!"),
                        _("It seems that your Purchase Order has not the"
                            " same amount that the according Sale Order."
                            " Please call the IT Support\n\n"
                            " * Purchase : %s \n"
                            " * Amount Untaxed : %d\n"
                            " * Taxes : %d\n\n"
                            " * Sale Order : %s \n"
                            " * Amount Untaxed : %d\n"
                            " * Taxes : %d\n\n" % (
                                po.name, po.amount_untaxed, po.amount_tax,
                                so.name, so.amount_untaxed, so.amount_tax)))
        return self.print_quotation(cr, uid, ids, context=context)

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        context = context if context else {}

        rit_obj = self.pool['intercompany.trade.config']
        rp_obj = self.pool['res.partner']
        so_obj = self.pool['sale.order']

        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_sale_order = (
            not context.get('intercompany_trade_do_not_propagate', False) and
            rp.intercompany_trade)

        if create_sale_order:
            line_ids = vals.get('order_line', [])
            vals.pop('order_line', None)

        res = super(purchase_order, self).create(
            cr, uid, vals, context=context)

        if create_sale_order:
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            # Get Created Purchase Order
            po = self.browse(cr, uid, res, context=context)

            # Get Intercompany Trade
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, po.partner_id.id, po.company_id.id, 'in',
                context=context)

            # Create associated Sale Order
            so_vals = self.prepare_intercompany_sale_order(
                cr, uid, po, rit, context=context)

            so_id = so_obj.create(
                cr, rit.supplier_user_id.id, so_vals, context=ctx)
            so = so_obj.browse(
                cr, rit.supplier_user_id.id, so_id, context=context)

            # Update Purchase Order
            self.write(cr, uid, [res], {
                'intercompany_trade_sale_order_id': so.id,
                'partner_ref': so.name,
                'order_line': line_ids,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        context = context if context else {}
        rit_obj = self.pool['intercompany.trade.config']
        so_obj = self.pool['sale.order']

        res = super(purchase_order, self).write(
            cr, uid, ids, vals, context=context)

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            for po in self.browse(cr, uid, ids, context=context):
                if po.intercompany_trade:
                    rit = rit_obj._get_intercompany_trade_by_partner_company(
                        cr, uid, po.partner_id.id, po.company_id.id,
                        'in', context=context)
                    # Disable possibility to change the supplier
                    if 'partner_id' in vals:
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the supplier because"""
                                """ of Intercompany Trade Rules. Please"""
                                """ create a new one Purchase Order."""))
                    # Disable possibility to change lines if the Purchase
                    # Order is not a 'draft' state
                    if (po.state not in ['draft', 'cancel'] and
                            vals.get('order_line', False)):
                        raise except_osv(
                            _("Error!"),
                            _("You can not change Lines of a Sent Purchase"
                                " Order because of Intercompany Trade"
                                " Rules. Please cancel this Purchase Order"
                                " and create a new one, duplicating it."))
                    # Disable possibility to set to draft again
                    if vals.get('state', False) == 'draft':
                        raise except_osv(
                            _("Error!"),
                            _("You can not change set to 'draft' again"
                                " this Quotation because of Intercompany"
                                " Trade Rules. Please cancel this"
                                " one and create a new one, duplicating it."))

                    # Update changes for according sale order
                    so_vals = self.prepare_intercompany_sale_order(
                        cr, uid, po, rit, context=context)
                    # FIXME : TODO investigate why we have to set the
                    # following line
                    so_vals.pop('company_id', False)
                    so_obj.write(
                        cr, rit.supplier_user_id.id,
                        [po.intercompany_trade_sale_order_id.id], so_vals,
                        context=ctx)

                    # Apply change of status 'draft' --> 'sent'
                    if vals.get('state', False) == 'sent':
                        # Change state of purchase order to 'sent' must change
                        # the status of the Sale Order (more easy to do that
                        # here, because the activity 'act_sent' is bad
                        # hardcoded)
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(
                            rit.supplier_user_id.id, 'sale.order',
                            po.intercompany_trade_sale_order_id.id,
                            'quotation_sent', cr)

                    # Apply change of status any --> 'cancel'
                    if vals.get('state', False) == 'cancel':
                        # Change state of purchase order to 'cancel' must
                        # change the status of the Sale Order
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(
                            rit.supplier_user_id.id, 'sale.order',
                            po.intercompany_trade_sale_order_id.id,
                            'cancel', cr)

        return res

    def unlink(self, cr, uid, ids, context=None):
        """Delete according Sale order"""
        # FIXME: Unlink purchase Order call workflow trigger and fails
        context = context if context else {}

        rit_obj = self.pool['intercompany.trade.config']
        so_obj = self.pool['sale.order']

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for po in self.browse(cr, uid, ids, context=context):
                if po.intercompany_trade:
                    rit = rit_obj._get_intercompany_trade_by_partner_company(
                        cr, uid, po.partner_id.id, po.company_id.id,
                        'in', context=context)
                    if po.intercompany_trade:
                        so_obj.unlink(
                            cr, rit.supplier_user_id.id,
                            [po.intercompany_trade_sale_order_id.id],
                            context=ctx)
        return super(purchase_order, self).unlink(
            cr, uid, ids, context=context)

    # Custom Section
    def prepare_intercompany_sale_order(
            self, cr, uid, po, rit, context=None):
        iv_obj = self.pool['ir.values']
        # WEIRD: sale_order has a bad _get_default_shop base on the
        # company of the current user, so we request ir.values
        # to have the correct one
        shop_id = iv_obj.get_default(
            cr, rit.supplier_user_id.id, 'sale.order', 'shop_id',
            company_id=rit.supplier_company_id.id)

        return {
            'shop_id': shop_id,
            'date_order': po.date_order,
            'company_id': rit.supplier_company_id.id,
            'partner_id': rit.customer_partner_id.id,
            'partner_invoice_id': rit.customer_partner_id.id,
            'partner_shipping_id': rit.customer_partner_id.id,
            'intercompany_trade_purchase_order_id': po.id,
            'pricelist_id': rit.sale_pricelist_id.id,
            'client_order_ref': po.name,
            'order_policy': 'picking',
        }

    def button_intercompany_trade_product_quantity(
            self, cr, uid, ids, context=None):
        ctx = context.copy()
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'intercompany.product.stock',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
