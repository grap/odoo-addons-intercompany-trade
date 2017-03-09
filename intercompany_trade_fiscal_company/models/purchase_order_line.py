# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class PurchaseOrderLine(Model):
    _inherit = 'purchase.order.line'

    def onchange_product_id(
            self, cr, uid, ids, pricelist_id, product_id, qty,
            uom_id, partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False, context=None):
        rit_obj = self.pool['intercompany.trade.config']
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
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, partner_id, company_id, 'in', context=context)

            if rit.same_fiscal_mother_company:
                # Remove VAT if it is a Trade between two company that belong
                # to the same fiscal mother company
                res['value']['taxes_id'] = False
        return res
