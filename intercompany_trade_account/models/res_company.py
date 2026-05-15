# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    intercompany_trade_account_id = fields.Many2one(
        comodel_name="account.account",
        domain="["
        "('company_id', '=', id),"
        "('internal_type', 'not in', ('expense', 'income')),"
        "('is_intercompany_trade', '=', True)]",
        string="Account for Intercompany Trade",
        help="Set an account if there"
        " is Intercompany Trade with this company. This setting will have"
        " an effect only in trade between two companies of the same"
        " cooperative. Typically a 181 account in France.",
    )

    intercompany_trade_fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        domain="["
        "('company_id', '=', id),"
        "('is_intercompany_trade', '=', True)"
        "]",
    )

    intercompany_trade_sale_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="["
        "('company_id', '=', id),"
        "('is_intercompany_trade', '=', True),"
        "('type', '='', 'sale'),"
        "]",
    )

    intercompany_trade_purchase_journal_id = fields.Many2one(
        comodel_name="account.journal",
        domain="["
        "('company_id', '=', id),"
        "('is_intercompany_trade', '=', True),"
        "('type', '='', 'purchase'),"
        "]",
    )
