# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools import config as tools_config


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # TODO V10. Check if it is required with workflow removing
    # Alternatively, we could add a check on the user. (Block if user != admin)
    _CUSTOMER_ALLOWED_FIELDS = [
        "state",
        "date_due",
        "period_id",
        "move_id",
        "move_name",
        "internal_number",
    ]

    # Columns Section
    intercompany_trade = fields.Boolean(
        string="Intercompany Trade",
        related="partner_id.intercompany_trade",
        store=True,
    )

    intercompany_trade_readonly = fields.Boolean(
        string="Intercompany Trade Readonly",
        compute="_compute_intercompany_trade_readonly",
    )

    # Compute Section
    @api.multi
    @api.depends("type", "intercompany_trade")
    def _compute_intercompany_trade_readonly(self):
        for invoice in self.filtered(
            lambda x: x.intercompany_trade and x.type in ["in_invoice", "in_refund"]
        ):
            invoice.intercompany_trade_readonly = True

    # Overload Section
    @api.model
    def create(self, vals):
        invoice = super().create(vals)
        invoice._check_intercompany_trade_write(vals)
        return invoice

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        self._check_intercompany_trade_write(vals)
        return res

    @api.multi
    def invoice_validate(self):
        for invoice in self.filtered(
            lambda x: x.intercompany_trade and "out_" in x.type
        ):
            invoice._create_intercompany_invoice()
        return super().invoice_validate()

    # Action Section
    @api.multi
    def check_intercompany_trade_links(self):
        self.ensure_one()
        product_list = []
        config = self._get_intercompany_trade_config_by_partner_company_type()
        for invoice_line in self._get_intercompany_trade_invoiceable_lines():
            customer_product = config.get_customer_product(invoice_line.product_id)
            if not customer_product:
                product_list.append(invoice_line.product_id)
        if product_list:
            raise UserError(
                _("Your customer should reference the following" " products: \n\n- %s")
                % (
                    "\n- ".join(
                        ["[{}] {}".format(x.code, x.name) for x in product_list]
                    )
                )
            )
        else:
            self.env.user.notify_success(
                message=_(
                    "Your customer did the job.\n\n"
                    " All the products are correctly referenced."
                ),
                sticky=True,
            )

    # Custom Section
    @api.multi
    def _get_intercompany_trade_invoiceable_lines(self):
        return self.mapped("invoice_line_ids").filtered(lambda x: not x.display_type)

    @api.multi
    def _check_intercompany_trade_write(self, vals):
        # check if the operation is done in by a intercompany trade
        # process
        if self.env.context.get("intercompany_trade_create", False):
            return

        # Check if it s about a allowed fields
        copy_vals = vals.copy()
        for key in self._CUSTOMER_ALLOWED_FIELDS:
            copy_vals.pop(key, False)
        if not copy_vals:
            return

        for invoice in self.filtered(lambda x: x.intercompany_trade):
            if "in_" in invoice.type:
                raise UserError(
                    _(
                        "You can not create a supplier invoice or refund"
                        " for intercompany trade supplier. Please ask to"
                        " your supplier to create or update it"
                    )
                )

    @api.multi
    def _create_intercompany_invoice(self):
        AccountInvoiceLine = self.env["account.invoice.line"]
        self.ensure_one()
        config = self._get_intercompany_trade_config_by_partner_company_type()
        invoice_vals = self._prepare_intercompany_vals(config)
        # Create Customer invoice
        customer_invoice = (
            self.sudo(config.customer_user_id)
            .with_context(intercompany_trade_create=True)
            .create(invoice_vals)
        )

        # Create lines
        for invoice_line in self._get_intercompany_trade_invoiceable_lines():
            line_vals = invoice_line._prepare_intercompany_vals(
                config, customer_invoice
            )
            # TODO: V10 Check if it is mandatory to use suspend_security()
            # TODO: V10, check if suspend_security() is better implemented
            # for the time being, doesn't work in test part.
            if tools_config.get("test_enable", False):
                line = (
                    AccountInvoiceLine.sudo()
                    .with_context(
                        force_company=config.customer_company_id.id,
                        intercompany_trade_create=True,
                    )
                    .create(line_vals)
                )
            else:
                line = (
                    AccountInvoiceLine.sudo(config.customer_user_id)
                    .suspend_security()
                    .with_context(intercompany_trade_create=True)
                    .create(line_vals)
                )
            line._onchange_product_id()

        for field_name in ["amount_untaxed", "amount_tax", "amount_total"]:
            supplier_value = getattr(self, field_name)
            customer_value = getattr(customer_invoice, field_name)
            if supplier_value != customer_value:
                raise UserError(
                    _(
                        "Unable to confirm this intercompany Trade invoice (or"
                        " refund) because the field '%s' is not the same: \n"
                        " - customer value : %s\n"
                        " - supplier value : %s"
                    )
                    % (field_name, customer_value, supplier_value)
                )

        # Confirm Customer invoice
        customer_invoice.sudo(config.customer_user_id).with_context(
            intercompany_trade_create=True
        ).action_invoice_open()
        self.name = customer_invoice.number

    @api.multi
    def _get_intercompany_trade_config_by_partner_company_type(self):
        Config = self.env["intercompany.trade.config"]

        self.ensure_one()
        if self.type in ("in", "in_invoice", "in_refund"):
            regular_type = "in"
        else:
            regular_type = "out"

        return Config._get_intercompany_trade_by_partner_company(
            self.partner_id.id, self.company_id.id, regular_type
        )

    @api.multi
    def _prepare_intercompany_vals(self, config):
        self.ensure_one()
        customer_user = config.customer_user_id
        other_company_id = config.customer_company_id.id
        other_partner_id = config.supplier_partner_id.id
        if self.type == "out_invoice":
            # A Sale Invoice Create a Purchase Invoice
            other_type = "in_invoice"
        elif self.type == "out_refund":
            # A Sale Refund Create a Purchase Refund
            other_type = "in_refund"

        account_journal = (
            self.sudo(customer_user)
            .with_context(type=other_type, company_id=other_company_id)
            ._default_journal()
        )

        vals = {
            "type": other_type,
            "company_id": other_company_id,
            "date_invoice": self.date_invoice,
            "date_due": self.date_due,
            "currency_id": self.currency_id.id,
            "comment": self.comment,
            "reference": self.number,
            "partner_id": other_partner_id,
            "journal_id": account_journal.id,
        }
        return vals
