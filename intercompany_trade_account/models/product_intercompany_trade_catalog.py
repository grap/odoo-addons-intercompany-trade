# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.addons import decimal_precision as dp


class ProductIntercompanyTradeCatalog(models.Model):
    _inherit = 'product.intercompany.trade.catalog'

    # TODO : Is it usefull ?
    # Column Section
    supplier_sale_price_tax_excluded = fields.Float(
        string='Supplier Sale Price Taxes Excluded',
        compute='_compute_sale_info', multi='_compute_sale_info',
        digits_compute=dp.get_precision('Intercompany Trade Product Price'))

    supplier_sale_price_tax_included = fields.Float(
        string='Supplier Sale Price Taxes Included',
        compute='_compute_sale_info', multi='_compute_sale_info',
        digits_compute=dp.get_precision('Intercompany Trade Product Price'))

    supplier_tax_name = fields.Char(
        string='Supplier Taxes Name',
        compute='_compute_sale_info', multi='_compute_sale_info')
