# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    intercompany_trade_account_id = fields.Many2one(
        related="company_id.fiscal_company_id.intercompany_trade_account_id",
        readonly=False,
    )

    intercompany_trade_fiscal_position_id = fields.Many2one(
        related="company_id.fiscal_company_id.intercompany_trade_fiscal_position_id",
        readonly=False,
    )

    intercompany_trade_sale_journal_id = fields.Many2one(
        related="company_id.fiscal_company_id.intercompany_trade_sale_journal_id",
        readonly=False,
    )

    intercompany_trade_purchase_journal_id = fields.Many2one(
        related="company_id.fiscal_company_id.intercompany_trade_purchase_journal_id",
        readonly=False,
    )
