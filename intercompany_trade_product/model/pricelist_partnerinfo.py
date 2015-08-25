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

from openerp.osv.orm import Model


class pricelist_partnerinfo(Model):
    _inherit = 'pricelist.partnerinfo'

    def write(self, cr, uid, ids, vals, context=None):
        # TODO: Check if the user doesn't update manualy this info
        # (manage context)
        res = super(pricelist_partnerinfo, self).write(
            cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        # TODO: Check if there is no pending transaction
        res = super(pricelist_partnerinfo, self).unlink(
            cr, uid, ids, context=context)
        return res
