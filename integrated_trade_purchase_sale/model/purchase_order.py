# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Purchase module for OpenERP
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
    def _get_integrated_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for po in self.browse(cr, uid, ids, context=context):
            res[po.id] = po.partner_id.integrated_trade
        return res

    # Columns Section
    _columns = {
        'integrated_trade': fields.function(
            _get_integrated_trade, type='boolean', string='Integrated Trade',
            store={'purchase.order': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'integrated_trade_sale_order_id': fields.many2one(
            'sale.order', string='Integrated Trade Sale Order',
            readonly=True,
        ),
    }

    # Constraint Section
    def _check_integrated_trade_invoice_method(
            self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            if po.integrated_trade and po.invoice_method != 'picking':
                return False
        return True

    _constraints = [
        (
            _check_integrated_trade_invoice_method,
            """Error: The module 'Integrated Trade' Only works with"""
            """ 'Invoice Method' set to 'Picking'.""",
            ['integrated_trade', 'invoice_method']),
    ]

    # # Private Function
    # def _get_res_integrated_trade(
    #         self, cr, uid, supplier_partner_id, customer_company_id,
    #         context=None):
    #     rit_obj = self.pool['res.integrated.trade']
    #     rit_id = rit_obj.search(cr, uid, [
    #         ('supplier_partner_id', '=', supplier_partner_id),
    #         ('customer_company_id', '=', customer_company_id),
    #     ], context=context)[0]
    #     return rit_obj.browse(cr, uid, rit_id, context=context)

    # View Section
    def integrated_trade_request(self, cr, uid, ids, context=None):
        return self.print_quotation(cr, uid, ids, context=context)

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        rit_obj = self.pool['res.integrated.trade']
        rp_obj = self.pool['res.partner']
        so_obj = self.pool['sale.order']
        iv_obj = self.pool['ir.values']

        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_sale_order = (
            not context.get('integrated_trade_do_not_propagate', False) and
            rp.integrated_trade)

        if create_sale_order:
            line_ids = vals['order_line']
            vals.pop('order_line')

        res = super(purchase_order, self).create(
            cr, uid, vals, context=context)

        if create_sale_order:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True

            # Create associated Sale Order
            po = self.browse(cr, uid, res, context=context)
            rit = rit_obj._get_integrated_trade_by_partner_company(
                cr, uid, po.partner_id.id, po.company_id.id, 'in',
                context=context)

            # WEIRD: sale_order has a bad _get_default_shop base on the
            # company of the current user, so we request ir.values
            # to have the correct one

            shop_id = iv_obj.get_default(
                cr, rit.supplier_user_id.id, 'sale.order', 'shop_id',
                company_id=rit.supplier_company_id.id)
            so_vals = {
                'company_id': rit.supplier_company_id.id,
                'partner_id': rit.customer_partner_id.id,
                'partner_invoice_id': rit.customer_partner_id.id,
                'partner_shipping_id': rit.customer_partner_id.id,
                'integrated_trade_purchase_order_id': res,
                'shop_id': shop_id,
                'pricelist_id': rit.pricelist_id.id,
                'client_order_ref': po.name,
            }
            so_id = so_obj.create(
                cr, rit.supplier_user_id.id, so_vals, context=ctx)
            so = so_obj.browse(
                cr, rit.supplier_user_id.id, so_id, context=context)

            # Update Purchase Order
            self.write(cr, uid, [res], {
                'integrated_trade_sale_order_id': so.id,
                'partner_ref': so.name,
                'order_line': line_ids,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        rit_obj = self.pool['res.integrated.trade']

        context = context if context else {}
        res = super(purchase_order, self).write(
            cr, uid, ids, vals, context=context)

        if 'integrated_trade_do_not_propagate' not in context.keys():
            for po in self.browse(cr, uid, ids, context=context):
                if po.integrated_trade:
                    if 'partner_id' in vals:
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the customer because"""
                                """ of 'Integrated Trade' Rules'. Please"""
                                """ create a new one Purchase Order."""))
                    # Disable possibility to change lines if the Purchase
                    # Order is not a 'draft' state
                    if (po.state not in ['draft', 'cancel'] and
                            vals.get('order_line', False)):
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change Lines of a Sent Purchase"""
                                """ Order because of 'Integrated 'Trade'"""
                                """ Rules. Please cancel this Purchase Order"""
                                """  and create a new one, duplicating it."""))
                    rit = rit_obj._get_integrated_trade_by_partner_company(
                        cr, uid, po.partner_id.id, po.company_id.id,
                        'in', context=context)
                    if vals.get('state', False) == 'sent':
                        # Change state of purchase order to 'sent' must change
                        # the status of the Sale Order (more easy to do that
                        # here, because the activity 'act_sent' is bad
                        # hardcoded)
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(
                            rit.supplier_user_id.id, 'sale.order',
                            po.integrated_trade_sale_order_id.id,
                            'quotation_sent', cr)
                    if vals.get('state', False) == 'cancel':
                        # Change state of purchase order to 'cancel' must
                        # change the status of the Sale Order
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(
                            rit.supplier_user_id.id, 'sale.order',
                            po.integrated_trade_sale_order_id.id,
                            'cancel', cr)
                    if vals.get('state', False) == 'draft':
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change set to 'draft' again"""
                                """ this Quotation because of 'Integrated"""
                                """ 'Trade' Rules. Please cancel this"""
                                """ one and create a new one, duplicating"""
                                """ it."""))
        return res

    def unlink(self, cr, uid, ids, context=None):
        """Delete according Purchase order"""
        rit_obj = self.pool['res.integrated.trade']
        so_obj = self.pool['sale.order']

        context = context if context else {}
        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for po in self.browse(cr, uid, ids, context=context):
                rit = self._get_integrated_trade_by_partner_company(
                    cr, uid, po.partner_id.id, po.company_id.id,
                    'in', context=context)
                if po.integrated_trade:
                    so_obj.unlink(
                        cr, rit.supplier_user_id.id,
                        [po.integrated_trade_sale_order_id.id], context=ctx)
        res = super(purchase_order, self).unlink(
            cr, uid, ids, context=context)
        return res
