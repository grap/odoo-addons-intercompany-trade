# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
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
        precompute=True,
    )

    @api.depends("partner_id", "partner_shipping_id", "company_id")
    def _compute_fiscal_position_id(self):
        intercompany_trade_moves = self.filtered(lambda move: move.intercompany_trade)
        for move in intercompany_trade_moves:
            move.fiscal_position_id = (
                move.fiscal_company_id.intercompany_trade_fiscal_position_id
            )
            if not move.fiscal_position_id:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner"
                        "'%(partner_name)s' because, your accountant did'nt set"
                        " any intercompany trade fiscal position"
                        " at the Mother company level.",
                        partner_name=self.partner_id.name,
                    ),
                )

        return super(
            AccountMove, self - intercompany_trade_moves
        )._compute_fiscal_position_id()

    @api.depends("move_type", "intercompany_trade")
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
                        "You can not select an Intercompany Trade partner"
                        "'%(partner_name)s' to create accouning move,"
                        " that are not sale or purchase.",
                        partner_name=self.partner_id.name,
                    ),
                )
            move.journal_id = getattr(move.fiscal_company_id, field_name)
            if not move.journal_id:
                raise UserError(
                    _(
                        "You can not select an Intercompany Trade partner"
                        "'%(partner_name)s' because, your accountant did'nt set"
                        " any intercompany trade journal (sale & purchase)"
                        " at the Mother company level.",
                        partner_name=self.partner_id.name,
                    ),
                )
        # reset journal to false, if there is an intercompany trade journal
        # on classic account moves.
        # so calling super will rededuce correct account journal
        for move in (self - intercompany_trade_moves).filtered(
            lambda x: x.journal_id.is_intercompany_trade
        ):
            move.journal_id = False

        return super(AccountMove, self - intercompany_trade_moves)._compute_journal_id()

    def _post(self, *args, **kwargs):
        intercompany_trade_invoices = self.filtered(lambda x: x.intercompany_trade)

        for invoice in self - intercompany_trade_invoices:
            invoice._check_not_intercompany_trade_settings()

        for invoice in intercompany_trade_invoices:
            invoice._check_intercompany_trade_settings()

        for invoice in intercompany_trade_invoices.filtered(
            lambda x: x.is_purchase_document(include_receipts=True)
        ):
            invoice._check_intercompany_trade_purchase_invoice()
        return super()._post(*args, **kwargs)

    # Custom Section
    def _check_intercompany_trade_settings(self):
        self.ensure_one()

        # Check that Journal is OK for intercompany trade
        if not self.journal_id.is_intercompany_trade:
            raise UserError(
                _(
                    "You can not use the journal '%(journal_name)s'"
                    " for Intercompany Trade.",
                    journal_name=self.journal_id.name,
                ),
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
                    " for Intercompany Trade.",
                    fiscal_position_name=self.fiscal_position_id.name,
                ),
            )

        # Check that main account is OK for intercompany trade
        for line in self.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        ):
            if line.account_id != self.fiscal_company_id.intercompany_trade_account_id:
                raise UserError(
                    _(
                        "the account %(code)s-%(name)s is not the correct one in the"
                        " case of intercompany trade invoice between two companies"
                        " that belong the same fiscal company (CAE).\n"
                        " Please contact your accountant.",
                        code=line.account_id.code,
                        name=line.account_id.name,
                    )
                )

        # check that expense / income account lines are OK for intercompany trade
        for line in self.line_ids.filtered(
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
                    " for Non Intercompany Trade.",
                    journal_name=self.journal_id.name,
                ),
            )

        # Check that Fiscal Position is OK for NON intercompany trade
        if self.fiscal_position_id and self.fiscal_position_id.is_intercompany_trade:
            raise UserError(
                _(
                    "You can not use the fiscal position '%(fiscal_position_name)s'"
                    " for Non Intercompany Trade.",
                    fiscal_position_name=self.fiscal_position_id.name,
                ),
            )

        # Check that main account is OK for NON intercompany trade
        for line in self.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        ):
            if line.account_id == self.fiscal_company_id.intercompany_trade_account_id:
                raise UserError(
                    _(
                        "the account %(code)s-%(name)s is not the correct one"
                        " for Non Intercompany Trade.",
                        code=line.account_id.code,
                        name=line.account_id.name,
                    )
                )

        # check that expense / income account lines are OK for NON intercompany trade
        for line in self.line_ids.filtered(
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

    def _check_intercompany_trade_purchase_invoice(self):
        """Check if there is an according sale invoice
        and if the data are matching."""
        self.ensure_one()
        if not self.ref:
            raise UserError(
                _(
                    "Intercompany Trade Supplier invoice should have"
                    " a Bill reference to be confirmed.",
                )
            )
        supplier_company = self.env["res.company"].search(
            [("intercompany_trade_partner_id", "=", self.partner_id.id)]
        )
        if not supplier_company:
            raise UserError(
                _(
                    "Unexpected error. The related supplier company has not been"
                    " identified for the supplier %(supplier_name)s."
                    " Please contact the IT Team.",
                    supplier_name=self.partner_id.name,
                )
            )

        supplier_invoice = (
            self.env["account.move"]
            .sudo()
            .search([("company_id", "=", supplier_company.id), ("name", "=", self.ref)])
        )

        if not supplier_invoice:
            raise UserError(
                _(
                    "The related intercompany supplier invoice"
                    " %(supplier_invoice_name)s has not be found in its database.\n\n"
                    " Did you entered correctly the reference ?",
                    supplier_invoice_name=self.ref,
                )
            )
        import pdb

        pdb.set_trace()
