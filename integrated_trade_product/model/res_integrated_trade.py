# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Base module for OpenERP
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
from openerp.osv.osv import except_osv
from openerp.osv.orm import Model
from openerp.tools.translate import _


class res_integrated_trade(Model):
    _inherit = 'res.integrated.trade'

#    def _get_supplier_info(
#            self, cr, uid, integrated_trade,
#            customer_product, customer_price, customer_taxes,
#            supplier_line=None, supplier_product_field=None,
#            supplier_taxe_fields=None, context=None):
#        """
#        Use this function to have Supplier information when a customer realize
#        a Purchase Order or an Invoice type 'in'.
#        @param integrate_trade: (res.integrated.trade)
#            current integrated trade to use for the computation.
#        @param customer_product: (product.product)
#            Product to buy in the customer company;
#        @param customer_price: (float)
#            Purchase price for the product to purchase;
#        @param customer_taxe_ids: (List of account.tax)
#            list of taxes defined in the current purchase order line;

#        @return a dictionary:{
#            'supplier_product_id': id of the product in the supplier company;
#            'supplier_price': Sale price of the supplier, depending of taxes;
#            'supplier_taxe_ids': list of taxes set;
#            }
#        @raise:
#            * Error if supplier and customer products are not linked;
#        """
#        psi_obj = self.pool['product.supplierinfo']
#        pp_obj = self.pool['product.product']

#        res = {}
#        if not supplier_line:
#            # Get Supplier Product
#            psi_ids = psi_obj.search(cr, uid, [
#                ('product_id', '=', customer_product.product_tmpl_id.id),
#                ('name', '=', integrated_trade.supplier_partner_id.id),
#            ], context=context)
#            if len(psi_ids) == 0:
#                raise except_osv(
#                    _("Product Selection Error!"),
#                    _("""You can not add the product '%s' to the current"""
#                        """ Purchase Order because you didn't linked the"""
#                        """ product to any Supplier Product. Please do it"""
#                        """ in the 'Integrated Trade' menu.""" % (
#                            customer_product.name)))
#            psi = psi_obj.browse(cr, uid, psi_ids[0], context=context)
#            supplier_product = pp_obj.browse(
#                cr, integrated_trade.supplier_user_id.id,
#                psi.supplier_product_id.id, context=context)

#            res['supplier_complete_product_name'] = '[%s] %s' % (
#                supplier_product.default_code, supplier_product.name)

#            # Get Supplier Taxes
#            if customer_taxes:
#                # TODO CHECK
#                supplier_taxes = supplier_product.taxes_id
#            else:
#                # If there is not Customer Taxes, we drop Customer Taxes
#                supplier_taxes = []

#            # Get Supplier Price
#            supplier_price = customer_price
#            if customer_taxes:
#                supplier_tax = supplier_taxes[0]
#                customer_tax = customer_product.supplier_taxes_id[0]
#                if (customer_tax.amount != 0 and
#                        customer_tax.price_include !=
#                        supplier_tax.price_include):
#                    if customer_tax.price_include:
#                        supplier_price = (
#                            customer_price /
#                            (1 + customer_tax.amount))
#                    else:
#                        supplier_price = (
#                            customer_price *
#                            (1 + customer_tax.amount))

#        res.update({
#            'supplier_product_id': supplier_product.id,
#            'supplier_price': supplier_price,
#            'supplier_tax_ids': [x.id for x in supplier_taxes],
#        })
#        return res

    def _get_integrated_trade_from_pricelist(self, cr, uid, ids, context=None):
        """Return Integrated Trade ids depending on changes of pricelist"""
        res = []
        rp_obj = self.pool['res.partner']
        rit_obj = self.pool['res.integrated.trade']
        for rp in rp_obj.browse(cr, uid, ids, context=context):
            if rp.integrated_trade and rp.customer:
                res.extend(rit_obj.search(cr, uid, [
                    ('customer_partner_id', '=', rp.id),
                ], context=context))
        return list(set(res))

    def _get_pricelist_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        rp_obj = self.pool['res.partner']
        for rit in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx['force_company'] = rit.supplier_company_id.id
            rp = rp_obj.browse(
                cr, uid, rit.customer_partner_id.id, context=ctx)
            res[rit.id] = rp.property_product_pricelist.id
        return res

    # Columns section
    _columns = {
        'pricelist_id': fields.function(
            _get_pricelist_id,
            string='Customer Pricelist in the Supplier Company',
            type='many2one', relation='product.pricelist', store={
                'res.partner': (
                    _get_integrated_trade_from_pricelist,
                    ['property_product_pricelist'], 10),
                'res.integrated.trade': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['customer_partner_id', 'supplier_company_id'], 10),
            })
    }
