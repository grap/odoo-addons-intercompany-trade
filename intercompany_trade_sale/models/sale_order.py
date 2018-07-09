# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    intercompany_trade = fields.Boolean(
        string='Intercompany Trade', related='partner_id.intercompany_trade')

    @api.multi
    def action_invoice_create(
            self, grouped=False, states=None, date_invoice=False):
        """This function doesn't create invoices correctly. It creates
        first line, and after invoice. So Intercompany trade mecanism is
        broken. This path will duplicate all bad lines, and unlink them after.
        """
        invoice_obj = self.env['account.invoice']
        res = super(SaleOrder, self).action_invoice_create(
            grouped=grouped, states=states, date_invoice=date_invoice)
        invoices = invoice_obj.browse(res)
        for invoice in invoices.filtered(lambda x: x.intercompany_trade):
            lines = []
            for line in invoice.invoice_line:
                if not line.intercompany_trade_account_invoice_line_id:
                    lines.append(line)
            for line in lines:
                line.copy()
                line.unlink()
        return res
