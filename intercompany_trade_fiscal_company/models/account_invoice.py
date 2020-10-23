# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # Overload Section
    @api.multi
    def invoice_validate(self):
        config_obj = self.env["intercompany.trade.config"]
        for invoice in self.filtered(lambda x: x.intercompany_trade):
            config = config_obj._get_intercompany_trade_by_partner_company(
                invoice.partner_id.id, invoice.company_id.id, invoice.type
            )
            if config.same_fiscal_mother_company:
                invoice._check_intercompany_trade_fiscal_company()
        return super().invoice_validate()

    @api.model
    def create(self, vals):
        """Change Journal if it is trade between two company of the same
        cooperative"""
        partner_obj = self.env["res.partner"]
        journal_obj = self.env["account.journal"]
        config_obj = self.env["intercompany.trade.config"]

        partner = partner_obj.browse(vals["partner_id"])

        if partner.intercompany_trade:
            transaction_type = False
            journal = journal_obj.browse(int(vals["journal_id"]))
            if journal.type in ("sale"):
                transaction_type = "out"
            elif journal.type in ("purchase"):
                transaction_type = "in"
            config = config_obj._get_intercompany_trade_by_partner_company(
                partner.id, partner.company_id.id, transaction_type
            )
            if config.same_fiscal_mother_company:

                if journal.type in ("sale"):
                    vals["journal_id"] = config.sale_journal_id.id
                elif journal.type in ("purchase"):
                    vals["journal_id"] = config.purchase_journal_id.id

        return super().create(vals)

    @api.multi
    def write(self, vals):
        config_obj = self.env["intercompany.trade.config"]
        if vals.get("journal_id", False):
            for invoice in self:
                if (
                    invoice.intercompany_trade
                    and invoice.journal_id.id != vals["journal_id"]
                ):
                    config = config_obj._get_intercompany_trade_by_partner_company(
                        invoice.partner_id.id,
                        invoice.company_id.id,
                        invoice.type,
                    )
                    if config.same_fiscal_mother_company:
                        vals.pop("journal_id")

        return super().write(vals)

    # Custom Section
    @api.multi
    def _check_intercompany_trade_fiscal_company(self):
        for invoice in self:
            if (
                invoice.account_id
                != invoice.company_id.intercompany_trade_account_id
            ):
                raise UserError(
                    _(
                        "the account %s-%s is not the correct one in the"
                        " case of intercompany trade invoice between two companies"
                        " that belong the same fiscal company (CAE).\n"
                        " Please contact your accountant."
                    )
                    % (invoice.account_id.code, invoice.account_id.name)
                )
            for line in invoice.invoice_line_ids:
                if not line.account_id.is_intercompany_trade_fiscal_company:
                    raise UserError(
                        _(
                            "the account %s-%s is not correct for an expense or an"
                            " income in the case of intercompany trade invoice"
                            " between two companies that belong the same fiscal"
                            " company (CAE).\n"
                            " Please contact your accountant."
                        )
                        % (line.account_id.code, line.account_id.name)
                    )
