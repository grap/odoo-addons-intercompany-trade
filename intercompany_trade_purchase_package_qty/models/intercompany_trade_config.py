# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase Package Quantity module for Odoo
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


class intercompany_trade_config(Model):
    _inherit = 'intercompany.trade.config'

    # Custom Section
    def _prepare_product_supplierinfo(
            self, cr, uid, id, supplier_product_id, customer_product_id,
            context=None):
        res = super(
            intercompany_trade_config, self)._prepare_product_supplierinfo(
                cr, uid, id, supplier_product_id, customer_product_id,
                context=context)
        res['indicative_package'] = True
        res['package_qty'] = 1

        return res
