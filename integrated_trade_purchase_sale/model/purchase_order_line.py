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

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class purchase_order_line(Model):
    _inherit = 'purchase.order.line'

    # Columns Section
    _columns = {
        'integrated_trade_sale_order_line_id': fields.many2one(
            'sale.order.line', string='Integrated Trade Sale Order Line',
            readonly=True,
        ),
    }

    # Private Function
    def _get_res_integrated_trade(
            self, cr, uid, supplier_partner_id, customer_company_id,
            context=None):
        rit_obj = self.pool['res.integrated.trade']
        rit_id = rit_obj.search(cr, uid, [
            ('supplier_partner_id', '=', supplier_partner_id),
            ('customer_company_id', '=', customer_company_id),
        ], context=context)[0]
        return rit_obj.browse(cr, uid, rit_id, context=context)

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create the according Sale Order Line."""
        po_obj = self.pool['purchase.order']
        sol_obj = self.pool['sale.order.line']
        psi_obj = self.pool['product.supplierinfo']

        po = po_obj.browse(cr, uid, vals['order_id'], context=context)
        create_sale_order_line = (
            not context.get('integrated_trade_do_not_propagate', False) and
            po.integrated_trade)

        # Call Super: Create
        res = super(purchase_order_line, self).create(
            cr, uid, vals, context=context)

        if create_sale_order_line:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True

            rit = self._get_res_integrated_trade(
                cr, uid, po.partner_id.id, po.company_id.id, context=context)

            # Create associated Sale Order Line
            pol = self.browse(cr, uid, res, context=context)
            psi_ids = psi_obj.search(cr, uid, [
                ('product_id', '=', pol.product_id.product_tmpl_id.id),
                ('name', '=', pol.order_id.partner_id.id),
            ], context=context)
            if len(psi_ids) == 0:
                raise except_osv(
                    _("Product Selection Error!"),
                    _("""You can not add the product '%s' to the current"""
                        """ Purchase Order because you didn't linked the"""
                        """ product to any Supplier Product. Please do it"""
                        """ in the 'Integrated Trade' menu.""" % (
                            pol.product_id.name)))
            psi = psi_obj.browse(cr, uid, psi_ids[0], context=context)

            sol_vals = {
                'order_id': pol.order_id.integrated_trade_sale_order_id.id,
                'price_unit': pol.price_unit,
                'name': '[%s] %s' % (
                    pol.product_id.default_code, pol.product_id.name),
                'product_id': psi.supplier_product_id.id,
                'product_uos_qty': pol.product_qty,
                'product_uos': pol.product_uom.id,
                'product_uom_qty': pol.product_qty,
                'product_uom': pol.product_uom.id,
                'integrated_trade_purchase_order_line_id': pol.id,
                # Constant TODO
                'tax_id': [[6, False, []]],
                # Constant
                'discount': 0,
                'delay': 0,
            }

            sol_id = sol_obj.create(
                cr, rit.supplier_user_id.id, sol_vals, context=ctx)
            # Force the call of the _amount_all
            sol_obj.write(
                cr, rit.supplier_user_id.id, sol_id,
                {'price_unit': pol.price_unit}, context=ctx)

#            # Update Purchase Order line
            self.write(cr, uid, res, {
                'integrated_trade_sale_order_line_id': sol_id,
            }, context=ctx)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Sale Order Line with new data.
            - Block any changes of product."""
        if not context:
            context = {}
        sol_obj = self.pool['sale.order.line']

        res = super(purchase_order_line, self).write(
            cr, uid, ids, vals, context=context)

        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for pol in self.browse(cr, uid, ids, context=context):
                if pol.integrated_trade_sale_order_line_id:
                    rit = self._get_res_integrated_trade(
                        cr, uid, pol.order_id.partner_id.id,
                        pol.order_id.company_id.id, context=context)
                    sol_vals = {}

                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product. %s"""
                                """Please remove this line and choose a"""
                                """ a new one.""" % (pol.product_id.name)))
                    if 'product_qty' in vals:
                        sol_vals['product_uos_qty'] = pol.product_qty
                        sol_vals['product_uom_qty'] = pol.product_qty
                    if 'product_uom' in vals:
                        sol_vals['product_uos'] = pol.product_uom.id
                        sol_vals['product_uom'] = pol.product_uom.id
                    # TODO Manage discount / delay / tax
                    sol_obj.write(
                        cr, rit.supplier_user_id.id,
                        pol.integrated_trade_sale_order_line_id.id,
                        sol_vals, context=ctx)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Sale Order Line."""
        if not context:
            context = {}
        sol_obj = self.pool['sale.order.line']
        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for pol in self.browse(cr, uid, ids, context=context):
                rit = self._get_res_integrated_trade(
                    cr, uid, pol.order_id.partner_id.id,
                    pol.order_id.company_id.id, context=context)
                sol_obj.unlink(
                    cr, rit.supplier_user_id.id,
                    [pol.integrated_trade_sale_order_line_id.id],
                    context=ctx)
        res = super(purchase_order_line, self).unlink(
            cr, uid, ids, context=context)
        return res
