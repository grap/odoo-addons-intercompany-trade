# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Product module for OpenERP
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

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.addons import decimal_precision as dp

from .custom_tools import _compute_integrated_prices


class product_supplierinfo(Model):
    _inherit = 'product.supplierinfo'

    def _integrated_trade_update_multicompany(
            self, cr, uid, supplier_product_ids, context=None):
        """
        This function update supplierinfo in customer database,
        depending of changes in supplier database, for all integrated trade
        define.
        Call this function when there is a change of product price,
        product taxes, partner pricelist, etc...
        :supplier_product_ids (list of ids of product.product):
            products that has been changed in the supplier database;
        """
        rit_obj = self.pool['res.integrated.trade']
        psi_obj = self.pool['product.supplierinfo']
        for supplier_product_id in supplier_product_ids:
            psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
                ('supplier_product_id', '=', supplier_product_id),
            ], context=context)
            for psi in psi_obj.browse(
                    cr, SUPERUSER_ID, psi_ids, context=context):
                rit_id = rit_obj.search(cr, uid, [
                    ('customer_company_id', '=', psi.company_id.id),
                    ('supplier_partner_id', '=', psi.name.id),
                ], context=context)[0]
                self._integrated_trade_update(
                    cr, uid, rit_id, [supplier_product_id],
                    context=context)

    def _integrated_trade_update(
            self, cr, uid, integrated_trade_id, supplier_product_ids,
            context=None):
        """
        This function update supplierinfo in customer database,
        depending of changes in supplier database, depending of
        a specific integrated trade.
        Call this function when there is a change of product price,
        product taxes, partner pricelist, etc...
        :param integrated_trade_id (id of res.integrated.trade):
            integrated trade impacted;
        :supplier_product_ids (list of ids of product.product):
            products that has been changed in the supplier database;
        """
        rit_obj = self.pool['res.integrated.trade']
        rit = rit_obj.browse(cr, uid, integrated_trade_id, context=context)
        if not supplier_product_ids:
            # Global Update
            psi_ids = self.search(cr, SUPERUSER_ID, [
                ('name', '=', rit.supplier_partner_id.id),
            ], context=context)
        else:
            psi_ids = self.search(cr, SUPERUSER_ID, [
                ('name', '=', rit.supplier_partner_id.id),
                ('supplier_product_id', 'in', supplier_product_ids)
            ], context=context)
        for psi in self.browse(cr, uid, psi_ids, context=context):
            psi_vals = self._integrated_trade_prepare(
                cr, uid, integrated_trade_id, psi.supplier_product_id.id,
                context=context)
            self.write(
                cr, SUPERUSER_ID, [psi.id], psi_vals, context=context)

    # Overloadable Section
    def _integrated_trade_prepare(
            self, cr, uid, integrated_trade_id, supplier_product_id,
            customer_product_id, context=None):
        """
        This function prepares supplier_info values.
        Please overload this function to change the datas of the supplierinfo
        created when a link between two products is done."""
        pp_obj = self.pool['product.product']
        rit_obj = self.pool['res.integrated.trade']
        rit = rit_obj.browse(
            cr, SUPERUSER_ID, integrated_trade_id, context=context)
        supplier_pp = pp_obj.browse(
            cr, SUPERUSER_ID, supplier_product_id, context=context)
        customer_pp = pp_obj.browse(
            cr, SUPERUSER_ID, customer_product_id, context=context)
        price_info = _compute_integrated_prices(
            self.pool, cr, SUPERUSER_ID, supplier_pp,
            rit.supplier_partner_id, rit.pricelist_id,
            customer_product=customer_pp, context=context)
        return {
            'min_qty': 0.0,
            'name': rit.supplier_partner_id.id,
            'product_name': supplier_pp.name,
            'product_code': supplier_pp.default_code,
            'company_id': rit.customer_company_id.id,
            'supplier_product_id': supplier_pp.id,
            'pricelist_ids': [[5], [0, False, {
                'min_quantity': 0.0,
                'price': price_info['customer_purchase_price']}]],
        }

    # Fields Function Section
    def _get_integrated_price(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for psi in self.browse(cr, uid, ids, context=context):
            if psi.supplier_product_id and psi.pricelist_ids:
                res[psi.id] = psi.pricelist_ids[0].price
            else:
                res[psi.id] = 0
        return res

    _columns = {
        'integrated_price': fields.function(
            _get_integrated_price, string='Unit Price', type='float',
            digits_compute=dp.get_precision('Integrated Product Price'),
            store={'product.supplierinfo': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'supplier_product_id',
                    'pricelist_ids',
                ], 10)}),
        'supplier_product_id': fields.many2one(
            'product.product', 'Product in the Supplier Catalog',
            readonly=True, selected=True),
    }
