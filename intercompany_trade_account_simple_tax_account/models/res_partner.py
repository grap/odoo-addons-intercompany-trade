# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _set_existing_simple_tax_type(self):
        """Initialize all intercompany trade partners with correct Taxes
        configuration"""
        partners = self.search(
            [
                ("intercompany_trade", "=", True),
                ("simple_tax_type", "!=", "excluded"),
            ]
        )
        partners.write({"simple_tax_type": "excluded"})

    @api.model
    def create(self, vals):
        if vals.get("intercompany_trade", False):
            vals["simple_tax_type"] = "excluded"
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get("intercompany_trade", False):
            vals["simple_tax_type"] = "excluded"
        return super(ResPartner, self).write(vals)
