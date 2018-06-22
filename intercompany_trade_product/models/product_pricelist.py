# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_intercompany_trade_prices(
            self, supplier_product, supplier_partner):
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
        self.ensure_one()
        dp_obj = self.env['decimal.precision']
        # Compute Sale Price
        supplier_price = self.sudo().price_get(
            supplier_product.id, 1.0, supplier_partner.id)[self.id]
        dp = dp_obj.precision_get('Intercompany Trade Product Price')
        res = {
            'supplier_sale_price': round(supplier_price, dp),
        }
        return res
