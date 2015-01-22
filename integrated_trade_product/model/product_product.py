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
        'name', 'default_code',
        'taxes_id',
        'standard_price', 'list_price',
    ]

    def write(self, cr, uid, ids, vals, context=None):
        """Update product supplierinfo in customer company, if required"""
        psi_obj = self.pool['product.supplierinfo']
        res = super(product_product, self).write(
            cr, uid, ids, vals, context=context)
        # Update product in customer database if required
        if list(set(vals.keys()) & set(self._INTEGRATED_FIELDS)):
            psi_obj._integrated_trade_update_multicompany(
                cr, uid, ids, context=context)
        return res
