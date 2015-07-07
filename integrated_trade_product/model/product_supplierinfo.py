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

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.addons import decimal_precision as dp


class product_supplierinfo(Model):
    _inherit = 'product.supplierinfo'

    # Fields Function Section
    def _get_integrated_price(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for psi in self.browse(cr, uid, ids, context=context):
            if psi.supplier_product_id and psi.pricelist_ids:
                res[psi.id] = psi.pricelist_ids[0].price
            else:
                res[psi.id] = 0
        return res

    _columns = {
        'integrated_price': fields.function(
            _get_integrated_price, string='Unit Price', type='float',
            digits_compute=dp.get_precision('Integrated Product Price'),
            store={'product.supplierinfo': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'supplier_product_id',
                    'pricelist_ids',
                ], 10)}),
        'supplier_product_id': fields.many2one(
            'product.product', 'Product in the Supplier Catalog',
            readonly=True, selected=True),
    }
