# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Product module for Odoo
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

from datetime import date


def _compute_supplier_price(
        pool, cr, uid, supplier_product_id, supplier_product_uom,
        supplier_partner_id, pricelist_id):
        # TODO supplier_product_uom: ?? Check if product_id is sufficient
        """
        This xxx

        :param supplier_product_id (product.product):
             Product to sell in the supplier database;
        :param supplier_product_uom (product.uom):
            
             UoM of the supplier product;
        :param supplier_partner_id (res.partner):
            Supplier in the CUSTOMER Database;
        : pricelist_id (product.pricelist):
            Sale Pricelist in the supplier database;
        :returns: return a dictionary containing
        """
        ppl_obj = pool['product.pricelist']
        at_obj = pool['account.tax']
        # Compute Sale Price
        supplier_price = ppl_obj.price_get(
            cr, uid, [pricelist_id.id],
            supplier_product_id.id,
            1.0, supplier_partner_id.id, {
                'uom': supplier_product_uom.id,
                'date': date.today().strftime('%Y-%m-%d'),
            })[pricelist_id.id]
        # Compute Taxes detail
        tax_info = at_obj.compute_all(
            cr, uid, supplier_product_id.taxes_id,
            supplier_price, 1.0, supplier_product_id.id)
        return {
            'supplier_sale_price': supplier_price,
            'supplier_sale_price_vat_excl': tax_info['total'],
            'supplier_sale_price_vat_incl': tax_info['total_included'],
        }
