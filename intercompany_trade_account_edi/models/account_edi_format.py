# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _get_move_applicability(self, move):
        if not move.intercompany_trade:
            return super()._get_move_applicability(move)
