# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    is_intercompany_trade = fields.Boolean(
        string="Integrated Trade into a CAE",
        help="Check this box to use this Fiscal position for integrated Trade"
        " into 2 companies of the same cooperative",
    )

    def _prepare_intercompany_trade_fiscal_position_vals(self, company):
        return {
            "name": _(
                "Intercompany Trade in %(company_name)s", company_name=company.name
            ),
            "company_id": self.id,
            "is_intercompany_trade": True,
        }
