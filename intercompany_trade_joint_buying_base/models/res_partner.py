# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _intercompany_trade_allowed_fields(self):
        """allow basic user to change link with global joint buying partner"""
        res = super()._intercompany_trade_allowed_fields()
        res.append("joint_buying_global_partner_id")
        return res
