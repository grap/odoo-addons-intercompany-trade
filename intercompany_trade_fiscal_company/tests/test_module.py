# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.intercompany_trade_product.tests.\
    test_module import\
    TestModule as TestIntercompanyTradeProduct

from openerp.addons.intercompany_trade_base.tests.\
    test_module import\
    TestModule as TestIntercompanyTradeBase


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super(TestBase, self).setUp()
        self.test_00_log_installed_modules()


class TestModuleProduct(TestIntercompanyTradeProduct):

    def setUp(self):
        super(TestModuleProduct, self).setUp()

    def test_01_product_association_by_product(self):
        self._test_01_product_association_by_product()

    def test_02_product_association_by_rule(self):
        self._test_02_product_association_by_rule()
