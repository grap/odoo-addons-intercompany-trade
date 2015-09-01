# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase - Sale Order Dates module for OpenERP
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


class sale_order(Model):
    _inherit = 'sale.order'

    # Overload Section
    def prepare_intercompany_purchase_order(
            self, cr, uid, so, rit, context=None):

        res = super(sale_order, self).prepare_intercompany_purchase_order(
            cr, uid, so, rit, context=context)

        res.update({
            'minimum_planned_date': so.requested_date,
        })

        return res
