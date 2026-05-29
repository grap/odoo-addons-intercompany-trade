# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    intercompany_trade_account_id = fields.Many2one(
        comodel_name="account.account",
        domain="["
        "('company_id', '=', id),"
        "('account_type', 'not in', ('expense', 'income')),"
        "('is_intercompany_trade', '=', True)]",
        string="Third Party Account for Intercompany Trade",
    )

    intercompany_trade_fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        string="Fiscal Position for Intercompany Trade",
        domain="["
        "('company_id', '=', id),"
        "('is_intercompany_trade', '=', True)"
        "]",
    )

    intercompany_trade_sale_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Sale Journal for Intercompany Trade",
        domain="["
        "('company_id', '=', id),"
        "('is_intercompany_trade', '=', True),"
        "('type', '=', 'sale'),"
        "]",
    )

    intercompany_trade_purchase_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Purchase Journal for Intercompany Trade",
        domain="["
        "('company_id', '=', id),"
        "('is_intercompany_trade', '=', True),"
        "('type', '=', 'purchase'),"
        "]",
    )

    def _prepare_intercompany_trade_partner_from_company(self):
        vals = super()._prepare_intercompany_trade_partner_from_company()
        position_id = self.fiscal_company_id.intercompany_trade_fiscal_position_id.id
        vals.update({"property_account_position_id": position_id})
        return vals

    def _get_intercompany_trade_partner_fields(self):
        res = super()._get_intercompany_trade_partner_fields()
        res += ["intercompany_trade_fiscal_position_id"]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        for company, vals in zip(companies, vals_list, strict=True):
            if vals.get("fiscal_type") == "fiscal_mother":
                company._create_intercompany_trade_fiscal_position_id()
        return companies

    def write(self, vals):
        res = super().write(vals)

        if vals.get("fiscal_type") == "fiscal_mother":
            self._create_intercompany_trade_fiscal_position_id()

        return res

    def _create_intercompany_trade_fiscal_position_id(self):
        self.ensure_one()
        if self.intercompany_trade_fiscal_position_id:
            return
        fiscal_position = self.env["account.fiscal.position"].create(
            self.env[
                "account.fiscal.position"
            ]._prepare_intercompany_trade_fiscal_position_vals(self)
        )
        self.intercompany_trade_fiscal_position_id = fiscal_position.id
        self.mapped("child_ids.intercompany_trade_partner_id").write(
            {"property_account_position_id": fiscal_position.id}
        )
