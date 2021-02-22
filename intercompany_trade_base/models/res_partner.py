# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Columns section
    intercompany_trade = fields.Boolean(
        string="Intercompany Trade",
        readonly=True,
        help="Indicate that this partner is a company in Odoo.",
    )

    # Overload Section
    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._check_intercompany_trade_access(vals.keys())
        return res

    @api.multi
    def write(self, vals):
        self._check_intercompany_trade_access(vals.keys())
        return super().write(vals)

    @api.multi
    def unlink(self):
        self._check_intercompany_trade_access([0])
        return super().unlink()

    # Custom Section
    @api.model
    def _intercompany_trade_allowed_fields(self):
        """Overload this function to allow basic users to change
        some fields for intercompany trade partner"""
        return []

    @api.multi
    def _check_intercompany_trade_access(self, fields):
        """Restrict access of partner set as intercompany_trade for only
        'intercompany_trade_manager' users."""
        if self.env.context.get("ignore_intercompany_trade_check", False):
            return
        unallowed_fields = set(fields) - set(self._intercompany_trade_allowed_fields())
        if not self.env.user.has_group(
            "intercompany_trade_base.intercompany_trade_manager"
        ):
            for partner in self:
                if partner.intercompany_trade and unallowed_fields:
                    raise UserError(
                        _(
                            "Error: You have no right to create or"
                            " update a partner that is set as"
                            " 'Intercompany Trade'"
                        )
                    )
