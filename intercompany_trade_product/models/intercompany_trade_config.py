# -*- encoding: utf-8 -*-
# Copyright (C) 2014 - Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class IntercompanyTradeConfig(models.Model):
    _inherit = 'intercompany.trade.config'

    # Compute Section
    @api.depends(
        'supplier_company_id',
        'customer_partner_id.property_product_pricelist')
    def _compute_sale_pricelist_id(self):
        partner_obj = self.env['res.partner']
        for config in self:
            partner = partner_obj.with_context(
                force_company=config.supplier_company_id.id).browse(
                    config.customer_partner_id.id)
            config.sale_pricelist_id = partner.property_product_pricelist

    # Columns section
    sale_pricelist_id = fields.Many2one(
        string='Sale Pricelist', comodel_name='product.pricelist',
        compute=_compute_sale_pricelist_id, store=True,
        help="Sale Pricelist in the Supplier Company")

    # Custom Section
    @api.multi
    def _prepare_product_supplierinfo(
            self, supplier_product_id, customer_product_id):
        """
        This function prepares supplier_info values.
        Please overload this function to change the datas of the supplierinfo
        created when a link between two products is done."""
        self.ensure_one()
        product_obj = self.env['product.product']
        pricelist_obj = self.env['product.pricelist']
        supplierinfo_obj = self.env['product.supplierinfo']
        vals = supplierinfo_obj._add_missing_default_values({})
        supplier_product = product_obj.sudo(user=self.supplier_user_id).browse(
            supplier_product_id)
        price_info = pricelist_obj.sudo(
            user=self.supplier_user_id)._compute_intercompany_trade_prices(
            supplier_product, self.supplier_partner_id, self.sale_pricelist_id)
        vals.update({
            'name': self.supplier_partner_id.id,
            'product_name': supplier_product.name,
            'product_code': supplier_product.default_code,
            'company_id': self.customer_company_id.id,
            'supplier_product_id': supplier_product.id,
            'pricelist_ids': [[5], [0, False, {
                'min_quantity': 0.0,
                'price': price_info['supplier_sale_price']}]],
        })
        return vals
