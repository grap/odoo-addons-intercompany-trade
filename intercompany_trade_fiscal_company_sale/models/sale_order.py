# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        config = (
            self.env["intercompany.trade.config"]
            .sudo()
            ._get_intercompany_trade_by_partner_company(
                vals["partner_id"], vals["company_id"], "out"
            )
        )
        if config:
            vals["journal_id"] = config.sale_journal_id.id
        return vals
