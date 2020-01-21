# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade - Product",
    "version": "12.0.1.0.0",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "http://www.grap.coop",
    "license": "AGPL-3",
    "depends": ["intercompany_trade_base", "product",],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/view_intercompany_trade_config.xml",
        # 'views/view_intercompany_trade_wizard_link_product.xml',
        # 'views/view_product_intercompany_trade_catalog.xml',
        "views/view_product_supplierinfo.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
        "demo/product_product.xml",
        "demo/product_pricelist.xml",
        "demo/product_product.xml",
        "demo/product_supplierinfo.xml",
        "demo/intercompany_trade_config_line.xml",
    ],
    "auto_install": True,
    "installable": True,
}
