# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        """Change Journal if it is trade between two company of the same
        cooperative"""
        partner_obj = self.env['res.partner']
        journal_obj = self.env['account.journal']

        partner = partner_obj.browse(vals['partner_id'])

        if partner.intercompany_trade:
            transaction_type = False
            journal = journal_obj.browse(int(vals['journal_id']))
            if journal.type in ('sale'):
                transaction_type = 'out'
            elif journal.type in ('purchase'):
                transaction_type = 'in'
            config = self._get_intercompany_trade_by_partner_company_type(
                partner.id, partner.company_id.id, transaction_type)
            if config.same_fiscal_mother_company:

                if journal.type in ('sale'):
                    vals['journal_id'] = config.sale_journal_id.id
                elif journal.type in ('purchase'):
                    vals['journal_id'] = config.purchase_journal_id.id

        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('journal_id', False):
            for invoice in self:
                if invoice.intercompany_trade\
                        and invoice.journal_id.id != vals['journal_id']:
                    config =\
                        self._get_intercompany_trade_by_partner_company_type(
                            invoice.partner_id.id, invoice.company_id.id,
                            invoice.type)
                    if config.same_fiscal_mother_company:
                        vals.pop('journal_id')

        return super(AccountInvoice, self).write(vals)
