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

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        print "*******************\npo::create"
        print vals
        rp_obj = self.pool['res.partner']
        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
        create_sale_order = (
            not vals.get('integrated_trade_sale_order_id', False)
            and rp.integrated_trade)

        if create_sale_order:
            line_ids = vals['order_line']
            vals.pop('order_line')

        # Peut etre pop line_id et le writer ensuite (plus simple)
        res = super(purchase_order, self).create(
            cr, uid, vals, context=context)

        if create_sale_order:
            so_obj = self.pool['sale.order']
            rit_obj = self.pool['res.integrated.trade']
            iv_obj = self.pool['ir.values']

            # Create associated Sale Order
            po = self.browse(cr, uid, res, context=context)
            rit_id = rit_obj.search(cr, uid, [
                ('supplier_partner_id', '=', po.partner_id.id),
                ('customer_company_id', '=', po.company_id.id),
            ], context=context)[0]
            rit = rit_obj.browse(cr, uid, rit_id, context=context)

            # WEIRD: sale_order has a bad _get_default_shop base on the
            # company of the current user, so we request ir.values
            # to have the correct one

            shop_id = iv_obj.get_default(
                cr, rit.supplier_user_id.id, 'sale.order', 'shop_id',
                company_id=rit.supplier_company_id.id)
            so_vals = {
                'company_id': rit.customer_company_id.id,
                'partner_id': rit.customer_partner_id.id,
                'partner_invoice_id': rit.customer_partner_id.id,
                'partner_shipping_id': rit.customer_partner_id.id,
                'integrated_trade_purchase_order_id': res,
                'shop_id': shop_id,
                'pricelist_id': rit.pricelist_id.id,
                'client_order_ref': po.name,
            }
            print "***** BEFORE"
            so_id = so_obj.create(
                cr, rit.supplier_user_id.id, so_vals, context=context)
            print "***** AFTER"
            so = so_obj.browse(
                cr, rit.supplier_user_id.id, so_id, context=context)
            # Update Purchase Order
            self.write(cr, uid, res, {
                'integrated_trade_sale_order_id': so.id,
                'partner_ref': so.name,
                'order_line': line_ids,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        print "*******************\npo::write"
        res = super(purchase_order, self).write(
            cr, uid, ids, vals, context=context)
        return res
