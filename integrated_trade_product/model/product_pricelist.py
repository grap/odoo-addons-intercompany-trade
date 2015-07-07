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

from openerp.osv.orm import Model


class product_pricelist(Model):
    _inherit = 'product.pricelist'

    #TODO FIXME
    # Set param -> RIT so, reduce params quantity
    # check supplier_partner, is it better customer_partner ?
    def _compute_integrated_prices(
            self, cr, uid, supplier_product,
            supplier_partner, pricelist,
            context=None):
        """
        This function return the purchase price of a product, depending
        of a supplier product, and a pricelist defined in the customer
        company

        :param @supplier_product (product.product):
             Product to sell in the SUPPLIER database;
        :param @supplier_partner (res.partner):
            Supplier in the CUSTOMER database;
        : pricelist (product.pricelist):
            Sale Pricelist in the SUPPLIER database;

        :returns:
            return a dictionary containing supplier price.

        """
        # Compute Sale Price
        supplier_price = self.price_get(
            cr, uid, [pricelist.id],
            supplier_product.id,
            1.0, supplier_partner.id, {
                'uom': supplier_product.uom_id.id,
                'date': date.today().strftime('%Y-%m-%d'),
            })[pricelist.id]
        res = {
            'supplier_sale_price': supplier_price,
        }
        return res
