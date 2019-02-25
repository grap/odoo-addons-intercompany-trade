# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    # Columns Section
    is_intercompany_trade = fields.Boolean(
        compute='_compute_is_intercompany_trade', store=True)

    intercompany_trade_id = fields.Many2one(
        string='Intercompany Trade', store=True,
        compute='_compute_intercompany_trade_id',
        comodel_name='intercompany.trade.config')

    supplier_product_id = fields.Many2one(
        comodel_name='product.product', string='Supplier Product',
        selected=True, _prefetch=False)

    catalog_id = fields.Many2one(
        comodel_name='intercompany.trade.catalog', string='Catalog',
        compute='_compute_catalog_id', inverse='_set_catalog_id',
        domain="[('intercompany_trade_id', '=', intercompany_trade_id)]")

    # Compute Section
    @api.multi
    @api.depends('name')
    def _compute_is_intercompany_trade(self):
        for supplierinfo in self.filtered(lambda x: x.name):
            supplierinfo.is_intercompany_trade =\
                supplierinfo.name.intercompany_trade

    @api.multi
    @api.depends('name')
    def _compute_intercompany_trade_id(self):
        IntercompanyTradeConfig = self.env['intercompany.trade.config']
        for supplierinfo in self.filtered(lambda x: x.name):
            supplierinfo.intercompany_trade_id =\
                IntercompanyTradeConfig.search([
                    ('customer_company_id', '=', supplierinfo.company_id.id),
                    ('supplier_partner_id', '=', supplierinfo.name.id)]).id

    @api.multi
    @api.depends('intercompany_trade_id', 'supplier_product_id')
    def _compute_catalog_id(self):
        for supplierinfo in self.filtered(
                lambda x: x.intercompany_trade_id and x.supplier_product_id):
            supplierinfo.catalog_id = int(
                '%s%s' % (
                    supplierinfo.supplier_product_id.id,
                    str(supplierinfo.intercompany_trade_id.id).rjust(4, '0')))

    @api.multi
    def _set_catalog_id(self):
        for supplierinfo in self.filtered(lambda x: x.catalog_id):
            res =\
                int(str(supplierinfo.catalog_id.id)[:-4])
            supplierinfo.supplier_product_id = res

    @api.onchange('catalog_id')
    def _onchange_catalog_id(self):
        for supplierinfo in self.filtered(lambda x: x.catalog_id):
            res = int(str(supplierinfo.catalog_id.id)[:-4])
            supplierinfo.supplier_product_id = res
