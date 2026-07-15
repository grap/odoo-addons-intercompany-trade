# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    intercompany_trade_partner_id = fields.Many2one(
        comodel_name="res.partner",
        help="Partner used for Intercompany Trade"
        " in the other Integrated Companies of the CAE.",
        readonly=True,
    )

    # Overload Section
    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        companies._manage_intercompany_trade_partners()
        return companies

    def write(self, vals):
        """update related 'intercompany_trade' partners."""

        res = super().write(vals)

        # Do not rewrite all related partners, if interesting data
        # didn't changed.
        if not list(
            set(vals.keys()) & set(self._get_intercompany_trade_partner_fields())
        ):
            return res

        self._manage_intercompany_trade_partners()

        return res

    def unlink(self):
        self.mapped("intercompany_trade_partner_id").unlink()
        return super().unlink()

    # Custom Section
    def _manage_intercompany_trade_partners(self):
        for company in self.filtered(
            lambda x: x.fiscal_type == "fiscal_child"
            and not x.intercompany_trade_partner_id
        ):
            company.intercompany_trade_partner_id = (
                self.env["res.partner"]
                .with_company(company.parent_id)
                .with_context(ignore_intercompany_trade_check=True)
                .create(company._prepare_intercompany_trade_partner_from_company())
            )

        for company in self.filtered(
            lambda x: x.fiscal_type == "fiscal_child"
            and x.intercompany_trade_partner_id
        ):
            company.intercompany_trade_partner_id.with_company(
                company.parent_id
            ).with_context(ignore_intercompany_trade_check=True).write(
                company._prepare_intercompany_trade_partner_from_company()
            )

        for company in self.filtered(
            lambda x: x.fiscal_type != "fiscal_child"
            and x.intercompany_trade_partner_id
        ):
            company.intercompany_trade_partner_id.with_company(
                company.parent_id
            ).with_context(ignore_intercompany_trade_check=True).unlink()

    def _prepare_intercompany_trade_partner_from_company(self):
        """
        Return vals for the creation of an 'intercompany_trade' partner.

        Note: if you change this function, please update also
        the function _get_intercompany_trade_partner_fields()
        """
        self.ensure_one()
        return {
            "name": self.name + " " + _("(Intercompany Trade)"),
            "active": self.active,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "zip": self.zip,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "website": self.website,
            "phone": self.phone,
            "email": self.email,
            "vat": self.vat,
            "is_company": True,
            "image_1920": self.logo,
            "intercompany_trade": True,
            "company_id": self.parent_id.id,
        }

    @api.model
    def _get_intercompany_trade_partner_fields(self):
        """
        List of company fields that should raise the rewrite of related
        intercompany_trade partners.

        Note: if you change this function, please update also
        the function _get_intercompany_trade_partner_fields()
        """
        return [
            "name",
            "active",
            "street",
            "street2",
            "city",
            "zip",
            "state_id",
            "country_id",
            "website",
            "phone",
            "email",
            "vat",
            "logo",
            "parent_id",
            "fiscal_type",
        ]
