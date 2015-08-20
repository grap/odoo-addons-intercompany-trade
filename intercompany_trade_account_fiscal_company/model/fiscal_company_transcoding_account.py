# -*- encoding: utf-8 -*-
##############################################################################
#
#    Fiscal Company for Fiscal Company Module for Odoo
#    Copyright (C) 2015 GRAP (http://www.grap.coop)
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


class FiscalCompanyTranscodingAccount(Model):
    _name = 'fiscal.company.transcoding.account'

    # Columns Section
    _columns = {
        'company_id': fields.many2one(
            'res.company', string='Fiscal Mother Company', required=True),
        'from_account_id': fields.many2one(
            'account.account', string='From Account', required=True,
            domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",
            ),
        'to_account_id': fields.many2one(
            'account.account', string='To Account', required=True,
            domain="[('type', '=', 'other'), ('company_id', '=', company_id)]",
            ),
    }

    # Default Section
    def _default_company_id(self, cr, uid, context=None):
        ru_obj = self.pool['res.users']
        ru = ru_obj.browse(cr, uid, uid, context=context)
        return ru.company_id.fiscal_company.id

    _defaults = {
        'company_id': _default_company_id,
    }

    # Constraint Section
    def _check_fiscal_mother_company_id(self, cr, uid, ids, context=None):
        for fcta in self.browse(cr, uid, ids, context=context):
            if fcta.company_id.fiscal_type != 'fiscal_mother':
                return False
        return True

    def _check_account_company_id(self, cr, uid, ids, context=None):
        for fcta in self.browse(cr, uid, ids, context=context):
            if fcta.from_account_id.company_id.id !=\
                    fcta.company_id.id or\
                    fcta.to_account_id.company_id.id !=\
                    fcta.company_id.id:
                return False
        return True

    _constraints = [
        (
            _check_fiscal_mother_company_id,
            """Error: Transcoding Account is only possible for"""
            """ fiscal mother company.""",
            ['company_id']),
        (
            _check_account_company_id,
            """Error: You have to select account that belong to the"""
            """ selected Company.""",
            ['company_id', 'from_account_id', 'to_account_id']),
    ]

    # SQL Constraint Section
    _sql_constraints = [(
        'company_id_from_account_id_uniq',
        'unique(company_id, from_account_id)',
        'An Account must only be to once time for a same company!')]
