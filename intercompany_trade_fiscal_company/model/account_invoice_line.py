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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from openerp import SUPERUSER_ID
# from openerp.osv.osv import except_osv
from openerp.osv.orm import Model
# from openerp.tools.translate import _


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
