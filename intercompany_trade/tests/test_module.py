# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.fiscal_company_base.tests.test_abstract import TestAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestModule(TestAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.customer_company = cls.env.ref("fiscal_company_base.company_fiscal_child_1")
        cls.supplier_company = cls.env.ref("fiscal_company_base.company_fiscal_child_2")
        cls.customer_partner = cls.customer_company.intercompany_trade_partner_id
        cls.supplier_partner = cls.customer_company.intercompany_trade_partner_id

        cls.random_partner = cls.env.ref("base.res_partner_address_15")

    # Test Section
    def test_00_hook(self):
        """[Functional Test] Check if that hooks create correctly intercompany trade
        for existing companies"""
        self.assertTrue(self.customer_partner)
        self.assertFalse(self.mother_company.intercompany_trade_partner_id)
        self.assertFalse(self.group_company.intercompany_trade_partner_id)

    def test_01_create_new_company_and_change_fiscal_type(self):
        """[Functional Test] Check if create a new company, create or not
        intercompany trade partners"""

        for fiscal_type in ["group", "normal", "fiscal_mother"]:
            company = self.env["res.company"].create(
                {
                    "name": f"Test Intercompany Trade Company {fiscal_type}",
                    "fiscal_type": fiscal_type,
                }
            )
            self.assertFalse(
                company.intercompany_trade_partner_id,
                f"Creating a company of type '{fiscal_type}'"
                " should not create an intercompany partner.",
            )

        company.write(
            {
                "fiscal_type": "fiscal_child",
                "parent_id": self.mother_company.id,
            }
        )
        self.assertTrue(
            company.intercompany_trade_partner_id,
            "Transform a company in type 'fiscal_child'"
            " should create an intercompany partner.",
        )

        company = self.env["res.company"].create(
            {
                "name": "Test Intercompany Trade Company fiscal_child",
                "fiscal_type": "fiscal_child",
                "parent_id": self.mother_company.id,
            }
        )
        self.assertTrue(
            company.intercompany_trade_partner_id,
            "Creating a company of type 'fiscal_child'"
            " should create an intercompany partner.",
        )

        company.write(
            {
                "fiscal_type": "normal",
                "parent_id": False,
            }
        )
        self.assertFalse(
            company.intercompany_trade_partner_id,
            "Transform an integrated company in type 'Normal'"
            " should unlink the intercompany partner.",
        )

    def test_02_write_on_company(self):
        """[Functional Test] Write on company should propagate data on
        intercompany trade partners"""
        self.customer_company.write({"street": "My Custom Street"})
        self.assertEqual(
            self.customer_partner.street,
            "My Custom Street",
            "Write on company should change data on related partner",
        )

    def test_03_write_active_on_partner(self):
        """[Security Test] Enable / disable intercompany trade partners should success
        for admin user, but not for demo user."""
        self.customer_partner.write({"active": False})
        self.customer_partner.write({"active": True})

        with self.assertRaises(UserError):
            self.customer_partner.with_user(self.env.ref("base.user_demo")).write(
                {"active": False}
            )

    def test_10_check_parent_partner(self):
        """[Constrains Test] Check if set a parent to a intercompany trade partner
        is blocked."""
        with self.assertRaises(ValidationError):
            self.customer_partner.with_context(
                ignore_intercompany_trade_check=True
            ).write({"parent_id": self.random_partner.id})

    def test_11_check_child_partner(self):
        """[Constrains Test] Check if set a child to a intercompany trade partner
        is blocked."""
        with self.assertRaises(ValidationError):
            self.random_partner.with_context(
                ignore_intercompany_trade_check=True
            ).write({"parent_id": self.customer_partner.id})
