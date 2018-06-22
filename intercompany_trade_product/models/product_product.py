# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


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
    seller_ids = fields.One2many(
        comodel_name='product.supplierinfo', inverse_name='product_tmpl_id',
        string='Supplier', copy=False)
