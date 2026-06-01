# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.osv.expression import OR


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        res["search_params"]["fields"].append("intercompany_trade")
        return res

    def _loader_params_account_fiscal_position(self):
        # Allways load intercompany trade fiscal position
        # to avoid error, if user create an invoice
        # for an Intercompany Trade partner.
        res = super()._loader_params_account_fiscal_position()
        domain = res["search_params"]["domain"]
        domain = OR(
            [
                domain,
                [
                    (
                        "id",
                        "=",
                        self.company_id.fiscal_company_id.intercompany_trade_fiscal_position_id.id,
                    )
                ],
            ]
        )
        res["search_params"]["domain"] = domain
        return res
