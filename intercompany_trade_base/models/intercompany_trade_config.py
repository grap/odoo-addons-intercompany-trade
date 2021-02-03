# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class IntercompanyTradeConfig(models.Model):
    _name = "intercompany.trade.config"
    _description = "Intercompany Trade Configuration"
    _order = "customer_company_id, supplier_company_id"

    name = fields.Char(string="Name", required=True, default="/")

    active = fields.Boolean(
        string="Active",
        default=True,
        help="By unchecking the active field"
        " you can disable the trading between the two company without"
        " deleting it.",
    )

    customer_user_id = fields.Many2one(
        string="Customer User",
        required=True,
        comodel_name="res.users",
        domain="[('company_id', '=', customer_company_id)]",
        help="This user will be used to create customer data when supplier"
        " users update datas.\n"
        " Please take that this user must have good access right on the"
        " customer company.",
    )

    customer_company_id = fields.Many2one(
        string="Customer Company",
        required=True,
        comodel_name="res.company",
        help="Select the company that could purchase to the other.",
    )

    supplier_company_id = fields.Many2one(
        string="Supplier Company",
        required=True,
        comodel_name="res.company",
        help="Select the company that could sale to the other.",
    )

    customer_partner_id = fields.Many2one(
        string="Customer Partner in the Supplier Company",
        readonly=True,
        comodel_name="res.partner",
    )

    supplier_partner_id = fields.Many2one(
        string="Supplier Partner in the Customer Company",
        readonly=True,
        comodel_name="res.partner",
    )

    _sql_constraints = [
        (
            "customer_supplier_company_uniq",
            "unique(customer_company_id, supplier_company_id)",
            "Customer and Supplier company must be uniq !",
        ),
    ]

    # Custom Section
    @api.model
    def _get_intercompany_trade_by_partner_company(
        self, partner_id, company_id, wkf_type
    ):
        """
        Return a intercompany.trade.config.
        * If wkf_type='in', partner_id is a supplier in the customer company;
          (purchase workflow)
        * If wkf_type='out', partner_id is a customer in the supplier company;
          (sale workflow)
        """
        if wkf_type in ["in", "in_invoice", "in_refund"]:
            domain = [
                ("supplier_partner_id", "=", partner_id),
                ("customer_company_id", "=", company_id),
            ]
        elif wkf_type in ["out", "out_invoice", "out_refund"]:
            domain = [
                ("customer_partner_id", "=", partner_id),
                ("supplier_company_id", "=", company_id),
            ]

        res = self.search(domain)
        return res and res[0] or False

    @api.model
    def _partner_from_company_fields(self):
        """
            Return the list of the fields, used for the function
            _prepare_partner_from_company()
        """
        return [
            "name", "street", "street2", "city", "zip", "state_id",
            "country_id", "website", "phone", "email", "vat",
            "logo"
        ]

    @api.model
    def _prepare_partner_from_company(self, company_id, inner_company_id):
        """
            Return vals for the creation of a partner, depending of
            a company_id.
            Note: if you change this function, please update also
            the function _prepare_partner_from_company()
        """
        company = self.env["res.company"].browse(company_id)
        return {
            "name": company.name + " " + _("(Intercompany Trade)"),
            "street": company.street,
            "street2": company.street2,
            "city": company.city,
            "zip": company.zip,
            "state_id": company.state_id.id,
            "country_id": company.country_id.id,
            "website": company.website,
            "phone": company.phone,
            "email": company.email,
            "vat": company.vat,
            "is_company": True,
            "image": company.logo,
            "intercompany_trade": True,
            "company_id": inner_company_id,
        }

    # Overload Section
    @api.model
    def create(self, vals):
        """Create or update associated partner in each company"""
        ResPartner = self.env["res.partner"]
        config = super().create(vals)
        other_config = self.search(
            [
                ("customer_company_id", "=", vals["supplier_company_id"]),
                ("supplier_company_id", "=", vals["customer_company_id"]),
            ]
        )
        if not other_config:
            # create supplier in customer company
            partner_vals = self._prepare_partner_from_company(
                vals["supplier_company_id"], vals["customer_company_id"]
            )
            partner_vals.update({"customer": False, "supplier": True})
            supplier_partner_id = (
                ResPartner.with_context(
                    force_company=vals["customer_company_id"],
                    ignore_intercompany_trade_check=True,
                )
                .sudo()
                .create(partner_vals)
            )

            # create customer in supplier company
            partner_vals = self._prepare_partner_from_company(
                vals["customer_company_id"], vals["supplier_company_id"]
            )
            partner_vals.update({"customer": True, "supplier": False})
            customer_partner_id = (
                ResPartner.with_context(
                    force_company=vals["supplier_company_id"],
                    ignore_intercompany_trade_check=True,
                )
                .sudo()
                .create(partner_vals)
            )

            # Update intercompany trade config
            config.write(
                {
                    "customer_partner_id": customer_partner_id.id,
                    "supplier_partner_id": supplier_partner_id.id,
                }
            )
        else:
            # Change the actual partners of the other config and use
            # existing partners
            other_config.customer_partner_id.supplier = True
            other_config.supplier_partner_id.customer = True
            config.write(
                {
                    "customer_partner_id": other_config.supplier_partner_id.id,
                    "supplier_partner_id": other_config.customer_partner_id.id,
                }
            )
        return config

    @api.multi
    def write(self, vals):
        """ Block possibility to change customer or supplier company"""
        if (
            "customer_company_id" in vals.keys()
            or "supplier_company_id" in vals.keys()
        ):
            if self.env.context.get("install_mode", False):
                vals.pop("customer_company_id")
                vals.pop("supplier_company_id")
            else:
                raise UserError(
                    _(
                        "You can not change customer or supplier company."
                        " If you want to do so, please disable this"
                        " intercompany trade and create a new one."
                    )
                )
        return super().write(vals)
