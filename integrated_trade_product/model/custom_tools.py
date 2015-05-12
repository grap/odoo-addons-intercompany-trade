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


def _compute_integrated_price(
        pool, cr, uid, supplier_product, supplier_product_uom,
        supplier_partner, pricelist, customer_product=False,
        context=None):
        # TODO supplier_product_uom: ?? Check if supplier_product is sufficient
        """
        This xxx

        :param supplier_product (product.product):
             Product to sell in the supplier database;
        :param supplier_product_uom (product.uom):
            
             UoM of the supplier product;
        :param supplier_partner (res.partner):
            Supplier in the CUSTOMER Database;
        : pricelist (product.pricelist):
            Sale Pricelist in the supplier database;
        :returns: return a dictionary containing
        """
        ppl_obj = pool['product.pricelist']
        at_obj = pool['account.tax']
        # Compute Sale Price
        supplier_price = ppl_obj.price_get(
            cr, uid, [pricelist.id],
            supplier_product.id,
            1.0, supplier_partner.id, {
                'uom': supplier_product_uom.id,
                'date': date.today().strftime('%Y-%m-%d'),
            })[pricelist.id]
        # Compute Taxes detail
        tax_info = at_obj.compute_all(
            cr, uid, supplier_product.taxes_id,
            supplier_price, 1.0, supplier_product.id)
        return {
            'supplier_sale_price': supplier_price,
            'supplier_sale_price_vat_excl': tax_info['total'],
            'supplier_sale_price_vat_incl': tax_info['total_included'],
        }
