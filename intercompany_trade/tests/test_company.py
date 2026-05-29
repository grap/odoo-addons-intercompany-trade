# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import tagged

from .test_abstract import TestIntercompanyTradeAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestIntercompanyTradeCompany(TestIntercompanyTradeAbstract):
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
