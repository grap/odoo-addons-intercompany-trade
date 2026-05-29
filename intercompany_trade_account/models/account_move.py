# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


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

        # check that expense / income account lines doesn't have any tax
        if self.line_ids.tax_ids:
            raise UserError(
                _(
                    "An intercompany trade invoice should not have"
                    " any taxes defined in lines",
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
        """Check if
        - the bill reference has been entered
        - we can indentify the related supplier invoice
        - if the related invoice has the same date
        """
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

        if supplier_invoice.state in ["draft", "cancel"]:
            raise UserError(
                _(
                    "The state of the supplier invoice is invalid:"
                    " '%(supplier_invoice_state)s'.",
                    supplier_invoice_state=supplier_invoice.state,
                )
            )
        if self.invoice_date != supplier_invoice.invoice_date:
            raise UserError(
                _(
                    "The date of your invoice %(your_invoice_date)s"
                    " doesn't match with the date of the supplier invoice"
                    " %(supplier_invoice_date)s.",
                    your_invoice_date=self.invoice_date,
                    supplier_invoice_date=supplier_invoice.invoice_date,
                )
            )

        currency = self.currency_id
        if float_compare(
            self.amount_untaxed,
            supplier_invoice.amount_untaxed,
            precision_digits=currency.decimal_places,
        ):
            raise UserError(
                _(
                    "The untaxed total of your invoice %(your_amount_untaxed)s"
                    " doesn't match with the untaxed total of the supplier invoice"
                    " %(supplier_amount_untaxed)s.",
                    your_amount_untaxed=currency.format(self.amount_untaxed),
                    supplier_amount_untaxed=currency.format(
                        supplier_invoice.amount_untaxed
                    ),
                )
            )

        if float_compare(
            self.amount_total,
            supplier_invoice.amount_total,
            precision_digits=currency.decimal_places,
        ):
            raise UserError(
                _(
                    "The Amount total of your invoice %(your_amount_total)s"
                    " doesn't match with the amount total of the supplier invoice"
                    " %(supplier_amount_total)s.",
                    your_amount_total=currency.format(self.amount_total),
                    supplier_amount_total=currency.format(
                        supplier_invoice.amount_total
                    ),
                )
            )
