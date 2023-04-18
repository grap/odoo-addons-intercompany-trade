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
        for partner in self:
            fiscal_position = partner.property_account_position_id
            if (
                not partner.intercompany_trade
                and fiscal_position.is_intercompany_trade_fiscal_company
            ):
                raise UserError(
                    _(
                        "It's not possible to set the fiscal position '%s' to this partner.\n\n"
                        " You should not use a fiscal position for intercompany trade"
                        " between same fiscal companies."
                    )
                    % (fiscal_position.name)
                )

            # ref "and self.property_account_position_id"
            # Ugly Hack do not check when creating partners from
            # the creation of intercompany.trade.config
            # this problem should come from the other problem with
            # property_account_position_id / no_property_account_position_id
            # TODO: Check in V16, if we can remove all the sudo() things.
            if (
                partner.intercompany_trade
                and fiscal_position
                and not fiscal_position.is_intercompany_trade_fiscal_company
            ):
                raise UserError(
                    _(
                        "It's not possible to set the fiscal position '%s' to this partner.\n\n"
                        " You should use a fiscal position for intercompany trade"
                        " between same fiscal companies."
                    )
                    % (fiscal_position.name)
                )
