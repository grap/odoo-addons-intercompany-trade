# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):
        vals = super()._get_account_vals(
            company, account_template, code_acc, tax_template_ref
        )
        vals.update({"is_intercompany_trade": account_template.is_intercompany_trade})
        return vals

    def _get_fp_vals(self, company, position):
        vals = super()._get_fp_vals(company, position)
        vals.update({"is_intercompany_trade": position.is_intercompany_trade})
        return vals
