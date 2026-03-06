# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_intercompany_trade_fiscal_company = fields.Boolean(
        string="Integrated Trade into a CAE",
        help="Check this box to use this journal for integrated Trade"
        " into 2 companies of the same cooperative",
    )

    # Constraints Section
    @api.constrains("is_intercompany_trade_fiscal_company", "type")
    def _check_is_intercompany_trade_fiscal_company(self):
        for journal in self.filtered(lambda x: x.is_intercompany_trade_fiscal_company):
            if journal.type not in ("sale", "purchase"):
                raise UserError(
                    _(
                        "Only 'Purchase' and 'Sale' Journals can be flaged as"
                        " 'Internal Journal for Intercompany Trade'"
                    )
                )
