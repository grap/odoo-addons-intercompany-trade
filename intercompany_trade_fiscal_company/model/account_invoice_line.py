# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class AccountInvoiceLine(Model):
    _inherit = 'account.invoice.line'

    def product_id_change(
            self, cr, uid, ids, product, uom_id, qty=0, name='',
            type='out_invoice', partner_id=False, fposition_id=False,
            price_unit=False, currency_id=False, context=None,
            company_id=None):
        rit_obj = self.pool['intercompany.trade.config']
        ai_obj = self.pool['account.invoice']
        rp_obj = self.pool['res.partner']
        ru_obj = self.pool['res.users']
        pp_obj = self.pool['product.product']
        res = super(AccountInvoiceLine, self).product_id_change(
            cr, uid, ids, product, uom_id, qty=qty, name=name,
            type=type, partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id, context=context,
            company_id=company_id)
        if not partner_id:
            return res
        rp = rp_obj.browse(cr, uid, partner_id, context=context)
        if rp.intercompany_trade:
            company_id = ru_obj.browse(
                cr, uid, uid, context=context).company_id.id
            rit = ai_obj._get_intercompany_trade_by_partner_company_type(
                cr, uid, partner_id, company_id, type, context=context)

            if rit.same_fiscal_mother_company:
                # Manage Transcoded account
                pp = pp_obj.browse(cr, uid, product, context=context)
                if res['value'].get('account_id', False):
                    res['value']['account_id'] = rit_obj.transcode_account_id(
                        cr, uid, rit, res['value']['account_id'], pp,
                        context=context)

                # Remove VAT if it is a Trade between two company that belong
                # to the same fiscal mother company
                res['value']['invoice_line_tax_id'] = False
        return res
