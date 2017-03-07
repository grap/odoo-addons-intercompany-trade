# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

from .custom_tools import _intercompany_trade_update_multicompany


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _INTEGRATED_FIELDS = [
        'name', 'default_code',
        'taxes_id',
        'standard_price', 'list_price',
    ]

    # TODO: improve me.
    # It's not necessary to remove all seller_ids, only ones that
    # come from intercompany_trade
    @api.multi
    def copy_data(self, default=None):
        default['seller_ids'] = False
        return super(ProductProduct, self).copy_data(default)

    @api.multi
    def write(self, vals):
        """Update product supplierinfo in customer company, if required"""
        res = super(ProductProduct, self).write(vals)
        # Update product in customer database if required
        if list(set(vals.keys()) & set(self._INTEGRATED_FIELDS)):
            _intercompany_trade_update_multicompany(
                self.pool, self.env.cr, self.env.user.id, self.ids,
                context=self.env.context)
        return res
