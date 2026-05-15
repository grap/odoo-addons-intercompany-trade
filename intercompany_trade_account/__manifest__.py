# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Account",
    "version": "16.0.1.0.0",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-intercompany-trade",
    "license": "AGPL-3",
    "depends": [
        # Odoo
        "account",
        # Custom
        "intercompany_trade",
    ],
    "demo": [
        "demo/res_groups.xml",
        "demo/account_journal.xml",
        "demo/account_account.xml",
        "demo/product_product.xml",
        "demo/account_fiscal_position.xml",
        "demo/res_company.xml",
        # "demo/account_invoice.xml",
    ],
    "data": [
        "views/view_account_move.xml",
        "views/view_res_config_settings.xml",
    ],
    "auto_install": True,
    "installable": True,
}
