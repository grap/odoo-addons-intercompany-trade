# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import tagged

from .test_abstract import TestIntercompanyTradeAccountAbstract

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestIntercompanyTradeAccountChartTemplate(TestIntercompanyTradeAccountAbstract):
    def test_01_classic_partner(self):
        chart_template = self.env["account.chart.template"].search([], limit=1)
        if not chart_template:
            return
        company = self.env["res.company"].create(
            {
                "name": "CAE company - Test chart template",
                "fiscal_type": "fiscal_mother",
            }
        )

        template_account = chart_template.account_ids[0]
        template_account.is_intercompany_trade = True

        # Load chart template
        chart_template.try_loading(company=company, install_demo=False)

        # check if account setting is correct
        new_account = self.env["account.account"].search(
            [("company_id", "=", company.id), ("is_intercompany_trade", "=", True)]
        )
        self.assertEqual(len(new_account), 1)

        # Note: We can not test fiscal position correct setting because demo CoA
        # doesn't contain any fiscal position. Maybe the coA-pocalypse
        # in most recent version will fix that.
