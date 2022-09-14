# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    # Due to bad design, some field are written on computed function
    # with account_invoice_triple_discount
    # To avoid error, the following fields are allowed for the time being
    # TODO V10. Check if it is required.
    # Alternatively, we could add a check on the user. (Block if user != admin)
    # _CUSTOMER_ALLOWED_FIELDS = [
    #     'discount', 'price_unit']

    # Columns Section
    intercompany_trade = fields.Boolean(
        string="Intercompany Trade",
        related="invoice_id.intercompany_trade",
        store=True,
    )

    # Custom Section
    @api.multi
    def _prepare_intercompany_vals(self, config, customer_invoice):
        self.ensure_one()

        # Create according account invoice line
        customer_product = config.get_customer_product(self.product_id)

        if not self.display_type:
            if not customer_product:
                raise UserError(
                    _(
                        "It is not possible to confirm this invoice, because"
                        " your customer didn't referenced your product %s-%s"
                    )
                    % (self.product_id.default_code, self.product_id.name)
                )

            customer_template_product = customer_product.product_tmpl_id

            account_id = customer_template_product._get_product_accounts()["expense"].id

            if not account_id:
                raise UserError(
                    _(
                        "It is not possible to confirm this invoice, because"
                        " the product of your customer doesn't have a correct"
                        " accounting setting %s - %s"
                    )
                    % (
                        customer_template_product.default_code,
                        customer_template_product.name,
                    )
                )
            vals = {
                "name": customer_product.name,
                "account_id": account_id,
                "product_id": customer_product.id,
            }
        else:
            vals = {
                "name": self.name,
            }
        vals.update(
            {
                "invoice_id": customer_invoice.id,
                "company_id": customer_invoice.company_id.id,
                "partner_id": customer_invoice.partner_id.id,
                "quantity": self.quantity,
                "price_unit": self.price_unit,
                "discount": self.discount,
                "display_type": self.display_type,
            }
        )
        return vals
