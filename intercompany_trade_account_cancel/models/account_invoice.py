# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_cancel(self):
        invoices = self.filtered(lambda x: x.intercompany_trade)
        if invoices:
            raise UserError(_("Unable to cancel intercompany trade Invoices"))
        return super().action_cancel()
