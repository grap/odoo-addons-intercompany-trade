# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Constraints Section
    @api.constrains(
        "intercompany_trade",
        "property_account_position_id",
    )
    def _check_intercompany_trade_same_fiscal_company_fiscal_position(self):
        if not self.intercompany_trade:
            if self.property_account_position_id.is_intercompany_trade_fiscal_company:
                raise UserError(
                    _(
                        "It's not possible to set the fiscal position %s to this partner."
                        " You should not use a fiscal position for intercompany trade"
                        " between same fiscal companies."
                    )
                    % (self.property_account_position_id.name)
                )
            return

        IntercompanyTradeConfig = self.env["intercompany.trade.config"]
        same_fiscal_mother_company = any(
            IntercompanyTradeConfig.search(
                [
                    "|",
                    ("customer_partner_id", "=", self.id),
                    ("supplier_partner_id", "=", self.id),
                ]
            ).mapped("same_fiscal_mother_company")
        )
        if (
            same_fiscal_mother_company
            != self.property_account_position_id.is_intercompany_trade_fiscal_company
        ):
            raise UserError(
                _("It's not possible to set the fiscal position %s to this partner.")
                % (self.property_account_position_id.name)
            )
