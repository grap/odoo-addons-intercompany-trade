# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Product module for Odoo
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
from openerp.tools.translate import _
from openerp.osv.osv import except_osv


def _integrated_trade_update_multicompany(
        pool, cr, uid, supplier_product_ids, context=None):
    """
    This function update supplierinfo in customer database,
    depending of changes in supplier database, for all integrated trade
    define.
    Call this function when there is a change of product price,
    product taxes, partner pricelist, etc...
    :supplier_product_ids (list of ids of product.product):
        products that has been changed in the supplier database;
    """
    rit_obj = pool['res.integrated.trade']
    psi_obj = pool['product.supplierinfo']
    for supplier_product_id in supplier_product_ids:
        psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
            ('supplier_product_id', '=', supplier_product_id),
        ], context=context)
        for psi in psi_obj.browse(
                cr, SUPERUSER_ID, psi_ids, context=context):
            rit_id = rit_obj.search(cr, uid, [
                ('customer_company_id', '=', psi.company_id.id),
                ('supplier_partner_id', '=', psi.name.id),
            ], context=context)[0]
            _integrated_trade_update(
                pool, cr, uid, rit_id, [supplier_product_id],
                context=context)


# TODO Remove SUPERUSER_ID
def _integrated_trade_update(
        pool, cr, uid, integrated_trade_id, supplier_product_ids,
        context=None):
    """
    This function update supplierinfo in customer database,
    depending of changes in supplier database, depending of
    a specific integrated trade.
    Call this function when there is a change of product price,
    product taxes, partner pricelist, etc...
    :param integrated_trade_id (id of res.integrated.trade):
        integrated trade impacted;
    :supplier_product_ids (list of ids of product.product):
        products that has been changed in the supplier database;
    """
    rit_obj = pool['res.integrated.trade']
    psi_obj = pool['product.supplierinfo']
    pp_obj = pool['product.product']
    rit = rit_obj.browse(cr, uid, integrated_trade_id, context=context)
    if not supplier_product_ids:
        # Global Update
        psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
            ('name', '=', rit.supplier_partner_id.id),
        ], context=context)
    else:
        psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
            ('name', '=', rit.supplier_partner_id.id),
            ('supplier_product_id', 'in', supplier_product_ids)
        ], context=context)
    for psi in psi_obj.browse(cr, SUPERUSER_ID, psi_ids, context=context):
        pp_ids = pp_obj.search(cr, SUPERUSER_ID, [
            ('product_tmpl_id', '=', psi.product_id.id)], context=context)
        psi_vals = _integrated_trade_prepare(
            pool, cr, SUPERUSER_ID, integrated_trade_id,
            psi.supplier_product_id.id, pp_ids[0], context=context)
        psi_obj.write(
            cr, SUPERUSER_ID, [psi.id], psi_vals, context=context)

#def _check_taxes(
#        pool, cr, uid, supplier_product, customer_product, context=None):
#    """
#    :error raised:
#        * If customer and supplier product taxes quantities doesn't match;
#        * if supplier product has more than one tax;
#        * if tax amount are different;
#        * if tax type is not 'percent';
#    """
#    # Check if taxes are correct
#    if (len(supplier_product.taxes_id)
#            != len(customer_product.supplier_taxes_id)):
#        raise except_osv(
#            _("Taxes Mismatch!"),
#            _(
#                """You can not link Supplier Product that has %d Sale"""
#                """ Tax(es) with this Customer Product that has %d"""
#                """ Supplier Taxes.""") % (
#                    len(supplier_product.taxes_id),
#                    len(customer_product.supplier_taxes_id)))
#    if (len(supplier_product.taxes_id) > 1):
#        raise except_osv(
#            _("Too Complex Taxes Setting!"),
#            _(
#                """You can not link this Supplier Product. It has more"""
#                """ than 1 Sale Taxes (%d)"""
#                """""") % (len(supplier_product.taxes_id)))
#    if supplier_product.taxes_id:
#        supplier_tax = supplier_product.taxes_id[0]
#        customer_tax = customer_product.supplier_taxes_id[0]
#        # Check percent type
#        if supplier_tax.type != 'percent':
#            raise except_osv(
#                _("Too Complex Taxes Setting!"),
#                _(
#                    """You can not link this Supplier Product. The tax """
#                    """ setting of %s is %s. (Only 'percent' is accepted)"""
#                    """""") % (supplier_tax.name, supplier_tax.type))
#        if customer_tax.type != 'percent':
#            raise except_osv(
#                _("Too Complex Taxes Setting!"),
#                _(
#                    """You can not link this Customer Product. The tax """
#                    """ setting of %s is %s. (Only 'percent' is accepted)"""
#                    """""") % (customer_tax.name, customer_tax.type))
#        # Check amount
#        if supplier_tax.amount != customer_tax.amount:
#            raise except_osv(
#                _("Taxes Mismatch!"),
#                _(
#                    """You can not link this Customer Product to this"""
#                    """ Supplier Product because taxes values doesn't"""
#                    """ match:\n"""
#                    """  Customer Tax value: %s %%;\n """
#                    """  Supplier Tax value: %s %%;\n """
#                    """""") % (
#                        customer_tax.amount * 100, supplier_tax.amount * 100))


#def _compute_integrated_customer_price(
#        pool, cr, uid, supplier_product, customer_product,
#        supplier_price, context=None):
#    # FIXME
#    pass

#    customer_price = supplier_price
#    _check_taxes(
#        pool, cr, uid, supplier_product, customer_product, context=context)

#    if supplier_product.taxes_id:
#        supplier_tax = supplier_product.taxes_id[0]
#        customer_tax = customer_product.supplier_taxes_id[0]
#        if (customer_tax.amount != 0 and
#                customer_tax.price_include != supplier_tax.price_include):
#            if supplier_tax.price_include:
#                customer_price = supplier_price / (1 + supplier_tax.amount)
#            else:
#                customer_price = supplier_price * (1 + supplier_tax.amount)
#    return {
#        'customer_purchase_price': customer_price,
#        'customer_taxes_id': customer_tax and [customer_tax.id] or [],
#    }


#def _compute_integrated_supplier_price(
#        pool, cr, uid, supplier_product, customer_product,
#        customer_price, context=None):

#    supplier_price = customer_price
#    _check_taxes(
#        pool, cr, uid, supplier_product, customer_product, context=context)

#    if supplier_product.taxes_id:
#        supplier_tax = supplier_product.taxes_id[0]
#        customer_tax = customer_product.supplier_taxes_id[0]
#        if (customer_tax.amount != 0 and
#                customer_tax.price_include != supplier_tax.price_include):
#            if customer_tax.price_include:
#                supplier_price = customer_price / (1 + customer_tax.amount)
#            else:
#                supplier_price = customer_price * (1 + customer_tax.amount)
#    return {
#        'supplier_sale_price': supplier_price,
#        'supplier_taxes_id': supplier_tax and [supplier_tax.id] or [],
#    }


# Overloadable Section
def _integrated_trade_prepare(
        pool, cr, uid, integrated_trade_id, supplier_product_id,
        customer_product_id, context=None):
    """
    This function prepares supplier_info values.
    Please overload this function to change the datas of the supplierinfo
    created when a link between two products is done."""
    pp_obj = pool['product.product']
    rit_obj = pool['res.integrated.trade']
    ppl_obj = pool['product.pricelist']
    rit = rit_obj.browse(
        cr, uid, integrated_trade_id, context=context)
    supplier_pp = pp_obj.browse(
        cr, rit.supplier_user_id.id, supplier_product_id, context=context)
    customer_pp = pp_obj.browse(
        cr, rit.customer_user_id.id, customer_product_id, context=context)
    price_info = ppl_obj._compute_integrated_prices(
        cr, rit.supplier_user_id.id, supplier_pp,
        rit.supplier_partner_id, rit.pricelist_id, context=context)
    return {
        'min_qty': 0.0,
        'name': rit.supplier_partner_id.id,
        'product_name': supplier_pp.name,
        'product_code': supplier_pp.default_code,
        'company_id': rit.customer_company_id.id,
        'supplier_product_id': supplier_pp.id,
        'pricelist_ids': [[5], [0, False, {
            'min_quantity': 0.0,
            'price': price_info['supplier_sale_price']}]],
    }
