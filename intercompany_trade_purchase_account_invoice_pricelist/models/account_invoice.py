# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _prepare_intercompany_vals(self, config):
        self.ensure_one()
        res = super()._prepare_intercompany_vals(config)
        pricelist = (
            config.sudo()
            .with_context(force_company=config.supplier_company_id.id,)
            .supplier_partner_id.property_product_pricelist_purchase
        )
        res["pricelist_id"] = pricelist.id
        return res
