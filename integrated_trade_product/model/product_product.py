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

from openerp.osv.orm import Model


class product_product(Model):
    _inherit = 'product.product'

    _INTEGRATED_FIELDS = [
        'name', 'default_code', 'lst_price', 'price', 'price_extra',
        #        'pricelist_id', # ?
        #        'price_margin', # ?
        'taxes_id',
        'list_price',
    ]

#    def write(self, cr, uid, ids, vals, context=None):
#        res = super(product_product, self).write(
#            cr, uid, ids, vals, context=context)
#        # Update product in customer database if required
#        if list(set(vals.keys()) & set(self._INTEGRATED_FIELDS)):
#            pitc_obj = self.pool['product.integrated.trade.catalog']
#            pitc_ids = pitc_obj.search(
#                cr, uid,
#                [('supplier_product_id', 'in', ids)], context=context)

#            pitc_obj.update_product(cr, uid, pitc_ids, context=context)
#        return res
