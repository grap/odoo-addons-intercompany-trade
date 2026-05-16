# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import time

from odoo import Command
from odoo.tests import tagged

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


# class TestIntercompanyTradeAccountAccountMove(TestIntercompanyTradeAccountAbstract):
@tagged("post_install", "-at_install")
class TestIntercompanyTradeAccountAccountMove(TestIntercompanyTradeAccountAbstract):
    # AccountTestInvoicingCommon
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.AccountJournal = cls.env["account.account"]
        cls.normal_partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_5")

        # TestIntercompanyTradeAccountAbstract create
        # dedicated user for test.
        # so we add Intercompany trade companies
        # new_companies = (
        #     cls.env.user.company_ids | cls.customer_company | cls.supplier_company
        # )
        # cls.env.user.write(
        #     {
        #         "company_ids": [Command.set(new_companies.ids)],
        #         "company_id": cls.supplier_company.id,
        #     }
        # )

    def _create_account_move_invoice(
        self, move_type="out_invoice", partner=False, company=False
    ):
        date_invoice = time.strftime("%Y") + "-07-01"
        if not company:
            company = self.supplier_company
        invoice_vals = {
            "move_type": move_type,
            "partner_id": partner and partner.id or self.normal_partner.id,
            "invoice_date": date_invoice,
            "company_id": company.id,
            "date": date_invoice,
            "invoice_line_ids": [
                Command.create({"product_id": self.product.id, "tax_ids": []})
            ],
        }
        return (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            .create(invoice_vals)
        )

    def test_post_normal_sale_invoice(self):
        self._create_account_move_invoice(
            move_type="out_invoice",
            partner=self.normal_partner,
        ).action_post()

    def test_post_intercompany_trade_sale_invoice(self):
        self._create_account_move_invoice(
            move_type="out_invoice",
            partner=self.customer_company.intercompany_trade_partner_id,
        ).action_post()
