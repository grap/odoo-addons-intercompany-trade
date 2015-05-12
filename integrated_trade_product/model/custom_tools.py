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

from openerp.tools.translate import _
from openerp.osv.osv import except_osv


def _compute_integrated_customer_price(
        pool, cr, uid, supplier_product, customer_product,
        supplier_price, context=None):
    """
    :error raised:
        * If customer and supplier product taxes quantities doesn't match;
        * if supplier product has more than one tax;
        * if tax amount are different;
        * if tax type is not 'percent';
    """
    customer_price = supplier_price
    print "_compute_integrated_customer_price"
    # Check if taxes are correct
    if (len(supplier_product.taxes_id)
            != len(customer_product.supplier_taxes_id)):
        raise except_osv(
            _("Taxes Mismatch!"),
            _("""You can not link Supplier Product that has %d Sale"""
            """ Tax(es) with this Customer Product that has %d"""
            """ Supplier Taxes.""") % (
                len(supplier_product.taxes_id),
                len(customer_product.supplier_taxes_id)))
    if (len(supplier_product.taxes_id) > 1):
        raise except_osv(
            _("Too Complex Taxes Setting!"),
            _("""You can not link this Supplier Product. It has more"""
            """ than 1 Sale Taxes (%d)"""
            """""") % (len(supplier_product.taxes_id)))
    if supplier_product.taxes_id:
        supplier_tax = supplier_product.taxes_id[0]
        customer_tax = customer_product.supplier_taxes_id[0]
        # Check percent type
        if supplier_tax.type != 'percent':
            raise except_osv(
                _("Too Complex Taxes Setting!"),
                _("""You can not link this Supplier Product. The tax """
                """ setting of %s is %s. (Only 'percent' is accepted)"""
                """""") % (supplier_tax.name, supplier_tax.type))
        if customer_tax.type != 'percent':
            raise except_osv(
                _("Too Complex Taxes Setting!"),
                _("""You can not link this Customer Product. The tax """
                """ setting of %s is %s. (Only 'percent' is accepted)"""
                """""") % (customer_tax.name, customer_tax.type))
        # Check amount
        if supplier_tax.amount != customer_tax.amount:
            raise except_osv(
                _("Taxes Mismatch!"),
                _("""You can not link this Customer Product to this"""
                """ Supplier Product because taxes values doesn't"""
                """ match:\n"""
                """  Customer Tax value: %s %%;\n """
                """  Supplier Tax value: %s %%;\n """
                """""") % (
                    customer_tax.amount * 100, supplier_tax.amount * 100))
        if (customer_tax.amount != 0 and
                customer_tax.price_include != supplier_tax.price_include):
            print "type different"
            if supplier_tax.price_include:
                customer_price = supplier_price / (1 + supplier_tax.amount)
                print "type 1"
            else:
                customer_price = supplier_price * (1 + supplier_tax.amount)
                print "type 2"
    return {
        'customer_purchase_price': customer_price,
    }

def _compute_integrated_prices(
        pool, cr, uid, supplier_product,
        supplier_partner, pricelist, customer_product=False,
        context=None):
    """
    This xxx

    :param supplier_product (product.product):
         Product to sell in the supplier database;
    :param supplier_partner (res.partner):
        Supplier in the CUSTOMER Database;
    : pricelist (product.pricelist):
        Sale Pricelist in the supplier database;
    :param customer_product (product.product) - Optional:
         Product to buy in the customer database;
    :returns:
        return a dictionary containing supplier and optionaly
        customer price;

    """
    ppl_obj = pool['product.pricelist']
    at_obj = pool['account.tax']
    # Compute Sale Price
    supplier_price = ppl_obj.price_get(
        cr, uid, [pricelist.id],
        supplier_product.id,
        1.0, supplier_partner.id, {
            'uom': supplier_product.uom_id.id,
            'date': date.today().strftime('%Y-%m-%d'),
        })[pricelist.id]
    # Compute Taxes detail
    tax_info = at_obj.compute_all(
        cr, uid, supplier_product.taxes_id,
        supplier_price, 1.0, supplier_product.id)
    res = {
        'supplier_sale_price': supplier_price,
        'supplier_sale_price_vat_excl': tax_info['total'],
        'supplier_sale_price_vat_incl': tax_info['total_included'],
    }
    if customer_product:
        res.update(_compute_integrated_customer_price(
            pool, cr, uid, supplier_product, customer_product,
            supplier_price))
    return res
