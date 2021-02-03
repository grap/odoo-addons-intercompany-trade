# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Purchase",
    "version": "12.0.1.0.2",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "http://www.grap.coop",
    "license": "AGPL-3",
    "depends": [
        "intercompany_trade_base",
        "purchase",
    ],
    "data": ["views/view_purchase_order.xml"],
    "auto_install": True,
    "installable": True,
}
