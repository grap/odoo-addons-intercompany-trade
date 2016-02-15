# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Account module for OpenERP
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
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
    'name': 'Intercompany Trade - Account',
    'version': '1.0',
    'category': 'Intercompany Trade',
    'description': """
Module for Intercompany Trade for Account Module
==============================================

Features :
----------
    * Add Demo Data;
    * Create link between:
        * customer 'account.invoice' and supplier 'account.invoice';
        * customer 'account.invoice.line' and supplier 'account.invoice.line';
    * create or delete a customer / supplier invoice update the according
      customer / supplier invoice;
    * create, update or delete a customer / supplier line update the according
      customer / supplier line;
    * Add Tax management to avoid Tax Bug:
        * All invoices are Tax excluded allways;

    * Customers doesn't have the possibility to change price_unit;
    * Users doesn't the right to copy an 'intercompany_trade' invoice;

Copyright, Authors and Licence:
-------------------------------
    * Copyright: 2015, GRAP: Groupement Régional Alimentaire de Proximité;
    * Author:
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence: AGPL-3 (http://www.gnu.org/licenses/);""",
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'intercompany_trade_base',
        'simple_tax_account',
        'account_invoice_pricelist',
    ],
    'demo': [
        #        'demo/res_groups.yml',
        #        'demo/account_account.yml',
        #        'demo/account_journal.yml',
        #        'demo/ir_property.xml',
        #        'demo/account_tax.yml',
        #        'demo/product_product.yml',
    ],
    'data': [
        'views/product_intercompany_trade_catalog_view.xml',
        'views/intercompany_trade_wizard_link_product_view.xml',
        'views/account_invoice_view.xml',
        'views/action.xml',
        'views/menu.xml',
        'data/init.xml',
    ],
    'auto_install': True,
}
