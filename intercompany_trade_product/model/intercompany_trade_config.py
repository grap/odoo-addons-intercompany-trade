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
    def _prepare_product_supplierinfo(
            self, cr, uid, id, supplier_product_id,
            customer_product_id, context=None):
        """
        This function prepares supplier_info values.
        Please overload this function to change the datas of the supplierinfo
        created when a link between two products is done."""
        pp_obj = self.pool['product.product']
        ppl_obj = self.pool['product.pricelist']
        psi_obj = self.pool['product.supplierinfo']
        res = psi_obj._add_missing_default_values(cr, uid, {})
        rit = self.browse(cr, uid, id, context=context)
        supplier_pp = pp_obj.browse(
            cr, rit.supplier_user_id.id, supplier_product_id, context=context)
        price_info = ppl_obj._compute_intercompany_trade_prices(
            cr, rit.supplier_user_id.id, supplier_pp,
            rit.supplier_partner_id, rit.sale_pricelist_id, context=context)
        res.update({
            'name': rit.supplier_partner_id.id,
            'product_name': supplier_pp.name,
            'product_code': supplier_pp.default_code,
            'company_id': rit.customer_company_id.id,
            'supplier_product_id': supplier_pp.id,
            'pricelist_ids': [[5], [0, False, {
                'min_quantity': 0.0,
                'price': price_info['supplier_sale_price']}]],
        })
        return res
