# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import Warning as UserError
from odoo.tests.common import TransactionCase

# from odoo.addons.intercompany_trade_base.tests.test_module import (
#     TestModule as TestIntercompanyTradeBase,
# )


_logger = logging.getLogger(__name__)


# class TestBase(TestIntercompanyTradeBase):
#     def setUp(self):
#         super().setUp()

#     def test_super(self):
#         self.test_00_log_installed_modules()


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super().setUp()

        # Get Registries
        self.AccountInvoice = self.env["account.invoice"]

        # Get object from xml_ids
        self.customer_user = self.env.ref(
            "intercompany_trade_base.customer_user"
        )
        self.supplier_user = self.env.ref(
            "intercompany_trade_base.supplier_user"
        )

        self.intercompany_invoice = self.env.ref(
            "intercompany_trade_account.intercompany_invoice"
        )

    def test_01_cancel_invoice_confirmed(self):
        """Cancel an Out or In confirmed invoice should fail"""

        self.intercompany_invoice.sudo(
            self.supplier_user).action_invoice_open()

        with self.assertRaises(UserError):
            # Try to cancel 'out invoice' should fail
            self.intercompany_invoice.sudo(
                self.supplier_user).action_invoice_cancel()

        # Try to get the customer invoice
        invoices = self.AccountInvoice.search(
            [("reference", "=", self.intercompany_invoice.number)]
        )

        with self.assertRaises(UserError):
            # Try to cancel 'in invoice' should fail
            invoices.sudo(self.customer_user).action_invoice_cancel()

    def test_02_cancel_invoice_draft(self):
        """Cancel a draft invoice should success"""

        invoice = self.intercompany_invoice.sudo(
            self.supplier_user)
        invoice.action_invoice_cancel()
