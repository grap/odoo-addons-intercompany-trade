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


from openerp.osv import fields
from openerp.osv.orm import TransientModel


class intercompany_product_stock(TransientModel):
    _name = 'intercompany.product.stock'

    # Fields Function Section
    def _default_line_ids(self, cr, uid, context=None):
        po_obj = self.pool['purchase.order']
        sol_obj = self.pool['sale.order.line']
        rit_obj = self.pool['intercompany.trade.config']
        res = []
        sol_ids = []
        po = po_obj.browse(cr, uid, context.get('active_id'), context=context)
        rit = rit_obj._get_intercompany_trade_by_partner_company(
            cr, uid, po.partner_id.id, po.company_id.id,
            'in', context=context)

        for line in po.order_line:
            sol_ids.append(line.intercompany_trade_sale_order_line_id.id)

        for sol in sol_obj.browse(
                cr, rit.supplier_user_id.id, sol_ids, context=context):
            pp = sol.product_id
            res.append((0, 0, {
                'product_code': pp.default_code,
                'product_name': pp.name,
                'product_qty_available': pp.qty_available,
                'product_virtual_available': pp.virtual_available,
            }))
        return res

    # Columns section
    _columns = {
        'line_ids': fields.one2many(
            'intercompany.product.stock.line', 'wizard_id', 'Lines'),
    }

    # Default values Section
    _defaults = {
        'line_ids': _default_line_ids,
    }
