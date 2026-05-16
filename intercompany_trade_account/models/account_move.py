# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # We allow to create invoice for partner that belong to the
    # fiscal company
    partner_id = fields.Many2one(check_company=False)

    fiscal_company_id = fields.Many2one(
        comodel_name="res.company", related="company_id.fiscal_company_id"
    )

    intercompany_trade = fields.Boolean(
        string="Intercompany Trade",
        related="partner_id.intercompany_trade",
        store=True,
    )

    def _compute_fiscal_position_id(self):
        intercompany_trade_moves = self.filtered(lambda move: move.intercompany_trade)
        for move in intercompany_trade_moves:
            move.fiscal_position_id = (
                move.company_id.intercompany_trade_fiscal_position_id
            )
            if not move.fiscal_position_id:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner '%s'"
                        " because, your accountant did'nt set"
                        " any intercompany trade fiscal position"
                        " at the Mother company level."
                        " Please ask to your accountant to do it."
                    )
                    % (self.partner_id.name)
                )

        return super(
            AccountMove, self - intercompany_trade_moves
        )._compute_fiscal_position_id()

    def _compute_journal_id(self):
        intercompany_trade_moves = self.filtered(lambda move: move.intercompany_trade)
        for move in intercompany_trade_moves:
            if move.is_sale_document(include_receipts=True):
                field_name = "intercompany_trade_sale_journal_id"
            elif move.is_purchase_document(include_receipts=True):
                field_name = "intercompany_trade_purchase_journal_id"
            else:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner '%s'"
                        " to create accouning move, that are not sale or purchase"
                    )
                )
            move.journal_id = getattr(move.company_id, field_name)
            if not move.journal_id:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner '%s'"
                        " because, your accountant did'nt set"
                        " any intercompany trade journal (sale & purchase)"
                        " at the Mother company level."
                        " Please ask to your accountant to do it."
                    )
                    % (self.partner_id.name)
                )

        return super(AccountMove, self - intercompany_trade_moves)._compute_journal_id()

    # TODO, when validating in_ invoices (and related refund)
    # Check if the according sale (out) invoice is correct.
    #
    # def invoice_validate(self):
    #     for invoice in self.filtered(
    #         lambda x: x.intercompany_trade and "out_" in x.type
    #     ):
    #         invoice._create_intercompany_invoice()
    #     return super().invoice_validate()

    def invoice_validate(self):
        intercompany_trade_invoices = self.filtered(lambda x: x.intercompany_trade)

        for invoice in self - intercompany_trade_invoices:
            invoice._check_not_intercompany_trade_settings()

        for invoice in intercompany_trade_invoices:
            invoice._check_intercompany_trade_settings()

        for _invoice in intercompany_trade_invoices.filtered(
            lambda x: x.is_purchase_document(include_receipts=True)
        ):
            pass

        return super().invoice_validate()

    # Custom Section
    def _check_intercompany_trade_settings(self):
        self.ensure_one()

        # Check that Journal is OK for intercompany trade
        if not self.journal_id.is_intercompany_trade:
            raise UserError(
                _(
                    "You can not use the journal '%(journal_name)s'"
                    " for Intercompany Trade."
                ),
                journal_name=self.journal_id.name,
            )

        # Check that Fiscal Position is defined for intercompany trade
        if not self.fiscal_position_id:
            raise UserError(
                _("You have to set a Fiscal position for Intercompany Trade.")
            )

        # Check that Fiscal Position is OK for intercompany trade
        if not self.fiscal_position_id.is_intercompany_trade:
            raise UserError(
                _(
                    "You can not use the fiscal position '%(fiscal_position_name)s'"
                    " for Intercompany Trade."
                ),
                fiscal_position_name=self.fiscal_position_id.name,
            )

        # Check that main account is OK for intercompany trade
        for line in self.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        ):
            if line.account_id != self.company_id.intercompany_trade_account_id:
                raise UserError(
                    _(
                        "the account %(code)s-%(name)s is not the correct one in the"
                        " case of intercompany trade invoice between two companies"
                        " that belong the same fiscal company (CAE).\n"
                        " Please contact your accountant.",
                        code=self.account_id.code,
                        name=self.account_id.name,
                    )
                )

        # check that expense / income account lines are OK for intercompany trade
        for line in self.filtered(
            lambda line: line.display_type == "product"
            and line.move_id.is_invoice(True)
        ):
            if not line.account_id.is_intercompany_trade:
                raise UserError(
                    _(
                        "the account %(code)s-%(name)s is not"
                        " correct for an expense or an"
                        " income in the case of intercompany trade invoice"
                        " between two companies that belong the same fiscal"
                        " company (CAE).\n"
                        " Please contact your accountant.",
                        code=line.account_id.code,
                        name=line.account_id.name,
                    )
                )

    def _check_not_intercompany_trade_settings(self):
        # Check that Journal is OK for NON intercompany trade
        if self.journal_id.is_intercompany_trade:
            raise UserError(
                _(
                    "You can not use the journal '%(journal_name)s'"
                    " for Non Intercompany Trade."
                ),
                journal_name=self.journal_id.name,
            )

        # Check that Fiscal Position is OK for NON intercompany trade
        if self.fiscal_position_id and self.fiscal_position_id.is_intercompany_trade:
            raise UserError(
                _(
                    "You can not use the fiscal position '%(fiscal_position_name)s'"
                    " for Non Intercompany Trade."
                ),
                fiscal_position_name=self.fiscal_position_id.name,
            )

        # Check that main account is OK for NON intercompany trade
        for line in self.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        ):
            if line.account_id == self.company_id.intercompany_trade_account_id:
                raise UserError(
                    _(
                        "the account %(code)s-%(name)s is not the correct one"
                        " for Non Intercompany Trade.",
                        code=self.account_id.code,
                        name=self.account_id.name,
                    )
                )

        # check that expense / income account lines are OK for NON intercompany trade
        for line in self.filtered(
            lambda line: line.display_type == "product"
            and line.move_id.is_invoice(True)
        ):
            if line.account_id.is_intercompany_trade:
                raise UserError(
                    _(
                        "the account %(code)s-%(name)s is not"
                        " correct for Non Intercompany Trade.\n",
                        code=line.account_id.code,
                        name=line.account_id.name,
                    )
                )
