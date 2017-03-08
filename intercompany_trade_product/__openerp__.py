# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Intercompany Trade - Product',
    'version': '8.0.1.0.0',
    'category': 'Intercompany Trade',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'intercompany_trade_base',
        'product',
    ],
    'demo': [
        'demo/product_product.yml',
        'demo/res_groups.yml',
        'demo/product_pricelist.yml',
        'demo/product_product.xml',
        'demo/wizard_link_product.xml',
    ],
    'data': [
        'security/ir_model_access.yml',
        'security/ir_rule.yml',
        'views/view_intercompany_trade_config.xml',
        'views/view_intercompany_trade_wizard_link_product.xml',
        'views/view_product_intercompany_trade_catalog.xml',
        'views/view_product_supplierinfo.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'auto_install': True,
    'installable': True,
}
