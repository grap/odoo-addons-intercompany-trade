# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Purchase",
    "version": "12.0.1.1.1",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-intercompany-trade",
    "license": "AGPL-3",
    "depends": ["intercompany_trade_base", "purchase"],
    "data": [
        "views/view_purchase_order.xml",
    ],
    "demo": [],
    "auto_install": True,
    "installable": True,
}
