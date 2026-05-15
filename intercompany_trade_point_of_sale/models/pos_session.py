# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _get_pos_ui_res_partner(self, params):
        return self.env["res.partner"].search_read(**params["search_params"])
