# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IntercompanyTradeConfig(models.Model):
    _inherit = "intercompany.trade.config"

    # Columns Section

    sale_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal in Supplier Company",
        help="Set a journal to use for intercompany trade. This setting is"
        " used only for trade between child companies of the same fiscal"
        " company.",
    )

    purchase_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal in Customer Company",
        help="Set a journal to use for intercompany trade. This setting is"
        " used only for trade between child companies of the same fiscal"
        " company.",
    )

    fiscal_company_customer_account_id = fields.Many2one(
        related="customer_company_id.intercompany_trade_account_id",
        comodel_name="account.account",
        readonly=True,
        string="Receivable Account for the Customer",
    )

    fiscal_company_supplier_account_id = fields.Many2one(
        related="supplier_company_id.intercompany_trade_account_id",
        comodel_name="account.account",
        readonly=True,
        string="Payable Account for the Supplier",
    )

    # Custom Section
    def _prepare_partner_from_company(self, company_id, inner_company_id):
        res = super()._prepare_partner_from_company(company_id, inner_company_id)
        company_obj = self.env["res.company"]
        company = company_obj.browse(inner_company_id)
        account_id = company.intercompany_trade_account_id
        fiscal_position = (
            company.fiscal_company_id.intercompany_trade_fiscal_position_id
        )
        if self.same_fiscal_mother_company:
            res.update(
                {
                    "property_account_receivable_id": account_id.id,
                    "property_account_payable_id": account_id.id,
                    "property_account_position_id": fiscal_position.id,
                }
            )
        return res
