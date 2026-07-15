# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _prepare_intercompany_trade_partner_from_company(self):
        vals = super()._prepare_intercompany_trade_partner_from_company()
        vals.update(
            {
                "siren": self.siren,
                "nic": self.nic,
            }
        )
        return vals

    @api.model
    def _get_intercompany_trade_partner_fields(self):
        res = super()._get_intercompany_trade_partner_fields()
        res += ["siren", "nic"]
        return res
