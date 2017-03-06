# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.addons import decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    # Columns Section
    intercompany_trade_price = fields.Float(
        string='Unit Price', compute='_compute_intercompany_trade_price',
        store=True,
        digits_compute=dp.get_precision('Intercompany Trade Product Price'))

    supplier_product_id = fields.Many2one(
        comodel_name='product.product', string='Supplier Product',
        readonly=True, selected=True, _prefetch=False)

    # Compute Section
    @api.multi
    @api.depends('supplier_product_id', 'pricelist_ids')
    def _compute_intercompany_trade_price(self):
        for supplierinfo in self:
            if supplierinfo.supplier_product_id and supplierinfo.pricelist_ids:
                supplierinfo.intercompany_trade_price =\
                    supplierinfo.pricelist_ids[0].price
            else:
                supplierinfo.intercompany_trade_price = 0

    # Constrains Section
    @api.multi
    @api.constrains('supplier_product_id', 'name')
    def _check_supplier_product_id(self):
        for supplierinfo in self.browse():
            if not supplierinfo.supplier_product_id and\
                    supplierinfo.name.intercompany_trade:
                raise UserError(_(
                    "Error ! You can not link this product in this manner"
                    " because the supplier is flagged as Inter Company Trade."
                    " Please use the dedicated interface in the Intercompany"
                    " Trade menu."))
