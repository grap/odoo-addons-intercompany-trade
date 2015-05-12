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

#            # Create associated Purchase Order Line
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
            pp_ids = pp_obj.search(cr, SUPERUSER_ID, [
                ('company_id', '=', rit.customer_company_id.id),
                ('product_tmpl_id', '=', psi.product_id.id),
            ], context=context)
            if len(pp_ids) != 1:
                raise except_osv(
                    _("Product Selection Error!"),
                    _("""You can not add the product '%s' to the current"""
                        """ Sale Order because the customer referenced many"""
                        """ variants of this product. Please contact him and"""
                        """ say him to add the product to him purchase"""
                        """ order.""" % (
                            sol.product_id.name)))

            pol_vals = {
                'order_id': sol.order_id.integrated_trade_purchase_order_id.id,
                'price_unit': sol.price_unit,
                'name': '[%s] %s' % (
                    sol.product_id.default_code, sol.product_id.name),
                'product_id': pp_ids[0],
                'product_qty': sol.product_uos_qty,
                'product_uom': sol.product_uos.id,
                'integrated_trade_purchase_order_line_id': sol.id,
                # Constant TODO
                'date_planned': datetime.now().strftime('%d-%m-%Y'),
                'tax_id': [[6, False, []]],
                # Constant
                'discount': 0,
                'delay': 0,
            }

            pol_id = pol_obj.create(
                cr, rit.customer_user_id.id, pol_vals, context=ctx)
            # Force the call of the _amount_all
            pol_obj.write(
                cr, rit.customer_user_id.id, pol_id,
                {'price_unit': sol.price_unit}, context=ctx)

#            # Update Sale Order line
            self.write(cr, uid, res, {
                'integrated_trade_purchase_order_line_id': pol_id,
            }, context=ctx)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Purchase Order Line with new data;
            - Block any changes of product."""
        if not context:
            context = {}
        pol_obj = self.pool['purchase.order.line']

        res = super(sale_order_line, self).write(
            cr, uid, ids, vals, context=context)

        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for sol in self.browse(cr, uid, ids, context=context):
                if sol.integrated_trade_purchase_order_line_id:
                    rit = self._get_res_integrated_trade(
                        cr, uid, sol.order_id.partner_id.id,
                        sol.order_id.company_id.id, context=context)
                    pol_vals = {}

                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product. %s"""
                                """Please remove this line and choose a"""
                                """ a new one.""" % (sol.product_id.name)))
                    if 'product_uom_qty' in vals:
                        pol_vals['product_qty'] = sol.product_uom_qty
                    if 'product_uom' in vals:
                        pol_vals['product_uom'] = sol.product_uom.id
                    # TODO Manage discount / delay / tax
                    pol_obj.write(
                        cr, rit.customer_user_id.id,
                        sol.integrated_trade_purchase_order_line_id.id,
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
