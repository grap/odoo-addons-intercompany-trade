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

from openerp.osv import fields
from openerp.osv.orm import TransientModel
from openerp.addons import decimal_precision as dp


class integrated_trade_wizard_link_product(TransientModel):
    _name = 'integrated.trade.wizard.link.product'

    # Default Get Section
    def default_get(self, cr, uid, fields, context=None):
        psi_obj = self.pool['product.supplierinfo']
        pitc_obj = self.pool['product.integrated.trade.catalog']
        res = super(integrated_trade_wizard_link_product, self).default_get(
            cr, uid, fields, context=context)
        supplier_product_id = pitc_obj._get_supplier_product_id_from_id(
            context.get('active_id'))
        integrated_trade_id = pitc_obj._get_integrated_trade_id_from_id(
            context.get('active_id'))
        psi_vals = psi_obj._integrated_trade_prepare(
            cr, uid, integrated_trade_id, supplier_product_id, context=context)
        res.update({
            'supplier_product_id': supplier_product_id,
            'integrated_trade_id': integrated_trade_id,
            'supplier_product_name': psi_vals['product_name'],
            'supplier_product_code': psi_vals['product_code'],
            'supplier_product_price': psi_vals['pricelist_ids'][1][2]['price'],
        })
        return res

    # Column Section
    _columns = {
        'integrated_trade_id': fields.many2one(
            'res.integrated.trade', 'Integrated Trade',
            required=True, readonly=True),
        'customer_product_tmpl_id': fields.many2one(
            'product.template', 'Customer Product', required=True),
        'supplier_product_id': fields.many2one(
            'product.product', 'Supplier Product',
            required=True, readonly=True),
        # The Following Field are used to display external information
        # And avoir ACL problem
        'supplier_product_code': fields.char(
            'Supplier Product Code', readonly=True),
        'supplier_product_name': fields.char(
            'Supplier Product Name', readonly=True),
        'supplier_product_price': fields.float(
            'Supplier Product Price', readonly=True,
            digits_compute=dp.get_precision('Integrated Product Price')),

    }

    # Button Section
    def link_product(self, cr, uid, ids, context=None):
        psi_obj = self.pool['product.supplierinfo']
        for itwlp in self.browse(cr, uid, ids, context=context):
            # TODO raise error if there is a product linked
            psi_vals = psi_obj._integrated_trade_prepare(
                cr, uid, itwlp.integrated_trade_id.id,
                itwlp.supplier_product_id.id, context=context)
            psi_vals['product_id'] = itwlp.customer_product_tmpl_id.id
            psi_obj.create(cr, uid, psi_vals, context=context)
        return True
