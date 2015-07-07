# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Purchase & Sale module for OpenERP
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
    'name': 'Integrated Trade - Purchase & Sale',
    'version': '0.1',
    'category': 'Purchase',
    'description': """
Module for Integrated Trade for Purchase and Sale Module
========================================================

With this module, create a Purchase Order (or a Sale Order) will create a Sale
Order (respectivly, a Purchase Order) in the according company of the supplier
(respectivly, the customer), based on the settings done in the module
'integrated_trade_base'.

Features:
---------
    * Link between Purchase Order and Sale Order;
        * Add / update / delete lines (bi-directionnal);
        * PO.status 'sent' -> SO.status 'sent';
        * PO.status 'cancel' -> SO.status 'cancel';
        * PO set to 'draft' -> forbidden;
        * PO set to 'confirm' -> forbiden;
        * SO set to 'sent' -> forbiden;
        * SO set to 'cancel' -> forbiden;
        * SO from 'draft' to 'confirm' -> forbiden;

TODO Features:
--------------
    * Fix possibility to change some values when creating a new line in a
      Sale Order or a Purchase Order;

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
        'purchase',
        'sale',
    ],
    'demo': [
        'demo/product_pricelist_item.yml',
        'demo/res_partner.yml',
        'demo/res_groups.yml',
        'demo/sale_shop.yml',
        'demo/ir_values.xml',
        'demo/ir_values.yml',
    ],
    'data': [
        'view/view.xml',
    ],
    'auto_install': True,
}