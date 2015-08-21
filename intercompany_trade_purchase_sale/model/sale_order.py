# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase - Sale module for OpenERP
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
    def _get_intercompany_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for so in self.browse(cr, uid, ids, context=context):
            res[so.id] = so.partner_id.intercompany_trade
        return res

    # Columns Section
    _columns = {
        'intercompany_trade': fields.function(
            _get_intercompany_trade, type='boolean', string='Intercompany Trade',
            store={'sale.order': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'intercompany_trade_purchase_order_id': fields.many2one(
            'purchase.order', string='Intercompany Trade Purchase Order',
            readonly=True,
        ),
    }

    # Constraint Section
    def _check_intercompany_trade_order_policy(
            self, cr, uid, ids, context=None):
        for so in self.browse(cr, uid, ids, context=context):
            if so.intercompany_trade and so.order_policy != 'picking':
                return False
        return True

    _constraints = [
        (
            _check_intercompany_trade_order_policy,
            """Error: The module 'Intercompany Trade' Only works with"""
            """ 'Order Policy' set to 'Picking'.""",
            ['intercompany_trade', 'order_policy']),
    ]

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        rit_obj = self.pool['intercompany.trade.config']
        rp_obj = self.pool['res.partner']
        po_obj = self.pool['purchase.order']
        iv_obj = self.pool['ir.values']

        context = context and context or {}

        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_purchase_order = (
            not context.get('intercompany_trade_do_not_propagate', False) and
            rp.intercompany_trade)

        if create_purchase_order:
            line_ids = vals.get('order_line', False)
            vals.pop('order_line', None)

        
        print "uid : %s " % uid
        print "name : %s " % self.pool['res.users'].browse(cr, uid, uid).name
        print vals
        res = super(sale_order, self).create(
            cr, uid, vals, context=context)

        if create_purchase_order:
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            # Create associated Purchase Order
            so = self.browse(cr, uid, res, context=context)
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, so.partner_id.id, so.company_id.id, 'out',
                context=context)

            # Get default warehouse
            sw_id = iv_obj.get_default(
                cr, rit.customer_user_id.id, 'purchase.order', 'warehouse_id',
                company_id=rit.customer_company_id.id)
            # Get default stock location
            sl_id = po_obj.onchange_warehouse_id(
                cr, rit.customer_user_id.id, [], sw_id)['value']['location_id']
#            # Get default purchase Pricelist
#            rp2 = rp_obj.browse(
#                cr, rit.customer_user_id.id, rit.supplier_partner_id.id,
#                context=context)

            po_vals = {
                'company_id': rit.customer_company_id.id,
                'partner_id': rit.supplier_partner_id.id,
                'warehouse_id': sw_id,
                'location_id': sl_id,
                'intercompany_trade_sale_order_id': res,
                'pricelist_id': rit.purchase_pricelist_id.id,
                'partner_ref': so.name,
                'invoice_method': 'picking',
            }
            po_id = po_obj.create(
                cr, rit.customer_user_id.id, po_vals, context=ctx)
            po = po_obj.browse(
                cr, rit.customer_user_id.id, po_id, context=ctx)

            # Update Sale Order
            self.write(cr, uid, [res], {
                'intercompany_trade_purchase_order_id': po.id,
                'client_order_ref': po.name,
                'order_line': line_ids,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        context = context if context else {}
        res = super(sale_order, self).write(
            cr, uid, ids, vals, context=context)
        if 'intercompany_trade_do_not_propagate' not in context.keys():
            for so in self.browse(cr, uid, ids, context=context):
                if so.intercompany_trade:
                    if 'partner_id' in vals:
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the customer because"""
                                """ of Intercompany Trade Rules. Please"""
                                """ create a new one Sale Order."""))
                    # Disable possibility to change lines if the Sale
                    # Order is not a 'draft' state
                    if (so.state not in ['draft', 'cancel'] and
                            vals.get('order_line', False)):
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change Lines of a Sent Sale"""
                                """ Order because of Intercompany Trade"""
                                """ Rules. Please ask to your Customer to"""
                                """ cancel the Purchase Order and create a"""
                                """ new one, duplicating it."""))
        return res

    def unlink(self, cr, uid, ids, context=None):
        """Delete according Purchase order"""
        context = context if context else {}

        rit_obj = self.pool['intercompany.trade.config']
        po_obj = self.pool['purchase.order']

        ctx = context.copy()
        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx['intercompany_trade_do_not_propagate'] = True
            for so in self.browse(cr, uid, ids, context=context):
                rit = rit_obj._get_intercompany_trade_by_partner_company(
                    cr, uid, so.partner_id.id, so.company_id.id, 'out',
                    context=context)
                if so.intercompany_trade:
                    po_obj.unlink(
                        cr, rit.customer_user_id.id,
                        [so.intercompany_trade_purchase_order_id.id],
                        context=ctx)
        return super(sale_order, self).unlink(
            cr, uid, ids, context=ctx)

    def action_button_confirm(self, cr, uid, ids, context=None):
        sp_obj = self.pool['stock.picking']
        sm_obj = self.pool['stock.move']
        spp_wizard_obj = self.pool['stock.partial.picking']
        rit_obj = self.pool['intercompany.trade.config']
        wf_service = netsvc.LocalService('workflow')

        res = super(sale_order, self).action_button_confirm(
            cr, uid, ids, context=context)
        so = self.browse(cr, uid, ids[0], context=context)
        if so.intercompany_trade:
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, so.partner_id.id, so.company_id.id, 'out',
                context=context)

            # Validate The according Purchase Order
            wf_service.trg_validate(
                rit.customer_user_id.id, 'purchase.order',
                so.intercompany_trade_purchase_order_id.id,
                'purchase_confirm', cr)

            # Get Picking In generated (from purchase)
            spi_id = sp_obj.search(cr, rit.customer_user_id.id, [
                ('purchase_id', '=',
                    so.intercompany_trade_purchase_order_id.id)],
                context=context)[0]

            # Get Picking Out generated (from sale)
            spo_id = sp_obj.search(cr, uid, [
                ('sale_id', '=', so.id)],
                context=context)[0]

            # Associate Picking Out and Picking In
            sp_obj.write(cr, uid, [spo_id], {
                'intercompany_trade_picking_in_id': spi_id}, context=context)
            sp_obj.write(cr, rit.customer_user_id.id, [spi_id], {
                'intercompany_trade_picking_out_id': spo_id}, context=context)

            # FIXME : set this part of code in a module
            # intercompany_trade_stock
            # Confirm Supplier Picking Out
            sp_obj.action_assign(
                cr, uid, [spo_id], context)
            sp_obj.force_assign(cr, uid, [spo_id])
            ctx = context.copy()
            ctx['active_ids'] = [spo_id]
            ctx['active_model'] = 'stock.picking.out'
            spp_wizard_id = spp_wizard_obj.create(
                cr, uid, {}, context=ctx)
            spp_wizard_obj.do_partial(
                cr, uid, [spp_wizard_id], context=context)

            # Confirm Customer Picking In
            ctx = context.copy()
            ctx['active_ids'] = [spi_id]
            ctx['active_model'] = 'stock.picking.in'
            spp_wizard_id = spp_wizard_obj.create(
                cr, rit.customer_user_id.id, {}, context=ctx)
            spp_wizard_obj.do_partial(
                cr, rit.customer_user_id.id, [spp_wizard_id], context=context)

            # Link Stock moves
            for sol in so.order_line:
                sol_id = sol.id
                pol_id = sol.intercompany_trade_purchase_order_line_id.id

                sm_sol_id = sm_obj.search(cr, uid, [
                    ('sale_line_id', '=', sol_id)], context=context)[0]

                sm_pol_id = sm_obj.search(cr, rit.customer_user_id.id, [
                    ('purchase_line_id', '=', pol_id)], context=context)[0]

                sm_obj.write(cr, uid, [sm_sol_id], {
                    'intercompany_trade_stock_move_id': sm_pol_id,
                }, context=context)

                sm_obj.write(cr, rit.customer_user_id.id, [sm_pol_id], {
                    'intercompany_trade_stock_move_id': sm_sol_id,
                }, context=context)

        return res
