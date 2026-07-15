# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"

    is_intercompany_trade = fields.Boolean(
        string="Integrated Trade into a CAE",
        help="Check this box for integrated Trade into 2 companies of"
        " the same cooperative for the 'receivable' / 'payable' /"
        " 'Income' / 'Expense' accounts.",
    )
