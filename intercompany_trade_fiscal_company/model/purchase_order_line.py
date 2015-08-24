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

from openerp.osv.orm import Model


class PurchaseOrderLine(Model):
    _inherit = 'purchase.order.line'

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
            uom_id, partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False, context=None):
        rit_obj = self.pool['intercompany.trade.config']
        ai_obj = self.pool['account.invoice']
        rp_obj = self.pool['res.partner']
        ru_obj = self.pool['res.users']
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)

        if not partner_id:
            return res
        rp = rp_obj.browse(cr, uid, partner_id, context=context)
        if rp.intercompany_trade:
            company_id = ru_obj.browse(
                cr, uid, uid, context=context).company_id.id
            rit = ai_obj._get_intercompany_trade_config(
                cr, uid, partner_id, company_id, 'in_invoice', context=context)

            if rit.same_fiscal_mother_company:
                # Remove VAT if it is a Trade between two company that belong
                # to the same fiscal mother company
                res['value']['taxes_id'] = False
        return res
