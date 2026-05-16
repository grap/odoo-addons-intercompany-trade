# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.intercompany_trade.tests.test_abstract import (
    TestIntercompanyTradeAbstract,
)

_logger = logging.getLogger(__name__)


class TestIntercompanyTradeAccountAbstract(TestIntercompanyTradeAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position_it = cls.env.ref(
            "intercompany_trade_account.fiscal_position"
        )
        cls.journal_sale_it = cls.env.ref("intercompany_trade_account.journal_sale")
        cls.account_partner_it = cls.env.ref(
            "intercompany_trade_account.intercompany_trade_account_company"
        )
        cls.account_income_it = cls.env.ref(
            "intercompany_trade_account.intercompany_trade_account_income"
        )
