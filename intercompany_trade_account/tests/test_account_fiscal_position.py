# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import UserError
from odoo.tests import tagged

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestIntercompanyTradeAccountFiscalPosition(TestIntercompanyTradeAccountAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.normal_partner = cls.env.ref("base.res_partner_2").with_company(
            cls.customer_company
        )
        cls.it_partner = (
            cls.customer_company.intercompany_trade_partner_id.with_company(
                cls.customer_company
            )
        )
        cls.it_fiscal_position = cls.env.ref(
            "intercompany_trade_account.fiscal_position"
        )
        cls.cae_fiscal_position = cls.env.ref("fiscal_company_account.fiscal_position")
        cls.product = cls.env.ref(
            "intercompany_trade_account.product_supplier_service_10_excl"
        )

    def test_01_correct_fiscal_configuration(self):
        self.assertEqual(
            self.it_partner.property_account_position_id,
            self.it_fiscal_position,
        )

    def test_10_correct_check_normal_partner(self):
        # this command should success
        self.normal_partner.property_account_position_id = self.cae_fiscal_position

        with self.assertRaises(UserError):
            self.normal_partner.property_account_position_id = self.it_fiscal_position

    def test_11_correct_check_intercompany_trade_partner(self):
        # this command should success
        self.it_partner.property_account_position_id = self.it_fiscal_position

        with self.assertRaises(UserError):
            self.it_partner.property_account_position_id = self.cae_fiscal_position

    def test_20_propagate_taxes(self):
        new_tax = self.env["account.tax"].create(
            {"name": "New Tax", "company_id": self.mother_company.id}
        )

        self.assertNotIn(new_tax, self.it_fiscal_position.mapped("tax_ids.tax_src_id"))

        self.product.taxes_id |= new_tax

        self.assertIn(new_tax, self.it_fiscal_position.mapped("tax_ids.tax_src_id"))
