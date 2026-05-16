# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


# class TestIntercompanyTradeAccountAccountMove(TestIntercompanyTradeAccountAbstract):
@tagged("post_install", "-at_install")
class TestIntercompanyTradeAccountAccountMove(
    TestIntercompanyTradeAccountAbstract, AccountTestInvoicingCommon
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.AccountJournal = cls.env["account.account"]
        cls.normal_partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_5")

        # TestIntercompanyTradeAccountAbstract create
        # dedicated user for test.
        # so we add Intercompany trade companies
        new_companies = (
            cls.env.user.company_ids | cls.customer_company | cls.supplier_company
        )
        cls.env.user.write(
            {
                "company_ids": [Command.set(new_companies.ids)],
            }
        )
        cls.normal_sale_invoice = cls.init_invoice(
            "out_invoice",
            partner=cls.normal_partner,
            products=[cls.product],
            company=cls.supplier_company,
        )
        cls.intercompany_trade_sale_invoice = cls.init_invoice(
            "out_invoice",
            partner=cls.customer_company.intercompany_trade_partner_id,
            products=[cls.product],
            company=cls.supplier_company,
        )

    def test_post_normal_sale_invoice(self):
        self.normal_sale_invoice.action_post()

    def test_post_intercompany_trade_sale_invoice(self):
        self.intercompany_trade_sale_invoice.action_post()
