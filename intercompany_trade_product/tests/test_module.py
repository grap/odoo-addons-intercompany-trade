# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp.exceptions import Warning as UserError
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase

from openerp.addons.intercompany_trade_base.tests.\
    test_module import\
    TestModule as TestIntercompanyTradeBase


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super(TestBase, self).setUp()
        self.test_00_log_installed_modules()


_logger = logging.getLogger(__name__)


class TestModule(TransactionCase):

    # Overload Section
    def setUp(self):
        super(TestModule, self).setUp()

        # Get Registries
        self.module_obj = self.env['ir.module.module']
        self.config_obj = self.env['intercompany.trade.config']
        self.product_obj = self.env['product.product']
        self.supplierinfo_obj = self.env['product.supplierinfo']
        self.partner_obj = self.env['res.partner']

        self.catalog_obj = self.env['product.intercompany.trade.catalog']
        self.link_obj = self.env['intercompany.trade.wizard.link.product']

        # Get ids from xml_ids
        self.supplier_normal = self.env.ref('base.res_partner_1')
        self.config = self.env.ref(
            'intercompany_trade_base.intercompany_trade')
        self.supplier_banana = self.env.ref(
            'intercompany_trade_product.product_supplier_banana')
        self.supplier_apple = self.env.ref(
            'intercompany_trade_product.product_supplier_apple')
        self.customer_apple = self.env.ref(
            'intercompany_trade_product.product_customer_apple')
        self.pricelist_discount = self.env.ref(
            'intercompany_trade_product.pricelist_discount')
        self.customer_user = self.env.ref(
            'intercompany_trade_base.customer_user')
        self.supplier_user = self.env.ref(
            'intercompany_trade_base.supplier_user')
        self.precision = self.env['decimal.precision'].precision_get(
            'Intercompany Trade Product Price')

    def test_01_product_association(self):
        """[Functional Test] Check if associate a product create a
        product supplierinfo"""
        # this test creates pricelist.partnerinfo
        # if product_fiscal_company is installed, company_id is added
        # and so ir.rule contains company_id, but at this step
        # this field is not in the model, so an error is raised
        # in openerp/osv/expression.py #830
        # to avoid this bug, we prevent running this this if
        # product_fiscal_company is installed.
        if not self.module_obj.search([
                ('name', '=', 'product_fiscal_company'),
                ('state', '=', 'installed')]):
            self._test_01_product_association()
        else:
            _logger.info(
                "test skipped, will be run later in"
                " intercompany_trade_fiscal_company")

    def test_02_product_association_recovery(self):
        """
            - Get supplier product from customer product
            - Get Customer Product from supplier Product"""
        # Same reason here.
        if not self.module_obj.search([
                ('name', '=', 'product_fiscal_company'),
                ('state', '=', 'installed')]):
            self._test_02_product_association_recovery()
        else:
            _logger.info(
                "test skipped, will be run later in"
                " intercompany_trade_fiscal_company")

    def test_03_create_manual_supplier_info(self):
        """ Check if create manual supplierinfo fail if partner
        is flagged as Intercompany Trade."""
        # Same reason here.
        if not self.module_obj.search([
                ('name', '=', 'product_fiscal_company'),
                ('state', '=', 'installed')]):
            self._test_03_create_manual_supplier_info()
        else:
            _logger.info(
                "test skipped, will be run later in"
                " intercompany_trade_fiscal_company")

    # Test Section
    def _test_01_product_association(self):
        # Associate with bad product (customer apple - supplier banana)
        catalog = self.catalog_obj.sudo(self.customer_user).search([
            ('supplier_product_id', '=', self.supplier_banana.id)])

        link = self.link_obj.with_context(active_id=catalog.id).sudo(
            self.customer_user).create({
                'customer_product_id': self.customer_apple.id})
        link.sudo(self.customer_user).link_product()

        supplierinfos = self.supplierinfo_obj.search([
            ('product_tmpl_id', '=', self.customer_apple.product_tmpl_id.id)])

        self.assertEqual(
            len(supplierinfos), 1,
            "Associate a Customer Product to a Supplier Product must"
            " create a Product Supplierinfo.")

        self.assertEqual(
            supplierinfos[0].intercompany_trade_price,
            round(self.supplier_banana.list_price, self.precision),
            "Associate a Customer Product to a Supplier Product must"
            " set as intercompany trade price in customer database the"
            " sale price of the supplier product.")

        self.assertEqual(
            supplierinfos[0].pricelist_ids[0].price,
            round(self.supplier_banana.list_price, self.precision),
            "Associate a Customer Product to a Supplier Product must"
            " set as intercompany trade price in customer database the"
            " sale price of the supplier product in items list.")

        # Reassociate with correct product (customer apple - supplier apple)
        # Must Fail
        catalog_2 = self.catalog_obj.sudo(self.customer_user).search([
            ('supplier_product_id', '=', self.supplier_apple.id)])

        link = self.link_obj.with_context(active_id=catalog_2.id).sudo(
            self.customer_user).create({
                'customer_product_id': self.customer_apple.id})

        with self.assertRaises(UserError):
            # this must fail
            link.sudo(self.customer_user).link_product()

        # Remove association
        catalog.sudo(self.customer_user).button_unlink_product()

        supplierinfos = self.supplierinfo_obj.search([
            ('product_tmpl_id', '=', self.customer_apple.product_tmpl_id.id)])

        self.assertEqual(
            len(supplierinfos), 0,
            "Unlink a Customer Product must delete The Product Supplierinfo.")

    def _test_02_product_association_recovery(self):
        # Associate a product
        catalog = self.catalog_obj.sudo(self.customer_user).search([
            ('supplier_product_id', '=', self.supplier_apple.id)])

        link = self.link_obj.with_context(active_id=catalog.id).sudo(
            self.customer_user).create({
                'customer_product_id': self.customer_apple.id})

        link.sudo(self.customer_user).link_product()

        customer_product = self.config.sudo(
            self.supplier_user)._get_product_in_customer_company(
                self.supplier_apple)
        self.assertEqual(
            self.customer_apple,
            customer_product,
            "Function to recovery customer product info from supplier"
            " product doesn't work.")

    def _test_03_create_manual_supplier_info(self):
        # Associate the product with a Normal Supplier. Should success
        self.supplierinfo_obj.create({
            'name': self.supplier_normal.id,
            'product_tmpl_id': self.supplier_apple.product_tmpl_id.id,
        })

        # Associate the product with a Intercompany Trade Supplier. Should fail
        with self.assertRaises(ValidationError):
            self.supplierinfo_obj.create({
                'name': self.config.supplier_partner_id.id,
                'product_tmpl_id': self.customer_apple.product_tmpl_id.id,
            })
