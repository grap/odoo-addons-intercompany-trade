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

from datetime import datetime

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

from openerp.addons.intercompany_trade_product.model.custom_tools\
    import _get_other_product_info


class sale_order_line(Model):
    _inherit = 'sale.order.line'

    # Columns Section
    _columns = {
        'intercompany_trade': fields.related(
            'order_id', 'intercompany_trade', type='boolean',
            string='Intercompany Trade'),
        'intercompany_trade_purchase_order_line_id': fields.many2one(
            'purchase.order.line',
            string='Intercompany Trade Purchase Order Line', readonly=True,
        ),
    }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create the according Purchase Order Line."""
        context = context and context or {}
        rit_obj = self.pool['intercompany.trade.config']
        so_obj = self.pool['sale.order']
        pol_obj = self.pool['purchase.order.line']

        so = so_obj.browse(cr, uid, vals['order_id'], context=context)
        create_purchase_order_line = (
            not context.get('intercompany_trade_do_not_propagate', False) and
            so.intercompany_trade)

        # Call Super: Create
        res = super(sale_order_line, self).create(
            cr, uid, vals, context=context)

        if create_purchase_order_line:
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True

            # Get Created Sale Order Line
            sol = self.browse(cr, uid, res, context=context)

            # Get Intercompany Trade
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, so.partner_id.id, so.company_id.id, 'out',
                context=context)

            # Prepare and create associated Purchase Order Line
            pol_vals = self.prepare_intercompany_purchase_order_line(
                cr, uid, sol, rit, context=context)

            pol_id = pol_obj.create(
                cr, rit.customer_user_id.id, pol_vals, context=ctx)

            # Force the call of the _amount_all
            pol_obj.write(
                cr, rit.customer_user_id.id, [pol_id], {
                    'price_unit': vals['price_unit'],
                }, context=ctx)

            # Update Sale Order line
            self.write(cr, uid, [res], {
                'intercompany_trade_purchase_order_line_id': pol_id,
            }, context=ctx)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Purchase Order Line with new data;
            - Block any changes of product."""
        context = context and context or {}
        rit_obj = self.pool['intercompany.trade.config']
        pol_obj = self.pool['purchase.order.line']

        res = super(sale_order_line, self).write(
            cr, uid, ids, vals, context=context)

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for sol in self.browse(cr, uid, ids, context=context):
                if sol.intercompany_trade_purchase_order_line_id:
                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product '%s'.\n"""
                                """ Please remove this line and create"""
                                """ a new one.""" % (sol.product_id.name)))

                    # Get Intercompany Trade
                    rit = rit_obj._get_intercompany_trade_by_partner_company(
                        cr, uid, sol.order_id.partner_id.id,
                        sol.order_id.company_id.id, 'out', context=context)

                    # Prepare and update associated Purchase Order Line
                    pol_vals = self.prepare_intercompany_purchase_order_line(
                        cr, uid, sol, rit, context=context)

                    pol_obj.write(
                        cr, rit.customer_user_id.id,
                        [sol.intercompany_trade_purchase_order_line_id.id],
                        pol_vals, context=ctx)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Purchase Order Line."""
        context = context and context or {}
        rit_obj = self.pool['intercompany.trade.config']
        pol_obj = self.pool['purchase.order.line']

        if 'intercompany_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['intercompany_trade_do_not_propagate'] = True
            for sol in self.browse(cr, uid, ids, context=context):
                if sol.intercompany_trade:
                    rit = rit_obj._get_intercompany_trade_by_partner_company(
                        cr, uid, sol.order_id.partner_id.id,
                        sol.order_id.company_id.id, 'out', context=context)
                    pol_obj.unlink(
                        cr, rit.customer_user_id.id,
                        [sol.intercompany_trade_purchase_order_line_id.id],
                        context=ctx)
        res = super(sale_order_line, self).unlink(
            cr, uid, ids, context=context)
        return res

    # Custom Section
    def prepare_intercompany_purchase_order_line(
            self, cr, uid, sol, rit, context=None):
        pol_obj = self.pool['purchase.order.line']

        other_product_info = _get_other_product_info(
            self.pool, cr, uid, rit, sol.product_id.id, 'out',
            context=context)

        res = pol_obj.onchange_product_id(
            cr, rit.customer_user_id.id, False,
            rit.purchase_pricelist_id.id,
            other_product_info['product_id'], sol.product_uom_qty,
            sol.product_uom.id, rit.supplier_partner_id.id,
            context=context)['value']

        res.update({
            'order_id':
                sol.order_id.intercompany_trade_purchase_order_id.id,
            'name': '[%s] %s' % (
                sol.product_id.default_code, sol.product_id.name),
            'price_unit': sol.price_unit,
            'product_id': other_product_info['product_id'],
            'product_qty': sol.product_uom_qty,
            'product_uom': sol.product_uom.id,
            'intercompany_trade_sale_order_line_id': sol.id,
            'date_planned': datetime.now().strftime('%Y-%m-%d'),
            'taxes_id': (
                res['taxes_id'] and [[6, False, res['taxes_id']]] or False),
        })
        return res
