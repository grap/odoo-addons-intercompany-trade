# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _prepare_intercompany_vals(self, config):
        res = super()._prepare_intercompany_vals(config)
        res.update({"supplier_invoice_number": self.number})
        return res
