# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from odoo.addons.intercompany_trade.tests.test_abstract import (
    TestIntercompanyTradeAbstract,
)


@tagged("post_install", "-at_install")
class TestIntercompanyTradeCompany(TestIntercompanyTradeAbstract):
    def test_01_write_on_company(self):
        """[Functional Test] Write on company should propagate SIRET / NIC on
        intercompany trade partners"""
        self.customer_company.write({"siren": "790058572", "nic": "00047"})
        self.assertEqual(
            self.customer_partner.siren,
            "790058572",
            "Write on company should propagate siren",
        )
        self.assertEqual(
            self.customer_partner.nic,
            "00047",
            "Write on company should propagate nic",
        )
        self.customer_company.write({"siren": False, "nic": False})
        self.assertEqual(
            self.customer_partner.siret,
            False,
            "Write empty siren / Nic on company should recompute siret.",
        )
