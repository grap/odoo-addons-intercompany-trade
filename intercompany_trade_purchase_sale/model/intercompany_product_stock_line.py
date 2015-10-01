# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase and Sale module for OpenERP
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

from openerp.osv.orm import TransientModel
from openerp.osv import fields


class intercompany_product_stock_line(TransientModel):
    _name = 'intercompany.product.stock.line'

    # Columns Section
    _columns = {
        'wizard_id': fields.many2one('intercompany.product.stock', 'Wizard'),
        'product_code': fields.char('Supplier Product Internal Reference'),
        'product_name': fields.char('Supplier Product Name'),
        'product_qty_available': fields.float('Quantity On Hand'),
        'product_virtual_available': fields.float('Forcasted Quantity'),
    }
