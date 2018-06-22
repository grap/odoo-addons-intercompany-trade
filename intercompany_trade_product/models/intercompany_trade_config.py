# coding: utf-8
# Copyright (C) 2014 - Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class IntercompanyTradeConfig(models.Model):
    _inherit = 'intercompany.trade.config'

    # Columns section
    sale_pricelist_id = fields.Many2one(
        string='Sale Pricelist', comodel_name='product.pricelist',
        compute='_compute_sale_pricelist_id', store=True,
        help="Sale Pricelist in the Supplier Company")

    # Compute Section
    @api.multi
    @api.depends(
        'supplier_company_id',
        'customer_partner_id.property_product_pricelist')
    def _compute_sale_pricelist_id(self):
        partner_obj = self.env['res.partner']
        for config in self:
            partner = partner_obj.with_context(
                force_company=config.supplier_company_id.id).browse(
                    config.customer_partner_id.id)
            config.sale_pricelist_id = partner.property_product_pricelist

    # Custom Section
    @api.multi
    def _prepare_product_supplierinfo(
            self, supplier_product_id, customer_product_id):
        """
        This function prepares supplier_info values.
        Please overload this function to change the datas of the supplierinfo
        created when a link between two products is done."""
        self.ensure_one()
        product_obj = self.env['product.product']
        supplierinfo_obj = self.env['product.supplierinfo']
        vals = supplierinfo_obj._add_missing_default_values({})
        supplier_product = product_obj.sudo().browse(supplier_product_id)
        price_info =\
            self.sale_pricelist_id.sudo()._compute_intercompany_trade_prices(
                supplier_product, self.supplier_partner_id)
        vals.update({
            'name': self.supplier_partner_id.id,
            'product_name': supplier_product.name,
            'product_code': supplier_product.default_code,
            'company_id': self.customer_company_id.id,
            'supplier_product_id': supplier_product.id,
            'pricelist_ids': [[5], [0, False, {
                'min_quantity': 0.0,
                'price': price_info['supplier_sale_price']}]],
        })
        return vals

    @api.multi
    def _get_other_product_info(self, product_id, direction):
        """
            Deliver a product id from another product id.
            Usefull to call when create (sale / purchase / invoice) line to
            create according line with correct product;

            Realize correct check if the product is not referenced.

            :param @product_id: id of a product.product
                Current product, added by the customer / the supplier.
            :param @direction: 'in' / 'out'.
                'in': for a 'purchase' / 'In Invoice';
                'out': for a 'sale' / 'Out Invoice';

            :return : {
                'product_id': xxx;
                'price_unit': xxx; (only if direction is in);
            }
        """
        self.ensure_one()
        res = {}

        product_obj = self.env['product.product']
        supplierinfo_obj = self.env['product.supplierinfo']

        # Get current Product
        product = product_obj.browse(product_id)

        if direction == 'in':
            # Get product supplier info (if any)
            supplierinfos = supplierinfo_obj.sudo().search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('name', '=', self.supplier_partner_id.id),
                ('company_id', '=', self.customer_company_id.id)])
            if len(supplierinfos) == 0:
                raise UserError(_(
                    "You can not add '%s' to the current Order or Invoice"
                    " because you didn't linked the product to any Supplier"
                    " Product. Please do it in the 'Intercompany Trade'"
                    " menu.") % (product.name))

            supplierinfo = supplierinfos[0]
            res['product_id'] = supplierinfo.supplier_product_id.id

            # Get Supplier Sale Price
            res['price_unit'] =\
                self.sale_pricelist_id._compute_intercompany_trade_prices(
                    supplierinfo.supplier_product_id.id,
                    self.supplier_partner_id)['supplier_sale_price']

        else:
            supplierinfos = supplierinfo_obj.search([
                ('supplier_product_id', '=', product_id),
                ('name', '=', self.supplier_partner_id.id),
                ('company_id', '=', self.customer_company_id.id)])
            if len(supplierinfos) == 0:
                raise UserError(_(
                    "You can not add the product '%s' to the"
                    " current Order or Invoice because the customer didn't"
                    " referenced your product. Please contact him and"
                    " say him to do it.") % (product.name))
            supplierinfo = supplierinfos[0]
            customer_products = product_obj.sudo().with_context(
                active_test=False).search([
                    ('company_id', '=', self.customer_company_id.id),
                    ('product_tmpl_id', '=', supplierinfo.product_tmpl_id.id),
                ])
            if len(customer_products) != 1:
                raise UserError(_(
                    "You can not add '%s' to the current Order or Invoice"
                    " because the customer referenced many variants of"
                    "  this template. Please contact him and say him to add"
                    "  the product manually to his Order or Invoice .") % (
                        product.name))
            res['product_id'] = customer_products[0].id
        return res
