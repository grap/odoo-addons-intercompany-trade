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

from datetime import datetime

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

from openerp.addons.integrated_trade_product.model.custom_tools \
    import _compute_integrated_customer_price


class sale_order_line(Model):
    _inherit = 'sale.order.line'

    # Columns Section
    _columns = {
        'integrated_trade_purchase_order_line_id': fields.many2one(
            'purchase.order.line',
            string='Integrated Trade Purchase Order Line', readonly=True,
        ),
    }

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
        """Create the according Purchase Order Line."""
        context = context and context or {}
        pp_obj = self.pool['product.product']
        so_obj = self.pool['sale.order']
        pol_obj = self.pool['purchase.order.line']
        psi_obj = self.pool['product.supplierinfo']

        so = so_obj.browse(cr, uid, vals['order_id'], context=context)
        create_purchase_order_line = (
            not context.get('integrated_trade_do_not_propagate', False) and
            so.integrated_trade)

        # Call Super: Create
        res = super(sale_order_line, self).create(
            cr, uid, vals, context=context)

        if create_purchase_order_line:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True

            rit = self._get_res_integrated_trade(
                cr, uid, so.partner_id.id, so.company_id.id, context=context)

            # Create associated Purchase Order Line
            # TODO Check if taxes are changed (with products value)
            sol = self.browse(cr, uid, res, context=context)
            psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
                ('supplier_product_id', '=', sol.product_id.id),
                ('name', '=', rit.supplier_partner_id.id),
                ('company_id', '=', rit.customer_company_id.id),
            ], context=context)
            if len(psi_ids) == 0:
                raise except_osv(
                    _("Product Selection Error!"),
                    _("""You can not add the product '%s' to the current"""
                        """ Sale Order because the customer didn't"""
                        """ referenced your product. Please contact him and"""
                        """ say him to do it.""" % (
                            sol.product_id.name)))
            psi = psi_obj.browse(cr, SUPERUSER_ID, psi_ids[0], context=context)
            customer_pp_ids = pp_obj.search(cr, SUPERUSER_ID, [
                ('company_id', '=', rit.customer_company_id.id),
                ('product_tmpl_id', '=', psi.product_id.id),
            ], context=context)
            if len(customer_pp_ids) != 1:
                raise except_osv(
                    _("Product Selection Error!"),
                    _("""You can not add the product '%s' to the current"""
                        """ Sale Order because the customer referenced many"""
                        """ variants of this product. Please contact him and"""
                        """ say him to add the product to him purchase"""
                        """ order.""" % (
                            sol.product_id.name)))
            else:
                customer_pp = pp_obj.browse(
                    cr, SUPERUSER_ID, customer_pp_ids[0], context=context)

            price_info = _compute_integrated_customer_price(
                self.pool, cr, SUPERUSER_ID, sol.product_id, customer_pp,
                (100 - sol.discount) / 100 * sol.price_unit, context=context)

            pol_vals = {
                'order_id': sol.order_id.integrated_trade_purchase_order_id.id,
                'price_unit': 0,
                'name': '[%s] %s' % (
                    sol.product_id.default_code, sol.product_id.name),
                'product_id': customer_pp.id,
                'product_qty': sol.product_uom_qty,
                'product_uom': sol.product_uom.id,
                'integrated_trade_sale_order_line_id': sol.id,
                'date_planned': datetime.now().strftime('%d-%m-%Y'),
                'taxes_id': [[6, False, price_info['customer_taxes_id']]],
            }

            pol_id = pol_obj.create(
                cr, rit.customer_user_id.id, pol_vals, context=ctx)
            # Force the call of the _amount_all
            pol_obj.write(
                cr, rit.customer_user_id.id, pol_id, {
                    'price_unit': price_info['customer_purchase_price'],
                }, context=ctx)

            # Update Sale Order line
            self.write(cr, uid, res, {
                'integrated_trade_purchase_order_line_id': pol_id,
            }, context=ctx)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Purchase Order Line with new data;
            - Block any changes of product."""
        context = context and context or {}
        pol_obj = self.pool['purchase.order.line']
        pp_obj = self.pool['product.product']

        res = super(sale_order_line, self).write(
            cr, uid, ids, vals, context=context)

        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for sol in self.browse(cr, SUPERUSER_ID, ids, context=context):
                pol = sol.integrated_trade_purchase_order_line_id
                if pol:
                    rit = self._get_res_integrated_trade(
                        cr, uid, sol.order_id.partner_id.id,
                        sol.order_id.company_id.id, context=context)
                    customer_pp = pp_obj.browse(
                        cr, SUPERUSER_ID, pol.product_id.id, context=context)
                    pol_vals = {}

                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product '%s'.\n"""
                                """ Please remove this line and choose a"""
                                """ a new one.""" % (sol.product_id.name)))
                    if 'tax_id' in vals.keys():
                        raise except_osv(
                            _("Integrated Trade Error!"),
                            _("""You can not change Taxes in a Sale"""))
                    if 'product_uom_qty' in vals:
                        pol_vals['product_qty'] = sol.product_uom_qty
                    if 'product_uom' in vals:
                        pol_vals['product_uom'] = sol.product_uom.id
                    if 'discount' in vals or 'price_unit' in vals:
                        pol_vals['discount'] = sol.discount
                        price_info = _compute_integrated_customer_price(
                            self.pool, cr, SUPERUSER_ID, sol.product_id,
                            customer_pp,
                            (100 - sol.discount) / 100 * sol.price_unit,
                            context=context)
                        pol_vals['price_unit'] =\
                            price_info['customer_purchase_price']

                    pol_obj.write(
                        cr, rit.customer_user_id.id,
                        pol.id,
                        pol_vals, context=ctx)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Purchase Order Line."""
        pol_obj = self.pool['purchase.order.line']
        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for sol in self.browse(cr, uid, ids, context=context):
                rit = self._get_res_integrated_trade(
                    cr, uid, sol.order_id.partner_id.id,
                    sol.order_id.company_id.id, context=context)
                pol_obj.unlink(
                    cr, rit.customer_user_id.id,
                    [sol.integrated_trade_purchase_order_line_id.id],
                    context=ctx)
        res = super(sale_order_line, self).unlink(
            cr, uid, ids, context=context)
        return res
