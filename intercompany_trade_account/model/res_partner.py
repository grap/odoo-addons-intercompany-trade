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

from openerp.osv.orm import Model


class ResPartner(Model):
    _inherit = 'res.partner'

    def _set_existing_simple_tax_type(self, cr, uid, context=None):
        """Initialize all intercompany trade partners with correct VAT configuration"""
        rp_ids = self.search(cr, uid, [
            ('intercompany_trade', '=', True),
            ('simple_tax_type', '!=', 'excluded'),
        ], context=context)
        self.write(cr, uid, rp_ids, {
            'simple_tax_type': 'excluded'}, context=context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('intercompany_trade', False):
            vals['simple_tax_type'] = 'excluded'
        return super(ResPartner, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('intercompany_trade', False):
            vals['simple_tax_type'] = 'excluded'
        self._check_intercompany_trade_access(
            cr, uid, ids, vals.keys(), context=context)
        return super(ResPartner, self).write(
            cr, uid, ids, vals, context=context)
