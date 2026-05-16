# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import tagged

from .test_abstract import TestIntercompanyTradeAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestIntercompanyTradeHook(TestIntercompanyTradeAbstract):
    def test_00_hook(self):
        """[Functional Test] Check if that hooks create correctly intercompany trade
        for existing companies"""
        self.assertTrue(self.customer_partner)
        self.assertFalse(self.mother_company.intercompany_trade_partner_id)
        self.assertFalse(self.group_company.intercompany_trade_partner_id)
