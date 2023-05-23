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
        for invoice in self:
            invoice._check_intercompany_trade_same_fiscal_company()
        return super().invoice_validate()

    # Custom Section
    @api.multi
    def _check_intercompany_trade_same_fiscal_company(self):
        config_obj = self.env["intercompany.trade.config"]
        self.ensure_one()

        same_fiscal_mother_company = False
        if self.partner_id.intercompany_trade:
            config = config_obj._get_intercompany_trade_by_partner_company(
                self.partner_id.id, self.company_id.id, self.type
            )
            same_fiscal_mother_company = config.same_fiscal_mother_company

        if same_fiscal_mother_company:
            # Check that main account is for intercompany trade
            if self.account_id != self.company_id.intercompany_trade_account_id:
                raise UserError(
                    _(
                        "the account %s-%s is not the correct one in the"
                        " case of intercompany trade invoice between two companies"
                        " that belong the same fiscal company (CAE).\n"
                        " Please contact your accountant."
                    )
                    % (self.account_id.code, self.account_id.name)
                )

            # check that expense / income account lines are OK for intercompany trade
            for line in self._get_intercompany_trade_invoiceable_lines():
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

            # Check that Journal is OK for intercompany trade
            if not self.journal_id.is_intercompany_trade_fiscal_company:
                raise UserError(
                    _("You can not use the journal '%s'" " for Intercompany Trade.")
                    % (self.journal_id.name)
                )
        else:
            # Check that Journal is OK for NON intercompany trade
            if self.journal_id.is_intercompany_trade_fiscal_company:
                raise UserError(
                    _("You can not use the journal '%s'" " for Non Intercompany Trade.")
                    % (self.journal_id.name)
                )

    @api.multi
    def _prepare_intercompany_vals(self, config):
        vals = super()._prepare_intercompany_vals(config)
        if self.type == "out_invoice":
            vals["journal_id"] = config.purchase_journal_id.id
        elif self.type == "out_refund":
            vals["journal_id"] = config.sale_journal_id
        return vals

    @api.onchange("partner_id", "company_id", "type")
    def _onchange_partner_id_intercompany_trade(self):
        config_obj = self.env["intercompany.trade.config"]
        if not (self.partner_id and self.company_id and self.type):
            return

        config = config_obj._get_intercompany_trade_by_partner_company(
            self.partner_id.id, self.company_id.id, self.type
        )
        if not config:
            # TODO, improve ME.
            return

        if self.type in ["in_invoice", "in_refund"] and config.purchase_journal_id:
            self.journal_id = config.purchase_journal_id

        if self.type in ["out_invoice", "out_refund"] and config.sale_journal_id:
            self.journal_id = config.sale_journal_id
