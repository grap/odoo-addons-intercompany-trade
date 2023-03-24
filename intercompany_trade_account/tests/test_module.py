# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.intercompany_trade_base.tests.test_module import (
    TestModule as TestIntercompanyTradeBase,
)

_logger = logging.getLogger(__name__)


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super().setUp()

    def test_super(self):
        self.test_00_log_installed_modules()


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super().setUp()

        # Get Registries
        self.AccountInvoice = self.env["account.invoice"]

        # Get object from xml_ids
        self.supplier_user = self.env.ref("intercompany_trade_base.supplier_user")

        self.customer_company = self.env.ref("intercompany_trade_base.customer_company")

        self.intercompany_invoice = self.env.ref(
            "intercompany_trade_account.intercompany_invoice"
        )
        self.supplier_invoice_line_3_product = self.env.ref(
            "intercompany_trade_account.supplier_invoice_line_3_product"
        )
        self.random_product = self.env.ref("product.product_product_4d")

    def test_01_confirm_invoice_out(self):
        """Confirm an Out Invoice by the supplier must create an In Invoice"""

        # Confirm supplier invoice and get it's name
        self.intercompany_invoice.sudo(self.supplier_user).action_invoice_open()

        # Try to get the customer invoice
        invoices = self.AccountInvoice.search(
            [("reference", "=", self.intercompany_invoice.number)]
        )

        self.assertEqual(
            len(invoices),
            1,
            "Confirming a supplier invoice should create a customer invoice.",
        )

        customer_invoice = invoices[0]
        # Check the company of the created invoice
        self.assertEqual(
            customer_invoice.company_id.id,
            self.customer_company.id,
            "The generated customer invoice should be linked to the"
            " customer company.",
        )

        # Check the state of the customer invoice
        self.assertEqual(
            customer_invoice.state,
            "open",
            "Confirming a supplier invoice should create a confirmed"
            " customer invoice",
        )

        customer_invoice_notes = customer_invoice.invoice_line_ids.filtered(
            lambda x: x.display_type == "line_note"
        )
        customer_invoice_sections = customer_invoice.invoice_line_ids.filtered(
            lambda x: x.display_type == "line_section"
        )
        customer_invoice_products = customer_invoice.invoice_line_ids.filtered(
            lambda x: not x.display_type
        )

        self.assertEqual(
            len(customer_invoice_notes),
            0,
            "Intercompany Trade In invoice should not contain notes.",
        )
        self.assertEqual(
            len(customer_invoice_sections),
            0,
            "Intercompany Trade In invoice should not contain sections.",
        )
        self.assertEqual(
            len(customer_invoice_products),
            3,
            "Intercompany Trade In invoice should contain 3 product lines.",
        )

    def test_02_check_intercompany_trade_links(self):
        # Check correct invoice lines should not raise error
        self.intercompany_invoice.check_intercompany_trade_links()

        # set a product that is not referenced in the customer environment
        self.supplier_invoice_line_3_product.product_id = self.random_product
        with self.assertRaises(UserError):
            self.intercompany_invoice.check_intercompany_trade_links()
