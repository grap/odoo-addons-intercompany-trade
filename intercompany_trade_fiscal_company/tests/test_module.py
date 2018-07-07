# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.intercompany_trade_product.tests.\
    test_intercompany_trade_product import\
    Test as TestIntercompanyTradeProduct


class TestModule(TestIntercompanyTradeProduct):

    def setUp(self):
        super(TestModule, self).setUp()

    def test_01_product_association(self):
        """[Functional Test] Check if associate a product create a
        product supplierinfo"""
        self._test_01_product_association()

    def test_02_product_association_recovery(self):
        """
            - Get supplier product from customer product
            - Get Customer Product from supplier Product"""
        self._test_02_product_association_recovery()
