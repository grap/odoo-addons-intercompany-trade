# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            """Error: You have to select an account that belong to the"""
            """ selected Company.""",
            ['company_id', 'from_account_id', 'to_account_id']),
    ]

    # SQL Constraint Section
    _sql_constraints = [(
        'company_id_from_account_id_uniq',
        'unique(company_id, from_account_id)',
        'An Account must only be transcoded once time for a same company!')]
