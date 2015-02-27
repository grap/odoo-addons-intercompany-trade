# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Purchase module for OpenERP
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

from openerp import netsvc
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class stock_picking(Model):
    _inherit = 'stock.picking'

    # Fields Function Section
    def _get_integrated_trade(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for sp in self.browse(cr, uid, ids, context=context):
            res[sp.id] = sp.partner_id.integrated_trade
        return res

    # Columns Section
    _columns = {
        'integrated_trade': fields.function(
            _get_integrated_trade, type='boolean', string='Integrated Trade',
            store={'stock.picking': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'partner_id',
                ], 10)}),
        'integrated_trade_picking_out_id': fields.many2one(
            'stock.picking.out', string='Integrated Trade Picking Out',
            readonly=True,
        ),
        'integrated_trade_picking_in_id': fields.many2one(
            'stock.picking.in', string='Integrated Trade Picking In',
            readonly=True,
        ),
    }

