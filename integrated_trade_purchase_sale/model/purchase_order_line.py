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

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv.orm import Model


class purchase_order_line(Model):
    _inherit = 'purchase.order.line'

    # Fields Function Section
    def _get_integrated_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pol in self.browse(cr, uid, ids, context=context):
            res[pol.id] = pol.order_id.partner_id.integrated_trade
        return res

    # Columns Section
    _columns = {
        'integrated_trade': fields.function(
            _get_integrated_trade, type='boolean', string='Integrated Trade',
            store={'purchase.order.line': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'order_id',
                ], 10)}),
        'integrated_trade_sale_order_line_id': fields.many2one(
            'sale.order.line', string='Integrated Trade Sale Order Line',
            readonly=True,
        ),
    }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        print "*******************\npol::create"
        print vals
        po_obj = self.pool['purchase.order']
        po = po_obj.browse(cr, uid, vals['order_id'], context=context)
        create_sale_order_line = (
            not vals.get('integrated_trade_sale_order_line_id', False)
            and po.integrated_trade)

        res = super(purchase_order_line, self).create(
            cr, uid, vals, context=context)

        if create_sale_order_line:
            sol_obj = self.pool['sale.order.line']
            psi_obj = self.pool['product.supplierinfo']
            rit_obj = self.pool['res.integrated.trade']

#            # Create associated Sale Order Line
            pol = self.browse(cr, SUPERUSER_ID, res, context=context)
            psi_id = psi_obj.search(cr, uid, [
                ('product_id', '=', pol.product_id.id),
                ('name', '=', pol.order_id.partner_id.id),
            ], context=context)[0]
            psi = psi_obj.browse(cr, SUPERUSER_ID, psi_id, context=context)
            rit_id = rit_obj.search(cr, uid, [
                ('supplier_partner_id', '=', po.partner_id.id),
                ('customer_company_id', '=', po.company_id.id),
            ], context=context)[0]
            rit = rit_obj.browse(cr, uid, rit_id, context=context)

            sol_vals = {
                'order_id': pol.order_id.integrated_trade_sale_order_id.id,
                'price_unit': pol.price_unit,
                'name': '[%s] %s' % (
                    pol.product_id.default_code, pol.product_id.name),
                'product_id': psi.supplier_product_id.id,  # TODO,
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
                cr, rit.supplier_user_id.id, sol_vals, context=context)

#            # Update Purchase Order line
            self.write(cr, uid, res, {
                'integrated_trade_sale_order_line_id': sol_id,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # TODO Disable changing product_id
        print "*******************\npol::write"
        res = super(purchase_order_line, self).write(
            cr, uid, ids, vals, context=context)
        return res
