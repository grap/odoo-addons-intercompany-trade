# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Product module for OpenERP
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

from datetime import date

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.addons import decimal_precision as dp


class product_integrated_trade_catalog(Model):
    _name = 'product.integrated.trade.catalog'
    _auto = False
    _table = 'product_integrated_trade_catalog'

    # Custom Section
    def _get_supplier_product_id_from_id(self, str_id):
        return int(str_id[:-4])

    def _get_integrated_trade_id_from_id(self, str_id):
        return int(str_id[-4:])

    # Button Section
    def link_product_wizard(self, cr, uid, ids, context=None):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'integrated.trade.wizard.link.product',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def unlink_product(self, cr, uid, ids, context=None):
        psi_obj = self.pool['product.supplierinfo']
        for id in ids:
            supplier_product_id = self._get_supplier_product_id_from_id(id)
            psi_ids = psi_obj.search(cr, uid, [
                ('supplier_product_id', '=', supplier_product_id)],
                context=context)
            psi_obj.unlink(cr, uid, psi_ids, context=context)
        return True

    # Fields Function Section
    def _get_supplier_sale_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        ppl_obj = self.pool['product.pricelist']
        for pitc in self.browse(cr, uid, ids, context=context):
            if pitc.customer_purchase_price != 0:
                res[pitc.id] = pitc.customer_purchase_price
            else:
                res[pitc.id] = ppl_obj.price_get(
                    cr, SUPERUSER_ID, [pitc.pricelist_id.id],
                    pitc.supplier_product_id.id,
                    1.0, pitc.supplier_partner_id.id, {
                        'uom': pitc.supplier_product_uos.id,
                        'date': date.today().strftime('%Y-%m-%d'),
                    })[pitc.pricelist_id.id]
        return res

    # Column Section
    _columns = {
        'integrated_trade_id': fields.many2one(
            'res.integrated.trade', 'Integrated Trade', readonly=True),
        'customer_product_tmpl_id': fields.many2one(
            'product.template', 'Customer Product', readonly=True),
        'supplier_sale_price': fields.function(
            _get_supplier_sale_price, 'Supplier Sale Price', type='float',
            digits_compute=dp.get_precision('Integrated Product Price')),
        'customer_purchase_price': fields.float(
            'Customer Purchase Price', readonly=True),
        'pricelist_id': fields.many2one(
            'product.pricelist', 'Price List', readonly=True),
        'customer_company_id': fields.many2one(
            'res.company', 'Customer Company', readonly=True),
        'supplier_product_name': fields.char(
            'Supplier Product Name', readonly=True),
        'supplier_product_uos': fields.many2one(
            'product.uom', 'Supplier Product UoS', readonly=True),
        'supplier_product_default_code': fields.char(
            'Supplier Product Code', readonly=True),
        'supplier_partner_id': fields.many2one(
            'res.partner', 'Supplier Partner', readonly=True),
        'supplier_partner_name': fields.char(
            'Supplier Partner Name', readonly=True),
        'supplier_product_id': fields.many2one(
            'product.product', 'Supplier Product', readonly=True),

    }

    # View Section
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
CREATE OR REPLACE VIEW %s AS (
        SELECT
            to_char(s_pp.id, 'FM099999') || to_char(rit.id, 'FM0000') as id,
            rit.id as integrated_trade_id,
            c_psi.product_id as customer_product_tmpl_id,
            rit.customer_company_id,
            rit.pricelist_id as pricelist_id,
            rit.customer_partner_id,
            s_pp.id as supplier_product_id,
            s_pt.uos_id as supplier_product_uos,
            s_pt.name as supplier_product_name,
            s_pp.default_code as supplier_product_default_code,
            c_psi.integrated_price as customer_purchase_price,
            rit.supplier_company_id,
            rit.supplier_partner_id,
            c_rp.name as supplier_partner_name
        FROM product_product s_pp
        INNER JOIN product_template s_pt
            ON s_pp.product_tmpl_id = s_pt.id
        RIGHT JOIN res_integrated_trade rit
            ON s_pt.company_id = rit.supplier_company_id
        INNER JOIN res_partner c_rp
            ON rit.supplier_partner_id = c_rp.id
        LEFT JOIN product_supplierinfo c_psi
            ON c_psi.supplier_product_id = s_pp.id
)""" % (self._table))
