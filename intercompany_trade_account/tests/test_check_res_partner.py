# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import UserError

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


class TestIntercompanyTradeAccountCheckPartner(TestIntercompanyTradeAccountAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]

    def test_01_classic_partner(self):
        self.ResPartner.create({"name": "P1", "property_account_position_id": False})
        with self.assertRaises(UserError):
            self.ResPartner.create(
                {
                    "name": "P2",
                    "property_account_position_id": self.fiscal_position_it.id,
                }
            )
