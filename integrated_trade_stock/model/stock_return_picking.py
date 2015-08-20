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

from openerp.osv.orm import TransientModel
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class stock_return_picking(TransientModel):
    _inherit = 'stock.return.picking'

    # View Section
    def create_returns(self, cr, uid, ids, context=None):
        sp_obj = self.pool['stock.picking']
        sp_id = context.get('active_id', False)
        sp = sp_obj.browse(cr, uid, sp_id, context=context)
        if sp.intercompany_trade:
            raise except_osv(
                _("Integrated Trade - Unimplemented Feature!"),
                _(
                    """You can not return a Picking that come from"""
                    """ Integrated Trade. Please make another Sale Order"""
                    """ or Purchase Order."""))
        return super(stock_return_picking, self).create_returns(
            cr, uid, ids, context=context)
