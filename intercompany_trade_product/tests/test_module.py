# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

# from odoo.exceptions import Warning as UserError
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.intercompany_trade_base.tests.test_module import (
    TestModule as TestIntercompanyTradeBase,
)


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super().setUp()
        self.test_00_log_installed_modules()


_logger = logging.getLogger(__name__)


class TestModule(TransactionCase):

    # Overload Section
    def setUp(self):
        super(TestModule, self).setUp()

        # Get Registries
        self.IrModuleModule = self.env["ir.module.module"]
        self.ProductSupplierinfo = self.env["product.supplierinfo"]

        # Get objects from xml_ids
        self.config = self.env.ref(
            "intercompany_trade_base.intercompany_trade"
        )
        self.config_line_category = self.env.ref(
            "intercompany_trade_product.it_line"
        )

        self.category_it_raws = self.env.ref(
            "intercompany_trade_product.category_it_raws")

        self.supplier_banana = self.env.ref(
            "intercompany_trade_product.product_supplier_banana"
        )

        self.supplier_apple = self.env.ref(
            "intercompany_trade_product.product_supplier_apple"
        )
        self.customer_apple = self.env.ref(
            "intercompany_trade_product.product_customer_apple"
        )

        self.supplier_service = self.env.ref(
            "intercompany_trade_product.product_supplier_service"
        )
        self.customer_service = self.env.ref(
            "intercompany_trade_product.product_customer_service"
        )

        self.supplier_imac = self.env.ref(
            "intercompany_trade_product.product_supplier_imac_computer"
        )
        self.customer_it_raws = self.env.ref(
            "intercompany_trade_product.product_customer_it_raws"
        )

        self.customer_user = self.env.ref(
            "intercompany_trade_base.customer_user"
        )
        self.supplier_user = self.env.ref(
            "intercompany_trade_base.supplier_user"
        )

    # Test Section
    def test_01_product_association_by_product(self):
        # this test creates pricelist.partnerinfo
        # if product_fiscal_company is installed, company_id is added
        # and so ir.rule contains company_id, but at this step
        # this field is not in the model, so an error is raised
        # in openerp/osv/expression.py #830
        # to avoid this bug, we prevent running this this if
        # product_fiscal_company is installed.
        if not self.IrModuleModule.search(
            [
                ("name", "=", "product_fiscal_company"),
                ("state", "=", "installed"),
            ]
        ):
            self._test_01_product_association_by_product()
        else:
            _logger.info(
                "test skipped, will be run later in"
                " intercompany_trade_fiscal_company"
            )

    def test_02_product_association_by_rule(self):
        # Same reason here.
        if not self.IrModuleModule.search(
            [
                ("name", "=", "product_fiscal_company"),
                ("state", "=", "installed"),
            ]
        ):
            self._test_02_product_association_by_rule()
        else:
            _logger.info(
                "test skipped, will be run later in"
                " intercompany_trade_fiscal_company"
            )

    def _test_01_product_association_by_product(self):
        # Test if getting the product in the supplier context works.
        customer_product = self.config.sudo(
            self.supplier_user
        ).get_customer_product(self.supplier_apple)

        self.assertEqual(
            customer_product,
            self.customer_apple,
            "Recovering product in the supplier context failed",
        )

        # Try to link to the same customer product to another
        # supplier product, should fail
        vals = {
            "name": self.config.supplier_partner_id.id,
            "product_tmpl_id": self.customer_service.product_tmpl_id.id,
            "supplier_product_id": self.supplier_apple.id,
        }

        with self.assertRaises(ValidationError):
            # this must fail
            self.ProductSupplierinfo.sudo(self.customer_user).create(vals)

        # Test with another product
        customer_product = self.config.sudo(
            self.supplier_user
        ).get_customer_product(self.supplier_service)

        self.assertEqual(
            customer_product,
            self.customer_service,
            "Recovering product in the supplier context failed",
        )

    def _test_02_product_association_by_rule(self):
        # Test if getting the product in the supplier context works.
        # by rule
        customer_product = self.config.sudo(
            self.supplier_user
        ).get_customer_product(self.supplier_imac)

        self.assertEqual(
            customer_product,
            self.customer_it_raws,
            "Recovering by category rule should succeed. (exact category)",
        )

        # Change the rule category for a parent product
        self.config_line_category.categ_id = self.category_it_raws

        customer_product = self.config.sudo(
            self.supplier_user
        ).get_customer_product(self.supplier_imac)

        self.assertEqual(
            customer_product,
            self.customer_it_raws,
            "Recovering by category rule should succeed. (parent category)",
        )

        customer_product = self.config.sudo(
            self.supplier_user
        ).get_customer_product(self.supplier_banana)

        self.assertEqual(
            customer_product,
            False,
            "Recovering by incorrect category rule should not return product",
        )

        # Set no category for the rule
        self.config_line_category.categ_id = False
        self.config_line_category.categ_id = self.category_it_raws

        customer_product = self.config.sudo(
            self.supplier_user
        ).get_customer_product(self.supplier_imac)
