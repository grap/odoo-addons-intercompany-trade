# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase - Sale Order Dates module for OpenERP
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

from openerp.osv.orm import Model
from openerp.osv import fields


class sale_order(Model):
    _inherit = 'sale.order'

    # OVERWRITE SECTION
    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 0.0
            for line in sale.order_line:
                result[sale.id] += line.margin or 0.0
        return result

    # OVERWRITE SECTION
    _columns = {
        'margin': fields.function(
            _product_margin, string='Margin', store=True,
            help="It gives profitability by calculating the difference"
            " between the Unit Price and the cost price."),
    }
