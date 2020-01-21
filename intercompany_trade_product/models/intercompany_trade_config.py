# Copyright (C) 2014 - Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class IntercompanyTradeConfig(models.Model):
    _inherit = "intercompany.trade.config"

    # Columns section
    line_ids = fields.One2many(
        comodel_name="intercompany.trade.config.line", inverse_name="config_id"
    )

    # Custom Section
    @api.multi
    def get_customer_product(self, product):
        """
            Return the product in the customer company from a product in the
            supplier company

            :param @product: product in the supplier company
            :return : product, in the customer company
        """
        self.ensure_one()
        customer_product = self._get_customer_product_by_product(product)
        if not customer_product:
            customer_product = self._get_customer_product_by_rule(product)
        return customer_product

    @api.multi
    def _get_customer_product_by_product(self, product):
        self.ensure_one()

        product_obj = self.env["product.product"]
        supplierinfo_obj = self.env["product.supplierinfo"]

        # Get current Product
        product = product_obj.sudo().browse(product.id)
        supplierinfos = supplierinfo_obj.sudo().search(
            [
                ("supplier_product_id", "=", product.id),
                ("name", "=", self.supplier_partner_id.id),
                ("company_id", "=", self.customer_company_id.id),
            ]
        )
        if len(supplierinfos) == 0:
            return False
        supplierinfo = supplierinfos[0]
        customer_products = (
            product_obj.sudo(self.customer_user_id)
            .with_context(active_test=False)
            .search(
                [
                    ("company_id", "=", self.customer_company_id.id),
                    ("product_tmpl_id", "=", supplierinfo.product_tmpl_id.id),
                ]
            )
        )
        if len(customer_products) != 1:
            raise UserError(
                _(
                    "You can not add '%s' to the current Order or Invoice"
                    " because the customer referenced many variants of"
                    " this template."
                )
                % (product.name)
            )
        return customer_products[0]

    @api.multi
    def _get_customer_product_by_rule(self, product):
        """Overloadable function, allow to return a product if the
        customer did'nt referenced the supplier product, by category,
        or other rules."""
        self.ensure_one()
        for line in self.line_ids:
            if line.match_rule(product):
                return line.product_id
        return False
