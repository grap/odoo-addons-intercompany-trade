# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        invoice_obj = self.env['account.invoice']
        partner_obj = self.env['res.partner']
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        if not partner_id or not product:
            return res
        partner = partner_obj.browse(partner_id)
        if partner.intercompany_trade:
            company_id = self.env.user.company_id.id
            config =\
                invoice_obj._get_intercompany_trade_by_partner_company_type(
                    partner_id, company_id, type)

            res['value']['account_id'] = config.transcode_account_id(
                res['value'].get('account_id', False), product)
            res['value']['invoice_line_tax_id'] = config.transcode_tax_ids(
                res['value'].get('invoice_line_tax_id', False))

        return res
