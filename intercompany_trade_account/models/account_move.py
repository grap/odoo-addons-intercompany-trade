# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    intercompany_trade = fields.Boolean(
        string="Intercompany Trade",
        related="partner_id.intercompany_trade",
        store=True,
    )

    # TODO, when validating in_ invoices (and related refund)
    # Check if the according sale (out) invoice is correct.
    #
    # def invoice_validate(self):
    #     for invoice in self.filtered(
    #         lambda x: x.intercompany_trade and "out_" in x.type
    #     ):
    #         invoice._create_intercompany_invoice()
    #     return super().invoice_validate()
