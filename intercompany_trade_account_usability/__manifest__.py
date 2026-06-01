# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Account Usability",
    "version": "16.0.1.0.0",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-intercompany-trade",
    "license": "AGPL-3",
    "depends": [
        # OCA
        "account_usability",
        # GRAP
        "intercompany_trade",
    ],
    "data": [
        "views/view_account_account_template.xml",
    ],
    "auto_install": True,
    "installable": True,
}
