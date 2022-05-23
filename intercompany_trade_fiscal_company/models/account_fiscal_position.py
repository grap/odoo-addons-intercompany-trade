# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    is_intercompany_trade_fiscal_company = fields.Boolean(
        string="Integrated Trade into a CAE",
        help="Check this box to use this Fiscal position for integrated Trade"
        " into 2 companies of the same cooperative",
    )
