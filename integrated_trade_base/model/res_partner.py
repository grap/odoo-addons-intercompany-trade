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
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class ResPartner(Model):
    _inherit = 'res.partner'

    # Columns section
    _columns = {
        'integrated_trade': fields.boolean(
            'Integrated Trade',readonly=True,
            help="Indicate that this partner is a company in Odoo."),
    }

    def _integrated_fields_allowed(self):
        """Overload this function to allow basic to change
        some fields for integrated partner"""
        return []

    def _check_integrated_trade_access(
            self, cr, uid, ids, fields, context=None):
        """Restrict access of partner set as integrated_trade for only
        'integrated_trade_manager' users."""
        unallowed_fields =\
            set(fields) - set(self._integrated_fields_allowed())
        ru_obj = self.pool['res.users']
        if not ru_obj.has_group(
                cr, uid,
                'integrated_trade_base.integrated_trade_manager'):
            for rp in self.browse(cr, uid, ids, context=context):
                if rp.integrated_trade and unallowed_fields:
                    raise except_osv(
                        _("Access Denied!"),
                        _(
                            """Error: You have no right to create or"""
                            """ update a partner that is set as"""
                            """ 'Integrated Trade'"""))

    def create(self, cr, uid, vals, context=None):
        if vals.get('integrated_trade', False):
            vals['simple_tax_type'] = 'excluded'
        return super(ResPartner, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('integrated_trade', False):
            vals['simple_tax_type'] = 'excluded'
        self._check_integrated_trade_access(
            cr, uid, ids, vals.keys(), context=context)
        return super(ResPartner, self).write(
            cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        self._check_integrated_trade_access(
            cr, uid, ids, [0], context=context)
        return super(ResPartner, self).unlink(
            cr, uid, ids, context=context)
