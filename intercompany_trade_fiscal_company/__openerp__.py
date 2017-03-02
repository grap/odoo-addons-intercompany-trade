# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Intercompany Trade - Fiscal Company',
    'version': '8.0.1.0.0',
    'category': 'Intercompany Trade',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base_fiscal_company',
        'account_fiscal_company',
        'intercompany_trade_base',
        'purchase',
        'sale',
        'stock',
        'simple_tax_account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir_model_access.yml',
        'views/account_account_view.xml',
        'views/fiscal_company_transcoding_account_view.xml',
        'views/intercompany_trade_config_view.xml',
        'views/res_company_view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/account_tax.yml',
        'demo/account_account.xml',
        'demo/res_company.yml',
        'demo/fiscal_company_transcoding_account.yml',
        'demo/res_users.yml',
        'demo/res_groups.yml',
        'demo/intercompany_trade_config.yml',
        'demo/product_product.yml',
        'demo/stock_location.yml',
        'demo/stock_warehouse.yml',
        'demo/sale_shop.yml',
        'demo/ir_values.yml',
    ],
    'auto_install': True,
    'installable': True,
}
