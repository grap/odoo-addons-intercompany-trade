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

from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class stock_picking_out(Model):
    _inherit = 'stock.picking.out'

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        rp_obj = self.pool['res.partner']
        if vals.get('partner_id', False):
            rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
            if rp.integrated_trade:
                raise except_osv(
                    _("Integrated Trade - Unimplemented Feature!"),
                    _(
                        """You can not create a picking with a partner"""
                        """ flagged as 'Integrated Trade'."""))
        return super(stock_picking_out, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        rp_obj = self.pool['res.partner']
        if vals.get('partner_id', False):
            rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)
            if rp.integrated_trade:
                raise except_osv(
                    _("Integrated Trade - Unimplemented Feature!"),
                    _(
                        """You can not set a partner"""
                        """ flagged as 'Integrated Trade'."""))
        return super(stock_picking_out, self).write(
            cr, uid, ids, vals, context=context)
