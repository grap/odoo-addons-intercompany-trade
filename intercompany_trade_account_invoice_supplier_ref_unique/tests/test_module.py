# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

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

    def test_01_confirm_invoice_out(self):
        """Confirm an Out Invoice by the supplier must create an In Invoice"""

        # Confirm supplier invoice and get it's name
        self.intercompany_invoice.sudo(
            self.supplier_user
        ).with_context().action_invoice_open()

        # Try to get the customer invoice
        invoices = self.AccountInvoice.search(
            [("supplier_invoice_number", "=", self.intercompany_invoice.number)]
        )

        self.assertEqual(
            len(invoices),
            1,
            "Confirming a supplier invoice should create a customer invoice with"
            " the field supplier_invoice_number defined.",
        )
