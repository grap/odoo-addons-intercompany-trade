# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

        self.pos_session_obj = self.env['pos.session']
        self.pos_order_obj = self.env['pos.order']
        self.intercompany_trade = self.env.ref(
            'intercompany_trade_base.intercompany_trade')
        self.main_config = self.env.ref('point_of_sale.pos_config_main')

    # Test Section
    def test_01_pos_order_constrains(self):
        """[Functional Test] Check if creating a pos order with integrated
        Trade is blocked"""
        self.session = self.pos_session_obj.create(
            {'config_id': self.main_config.id})
        self.session.open_cb()
        self.partner = self.intercompany_trade.customer_partner_id
        with self.assertRaises(ValidationError):
            self.pos_order_obj.create({
                'session_id': self.session.id,
                'partner_id': self.partner.id,
            })
