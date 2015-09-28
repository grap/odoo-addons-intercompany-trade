# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Base module for OpenERP
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
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


class intercompany_trade_config(Model):
    _inherit = 'intercompany.trade.config'

    # Compute Section
    def _get_intercompany_trade_from_sale_pricelist(
            self, cr, uid, ids, context=None):
        """Return Intercompany Trade ids depending on changes of Sale
        Pricelist"""
        res = []
        rp_obj = self.pool['res.partner']
        rit_obj = self.pool['intercompany.trade.config']
        for rp in rp_obj.browse(cr, uid, ids, context=context):
            if rp.intercompany_trade and rp.customer:
                res.extend(rit_obj.search(cr, uid, [
                    ('customer_partner_id', '=', rp.id),
                ], context=context))
        return list(set(res))

    def _get_sale_pricelist_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        rp_obj = self.pool['res.partner']
        for rit in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx['force_company'] = rit.supplier_company_id.id
            rp = rp_obj.browse(
                cr, uid, rit.customer_partner_id.id, context=ctx)
            res[rit.id] = rp.property_product_pricelist.id
        return res

    # Columns section
    _columns = {
        'sale_pricelist_id': fields.function(
            _get_sale_pricelist_id,
            string='Sale Pricelist in the Supplier Company',
            type='many2one', relation='product.pricelist', store={
                'res.partner': (
                    _get_intercompany_trade_from_sale_pricelist,
                    ['property_product_pricelist'], 10),
                'intercompany.trade.config': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['customer_partner_id', 'supplier_company_id'], 10),
            }),
    }

    # Custom Section
    def _prepare_product_supplierinfo(
            self, cr, uid, id, supplier_product_id,
            customer_product_id, context=None):
        """
        This function prepares supplier_info values.
        Please overload this function to change the datas of the supplierinfo
        created when a link between two products is done."""
        pp_obj = self.pool['product.product']
        ppl_obj = self.pool['product.pricelist']
        rit = self.browse(cr, uid, id, context=context)
        supplier_pp = pp_obj.browse(
            cr, rit.supplier_user_id.id, supplier_product_id, context=context)
        price_info = ppl_obj._compute_intercompany_trade_prices(
            cr, rit.supplier_user_id.id, supplier_pp,
            rit.supplier_partner_id, rit.sale_pricelist_id, context=context)
        return {
            'min_qty': 0.0,
            'name': rit.supplier_partner_id.id,
            'product_name': supplier_pp.name,
            'product_code': supplier_pp.default_code,
            'company_id': rit.customer_company_id.id,
            'supplier_product_id': supplier_pp.id,
            'pricelist_ids': [[5], [0, False, {
                'min_quantity': 0.0,
                'price': price_info['supplier_sale_price']}]],
        }
