# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _prepare_invoice_line(
            self, group, picking, move_line, invoice_id,
            invoice_vals):
        config_obj = self.env['intercompany.trade.config']
        invoice_obj = self.env['account.invoice']
        res = super(StockPicking, self)._prepare_invoice_line(
            group, picking, move_line, invoice_id, invoice_vals)

        if picking.partner_id.intercompany_trade:
            config =\
                invoice_obj._get_intercompany_trade_by_partner_company_type(
                    picking.partner_id.id, picking.company_id.id, picking.type)

            if config.same_fiscal_mother_company:
                # Manage Transcoded account
                if res.get('account_id', False):
                    res['account_id'] = config_obj.transcode_account_id(
                        config, res['account_id'], picking.product_id)
                res['invoice_line_tax_id'] = False

        return res
