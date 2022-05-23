# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    intercompany_trade_account_id = fields.Many2one(
        comodel_name="account.account",
        domain="["
        "('company_id', '=', fiscal_company_id),"
        "('internal_type', '=', 'receivable'),"
        "('is_intercompany_trade_fiscal_company', '=', True)]",
        string="Account for Intercompany Trade",
        help="Set an account if there"
        " is Intercompany Trade with this company. This setting will have"
        " an effect only in trade between two companies of the same"
        " cooperative",
    )

    intercompany_trade_fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        domain="[" "('is_intercompany_trade_fiscal_company', '=', True)]",
    )
