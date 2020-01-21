# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestModule(TransactionCase):

    # Overload Section
    def setUp(self):
        super(TestModule, self).setUp()

        # Get Registries
        self.config_obj = self.env["intercompany.trade.config"]

        # Get ids from xml_ids
        self.intercompany_trade_config = self.env.ref(
            "intercompany_trade_base.intercompany_trade"
        )

        self.supplier_user = self.env.ref(
            "intercompany_trade_base.supplier_user"
        )

        self.customer_company = self.env.ref(
            "intercompany_trade_base.customer_company"
        )
        self.supplier_company = self.env.ref(
            "intercompany_trade_base.supplier_company"
        )

    def test_00_log_installed_modules(self):
        module_obj = self.env["ir.module.module"]
        modules = module_obj.search([("state", "=", "installed")])
        _logger.info("============== Installed Modules ================")
        _logger.info("%d modules installed." % len(modules))
        _logger.info("============== ================= ================")
        _logger.info("==> " + ",".join(modules.mapped("name")))
        _logger.info("============== ================= ================")

    # Test Section
    def test_01_create_reverse_intercompany_trade(self):
        """[Functional Test] Check if create intercompany trade with companies
        inverse of an existing intercompany trade affect correctly partners"""
        config = self.config_obj.create(
            {
                "name": "Reverse Intercompany Trade",
                "customer_company_id": self.supplier_company.id,
                "supplier_company_id": self.customer_company.id,
                "customer_user_id": self.supplier_user.id,
            }
        )
        old_config = self.config_obj.browse(self.intercompany_trade_config.id)

        self.assertEqual(
            old_config.customer_partner_id.id,
            config.supplier_partner_id.id,
            "Create a Reverse Intercompany Trade must reuse customer.",
        )

        self.assertEqual(
            old_config.supplier_partner_id.id,
            config.customer_partner_id.id,
            "Create a Reverse Intercompany Trade must reuse supplier.",
        )

    # Test Section
    def test_02_update_company_update_partner(self):
        """[Functional Test] Check if update company data change the data
        of the partner associated"""
        new_val = "NEW STREET"
        self.intercompany_trade_config.customer_company_id.street = new_val
        config = self.config_obj.browse(self.intercompany_trade_config.id)

        self.assertEqual(
            config.customer_partner_id.street,
            new_val,
            "Update a company must change the associated partner.",
        )
