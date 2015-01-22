# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Product module for OpenERP
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
    'name': 'Integrated Trade - Product',
    'version': '0.1',
    'category': 'Purchase',
    'description': """
Module for Integrated Trade for Product Module
==============================================

Features:
---------
    * Give the possibility to customer to link a product to a supplier product;
    * Change the pricelist on customer change the pricelist on
      res.integrated.trade object;

TODO:
-----
    * Check uom coherence;
    * Change product information must change supplierinfo;
    * Change price information must change supplierinfo;
    * Change pricelist information must change supplierinfo;
    * Supplierinfo is readonly in integrated trade;

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
        'product',
    ],
    'demo': [
        'demo/product_product.yml',
        'demo/res_groups.yml',
        'demo/product_pricelist.yml',
    ],
    'data': [
        'security/ir_model_access.yml',
        'view/view.xml',
        'view/action.xml',
        'view/menu.xml',
    ],
    'auto_install': True,
}
