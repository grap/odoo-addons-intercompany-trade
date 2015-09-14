# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Product module for Odoo
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

from openerp.osv.orm import Model


class ProductPricelist(Model):
    _inherit = 'product.pricelist'

    # Overlad Section
    def _compute_intercompany_trade_prices(
            self, cr, uid, supplier_product,
            supplier_partner, pricelist,
            context=None):
        """
        This function Overload the original one, adding vat exclude / incude
        values;
        Sale price is always said as vat excluded;
        """
        at_obj = self.pool['account.tax']

        res = super(ProductPricelist, self)._compute_intercompany_trade_prices(
            cr, uid, supplier_product, supplier_partner, pricelist,
            context=context)

        # Compute Taxes detail
        tax_info = at_obj.compute_all(
            cr, uid, supplier_product.taxes_id,
            res['supplier_sale_price'], 1.0, supplier_product.id)
        res.update({
            'supplier_sale_price': tax_info['total'],
            'supplier_sale_price_vat_excl': tax_info['total'],
            'supplier_sale_price_vat_incl': tax_info['total_included'],
            'supplier_vat_name': ', '.join(
                [x.name for x in supplier_product.taxes_id])
        })
        return res
