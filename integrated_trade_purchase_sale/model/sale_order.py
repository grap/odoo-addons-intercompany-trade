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


class sale_order(Model):
    _inherit = 'sale.order'

    # Fields Function Section
    def _get_integrated_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for so in self.browse(cr, uid, ids, context=context):
            res[so.id] = so.partner_id.integrated_trade
        return res

    # Columns Section
    _columns = {
        'integrated_trade': fields.function(
            _get_integrated_trade, type='boolean', string='Integrated Trade',
            store={'sale.order': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'integrated_trade_purchase_order_id': fields.many2one(
            'purchase.order', string='Integrated Trade Purchase Order',
            readonly=True,
        ),
    }

    # Constraint Section
    def _check_integrated_trade_order_policy(
            self, cr, uid, ids, context=None):
        for so in self.browse(cr, uid, ids, context=context):
            if so.integrated_trade and so.order_policy != 'picking':
                return False
        return True

    _constraints = [
        (
            _check_integrated_trade_order_policy,
            """Error: The module 'Integrated Trade' Only works with"""
            """ 'Order Policy' set to 'Picking'.""",
            ['integrated_trade', 'order_policy']),
    ]

    # Private Function
    def _get_res_integrated_trade(
            self, cr, uid, customer_partner_id, supplier_company_id,
            context=None):
        rit_obj = self.pool['res.integrated.trade']
        rit_id = rit_obj.search(cr, uid, [
            ('customer_partner_id', '=', customer_partner_id),
            ('supplier_company_id', '=', supplier_company_id),
        ], context=context)[0]
        return rit_obj.browse(cr, uid, rit_id, context=context)

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        rp_obj = self.pool['res.partner']
        po_obj = self.pool['purchase.order']
        iv_obj = self.pool['ir.values']

        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_purchase_order = (
            not context.get('integrated_trade_do_not_propagate', False) and
            rp.integrated_trade)

        if create_purchase_order:
            line_ids = vals['order_line']
            vals.pop('order_line')

        res = super(sale_order, self).create(
            cr, uid, vals, context=context)

        if create_purchase_order:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True

            # Create associated Purchase Order
            so = self.browse(cr, uid, res, context=context)
            rit = self._get_res_integrated_trade(
                cr, uid, so.partner_id.id, so.company_id.id, context=context)

            # Get default warehouse
            sw_id = iv_obj.get_default(
                cr, rit.customer_user_id.id, 'purchase.order', 'warehouse_id',
                company_id=rit.customer_company_id.id)
            # Get default stock location
            sl_id = po_obj.onchange_warehouse_id(
                cr, rit.customer_user_id.id, [], sw_id)['value']['location_id']
            # Get default purchase Pricelist
            rp2 = rp_obj.browse(
                cr, rit.customer_user_id.id, rit.supplier_partner_id.id,
                context=context)

            po_vals = {
                'company_id': rit.customer_company_id.id,
                'partner_id': rit.supplier_partner_id.id,
                'warehouse_id': sw_id,
                'location_id': sl_id,
                'integrated_trade_sale_order_id': res,
                'pricelist_id': rp2.property_product_pricelist_purchase.id,
                'partner_ref': so.name,
            }
            po_id = po_obj.create(
                cr, rit.customer_user_id.id, po_vals, context=ctx)
            po = po_obj.browse(
                cr, rit.customer_user_id.id, po_id, context=ctx)

            # Update Sale Order
            self.write(cr, uid, [res], {
                'integrated_trade_purchase_order_id': po.id,
                'client_order_ref': po.name,
                'order_line': line_ids,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        context = context if context else {}
        res = super(sale_order, self).write(
            cr, uid, ids, vals, context=context)
        if 'integrated_trade_do_not_propagate' not in context.keys():
            for so in self.browse(cr, uid, ids, context=context):
                if so.integrated_trade:
                    if 'partner_id' in vals:
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the customer because"""
                                """ of 'Integrated Trade' Rules'. Please"""
                                """ create a new one Sale Order."""))
                    # Disable possibility to change lines if the Sale
                    # Order is not a 'draft' state
                    if (so.state not in ['draft', 'cancel'] and
                            vals.get('order_line', False)):
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change Lines of a Sent Sale"""
                            """Order because of 'Integrated 'Trade' Rules."""
                            """ Please ask to your Customer to cancel the"""
                            """ Purchase Order and create a new one,"""
                            """ duplicating it."""))
        return res

    def action_button_confirm(self, cr, uid, ids, context=None):
        sp_obj = self.pool['stock.picking']
        wf_service = netsvc.LocalService('workflow')
        res = super(sale_order, self).action_button_confirm(
            cr, uid, ids, context=context)
        so = self.browse(cr, uid, ids[0], context=context)
        if so.integrated_trade:
            rit = self._get_res_integrated_trade(
                cr, uid, so.partner_id.id, so.company_id.id, context=context)

            # Validate The according Purchase Order
            wf_service.trg_validate(
                rit.customer_user_id.id, 'purchase.order',
                so.integrated_trade_purchase_order_id.id,
                'purchase_confirm', cr)

            # Get Picking In generated (from purchase)
            spi_id = sp_obj.search(cr, rit.customer_user_id.id, [
                ('purchase_id', '=', so.integrated_trade_purchase_order_id.id)],
                context=context)[0]

            # Get Picking Out generated (from sale)
            spo_id = sp_obj.search(cr, uid, [
                ('sale_id', '=', so.id)],
                context=context)[0]

            import pdb; pdb.set_trace()
            # Associate Picking Out and Picking In
            sp_obj.write(cr, uid, [spo_id], {
                'integrated_trade_picking_in_id': spi_id}, context=context)
            sp_obj.write(cr, rit.customer_user_id.id, [spi_id], {
                'integrated_trade_picking_out_id': spo_id}, context=context)

        return res
