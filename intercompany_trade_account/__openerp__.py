# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Intercompany Trade - Account',
    'version': '1.0',
    'category': 'Intercompany Trade',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'intercompany_trade_base',
        'account',
        'stock',
        'purchase',
        'simple_tax_account',
        'invoice_pricelist',
    ],
    'demo': [
        'demo/res_groups.yml',
        'demo/account_account.yml',
        'demo/account_journal.yml',
        'demo/ir_property.xml',
        'demo/account_tax.yml',
        'demo/product_product.yml',
        'demo/account_invoice.xml',
    ],
    'data': [
        'views/view_product_intercompany_trade_catalog.xml',
        'views/view_intercompany_trade_wizard_link_product.xml',
        'views/view_account_invoice.xml',
        'views/view_intercompany_trade_config.xml',
        'views/action.xml',
        'views/menu.xml',
        'data/init.xml',
    ],
    'auto_install': True,
    'installable': True,
}
