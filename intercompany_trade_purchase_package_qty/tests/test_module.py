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
        self.config = self.env.ref(
            'intercompany_trade_base.intercompany_trade')
        self.supplier_product = self.env.ref(
            'intercompany_trade_product.product_supplier_ref')
        self.customer_product = self.env.ref(
            'intercompany_trade_product.product_customer_ref')

    def test_01_prepare_package_qty(self):
        """[Functional Test] Test if the prepare is correct"""
        res = self.config._prepare_product_supplierinfo(
            self.supplier_product.id, self.customer_product.id)
        self.assertEqual(
            res.get('indicative_package', False), True,
            "supplierinfo created from Intercompany Trade should be marked"
            " as 'Indicative Package'")
        self.assertEqual(
            res.get('package_qty', 0), 1,
            "supplierinfo created from Intercompany Trade should have 1 as"
            " package quantity")
