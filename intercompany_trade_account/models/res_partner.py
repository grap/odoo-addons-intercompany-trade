# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains(
        "intercompany_trade",
        "property_account_position_id",
    )
    def _check_intercompany_trade_same_fiscal_company_fiscal_position(self):
        for partner in self:
            fiscal_position = partner.property_account_position_id
            if (
                fiscal_position
                and partner.intercompany_trade ^ fiscal_position.is_intercompany_trade
            ):
                raise UserError(
                    _(
                        "It's not possible to set the fiscal position"
                        " '%(fp_name)s' to this partner %(partner_name)s.\n\n"
                        " as there are incompatible in an Intercompany trade"
                        " point of view",
                        fp_name=fiscal_position.name,
                        partner_name=partner.name,
                    )
                )

    def write(self, vals):
        res = super().write(vals)
        if (
            "property_account_position_id" in vals.keys()
            and not vals.get("property_account_position_id")
            and self.filtered(lambda x: x.intercompany_trade)
        ):
            raise UserError(
                _(
                    "It's not possible to remove the fiscal position"
                    " 'to the partner(s) %(partner_names)s.\n\n"
                    " as there are Intercompany trade partners.",
                    partner_names=",".join(
                        self.filtered(lambda x: x.intercompany_trade).mapped("name")
                    ),
                )
            )
        return res
