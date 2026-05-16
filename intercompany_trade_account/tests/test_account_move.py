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
                Command.create({"product_id": self.product.id, "tax_ids": []})
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
