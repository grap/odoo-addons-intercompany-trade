# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.intercompany_trade_product.tests.\
    test_intercompany_trade_product import\
    Test as TestIntercompanyTradeProduct

from openerp.addons.intercompany_trade_stock_account.tests.\
    test_module import\
    TestModule as TestIntercompanyTradeStockAccount


class TestModuleProduct(TestIntercompanyTradeProduct):

    def setUp(self):
        super(TestModuleProduct, self).setUp()

    def test_01_product_association(self):
        """[Functional Test] Check if associate a product create a
        product supplierinfo"""
        self._test_01_product_association()

    def test_02_product_association_recovery(self):
        """
            - Get supplier product from customer product
            - Get Customer Product from supplier Product"""
        self._test_02_product_association_recovery()


class TestModuleStockAccount(TestIntercompanyTradeStockAccount):

    def setUp(self):
        super(TestModuleStockAccount, self).setUp()

    def test_01_invoice_stock_picking(self):
        """[Functional Test] Check if invoicing stock picking
        create correct intercompany trade invoice"""
        self._test_01_invoice_stock_picking()
