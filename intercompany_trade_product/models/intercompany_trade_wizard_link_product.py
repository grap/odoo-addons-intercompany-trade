# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

from openerp.addons import decimal_precision as dp


class IntercompanyTradeWizardLinkProduct(models.TransientModel):
    _name = 'intercompany.trade.wizard.link.product'

    # Default Get Section
    @api.model
    def default_get(self, fields):
        product_obj = self.env['product.product']
        catalog_obj = self.env['product.intercompany.trade.catalog']
        config_obj = self.env['intercompany.trade.config']
        pricelist_obj = self.env['product.pricelist']
        res = super(IntercompanyTradeWizardLinkProduct, self).default_get(
            fields)

        supplier_product_id = catalog_obj._get_supplier_product_id_from_id(
            self.env.context.get('active_id'))
        intercompany_trade_id = catalog_obj._get_intercompany_trade_id_from_id(
            self.env.context.get('active_id'))
        config = config_obj.browse(intercompany_trade_id)
        supplier_product = product_obj.sudo(
            user=config.supplier_user_id).browse(supplier_product_id)
        price_info = pricelist_obj.sudo(
            user=config.supplier_user_id)._compute_intercompany_trade_prices(
            supplier_product, config.supplier_partner_id,
            config.sale_pricelist_id)
        res.update({
            'supplier_product_id': supplier_product_id,
            'intercompany_trade_id': intercompany_trade_id,
            'supplier_product_name': supplier_product.name,
            'supplier_product_code': supplier_product.default_code,
            'supplier_product_uom_name': supplier_product.uom_id.name,
        })
        for k, v in price_info.items():
            res[k] = v
        return res

    # Column Section
    intercompany_trade_id = fields.Many2one(
        string='Intercompany Trade', comodel_name='intercompany.trade.config',
        required=True, readonly=True)

    customer_product_id = fields.Many2one(
        string='Customer Product', comodel_name='product.product',
        required=True)

    customer_product_tmpl_id = fields.Many2one(
        string='Customer Product', comodel_name='product.template',
        related='customer_product_id.product_tmpl_id', readonly=True)

    supplier_product_id = fields.Many2one(
        string='Supplier Product', comodel_name='product.product',
        required=True, readonly=True)

    # The Following Fields are used to display external information
    # And avoir ACL problem
    supplier_product_code = fields.Char(
        string='Supplier Product Code', readonly=True)

    supplier_product_name = fields.Char(
        string='Supplier Product Name', readonly=True)

    supplier_sale_price = fields.Float(
        string='Supplier Sale Price', readonly=True,
        digits_compute=dp.get_precision(
            'Intercompany Trade Product Price'))

    supplier_product_uom_name = fields.Char(
        string='Supplier Product UoM Name', readonly=True)

    # Button Section
    @api.multi
    def link_product(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        template_obj = self.env['product.template']
        product_obj = self.env['product.product']
        catalog_obj = self.env['product.intercompany.trade.catalog']

        self.ensure_one()
        # Prepare Product Supplierinfo
        supplierinfo_vals =\
            self.intercompany_trade_id._prepare_product_supplierinfo(
                self.supplier_product_id.id, self.customer_product_id.id)
        supplierinfo_vals['product_tmpl_id'] = self.customer_product_tmpl_id.id

        cus_template = template_obj.browse(
            supplierinfo_vals['product_tmpl_id'])
        sup_product = product_obj.sudo().browse(
            supplierinfo_vals['supplier_product_id'])

        # Raise error if there is many products associated to the template
        product_qty = product_obj.search([
            ('product_tmpl_id', '=', self.customer_product_tmpl_id.id)])
        if len(product_qty) != 1:
            raise UserError(_(
                "Too Many Variants for the Product !\nYou can not link this"
                " product %s because there are %d Variants associated.") % (
                    cus_template.name, len(product_qty)))

        # raise error if there is a product linked
        catalog_ids = catalog_obj.search([
            ('customer_product_tmpl_id', '=',
                supplierinfo_vals['product_tmpl_id']),
            ('customer_company_id', '=', supplierinfo_vals['company_id'])])
        if len(catalog_ids) != 0:
            raise UserError(_(
                "Duplicated References !\nYou can not link the Product"
                " %s because it is yet linked to another supplier product."
                " Please unlink the Product and try again.") % (
                    cus_template.name))

        # Raise an error if Unit doesn't match
        if cus_template.uom_id.category_id.id !=\
                sup_product.uom_id.category_id.id:
            raise UserError(_(
                "Unit Mismatch !\n The type of Unit of Mesure of your product"
                " is '%s'.\nThe type of Unit of Mesure of the supplier product"
                " is '%s'.\n\nThe type must be the same.") % (
                    cus_template.uom_id.category_id.name,
                    sup_product.uom_id.category_id.name))

        supplierinfo_obj.create(supplierinfo_vals)
