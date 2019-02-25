# coding: utf-8
# Copyright (C) 2019 - Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class IntercompanyTradeCatalog(models.Model):
    _name = 'intercompany.trade.catalog'
    _auto = False
    _rec_name = 'supplier_product_default_code'

    # Column Section
    intercompany_trade_id = fields.Many2one(
        string='Intercompany Trade', readonly=True,
        comodel_name='intercompany.trade.config')

    # customer_product_tmpl_id = fields.Many2one(
    #     string='Customer Product', readonly=True,
    #     comodel_name='product.template')

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

    supplier_product_id = fields.Many2one(
        string='Supplier Product', readonly=True,
        comodel_name='product.product')

    supplier_product_active = fields.Boolean(
        string='Supplier Product Active', readonly=True)

    supplier_product_sale_ok = fields.Boolean(
        string='Supplier Product Can be sold', readonly=True)

    # View Section
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
CREATE OR REPLACE VIEW %s AS (
        SELECT
            (to_char(s_pp.id, 'FM099999') || to_char(rit.id, 'FM0000'))::int
                as id,
            rit.id as intercompany_trade_id,
            rit.customer_company_id,
            rit.customer_partner_id,
            s_pp.id as supplier_product_id,
            s_pp.default_code as supplier_product_default_code,
            s_pt.uom_id as supplier_product_uom,
            s_pt.name as supplier_product_name,
            s_pp.active as supplier_product_active,
            s_pt.sale_ok as supplier_product_sale_ok,
            rit.supplier_company_id,
            rit.supplier_partner_id,
            c_rp.name as supplier_partner_name
        FROM product_product s_pp
        INNER JOIN product_template s_pt
            ON s_pp.product_tmpl_id = s_pt.id
        RIGHT JOIN intercompany_trade_config rit
            ON s_pt.company_id = rit.supplier_company_id
        INNER JOIN res_partner c_rp
            ON rit.supplier_partner_id = c_rp.id
        ORDER BY s_pt.name
)""" % (self._table))
