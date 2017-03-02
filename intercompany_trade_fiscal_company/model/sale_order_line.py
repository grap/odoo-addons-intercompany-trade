# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class SaleOrderLine(Model):
    _inherit = 'sale.order.line'

    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        rit_obj = self.pool['intercompany.trade.config']
        rp_obj = self.pool['res.partner']
        ru_obj = self.pool['res.users']
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)
        if not partner_id:
            return res
        rp = rp_obj.browse(cr, uid, partner_id, context=context)
        if rp.intercompany_trade:
            company_id = ru_obj.browse(
                cr, uid, uid, context=context).company_id.id
            rit = rit_obj._get_intercompany_trade_by_partner_company(
                cr, uid, partner_id, company_id, 'out',
                context=context)

            if rit.same_fiscal_mother_company:
                # Remove VAT if it is a Trade between two company that belong
                # to the same fiscal mother company
                res['value']['tax_id'] = False
        return res
