# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

from odoo.addons.intercompany_trade_base.tests.test_module import (
    TestModule as TestIntercompanyTradeBase,
)


class TestBase(TestIntercompanyTradeBase):
    def setUp(self):
        super().setUp()
        self.test_00_log_installed_modules()


class TestModule(TransactionCase):

    # Overload Section
    def setUp(self):
        super().setUp()

        self.PosSession = self.env["pos.session"]
        self.PosOrder = self.env["pos.order"]
        self.intercompany_trade = self.env.ref(
            "intercompany_trade_base.intercompany_trade"
        )
        self.pos_config = self.env.ref("point_of_sale.pos_config_main").copy()

    # Test Section
    def test_01_pos_order_constrains(self):
        """[Functional Test] Check if creating a pos order with integrated
        Trade is blocked"""
        self.pos_config.open_session_cb()
        self.partner = self.intercompany_trade.customer_partner_id
        with self.assertRaises(ValidationError):
            self.PosOrder.create({
                "session_id": self.pos_config.current_session_id.id,
                "partner_id": self.partner.id,
                "amount_tax": 0.0,
                "amount_total": 0.0,
                "amount_paid": 0.0,
                "amount_return": 0.0,
            })
