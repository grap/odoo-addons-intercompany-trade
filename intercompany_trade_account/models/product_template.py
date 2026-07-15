# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command, api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        templates._create_tax_mapping_in_intercompany_trade_fiscal_position()
        return templates

    def write(self, vals):
        res = super().write(vals)
        if "taxes_id" in vals.keys():
            self._create_tax_mapping_in_intercompany_trade_fiscal_position()
        return res

    def _create_tax_mapping_in_intercompany_trade_fiscal_position(self):
        """Create tax mapping the fiscal position for Intercompany trades
        for alle sale taxes related to self templates."""
        companies = (
            self.mapped("company_id")
            .filtered(lambda x: x.fiscal_company_id.fiscal_type == "fiscal_mother")
            .mapped("fiscal_company_id")
        )
        for company in companies:
            fiscal_position = company.intercompany_trade_fiscal_position_id
            if not fiscal_position:
                continue
            current_taxes = fiscal_position.mapped("tax_ids.tax_src_id")
            templates = self.filtered(
                lambda x, company=company: x.company_id.fiscal_company_id == company
            )
            missing_taxes = templates.mapped("taxes_id").filtered(
                lambda x, current_taxes=current_taxes: x not in current_taxes
            )
            if not missing_taxes:
                continue
            line_vals = []
            for missing_tax in missing_taxes:
                line_vals.append(Command.create({"tax_src_id": missing_tax.id}))
            fiscal_position.write({"tax_ids": line_vals})
