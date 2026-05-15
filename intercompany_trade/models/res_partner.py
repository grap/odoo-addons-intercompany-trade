# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import AND


class ResPartner(models.Model):
    _inherit = "res.partner"

    intercompany_trade = fields.Boolean(
        readonly=True,
        help="Indicate that this partner is an integrated company of a CAE in Odoo.",
    )

    def _fiscal_company_forbid_fiscal_type_allow_exceptions(self):
        res = super()._fiscal_company_forbid_fiscal_type_allow_exceptions()
        return res.filtered(lambda x: not x.intercompany_trade)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._check_intercompany_trade_access([0])
        return partners

    def write(self, vals):
        self._check_intercompany_trade_access(vals.keys())
        return super().write(vals)

    def unlink(self):
        self._check_intercompany_trade_access([0])
        return super().unlink()

    def _search(self, args, **kwargs):
        if self.env.company.fiscal_type == "fiscal_child":
            args = AND(
                [
                    args,
                    [("id", "!=", self.env.company.intercompany_trade_partner_id.id)],
                ]
            )
        return super()._search(args, **kwargs)

    @api.constrains("intercompany_trade", "parent_id")
    def _check_intercompany_trade_parent(self):
        bad_partners = self.filtered(lambda x: x.intercompany_trade and x.parent_id)
        if bad_partners:
            raise ValidationError(
                _("You can not set Parent Company to an Intercompany Trade Partner")
            )

    @api.constrains("parent_id")
    def _check_intercompany_trade_child(self):
        bad_partners = self.filtered(
            lambda x: x.parent_id and x.parent_id.intercompany_trade
        )
        if bad_partners:
            raise ValidationError(
                _("You can not set Child Partner to an Intercompany Trade Partner")
            )

    # Custom Section
    @api.model
    def _intercompany_trade_allowed_fields(self):
        """Overload this function to allow users to change
        some fields for intercompany trade partner"""
        res = []
        for field_name in self._fields.keys():
            if field_name.startswith("property_"):
                res.append(field_name)
        # User that can write companies could enable or disable
        # intercompany trade partners
        if self.env["res.company"].check_access_rights("write", raise_exception=False):
            res.append("active")
        return res

    def _check_intercompany_trade_access(self, fields):
        """Restrict access of intercompany_trade partner set only for allowed fields"""
        partners = self.filtered(lambda x: x.intercompany_trade)
        if not partners or self.env.context.get(
            "ignore_intercompany_trade_check", False
        ):
            return
        unallowed_fields = set(fields) - set(self._intercompany_trade_allowed_fields())

        if unallowed_fields:
            raise UserError(
                _(
                    "Error: You have no right to create, update or unlink"
                    " partners that are flagged as 'Intercompany Trade'.\n\n"
                    "%(partner_names)s",
                    partner_names=", ".join(self.mapped("name")),
                )
            )
