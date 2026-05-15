# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        # inject the intercompany trade for partners here (181)
        # It avoid to propagate the configuration
        # creating many the accounting properties for all partners and for all companies
        intercompany_trade_partner_lines = self.filtered(
            lambda line: line.move_id.intercompany_trade
        )
        for line in intercompany_trade_partner_lines:
            line.account_id = (
                line.move_id.company_id.fiscal_company_id.intercompany_trade_account_id
            )
            if not line.account_id:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner '%s'"
                        " because, your accountant did'nt set"
                        " any intercompany trade account"
                        " at the Mother company level."
                        " Please ask to your accountant to do it."
                    )
                    % (self.move_id.partner_id.name)
                )
        return super(
            AccountMoveLine, self - intercompany_trade_partner_lines
        )._compute_account_id()
