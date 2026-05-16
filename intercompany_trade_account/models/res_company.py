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
