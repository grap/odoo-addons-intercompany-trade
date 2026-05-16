# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        # inject the intercompany trade for partners here (181)
        # It avoid to propagate the configuration
        # creating many the accounting properties for all partners and for all companies
        intercompany_trade_partner_lines = self.filtered(
            lambda line: line.move_id.intercompany_trade
            and line.display_type == "payment_term"
        )
        for line in intercompany_trade_partner_lines:
            line.account_id = (
                line.move_id.fiscal_company_id.intercompany_trade_account_id
            )
            if not line.account_id:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner"
                        " '%(partner_name)s' because, your accountant did'nt set"
                        " any intercompany trade account"
                        " at the Mother company level.",
                        partner_name=self.move_id.partner_id.name,
                    ),
                )
        return super(
            AccountMoveLine, self - intercompany_trade_partner_lines
        )._compute_account_id()

    @api.constrains("account_id", "display_type")
    def _check_payable_receivable(self):
        # for intercompany trade move lines,
        # we requires for third party account (payment_term)
        # an account with type 'liability_non_current'.
        # (and not asset_receivable / liability_payable)
        intercompany_trade_partner_lines = self.filtered(
            lambda line: line.move_id.intercompany_trade
        )
        for line in intercompany_trade_partner_lines:
            account_type = line.account_id.account_type
            if line.move_id.is_sale_document(
                include_receipts=True
            ) or line.move_id.is_purchase_document(include_receipts=True):
                if (line.display_type == "payment_term") ^ (
                    account_type == "liability_non_current"
                ):
                    raise UserError(
                        _(
                            "In intercompany trade moves the account %(account_name)s"
                            " for partners should have a 'liability_non_current' type."
                        ),
                        account_name=f"{line.account_id.code} - {line.account_id.name}",
                    )
        return super(
            AccountMoveLine, self - intercompany_trade_partner_lines
        )._check_payable_receivable()
