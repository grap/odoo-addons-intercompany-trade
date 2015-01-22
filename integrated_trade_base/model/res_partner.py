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


class res_partner(Model):
    _inherit = 'res.partner'

    # Columns section
    _columns = {
        'integrated_trade': fields.boolean(
            'Integrated Trade',
            groups='integrated_trade_base.integrated_trade_user',
            help="Indicate that this partner is a company in Odoo."),
    }

    # TODO
    # Ref, check on write / create / delete / to have the possibility to
    # allow user to change pricelist;
    # if pricelist_changed, --> update the product;
    def _check_integrated_trade_access(self, cr, uid, ids, context=None):
        """Restrict access of partner set as integrated_trade for only
        'integrated_trade_manager' users."""
        ru_obj = self.pool['res.users']
        if not ru_obj.has_group(
                cr, uid,
                'integrated_trade_base.integrated_trade_manager'):
            for rp in self.browse(cr, uid, ids, context=context):
                if rp.integrated_trade:
                    return False
        return True

    _constraints = [
        (
            _check_integrated_trade_access,
            """Error: You have no right to create or update a partner"""
            """ that is set as 'Integrated Trade'""",
            []),
    ]
