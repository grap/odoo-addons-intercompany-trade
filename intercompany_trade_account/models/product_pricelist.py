# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class ProductPricelist(Model):
    _inherit = 'product.pricelist'

    # Overlad Section
    def _compute_intercompany_trade_prices(
            self, cr, uid, supplier_product,
            supplier_partner, pricelist,
            context=None):
        """
        This function Overload the original one, adding tax exclude / incude
        values;
        Sale price is always said as taxes excluded;
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
            'supplier_sale_price_tax_excluded': tax_info['total'],
            'supplier_sale_price_tax_included': tax_info['total_included'],
            'supplier_tax_name': ', '.join(
                [x.name for x in supplier_product.taxes_id])
        })
        return res
