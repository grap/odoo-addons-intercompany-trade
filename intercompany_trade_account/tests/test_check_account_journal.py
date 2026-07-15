# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.exceptions import UserError

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


class TestIntercompanyTradeAccountCheckJournal(TestIntercompanyTradeAccountAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountJournal = cls.env["account.journal"]

    def test_01_journal(self):
        self.AccountJournal.create(
            {"name": "J1", "is_intercompany_trade": False, "type": "bank"}
        )
        with self.assertRaises(UserError):
            self.AccountJournal.create(
                {"name": "J2", "is_intercompany_trade": True, "type": "bank"}
            )
