# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp.tests.common import TransactionCase

from openerp.addons.intercompany_trade_base.tests.\
    test_module import\
    TestModule as TestIntercompanyTradeBase


_logger = logging.getLogger(__name__)


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super(TestBase, self).setUp()

    def test_super(self):
        self.test_00_log_installed_modules()


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

        # Get Registries
        self.AccountInvoice = self.env['account.invoice']
        # self.invoice_line_obj = self.env['account.invoice.line']
        # self.product_obj = self.env['product.product']
        # self.catalog_obj = self.env['product.intercompany.trade.catalog']
        # self.config_obj = self.env['intercompany.trade.config']
        # self.link_obj = self.env['intercompany.trade.wizard.link.product']
        # self.module_obj = self.env['ir.module.module']

        # Get object from xml_ids
        # self.config = self.env.ref(
        #     'intercompany_trade_base.intercompany_trade')

        # self.customer_user = self.env.ref(
        #     'intercompany_trade_base.customer_user')
        self.supplier_user = self.env.ref(
            'intercompany_trade_base.supplier_user')

        self.intercompany_invoice = self.env.ref(
            'intercompany_trade_account.intercompany_invoice')

        # self.product_uom_unit = self.env.ref(
        #     'product.product_uom_unit')

        # self.product_customer_apple = self.env.ref(
        #     'intercompany_trade_product.product_customer_apple')

        # self.customer_product = self.env.ref(
        #     'intercompany_trade_product.product_customer_ref')
        # self.supplier_product = self.env.ref(
        #     'intercompany_trade_product.product_supplier_ref')

        # self.product_supplier_service_25_incl = self.env.ref(
        #     'intercompany_trade_account.product_supplier_service_25_incl')
        # self.product_supplier_service_10_incl = self.env.ref(
        #     'intercompany_trade_account.product_supplier_service_10_incl')
        # self.product_supplier_service_10_excl = self.env.ref(
        #     'intercompany_trade_account.product_supplier_service_10_excl')
        # self.product_customer_service_10_excl = self.env.ref(
        #     'intercompany_trade_account.product_customer_service_10_excl')
        # self.purchase_journal = self.env.ref(
        #     'intercompany_trade_account.customer_journal_purchase')
        # self.customer_account_payable = self.env.ref(
        #     'intercompany_trade_account.customer_account_payable')
        # self.supplier_account_receivable = self.env.ref(
        #     'intercompany_trade_account.supplier_account_receivable')

        # self.currency = self.env.ref('base.EUR')
        # self.out_journal = self.env.ref(
        #     'intercompany_trade_account.supplier_journal_sale')

    def test_01_confirm_invoice_out(self):
        """Confirm an Out Invoice by the supplier must create an In Invoice"""

        # Confirm supplier invoice and get it's name
        self.intercompany_invoice.sudo(self.supplier_user).with_context(
            demo_intercompany=True).signal_workflow('invoice_open')
        supplier_invoice_number = self.intercompany_invoice.number

        # Try to get the customer invoice
        invoices = self.AccountInvoice.search([
            ('supplier_invoice_number', '=', supplier_invoice_number)])

        self.assertEqual(
            len(invoices), 1,
            "Confirming a supplier invoice should create a customer invoice.")

        customer_invoice = invoices[0]
        # Check the state of the customer invoice
        self.assertEqual(
            customer_invoice.state, 'open',
            "Confirming a supplier invoice should create a confirmed"
            " customer invoice")

    #     out_invoice = self._create_out_invoice()
    #     in_invoice = self.invoice_obj.sudo(self.customer_user).browse(
    #         out_invoice.intercompany_trade_account_invoice_id)

    #     self.assertNotEqual(
    #         in_invoice.id, False,
    #         "Create an Out Invoice must create another Invoice.")

    #     self.assertEqual(
    #         in_invoice.type, 'in_invoice',
    #         "Create an In Invoice must create an Out invoice.")

    #     # Checks creation of the according Customer Invoice Line
    #     out_invoice_line = self._create_out_invoice_line(out_invoice)
    #     in_invoice_line = self.invoice_line_obj.sudo(
    #         self.customer_user).browse(
    #             out_invoice_line.
    #             intercompany_trade_account_invoice_line_id)

    #     self.assertNotEqual(
    #         out_invoice_line.id, False,
    #         "Create an Invoice Line must create another invoice Line.")

    #     # Update Customer Invoice Line (change price = must fail)
    #     with self.assertRaises(UserError):
    #         in_invoice_line.sudo(
    #             self.customer_user).write({'product_id': 10})

    #     # Update out Invoice Line (change price should update other line)
    #     out_invoice_line.sudo(
    #         self.supplier_user).write({'price_unit': 200})

    #     self.assertNotEqual(
    #         in_invoice_line.price_unit, 100,
    #         "Updating price unit on supplier invoice line should impact."
    #         " the according customer invoice line")

    #     # Update Out Invoice Line (change product = must fail)
    #     with self.assertRaises(UserError):
    #         out_invoice_line.sudo(
    #             self.supplier_user).write({
    #                 'product_id': self.product_supplier_service_25_incl.id})

    #     # Unlink Out Invoice line (must unlink according customer line)
    #     out_invoice_line.sudo(self.supplier_user).unlink()
    #     count = self.invoice_line_obj.search(
    #         [('invoice_id', '=', in_invoice.id)])

    #     self.assertEqual(
    #         len(count), 0,
    #         "Delete supplier Invoice Line must delete according"
    #         " customer Invoice Line.")

    # def test_04_confirm_invoice_out(self):
    #     """
    #         Confirm an Out Invoice (Customer Invoice) by the supplier
    #         must confirm the In Invoice
    #     """
    #     out_invoice = self._create_out_invoice()
    #     self._create_out_invoice_line(
    #         out_invoice)
    #     out_invoice.signal_workflow('invoice_open')
    #     customer_invoice = self.invoice_obj.sudo(self.customer_user).browse(
    #         out_invoice.intercompany_trade_account_invoice_id)
    #     self.assertEqual(
    #         customer_invoice.state, 'open',
    #         "Confirm an Out Invoice should confirm the according"
    # "" In Invoice.")

    # def test_05_unlink_invoice_out(self):
    #     """ Unlink an Out Invoice (Customer Invoice) by the supplier
    #         must unlink the In Invoice
    #     """
    #     # This test fail if sale module is installed, because
    #     # sale module inherit sale.order and mention that unlink()
    #     # should call action_cancel() that will fail because this module
    #     # prevent canceling intercompany_trade invoices.
    #     if not self.module_obj.search([
    #             ('name', '=', 'sale'),
    #             ('state', '=', 'installed')]):
    #         self._test_05_unlink_invoice_out()
    #     else:
    #         _logger.info(
    #             "test skipped, will be run later in"
    #             " intercompany_trade_sale")

    # def _test_05_unlink_invoice_out(self):
    #     out_invoice = self._create_out_invoice()
    #     customer_invoice_id =\
    #         out_invoice.intercompany_trade_account_invoice_id
    #     customer_invoices = self.invoice_obj.sudo(self.customer_user).search(
    #         [('id', '=', customer_invoice_id)])
    #     self.assertEqual(
    #         len(customer_invoices), 1,
    #         "Create an Out Invoice should create the according In Invoice.")
    #     out_invoice.unlink()
    #     customer_invoices = self.invoice_obj.sudo(self.customer_user).search(
    #         [('id', '=', customer_invoice_id)])
    #     self.assertEqual(
    #         len(customer_invoices), 0,
    #         "Unlink an Out Invoice should unlink the according In Invoice.")
