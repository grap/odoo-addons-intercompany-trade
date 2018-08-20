# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        invoice_obj = self.env['account.invoice']
        res = super(StockMove, self)._get_invoice_line_vals(
            move, partner, inv_type)
        if partner.intercompany_trade:
            config =\
                invoice_obj._get_intercompany_trade_by_partner_company_type(
                    partner.id, move.company_id.id, inv_type)

            if config.same_fiscal_mother_company:
                # Manage Transcoded account
                if res.get('account_id', False):
                    res['account_id'] = config.transcode_account_id(
                        res['account_id'], move.product_id.id)
                res['invoice_line_tax_id'] = False
        return res
