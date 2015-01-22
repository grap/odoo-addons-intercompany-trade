# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Base module for OpenERP
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


class res_integrated_trade(Model):
    _inherit = 'res.integrated.trade'

    def _get_integrated_trade_from_pricelist(self, cr, uid, ids, context=None):
        """Return Integrated Trade ids depending on changes of pricelist"""
        res = []
        rp_obj = self.pool['res.partner']
        rit_obj = self.pool['res.integrated.trade']
        for rp in rp_obj.browse(cr, uid, ids, context=context):
            if rp.integrated_trade and rp.customer:
                res.extend(rit_obj.search(cr, uid, [
                    ('customer_partner_id', '=', rp.id),
                ], context=context))
        return list(set(res))

    def _get_pricelist_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        rp_obj = self.pool['res.partner']
        for rit in self.browse(cr, uid, ids, context=context):
            context_tmp = context.copy()
            context_tmp['company_id'] = rit.supplier_company_id.id
            rp = rp_obj.browse(
                cr, uid, rit.customer_partner_id.id, context_tmp)
            res[rit.id] = rp.property_product_pricelist.id
        return res

    # Columns section
    _columns = {
        'pricelist_id': fields.function(
            _get_pricelist_id,
            string='Customer Pricelist in the Supplier Company',
            type='many2one', relation='product.pricelist', store={
                'res.partner': (
                    _get_integrated_trade_from_pricelist,
                    ['property_product_pricelist'], 10),
                'res.integrated.trade': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['customer_partner_id', 'supplier_company_id'], 10),
            })
    }
