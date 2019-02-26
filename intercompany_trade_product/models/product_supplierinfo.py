# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


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
        compute='_compute_catalog_id', inverse='_inverse_catalog_id',
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
    def _inverse_catalog_id(self):
        for supplierinfo in self.filtered(lambda x: x.catalog_id):
            res =\
                int(str(supplierinfo.catalog_id.id)[:-4])
            supplierinfo.supplier_product_id = res

    @api.onchange('catalog_id')
    def _onchange_catalog_id(self):
        for supplierinfo in self.filtered(lambda x: x.catalog_id):
            res = int(str(supplierinfo.catalog_id.id)[:-4])
            supplierinfo.supplier_product_id = res

    @api.constrains(
        'supplier_product_id', 'is_intercompany_trade', 'product_tmpl_id')
    def _check_intercompany_trade(self):
        for supplierinfo in self.filtered(lambda x: x.is_intercompany_trade):
            # Check if the supplier product has been linked to other
            # product
            res = self.search([
                ('supplier_product_id', '=',
                    supplierinfo.supplier_product_id.id),
                ('id', '!=', supplierinfo.id)
            ])
            if len(res):
                raise UserError(_(
                    "The product(s) %s  are still linked to the"
                    " the supplier product. You can not link the product"
                    " %s.") % (
                        ', '.join(res.mapped('product_tmpl_id.name')),
                        supplierinfo.product_tmpl_id.name,
                ))

    # TODO TODO TODO
    # ADD CHECK
    # @api.multi
    # def link_product(self):
    #     supplierinfo_obj = self.env['product.supplierinfo']
    #     template_obj = self.env['product.template']
    #     product_obj = self.env['product.product']
    #     catalog_obj = self.env['product.intercompany.trade.catalog']

    #     self.ensure_one()
    #     # Prepare Product Supplierinfo
    #     supplierinfo_vals =\
    #         self.intercompany_trade_id._prepare_product_supplierinfo(
    #             self.supplier_product_id.id, self.customer_product_id.id)
    #     supplierinfo_vals['product_tmpl_id'] =\
    #       self.customer_product_tmpl_id.id

    #     cus_template = template_obj.browse(
    #         supplierinfo_vals['product_tmpl_id'])
    #     sup_product = product_obj.sudo().browse(
    #         supplierinfo_vals['supplier_product_id'])

    #     # Raise error if there is many products associated to the template
    #     product_qty = product_obj.search([
    #         ('product_tmpl_id', '=', self.customer_product_tmpl_id.id)])
    #     if len(product_qty) != 1:
    #         raise UserError(_(
    #             "Too Many Variants for the Product !\nYou can not link this"
    #             " product %s because there are %d Variants associated.") % (
    #                 cus_template.name, len(product_qty)))

    #     # raise error if there is a product linked
    #     catalogs = catalog_obj.search([
    #         ('customer_product_tmpl_id', '=',
    #             supplierinfo_vals['product_tmpl_id']),
    #         ('customer_company_id', '=', supplierinfo_vals['company_id'])])
    #     if len(catalogs) != 0:
    #         if not self.env.context.get('demo_integrated', False):
    #             raise UserError(_(
    #                 "Duplicated References !\nYou can not link the Product"
    #                 " %s because it is yet linked to another supplier"
    # "product."
    #                 " Please unlink the Product and try again.") % (
    #                     cus_template.name))
    #         else:
    #             return

    #     # Raise an error if Unit doesn't match
    #     if cus_template.uom_id.category_id.id !=\
    #             sup_product.uom_id.category_id.id:
    #         raise UserError(_(
    #             "Unit Mismatch !\n The type of Unit of Mesure of your"
    # "" product"
    #             " is '%s'.\nThe type of Unit of Mesure of the supplier"
    # "" product"
    #             " is '%s'.\n\nThe type must be the same.") % (
    #                 cus_template.uom_id.category_id.name,
    #                 sup_product.uom_id.category_id.name))

    #     supplierinfo_obj.create(supplierinfo_vals)
