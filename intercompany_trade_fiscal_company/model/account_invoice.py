# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class AccountInvoice(Model):
    _inherit = 'account.invoice'

    def create(self, cr, uid, vals, context=None):
        rp_obj = self.pool['res.partner']
        aj_obj = self.pool['account.journal']
        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)

        if rp.intercompany_trade:
            transaction_type = False
            aj = aj_obj.browse(
                cr, uid, int(vals['journal_id']), context=context)
            if aj.type in ('sale'):
                transaction_type = 'out'
            elif aj.type in ('purchase'):
                transaction_type = 'in'
            rit = self._get_intercompany_trade_by_partner_company_type(
                cr, uid, rp.id, rp.company_id.id, transaction_type,
                context=context)
            if rit.same_fiscal_mother_company:

                if aj.type in ('sale'):
                    vals['journal_id'] = rit.sale_journal_id.id
                elif aj.type in ('purchase'):
                    vals['journal_id'] = rit.purchase_journal_id.id

        return super(AccountInvoice, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('journal_id', False):
            for ai in self.browse(cr, uid, ids, context=context):
                if ai.intercompany_trade\
                        and ai.journal_id.id != vals.get('journal_id', False):
                    rit = self._get_intercompany_trade_by_partner_company_type(
                        cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                        context=context)
                    if rit.same_fiscal_mother_company:
                        # TODO investigate why it is called
                        vals.pop('journal_id')

        # Call to super
        return super(AccountInvoice, self).write(
            cr, uid, ids, vals, context=context)
