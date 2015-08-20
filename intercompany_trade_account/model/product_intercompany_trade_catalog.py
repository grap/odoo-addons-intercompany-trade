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

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.addons import decimal_precision as dp


class ProductIntercompanyTradeCatalog(Model):
    _inherit = 'product.intercompany.trade.catalog'

    # Fields Function Section
    def _get_supplier_price(self, cr, uid, ids, name, arg, context=None):
        return super(ProductIntercompanyTradeCatalog, self)._get_supplier_price(
            cr, uid, ids, name, arg, context=context)

    # Column Section
    _columns = {
        'supplier_sale_price_vat_excl': fields.function(
            _get_supplier_price,
            string='Supplier Sale Price VAT Excluded',
            multi='supplier_price', type='float',
            digits_compute=dp.get_precision('Intercompany Trade Product Price')),
        'supplier_sale_price_vat_incl': fields.function(
            _get_supplier_price,
            string='Supplier Sale Price VAT Included',
            multi='supplier_price', type='float',
            digits_compute=dp.get_precision('Intercompany Trade Product Price')),
    }
