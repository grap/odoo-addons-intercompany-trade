# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
                _("Intercompany Trade - Unimplemented Feature!"),
                _(
                    """You can not return a Picking that come from"""
                    """ Intercompany Trade. Please make another Sale Order"""
                    """ or Purchase Order."""))
        return super(stock_return_picking, self).create_returns(
            cr, uid, ids, context=context)
