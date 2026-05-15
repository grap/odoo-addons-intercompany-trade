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
        # "demo/res_groups.xml",
        "demo/account_journal.xml",
        # "demo/account_account.xml",
        # "demo/ir_property.xml",
        # "demo/account_tax.xml",
        # "demo/product_product.xml",
        # "demo/product_supplierinfo.xml",
        # "demo/account_invoice.xml",
    ],
    "data": ["views/view_account_move.xml"],
    "auto_install": True,
    "installable": True,
}
