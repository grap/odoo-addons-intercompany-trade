# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import tagged

from odoo.addons.fiscal_company_base.tests.test_abstract import TestAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestIntercompanyTradeAbstract(TestAbstract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.customer_company = cls.env.ref("fiscal_company_base.company_fiscal_child_1")
        cls.supplier_company = cls.env.ref("fiscal_company_base.company_fiscal_child_2")
        cls.supplier_user = cls.env.ref("intercompany_trade.supplier_user")
        cls.customer_partner = cls.customer_company.intercompany_trade_partner_id
        cls.supplier_partner = cls.supplier_company.intercompany_trade_partner_id
        cls.random_partner = cls.env.ref("base.res_partner_address_15")
