# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Product module for OpenERP
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
    'name': 'Intercompany Trade - Product',
    'version': '1.0',
    'category': 'Intercompany Trade',
    'description': """
Module for Intercompany Trade for Product Module
==============================================

Features:
---------
    * Give the possibility to customer to link a product to a supplier product;
    * Change the pricelist on customer change the pricelist on
      intercompany.trade.config object;

Features TO TEST:
-----------------
    * Change product information changes supplierinfo;
    * Change price information changes supplierinfo;
    * Change pricelist on partner changes supplierinfo;

TODO:
-----
    * Check uom coherence;
    * Change pricelist information must change supplierinfo;
    * Supplierinfo is readonly in intercompany trade;

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
        'intercompany_trade_base',
        'product',
    ],
    'demo': [
        'demo/product_product.yml',
        'demo/res_groups.yml',
        'demo/product_pricelist.yml',
    ],
    'data': [
        'security/ir_model_access.yml',
        'security/ir_rule.yml',
        'views/intercompany_trade_config_view.xml',
        'views/intercompany_trade_wizard_link_product_view.xml',
        'views/product_intercompany_trade_catalog_view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'auto_install': True,
}
