# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import Warning as UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    intercompany_trade = fields.Boolean(
        string="Intercompany Trade", related="partner_id.intercompany_trade"
    )

    @api.multi
    def action_invoice_create(self):
        orders = self.filtered(lambda x: not x.intercompany_trade)
        return super().action_invoice_create()

    @api.multi
    def view_invoice(self):
        orders = self.filtered(lambda x: x.intercompany_trade)
        if orders:
            raise UserError(
                _(
                    "In Intercompany Trade context, The supplier invoices will"
                    " be created by your supplier"
                )
            )
        return self.view_invoice()

    @api.model
    def _prepare_order_line_move(
        self, order, order_line, picking_id, group_id
    ):
        res = super()._prepare_order_line_move(
            order, order_line, picking_id, group_id
        )
        if order.intercompany_trade:
            for item in res:
                item["invoice_state"] = "none"
        return res
