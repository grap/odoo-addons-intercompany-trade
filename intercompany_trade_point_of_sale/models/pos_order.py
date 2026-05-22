# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.constrains("partner_id")
    def _check_partner_integrated_trade(self):
        for order in self:
            if order.partner_id.intercompany_trade and not order.to_invoice:
                raise ValidationError(
                    _(
                        "You can not select a partner marked as 'integrated Trade'"
                        " to create a regular PoS Order. Please create"
                        " an PoS Order 'to invoice', or use the sale or"
                        " the invoice module instead."
                    )
                )

    def _prepare_invoice_vals(self):
        res = super()._prepare_invoice_vals()
        if self.partner_id.intercompany_trade:
            res[
                "journal_id"
            ] = self.company_id.fiscal_company_id.intercompany_trade_sale_journal_id.id
        return res
