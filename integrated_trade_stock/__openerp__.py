# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Stock module for OpenERP
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
    'name': 'Integrated Trade - Stock',
    'version': '1.0',
    'category': 'Integrated Trade',
    'description': """
Module for Integrated Trade for Stock Module
============================================

Features:
---------
    * Make a link between stock.picking.in and stock.picking.out model;
    * Block possibility to copy a stock.picking;
    * Block possibility to invoice a stock picking out;

TODO: 
    * block possibility to invoices multiple picking;

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
        'integrated_trade_base',
        'stock',
    ],
    'demo': [
        'demo/res_groups.yml',
        'demo/stock_location.yml',
        'demo/stock_warehouse.yml',
    ],
    'data': [
        'view/view.xml',
    ],
    'auto_install': True,
}
