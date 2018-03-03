# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
            name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        config_obj = self.env['intercompany.trade.config']
        partner_obj = self.env['res.partner']
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        if not partner_id:
            return res
        partner = partner_obj.browse(partner_id)
        if partner.intercompany_trade and res['value'].get('tax_id'):
            company_id = self.env.user.company_id.id
            config = config_obj._get_intercompany_trade_by_partner_company(
                partner_id, company_id, 'out')

            res['value']['tax_id'] = config.transcode_tax_ids(
                res['value']['tax_id'])

        return res
