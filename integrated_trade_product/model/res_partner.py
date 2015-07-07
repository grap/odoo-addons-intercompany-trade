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
from .custom_tools import _integrated_trade_update


class ResPartner(Model):
    _inherit = 'res.partner'

    def _integrated_fields_allowed(self):
        """allow basic user to change pricelist"""
        res = super(ResPartner, self)._integrated_fields_allowed()
        res.append('property_product_pricelist')
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """If customer partner pricelist has changed (in supplier database),
        recompute Pricelist info in customer database"""
        rit_obj = self.pool['res.integrated.trade']
        res = super(ResPartner, self).write(
            cr, uid, ids, vals, context=context)
        rit_ids = rit_obj.search(cr, uid, [
            ('customer_partner_id', 'in', ids)
        ], context=context)
        for rit in rit_obj.browse(cr, uid, rit_ids, context=context):
            # Recompute Pricelist
            _integrated_trade_update(
                self.pool, cr, uid, rit.id, None, context=context)
        return res
