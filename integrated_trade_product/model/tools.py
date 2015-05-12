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

def _compute_supplier_price(
        pool, cr, uid, supplier_product_id,supplier_product_uom,
        supplier_partner_id):
        """
        This xxx

        :param supplier_product_id (product.product):
             Product to sell in the supplier database;
        :param supplier_product_uom (product.uom):
             UoM of the supplier product;
        :param supplier_partner_id (res.partner):
            Supplier in the CUSTOMER Database;

        :returns: return a dictionary containing
        """
