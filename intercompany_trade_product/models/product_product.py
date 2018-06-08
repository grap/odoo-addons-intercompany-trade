# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # TODO: improve me.
    # It's not necessary to remove all seller_ids, only ones that
    # come from intercompany_trade
    seller_ids = fields.One2many(
        comodel_name='product.supplierinfo', inverse_name='product_tmpl_id',
        string='Supplier', copy=False)

    _INTEGRATED_FIELDS = [
        'name', 'default_code',
        'taxes_id',
        'standard_price', 'list_price',
    ]

# WIP : Syncronization disabled
#    @api.multi
#    def write(self, vals):
#        """Update product supplierinfo in customer company, if required"""
#        res = super(ProductProduct, self).write(vals)
#        # Update product in customer database if required
#        if list(set(vals.keys()) & set(self._INTEGRATED_FIELDS)):
#            _intercompany_trade_update_multicompany(
#                self.pool, self.env.cr, self.env.user.id, self.ids,
#                context=self.env.context)
#        return res
