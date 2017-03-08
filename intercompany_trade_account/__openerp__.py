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
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'intercompany_trade_base',
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
        'views/action.xml',
        'views/menu.xml',
        'data/init.xml',
    ],
    'auto_install': True,
    'installable': True,
}
