# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

from .custom_tools import _intercompany_trade_update


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _intercompany_tradefields_allowed(self):
        """allow basic user to change pricelist"""
        res = super(ResPartner, self)._intercompany_tradefields_allowed()
        res.append('property_product_pricelist')
        return res

    @api.multi
    def write(self, vals):
        """If customer partner pricelist has changed (in supplier database),
        recompute Pricelist info in customer database"""
        config_obj = self.env['intercompany.trade.config']
        res = super(ResPartner, self).write(vals)

        configs = config_obj.search([
            ('customer_partner_id', 'in', self.ids)])
        for config in configs:
            # Recompute Pricelist
            _intercompany_trade_update(
                self.pool, self.env.cr, self.env.user.id, config.id, None,
                context=self.env.context)
        return res
