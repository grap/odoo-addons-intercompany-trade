# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.purchase_id and picking.purchase_id.intercompany_trade:
                picking.purchase_id.button_done()
                picking.purchase_id.invoice_status = "no"
        return res
