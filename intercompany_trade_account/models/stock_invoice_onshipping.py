# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.multi
    def create_invoice(self):
        """This function doesn't create invoices correctly for services
        So Intercompany trade mecanism is
        broken. This path will duplicate all bad lines, and unlink them after.
        """
        invoice_obj = self.env['account.invoice']
        res = super(StockInvoiceOnshipping, self).create_invoice()
        invoices = invoice_obj.browse(res)
        for invoice in invoices:
            if invoice.intercompany_trade:
                lines = []
                for line in invoice.invoice_line:
                    if not line.intercompany_trade_account_invoice_line_id:
                        lines.append(line)
                for line in lines:
                    line.copy()
                    line.unlink()
        return res
