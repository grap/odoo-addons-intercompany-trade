# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class IntercompanyTradeConfig(models.Model):
    _inherit = 'intercompany.trade.config'

    @api.multi
    @api.depends(
        'supplier_partner_id.property_product_pricelist_purchase',
        'customer_company_id')
    def _compute_purchase_pricelist_id(self):
        partner_obj = self.env['res.partner']
        for config in self:
            partner = partner_obj.with_context(
                force_company=config.customer_company_id.id).browse(
                    config.supplier_partner_id.id)
            config.purchase_pricelist_id =\
                partner.property_product_pricelist_purchase.id

    # Columns section
    purchase_pricelist_id = fields.Many2one(
        compute='_compute_purchase_pricelist_id',
        comodel_name='product.pricelist',
        string='Purchase Pricelist in the Customer Company')
