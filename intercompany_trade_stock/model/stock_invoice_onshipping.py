# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Purchase module for OpenERP
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
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

from openerp.osv.orm import TransientModel
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class stock_invoice_onshipping(TransientModel):
    _inherit = 'stock.invoice.onshipping'

    # View Section
    def create_invoice(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        sp_obj = self.pool['stock.picking']
        rit_obj = self.pool['intercompany.trade.config']
        ai_obj = self.pool['account.invoice']

        sp_ids = context.get('active_ids', False)
        sp_lst = sp_obj.browse(cr, uid, sp_ids, context=context)
        intercompany_trade = any([x.intercompany_trade for x in sp_lst])
        if intercompany_trade:
            if len(sp_lst) > 1:
                raise except_osv(
                    _("Intercompany Trade - Unimplemented Feature!"),
                    _(
                        """You can not Invoice many Pickings Out that come"""
                        """ from Intercompany Trade."""))
            if not wizard.invoice_date:
                raise except_osv(
                    _("Intercompany Trade - Missing Information!"),
                    _(
                        """You have to set an invoice date for Invoices"""
                        """ in Intercompany Trade."""))
            if sp_lst[0].type != 'out':
                raise except_osv(
                    _("Intercompany Trade - Unimplemented Feature!"),
                    _(
                        """You can not Invoice a Picking In that come"""
                        """ from Intercompany Trade."""
                        """ Only Picking Out can be invoiced. Please ask"""
                        """ to your supplier to invoice the Trade."""))
        res = super(stock_invoice_onshipping, self).create_invoice(
            cr, uid, [wizard.id], context=context)

        if intercompany_trade:
            # get the intercompany trade
            sp_out = sp_lst[0]
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, sp_out.partner_id.id, sp_out.company_id.id, 'out',
                context=context)

            # Get the Picking In
            sp_out = sp_obj.browse(cr, uid, sp_ids[0], context=context)
            sp_in = sp_obj.browse(
                cr, rit.customer_user_id.id,
                sp_out.intercompany_trade_picking_in_id.id, context=context)

            # Set the picking In as 'invoiced'
            sp_obj.write(cr, rit.customer_user_id.id, sp_in.id, {
                'invoice_state': 'invoiced',
            }, context=context)

            # Get the Invoice In
            ai_out_id = res[sp_out.id]
            ai_out = ai_obj.browse(
                cr, uid, ai_out_id, context=context)
            ai_in_id = ai_out.intercompany_trade_account_invoice_id.id

            # update Invoice in with info of the picking in and the invoice out
            ai_in_vals = sp_obj._prepare_invoice(
                cr, rit.customer_user_id.id, sp_in, sp_in.partner_id,
                'in_invoice', False, context=context)

            ai_in_vals = {x: ai_in_vals[x] for x in ('origin', 'comment')}
            ai_in_vals['date_invoice'] = wizard.invoice_date

            ai_obj.write(
                cr, rit.customer_user_id.id, [ai_in_id], ai_in_vals,
                context=context)

        return res
