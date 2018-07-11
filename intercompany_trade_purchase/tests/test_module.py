# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        self.purchase_obj = self.env['purchase.order']
        self.line_obj = self.env['purchase.order.line']
        self.normal_supplier = self.env.ref(
            'intercompany_trade_base.normal_supplier')
        self.config = self.env.ref(
            'intercompany_trade_base.intercompany_trade')
        self.customer_user = self.env.ref(
            'intercompany_trade_base.customer_user')
        self.customer_company = self.env.ref(
            'intercompany_trade_base.customer_company')
        self.customer_product = self.env.ref(
            'intercompany_trade_product.product_customer_ref')
        self.warehouse = self.env.ref(
            'intercompany_trade_stock.customer_stock_warehouse')
        self.pricelist = self.env.ref(
            'intercompany_trade_purchase.purchase_pricelist')

    def test_01_invoice_purchase_order_intercompany_trade(self):
        """[Functional Test] Test if invoicing is not done for
        Intercompany Trade Purchases"""
        purchase_order = self._create_purchase_order(
            self.config.supplier_partner_id)
        purchase_order.wkf_confirm_order()
        res = purchase_order.action_invoice_create()
        self.assertEqual(
            res, False,
            "Invoicing an Intercompany Trade purchase order should not"
            " generate invoice")

    def test_02_invoice_purchase_order_not_intercompany_trade(self):
        """[Functional Test] Test if invoicing is done for
        Not Intercompany Trade Purchases"""
        purchase_order = self._create_purchase_order(self.normal_supplier)
        purchase_order.wkf_confirm_order()
        res = purchase_order.action_invoice_create()
        self.assertNotEqual(
            res, False,
            "Invoicing a non  Intercompany Trade purchase order should"
            " generate invoice")

    def _create_purchase_order(self, partner):
        purchase_order = self.purchase_obj.sudo(self.customer_user).create({
            'name': 'Intercompany Trade PO Test',
            'partner_id': partner.id,
            'company_id': self.customer_company.id,
            'pricelist_id': self.pricelist.id,
            'location_id': self.warehouse.lot_stock_id.id,
        })
        self.line_obj.sudo(self.customer_user).create({
            'order_id': purchase_order.id,
            'product_id': self.customer_product.id,
            'name': 'Intercompany Trade PO Line Test',
            'price_unit': 15.0,
            'date_planned': '1970-01-01',
        })
        return purchase_order
