# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import time

from odoo import Command
from odoo.exceptions import UserError

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


class TestIntercompanyTradeAccountAccountMove(TestIntercompanyTradeAccountAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.normal_partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_5")
        cls.account_receivable_cae = cls.env.ref(
            "fiscal_company_account.account_receivable_cae"
        )
        cls.account_income_cae = cls.env.ref(
            "fiscal_company_account.account_income_cae"
        )
        cls.journal_sale = cls.env.ref("fiscal_company_account.journal_sale")
        cls.fiscal_position = cls.env.ref("fiscal_company_account.fiscal_position")

    def _create_account_move_invoice(
        self, move_type="out_invoice", partner=False, company=False
    ):
        date_invoice = time.strftime("%Y") + "-07-01"
        if not company:
            company = self.supplier_company
        invoice_vals = {
            "move_type": move_type,
            "partner_id": partner and partner.id or self.normal_partner.id,
            "invoice_date": date_invoice,
            "company_id": company.id,
            "date": date_invoice,
            "invoice_line_ids": [
                Command.create(
                    {"product_id": self.product.id, "tax_ids": [], "price_unit": 100}
                )
            ],
        }
        return (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            .create(invoice_vals)
        )

    def test_post_normal_sale_invoice(self):
        invoice = self._create_account_move_invoice(
            move_type="out_invoice",
            partner=self.normal_partner,
        )
        invoice.action_post()

        # Put intercompany trade fiscal position on normal invoice
        new_invoice = invoice.copy()
        new_invoice.write({"fiscal_position_id": self.fiscal_position_it.id})
        with self.assertRaises(UserError):
            new_invoice.action_post()

        # Put intercompany trade journal on normal invoice
        new_invoice = invoice.copy()
        new_invoice.write({"journal_id": self.journal_sale_it.id})
        with self.assertRaises(UserError):
            new_invoice.action_post()

        # Put intercompany trade partner account on normal invoice
        new_invoice = invoice.copy()
        # specifict case where an error is raised by Odoo Core
        # because account_partner_it is not the correct type.
        # So we reconfigure the account to raise the error
        # defined in the intercompany_trade_account module.
        self.account_partner_it.account_type = "asset_receivable"
        new_invoice.line_ids.filtered(
            lambda line: line.display_type == "payment_term"
        ).write({"account_id": self.account_partner_it.id})
        with self.assertRaises(UserError):
            new_invoice.action_post()

        # Put intercompany trade product account on normal invoice
        new_invoice = invoice.copy()
        new_invoice.line_ids.filtered(
            lambda line: line.display_type == "product"
        ).write({"account_id": self.account_income_it.id})
        with self.assertRaises(UserError):
            new_invoice.action_post()

    def test_post_intercompany_trade_sale_invoice(self):
        invoice = self._create_account_move_invoice(
            move_type="out_invoice",
            partner=self.customer_company.intercompany_trade_partner_id,
        )
        invoice.action_post()

        # Put non IT fiscal position on IT invoice
        new_invoice = invoice.copy()
        new_invoice.write({"fiscal_position_id": self.fiscal_position.id})
        with self.assertRaises(UserError):
            new_invoice.action_post()

        # Put Non IT journal on IT invoice
        # Note: write on journal_id raise a recompute
        # of company_id that we don't want.
        # so we force to keep the existing company_id
        new_invoice = invoice.copy()
        new_invoice.write(
            {
                "journal_id": self.journal_sale.id,
                "company_id": new_invoice.company_id.id,
            }
        )
        with self.assertRaises(UserError):
            new_invoice.action_post()

        # Put Non IT partner account on IT invoice
        new_invoice = invoice.copy()
        with self.assertRaises(UserError):
            new_invoice.line_ids.filtered(
                lambda line: line.display_type == "payment_term"
            ).write({"account_id": self.account_receivable_cae.id})

        # Put Non IT product account on normal invoice
        new_invoice = invoice.copy()
        new_invoice.line_ids.filtered(
            lambda line: line.display_type == "product"
        ).write({"account_id": self.account_income_cae.id})
        with self.assertRaises(UserError):
            new_invoice.action_post()

    def test_post_intercompany_trade_purchase_invoice(self):
        sale_invoice = self._create_account_move_invoice(
            move_type="out_invoice",
            partner=self.customer_company.intercompany_trade_partner_id,
        )
        sale_invoice.action_post()

        purchase_invoice = self._create_account_move_invoice(
            move_type="in_invoice",
            company=self.customer_company,
            partner=self.supplier_company.intercompany_trade_partner_id,
        )

        with self.assertRaises(UserError):
            purchase_invoice.action_post()

        purchase_invoice.write(
            {
                "invoice_date": sale_invoice.invoice_date,
                "ref": sale_invoice.name,
            }
        )

        purchase_invoice.action_post()
