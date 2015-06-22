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

#from openerp import SUPERUSER_ID
#from openerp import tools
from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.addons import decimal_precision as dp


class ProductIntegratedTradeCatalog(Model):
    _inherit = 'product.integrated.trade.catalog'

#    # Custom Section
#    def _get_supplier_product_id_from_id(self, str_id):
#        return int(str_id[:-4])

#    def _get_integrated_trade_id_from_id(self, str_id):
#        return int(str_id[-4:])

#    # Button Section
#    def link_product_wizard(self, cr, uid, ids, context=None):
#        return {
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'integrated.trade.wizard.link.product',
#            'type': 'ir.actions.act_window',
#            'target': 'new',
#            'context': context,
#        }

#    def unlink_product(self, cr, uid, ids, context=None):
#        psi_obj = self.pool['product.supplierinfo']
#        for id in ids:
#            supplier_product_id = self._get_supplier_product_id_from_id(id)
#            psi_ids = psi_obj.search(cr, uid, [
#                ('supplier_product_id', '=', supplier_product_id)],
#                context=context)
#            psi_obj.unlink(cr, uid, psi_ids, context=context)
#        return True

#    # Fields Function Section
#    def _get_supplier_price(self, cr, uid, ids, name, arg, context=None):
#        ppl_obj = self.pool['product.pricelist']
#        res = {}
#        for pitc in self.browse(cr, SUPERUSER_ID, ids, context=context):
#            res[pitc.id] = ppl_obj._compute_integrated_prices(
#                cr, SUPERUSER_ID, pitc.supplier_product_id,
#                pitc.supplier_partner_id, pitc.pricelist_id, context=context)
#        return res

    # Fields Function Section
    def _get_supplier_price(self, cr, uid, ids, name, arg, context=None):
        
        res = super(ProductIntegratedTradeCatalog, self)._get_supplier_price(
            cr, uid, ids, name, arg, context=context)
        print "OVERLOAD : RES"
        print res
        return res

    # Column Section
    _columns = {
        'supplier_sale_price_vat_excl': fields.function(
            _get_supplier_price,
            string='Supplier Sale Price VAT Excluded',
            multi='supplier_price', type='float',
            digits_compute=dp.get_precision('Integrated Product Price')),
        'supplier_sale_price_vat_incl': fields.function(
            _get_supplier_price,
            string='Supplier Sale Price VAT Included',
            multi='supplier_price', type='float',
            digits_compute=dp.get_precision('Integrated Product Price')),
    }
