# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Intercompany Trade - Fiscal Company",
    "version": "12.0.2.0.4",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-intercompany-trade",
    "license": "AGPL-3",
    "depends": ["fiscal_company_base", "intercompany_trade_base", "account"],
    "data": [
        "views/view_account_account.xml",
        "views/view_account_fiscal_position.xml",
        "views/view_intercompany_trade_config.xml",
        "views/view_res_company.xml",
    ],
    "demo": [
        "demo/account_account.xml",
        "demo/res_company.xml",
        "demo/intercompany_trade_config.xml",
    ],
    "auto_install": True,
    "installable": True,
}
