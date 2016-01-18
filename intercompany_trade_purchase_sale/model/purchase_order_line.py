# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase module for OpenERP
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
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

from openerp.addons.intercompany_trade_product.model.custom_tools\
    import _get_other_product_info


class purchase_order_line(Model):
    _inherit = 'purchase.order.line'

    # Columns Section
    _columns = {
        'intercompany_trade': fields.related(
            'order_id', 'intercompany_trade', type='boolean',
            string='Intercompany Trade'),
        'intercompany_trade_sale_order_line_id': fields.many2one(
            'sale.order.line', string='Intercompany Trade Sale Order Line',
            readonly=True,
        ),
    }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create the according Sale Order Line."""
        context = context and context or {}

        rit_obj = self.pool['intercompany.trade.config']
        po_obj = self.pool['purchase.order']
        sol_obj = self.pool['sale.order.line']

        po = po_obj.browse(cr, uid, vals['order_id'], context=context)
        create_sale_order_line = (
            not context.get('intercompany_trade_do_not_propagate', False) and
            po.intercompany_trade)

        # Call Super: Create
        res = super(purchase_order_line, self).create(
            cr, uid, vals, context=context)

        if create_sale_order_line:
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            # Get Created Purchase Order Line
            pol = self.browse(cr, uid, res, context=context)

            # Get Intercompany Trade
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, po.partner_id.id, po.company_id.id, 'in',
                context=context)

            # Prepare and create associated Sale Order Line
            sol_vals = self.prepare_intercompany_sale_order_line(
                cr, uid, pol, rit, context=context)

            sol_id = sol_obj.create(
                cr, rit.supplier_user_id.id, sol_vals, context=ctx)

            # Update associated Sale Order Line to Force the call of the
            # the function '_amount_all'
            sol_obj.write(
                cr, rit.supplier_user_id.id, [sol_id], {
                    'intercompany_trade_purchase_order_line_id': pol.id,
                    'price_unit': sol_vals['price_unit'],
                }, context=ctx)

            sol = sol_obj.browse(
                cr, rit.supplier_user_id.id, sol_id, context=ctx)

            # Update Purchase Order line with Sale Order Line id created
            # Special : update price unit, because the purchaser can NOT
            # set (or change) price unit. And we use the precision of saler
            # and not the precision of the purchaser.
            self.write(cr, uid, [res], {
                'intercompany_trade_sale_order_line_id': sol_id,
                'price_unit': sol.price_unit,
            }, context=ctx)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Sale Order Line with new data.
            - Block some changes of product."""
        context = context and context or {}
        sol_obj = self.pool['sale.order.line']
        rit_obj = self.pool['intercompany.trade.config']

        res = super(purchase_order_line, self).write(
            cr, uid, ids, vals, context=context)

        if not context.get('intercompany_trade_do_not_propagate', False):
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for pol in self.browse(cr, uid, ids, context=context):
                if pol.intercompany_trade_sale_order_line_id:
                    # Block some changes of product
                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product '%s'\n."""
                                """ Please remove this line and create"""
                                """ a new one.""" % (pol.product_id.name)))
                    if 'product_uom' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the UoM of the Product"""
                                """ %s.""" % (pol.product_id.name)))
                    if 'price_unit' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the Price for"""
                                """ the product '%s'."""
                                """ Please ask to your supplier.""" % (
                                    pol.product_id.name)))

                    # Get Intercompany Trade
                    rit = rit_obj._get_intercompany_trade_by_partner_company(
                        cr, uid, pol.order_id.partner_id.id,
                        pol.order_id.company_id.id, 'in', context=context)

                    # Prepare and update associated Sale Order line
                    if pol.state != 'confirmed':
                        # Note : we will not update according sale order
                        # if purchase state is confirmed because it will
                        # recompute purchase that could be false
                        sol_vals = self.prepare_intercompany_sale_order_line(
                            cr, uid, pol, rit, context=context)

                        sol_obj.write(
                            cr, rit.supplier_user_id.id,
                            [pol.intercompany_trade_sale_order_line_id.id],
                            sol_vals, context=ctx)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Sale Order Line."""
        if not context:
            context = {}
        sol_obj = self.pool['sale.order.line']
        rit_obj = self.pool['intercompany.trade.config']
        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for pol in self.browse(cr, uid, ids, context=context):
                if pol.intercompany_trade:
                    rit = rit_obj._get_intercompany_trade_by_partner_company(
                        cr, uid, pol.order_id.partner_id.id,
                        pol.order_id.company_id.id, 'in', context=context)
                    sol_obj.unlink(
                        cr, rit.supplier_user_id.id,
                        [pol.intercompany_trade_sale_order_line_id.id],
                        context=ctx)
        res = super(purchase_order_line, self).unlink(
            cr, uid, ids, context=context)
        return res

    # Custom Section
    def prepare_intercompany_sale_order_line(
            self, cr, uid, pol, rit, context=None):
        sol_obj = self.pool['sale.order.line']
        # Get Product info of the other part
        other_product_info = _get_other_product_info(
            self.pool, cr, uid, rit, pol.product_id.id, 'in',
            context=context)

        res = sol_obj.product_id_change(
            cr, rit.supplier_user_id.id, False, rit.sale_pricelist_id.id,
            other_product_info['product_id'], qty=pol.product_qty,
            uom=pol.product_uom.id, partner_id=rit.customer_partner_id.id,
            context=context)['value']

        res.update({
            'order_id': pol.order_id.intercompany_trade_sale_order_id.id,
            'product_id': other_product_info['product_id'],
            'delay': 0,
            'tax_id': (res['tax_id'] and [[6, False, res['tax_id']]] or False),
            'product_uom': (
                res['product_uos'] and
                res['product_uos'] or pol.product_uom.id),
            'product_uom_qty': pol.product_qty,
            'product_uos_qty': pol.product_qty,
        })
        return res
