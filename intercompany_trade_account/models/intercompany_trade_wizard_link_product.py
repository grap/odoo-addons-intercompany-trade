# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from .custom_tools import _check_taxes
from openerp.addons import decimal_precision as dp


class IntercompanyTradeWizardLinkProduct(models.TransientModel):
    _inherit = 'intercompany.trade.wizard.link.product'

    # Column Section
    supplier_sale_price_tax_excluded = fields.Float(
        'Supplier Sale Price Taxes Excluded', readonly=True,
        digits_compute=dp.get_precision(
            'Intercompany Trade Product Price'))

    supplier_sale_price_tax_included = fields.Float(
        string='Supplier Sale Price Taxes Included', readonly=True,
        digits_compute=dp.get_precision(
            'Intercompany Trade Product Price'))

    # The Following Field are used to display external information
    # And avoir ACL problem
    supplier_tax_name = fields.Char(
        string='Supplier Taxes Name', readonly=True)

    # Button Section
    @api.multi
    def link_product(self):
        self.ensure_one()
        product_obj = self.env['product.product']

        for wizard in self:
            sup_product = product_obj.sudo().browse(
                wizard.supplier_product_id.id)
            cus_product = product_obj.sudo().browse(
                wizard.customer_product_id.id)
            _check_taxes(
                self.pool, self.env.cr, self.env.uid, sup_product, cus_product,
                context=self.env.context)

        return super(IntercompanyTradeWizardLinkProduct, self).link_product()
