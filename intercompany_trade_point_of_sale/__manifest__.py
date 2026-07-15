# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Intercompany Trade - Point Of Sale",
    "version": "16.0.1.0.0",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-intercompany-trade",
    "license": "AGPL-3",
    "depends": [
        # Odoo
        "point_of_sale",
        # GRAP
        "intercompany_trade",
        "fiscal_company_point_of_sale",
    ],
    "assets": {
        "point_of_sale.assets": [
            "intercompany_trade_point_of_sale/static/src/js/**/*.js",
        ],
    },
    "auto_install": True,
    "installable": True,
}
