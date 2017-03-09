# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty,
            uom_id, partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False):
        config_obj = self.env['intercompany.trade.config']
        partner_obj = self.env['res.partner']
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit)

        if not partner_id:
            return res
        partner = partner_obj.browse(partner_id)
        if partner.intercompany_trade:
            company_id = self.env.user.company_id.id
            config = config_obj._get_intercompany_trade_by_partner_company(
                partner_id, company_id, 'in')
            res['value']['taxes_id'] = config.transcode_tax_ids(
                res['value']['taxes_id'])
        return res
