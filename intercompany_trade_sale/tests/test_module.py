# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase

from openerp.addons.intercompany_trade_base.tests.\
    test_module import\
    TestModule as TestIntercompanyTradeBase


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super(TestBase, self).setUp()
        self.test_00_log_installed_modules()


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        self.sale_obj = self.env['sale.order']
        self.line_obj = self.env['sale.order.line']
        self.invoice_obj = self.env['account.invoice']
        self.config = self.env.ref(
            'intercompany_trade_base.intercompany_trade')
        self.supplier_user = self.env.ref(
            'intercompany_trade_base.supplier_user')
        self.supplier_company = self.env.ref(
            'intercompany_trade_base.supplier_company')
        self.pricelist = self.env.ref(
            'intercompany_trade_product.sale_pricelist')
        self.supplier_product = self.env.ref(
            'intercompany_trade_product.product_supplier_ref')

    def test_01_invoice_sale_order(self):
        """[Functional Test] Test if invoicing an sale order works correclty"""
        sale_order = self.sale_obj.sudo(self.supplier_user).create({
            'name': 'Intercompany Trade SO Test',
            'partner_id': self.config.customer_partner_id.id,
            'company_id': self.supplier_company.id,
            'pricelist_id': self.pricelist.id,
        })
        self.line_obj.sudo(self.supplier_user).create({
            'order_id': sale_order.id,
            'product_id': self.supplier_product.id,
            'name': 'Intercompany Trade SO Line Test',
            'price_unit': 15.0,
            'product_uom_qty': 2,
        })
        sale_order.action_button_confirm()
        res = sale_order.sudo(self.supplier_user).action_invoice_create()
        invoice = self.invoice_obj.browse(res)
        line = invoice.invoice_line[0]
        self.assertNotEqual(
            line.intercompany_trade_account_invoice_line_id, False,
            "Invoicing an Intercompany Trade sale order should generate"
            " invoice lines with related invoice id.")
