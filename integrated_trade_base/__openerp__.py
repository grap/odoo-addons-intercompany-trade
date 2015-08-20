# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Base module for OpenERP
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Integrated Trade - Base',
    'version': '1.0',
    'category': 'Integrated Trade',
    'description': """
Module for Integrated Trade for Base Module
===========================================

Features :
----------
    * Add a New Model Integrated trade that define that two company can realize
      purchases and sales between them with:
        * a supplier company;
        * a customer company;
    * Add a new field 'intercompany_trade' in 'res.partner' model;
    * Add new groups to manage intercompany trade;
    * When we set a new intercompany trade, OpenERP create a supplier in the
      customer company and a customer in the supplier company;

Demo Data:
----------
    * In demo mode, the module creates two new companies, and two users:
        * A supplier user: login: intercompany_tradesupplier // demo
        * A customer user: login: intercompany_tradecustomer // demo


Copyright, Authors and Licence:
-------------------------------
    * Copyright: 2014, GRAP: Groupement Régional Alimentaire de Proximité;
    * Author:
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence: AGPL-3 (http://www.gnu.org/licenses/);""",
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'demo': [
        'demo/res_company.yml',
        'demo/res_users.yml',
        'demo/res_groups.yml',
        'demo/intercompany_trade_config.yml',
    ],
    'data': [
        'security/ir_module_category.yml',
        'security/res_groups.yml',
        'security/ir_model_access.yml',
        'view/view.xml',
        'view/action.xml',
        'view/menu.xml',
    ],
    'css': [
        'static/src/css/itb.css',
    ],
}
