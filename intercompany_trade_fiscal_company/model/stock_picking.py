# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class StockPicking(Model):
    _inherit = 'stock.picking'

    def _prepare_invoice_line(
            self, cr, uid, group, picking, move_line, invoice_id,
            invoice_vals, context=None):
        rit_obj = self.pool['intercompany.trade.config']
        ai_obj = self.pool['account.invoice']
        res = super(StockPicking, self)._prepare_invoice_line(
            cr, uid, group, picking, move_line, invoice_id,
            invoice_vals, context=None)

        if picking.intercompany_trade:

            rit = ai_obj._get_intercompany_trade_by_partner_company_type(
                cr, uid, picking.partner_id.id, picking.company_id.id,
                picking.type, context=context)

            if rit.same_fiscal_mother_company:
                # Manage Transcoded account
                if res.get('account_id', False):
                    res['account_id'] = rit_obj.transcode_account_id(
                        cr, uid, rit, res['account_id'],
                        picking.product_id,
                        context=context)

                # Remove VAT if it is a Trade between two company that belong
                # to the same fiscal mother company
                res['invoice_line_tax_id'] = False

        return res
