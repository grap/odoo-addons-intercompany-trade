# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # Columns Section
    is_intercompany_trade = fields.Boolean(
        compute="_compute_is_intercompany_trade", store=True
    )

    intercompany_trade_id = fields.Many2one(
        string="Intercompany Trade",
        store=True,
        compute="_compute_intercompany_trade_id",
        compute_sudo=True,
        comodel_name="intercompany.trade.config",
    )

    supplier_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Supplier Product",
        selected=True,
        _prefetch=False,
    )

    catalog_id = fields.Many2one(
        comodel_name="intercompany.trade.catalog",
        string="Catalog",
        compute="_compute_catalog_id",
        inverse="_inverse_catalog_id",
        domain="[('intercompany_trade_id', '=', intercompany_trade_id)]",
    )

    # Compute Section
    @api.multi
    @api.depends("name")
    def _compute_is_intercompany_trade(self):
        for supplierinfo in self.filtered(lambda x: x.name):
            supplierinfo.is_intercompany_trade = supplierinfo.name.intercompany_trade

    @api.multi
    @api.depends("name")
    def _compute_intercompany_trade_id(self):
        IntercompanyTradeConfig = self.sudo().env["intercompany.trade.config"]
        for supplierinfo in self.filtered(lambda x: x.name):
            supplierinfo.intercompany_trade_id = IntercompanyTradeConfig.search(
                [
                    ("customer_company_id", "=", supplierinfo.name.company_id.id),
                    ("supplier_partner_id", "=", supplierinfo.name.id),
                ]
            ).id

    @api.multi
    @api.depends("intercompany_trade_id", "supplier_product_id")
    def _compute_catalog_id(self):
        for supplierinfo in self.filtered(
            lambda x: x.intercompany_trade_id and x.supplier_product_id
        ):
            supplierinfo.catalog_id = int(
                "%s%s"
                % (
                    supplierinfo.supplier_product_id.id,
                    str(supplierinfo.intercompany_trade_id.id).rjust(4, "0"),
                )
            )

    @api.multi
    def _inverse_catalog_id(self):
        for supplierinfo in self.filtered(lambda x: x.catalog_id):
            res = int(str(supplierinfo.catalog_id.id)[:-4])
            supplierinfo.supplier_product_id = res

    @api.onchange("catalog_id")
    def _onchange_catalog_id(self):
        ProductProduct = self.env["product.product"]
        for supplierinfo in self.filtered(lambda x: x.catalog_id):
            product_id = int(str(supplierinfo.catalog_id.id)[:-4])
            supplierinfo.supplier_product_id = product_id
            product = ProductProduct.sudo().browse(product_id)
            supplierinfo.product_name = product.name
            supplierinfo.product_code = product.code

    @api.constrains("supplier_product_id", "is_intercompany_trade", "product_tmpl_id")
    def _check_intercompany_trade(self):
        for supplierinfo in self.filtered(
            lambda x: x.is_intercompany_trade and x.supplier_product_id
        ):
            # Check if the supplier product has been linked to other
            # product
            res = self.search(
                [
                    (
                        "supplier_product_id",
                        "=",
                        supplierinfo.supplier_product_id.id,
                    ),
                    ("id", "!=", supplierinfo.id),
                ]
            )
            if len(res):
                raise UserError(
                    _(
                        "The product(s) %s  are still linked to the"
                        " the supplier product. You can not link the product"
                        " %s."
                    )
                    % (
                        ", ".join(res.mapped("product_tmpl_id.name")),
                        supplierinfo.product_tmpl_id.name,
                    )
                )
