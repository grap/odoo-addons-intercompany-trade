# -*- encoding: utf-8 -*-
##############################################################################
#
#    Fiscal Company for Fiscal Company Module for Odoo
#    Copyright (C) 2015 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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

            rit = ai_obj._get_intercompany_trade_config(
                cr, uid, picking.partner_id.id, picking.company_id.id,
                picking.type, context=context)

            if rit.same_fiscal_mother_company:
                # Manage Transcoded account
                if res.get('account_id', False):
                    res['account_id'] = rit_obj.transcode_account_id(
                        cr, uid, rit, res['account_id'],
                        picking.product_id.name,
                        context=context)

                # Remove VAT if it is a Trade between two company that belong
                # to the same fiscal mother company
                res['invoice_line_tax_id'] = False

        return res
