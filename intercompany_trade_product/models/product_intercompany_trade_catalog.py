# coding: utf-8
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, tools
from openerp.addons import decimal_precision as dp


class ProductIntercompanyTradeCatalog(models.Model):
    _name = 'product.intercompany.trade.catalog'
    _auto = False

    # Custom Section
    @api.model
    def _get_supplier_product_id_from_id(self, id):
        return int(str(id)[:-4])

    @api.model
    def _get_intercompany_trade_id_from_id(self, id):
        return int(id[-4:])

    # Button Section
    @api.multi
    def button_see_customer_product(self):
        self.ensure_one()
        psi_obj = self.env['product.supplierinfo']
        supplier_product_id = self._get_supplier_product_id_from_id(self.id)
        psi = psi_obj.search([
            ('supplier_product_id', '=', supplier_product_id)])[0]
        pp_ids = psi.product_tmpl_id.with_context(
            active_test=False).product_variant_ids.ids
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': pp_ids[0],
            'target': 'new',
            'context': self.env.context,
        }

    @api.multi
    def button_link_product_wizard(self):
        self.ensure_one()
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'intercompany.trade.wizard.link.product',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,
        }

    @api.multi
    def button_unlink_product(self):
        self.ensure_one()
        supplierinfo_obj = self.env['product.supplierinfo']
        supplier_product_id = self._get_supplier_product_id_from_id(self.id)
        supplierinfo_obj.search([
            ('supplier_product_id', '=', supplier_product_id)]).unlink()

    # Column Section
    intercompany_trade_id = fields.Many2one(
        string='Intercompany Trade', readonly=True,
        comodel_name='intercompany.trade.config')

    customer_product_tmpl_id = fields.Many2one(
        string='Customer Product', readonly=True,
        comodel_name='product.template')

    supplier_sale_price = fields.Float(
        string='Supplier Sale Price', compute='_compute_sale_info',
        multi='_compute_sale_info',
        digits_compute=dp.get_precision('Intercompany Trade Product Price'))

    customer_purchase_price = fields.Float(
        string='Customer Purchase Price', readonly=True)

    sale_pricelist_id = fields.Many2one(
        string='Sale Pricelist', readonly=True,
        comodel_name='product.pricelist')

    customer_company_id = fields.Many2one(
        string='Customer Company', readonly=True, comodel_name='res.company')

    supplier_product_name = fields.Char(
        string='Supplier Product Name', readonly=True)

    supplier_product_uom = fields.Many2one(
        string='Supplier Product UoM', readonly=True,
        comodel_name='product.uom')

    supplier_product_default_code = fields.Char(
        string='Supplier Product Code', readonly=True)

    supplier_partner_id = fields.Many2one(
        string='Supplier Partner', readonly=True, comodel_name='res.partner')

    supplier_partner_name = fields.Char(
        string='Supplier Partner Name', readonly=True)

    supplier_category_id = fields.Many2one(
        string='Supplier Product Category', readonly=True,
        comodel_name='product.category')

    supplier_category_name = fields.Char(
        string='Supplier Product Category', readonly=True)

    supplier_product_id = fields.Many2one(
        string='Supplier Product', readonly=True,
        comodel_name='product.product')

    supplier_product_active = fields.Boolean(
        string='Supplier Product Active', readonly=True)

    supplier_product_sale_ok = fields.Boolean(
        string='Supplier Product Can be sold', readonly=True)

    # Fields Function Section
    @api.multi
    def _compute_sale_info(self):
        """Overload _compute_intercompany_trade_prices to add extra computed
        values in this multi computation function"""
        for catalog in self.sudo():
            res = catalog.sale_pricelist_id.sudo().\
                _compute_intercompany_trade_prices(
                    catalog.supplier_product_id, catalog.supplier_partner_id)
            for field_name, value in res.iteritems():
                setattr(catalog, field_name, value)

    # View Section
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
CREATE OR REPLACE VIEW %s AS (
        SELECT
            to_char(s_pp.id, 'FM099999') || to_char(rit.id, 'FM0000') as id,
            rit.id as intercompany_trade_id,
            c_psi.product_tmpl_id as customer_product_tmpl_id,
            rit.customer_company_id,
            rit.sale_pricelist_id as sale_pricelist_id,
            rit.customer_partner_id,
            s_pp.id as supplier_product_id,
            s_pp.default_code as supplier_product_default_code,
            s_pt.uom_id as supplier_product_uom,
            s_pt.name as supplier_product_name,
            s_pp.active as supplier_product_active,
            s_pt.sale_ok as supplier_product_sale_ok,
            s_pc.id as supplier_category_id,
            s_pc.name as supplier_category_name,
            c_psi.intercompany_trade_price as customer_purchase_price,
            rit.supplier_company_id,
            rit.supplier_partner_id,
            c_rp.name as supplier_partner_name
        FROM product_product s_pp
        INNER JOIN product_template s_pt
            ON s_pp.product_tmpl_id = s_pt.id
        INNER JOIN product_category s_pc
            ON s_pt.categ_id = s_pc.id
        RIGHT JOIN intercompany_trade_config rit
            ON s_pt.company_id = rit.supplier_company_id
        INNER JOIN res_partner c_rp
            ON rit.supplier_partner_id = c_rp.id
        LEFT JOIN product_supplierinfo c_psi
            ON c_psi.supplier_product_id = s_pp.id
            AND c_psi.company_id = rit.customer_company_id
        WHERE
            (s_pp.active = True and s_pt.sale_ok = True)
            OR c_psi.product_tmpl_id is not null
        ORDER BY s_pt.name
)""" % (self._table))
