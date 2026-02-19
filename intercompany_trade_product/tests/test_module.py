# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.intercompany_trade.tests.test_module import (
    TestIntercompanyTradeAbstract,
)


class TestModule(TestIntercompanyTradeAbstract):
    def test_01_write_property_product_pricelist_on_partner(self):
        """[Security Test] write pricelist should be possible."""
        self.customer_partner.write({"property_product_pricelist": False})
