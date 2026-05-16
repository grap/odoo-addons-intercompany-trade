# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .test_abstract import TestIntercompanyTradeAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestIntercompanyTradePartner(TestIntercompanyTradeAbstract):
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
