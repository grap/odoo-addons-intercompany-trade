# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Intercompany Trade - Base',
    'version': '8.0.1.0.0',
    'category': 'Intercompany Trade',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'demo': [
        'demo/res_company.yml',
        'demo/res_users.xml',
        'demo/res_groups.xml',
        'demo/intercompany_trade_config.xml',
    ],
    'data': [
        'security/ir_module_category.yml',
        'security/res_groups.yml',
        'security/ir_model_access.yml',
        'views/res_partner_view.xml',
        'views/intercompany_trade_config_view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'css': [
        'static/src/css/itb.css',
    ],
    'installable': True,
}
