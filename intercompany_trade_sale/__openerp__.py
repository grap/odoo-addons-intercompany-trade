# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Intercompany Trade - Sale',
    'version': '8.0.1.0.0',
    'category': 'Intercompany Trade',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'intercompany_trade_base',
        'intercompany_trade_product',
        'intercompany_trade_account',
        'sale',
    ],
    'demo': [
        'demo/product_pricelist.xml',
        'demo/sale_order.xml',
    ],
    'auto_install': False,
    'installable': True,
}
