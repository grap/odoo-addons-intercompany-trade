# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Product module for OpenERP
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.addons import decimal_precision as dp


class ProductIntercompanyTradeCatalog(Model):
    _name = 'product.intercompany.trade.catalog'
    _auto = False
    _table = 'product_intercompany_trade_catalog'

    # Custom Section
    def _get_supplier_product_id_from_id(self, str_id):
        return int(str_id[:-4])

    def _get_intercompany_trade_id_from_id(self, str_id):
        return int(str_id[-4:])

    # Button Section
    def button_see_customer_product(self, cr, uid, ids, context=None):
        psi_obj = self.pool['product.supplierinfo']
        pp_obj = self.pool['product.product']
        id = ids[0]
        supplier_product_id = self._get_supplier_product_id_from_id(id)
        psi_ids = psi_obj.search(cr, uid, [
            ('supplier_product_id', '=', supplier_product_id)],
            context=context)
        psi = psi_obj.browse(cr, uid, psi_ids[0])
        pp_ids = pp_obj.search(cr, uid, [
            ('product_tmpl_id', '=', psi.product_id.id)],
            context=context)
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': pp_ids[0],
            'target': 'new',
            'context': context,
        }
        return res

    def button_link_product_wizard(self, cr, uid, ids, context=None):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'intercompany.trade.wizard.link.product',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def button_unlink_product(self, cr, uid, ids, context=None):
        psi_obj = self.pool['product.supplierinfo']
        for id in ids:
            supplier_product_id = self._get_supplier_product_id_from_id(id)
            psi_ids = psi_obj.search(cr, uid, [
                ('supplier_product_id', '=', supplier_product_id)],
                context=context)
            psi_obj.unlink(cr, uid, psi_ids, context=context)
        return True

    # Fields Function Section
    def _get_supplier_price(self, cr, uid, ids, name, arg, context=None):
        ppl_obj = self.pool['product.pricelist']
        res = {}
        for pitc in self.browse(cr, SUPERUSER_ID, ids, context=context):
            res[pitc.id] = ppl_obj._compute_intercompany_trade_prices(
                cr, SUPERUSER_ID, pitc.supplier_product_id,
                pitc.supplier_partner_id, pitc.sale_pricelist_id,
                context=context)
        return res

    # Column Section
    _columns = {
        'intercompany_trade_id': fields.many2one(
            'intercompany.trade.config', 'Intercompany Trade', readonly=True),
        'customer_product_tmpl_id': fields.many2one(
            'product.template', 'Customer Product', readonly=True),
        'supplier_sale_price': fields.function(
            _get_supplier_price, string='Supplier Sale Price',
            multi='supplier_price', type='float',
            digits_compute=dp.get_precision(
                'Intercompany Trade Product Price')),
        'customer_purchase_price': fields.float(
            'Customer Purchase Price', readonly=True),
        'sale_pricelist_id': fields.many2one(
            'product.pricelist', 'Sale Pricelist', readonly=True),
        'customer_company_id': fields.many2one(
            'res.company', 'Customer Company', readonly=True),
        'supplier_product_name': fields.char(
            'Supplier Product Name', readonly=True),
        'supplier_product_uom': fields.many2one(
            'product.uom', 'Supplier Product UoM', readonly=True),
        'supplier_product_default_code': fields.char(
            'Supplier Product Code', readonly=True),
        'supplier_partner_id': fields.many2one(
            'res.partner', 'Supplier Partner', readonly=True),
        'supplier_partner_name': fields.char(
            'Supplier Partner Name', readonly=True),
        'supplier_category_id': fields.many2one(
            'product.category', 'Supplier Product Category', readonly=True),
        'supplier_category_name': fields.char(
            'Supplier Product Category', readonly=True),
        'supplier_product_id': fields.many2one(
            'product.product', 'Supplier Product', readonly=True),
        'supplier_product_active': fields.boolean(
            'Supplier Product Active', readonly=True),
        'supplier_product_sale_ok': fields.boolean(
            'Supplier Product Can be sold', readonly=True),

    }

    # View Section
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
CREATE OR REPLACE VIEW %s AS (
        SELECT
            to_char(s_pp.id, 'FM099999') || to_char(rit.id, 'FM0000') as id,
            rit.id as intercompany_trade_id,
            c_psi.product_id as customer_product_tmpl_id,
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
            OR c_psi.product_id is not null
        ORDER BY s_pt.name
)""" % (self._table))
