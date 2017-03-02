# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class FiscalCompanyTranscodingAccount(models.Model):
    _name = 'fiscal.company.transcoding.account'

    # Default Section
    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.fiscal_company.id

    # Columns Section
    company_id = fields.Many2one(
        comodel_name='res.company', string='Fiscal Mother Company',
        required=True, default=_default_company_id)

    from_account_id = fields.Many2one(
        comodel_name='account.account', string='From Account', required=True,
        domain="[('type', '=', 'other'), ('company_id', '=', company_id)]")

    to_account_id = fields.Many2one(
        comodel_name='account.account', string='To Account', required=True,
        domain="[('type', '=', 'other'), ('company_id', '=', company_id)]")

    # Constrains Section
    @api.constrains('company_id')
    def _check_fiscal_mother_company_id(self):
        for transcoding in self:
            if transcoding.company_id.fiscal_type != 'fiscal_mother':
                raise UserError(_(
                    "Error: Transcoding Account is only possible for"
                    " fiscal mother company."))

    @api.constrains('company_id', 'from_account_id', 'to_account_id')
    def _check_account_company_id(self):
        for transcoding in self:
            if transcoding.from_account_id.company_id.id !=\
                    transcoding.company_id.id or\
                    transcoding.to_account_id.company_id.id !=\
                    transcoding.company_id.id:
                raise UserError(_(
                    "Error: You have to select an account that belong to the"
                    " selected Company."))

    # SQL Constrains Section
    _sql_constraints = [(
        'company_id_from_account_id_uniq',
        'unique(company_id, from_account_id)',
        'An Account must only be transcoded once time for a same company!')]
