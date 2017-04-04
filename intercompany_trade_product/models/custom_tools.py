# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.translate import _
from openerp.osv.osv import except_osv


# WIP : Syncronization disabled
# def _intercompany_trade_update_multicompany(
#        pool, cr, uid, supplier_product_ids, context=None):
#    """
#    This function update supplierinfo in customer database,
#    depending of changes in supplier database, for all intercompany trade
#    define.
#    Call this function when there is a change of product price,
#    product taxes, partner pricelist, etc...
#    :supplier_product_ids (list of ids of product.product):
#        products that has been changed in the supplier database;
#    """
#    rit_obj = pool['intercompany.trade.config']
#    psi_obj = pool['product.supplierinfo']
#    for supplier_product_id in supplier_product_ids:
#        psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
#            ('supplier_product_id', '=', supplier_product_id),
#        ], context=context)
#        for psi in psi_obj.browse(
#                cr, SUPERUSER_ID, psi_ids, context=context):
#            rit_id = rit_obj.search(cr, uid, [
#                ('customer_company_id', '=', psi.company_id.id),
#                ('supplier_partner_id', '=', psi.name.id),
#            ], context=context)[0]
#            _intercompany_trade_update(
#                pool, cr, uid, rit_id, [supplier_product_id],
#                context=context)


# def _intercompany_trade_update(
#        pool, cr, uid, intercompany_trade_id, supplier_product_ids,
#        context=None):
#    """
#    This function update supplierinfo in customer database,
#    depending of changes in supplier database, depending of
#    a specific intercompany trade.
#    Call this function when there is a change of product price,
#    product taxes, partner pricelist, etc...
#    :param intercompany_trade_id (id of intercompany.trade.config):
#        intercompany trade impacted;
#    :supplier_product_ids (list of ids of product.product):
#        products that has been changed in the supplier database;
#    """
#    context = context and context or {}
#    rit_obj = pool['intercompany.trade.config']
#    psi_obj = pool['product.supplierinfo']
#    rit = rit_obj.browse(cr, uid, intercompany_trade_id, context=context)
#    if not supplier_product_ids:
#        # Global Update
#        psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
#            ('name', '=', rit.supplier_partner_id.id),
#        ], context=context)
#    else:
#        psi_ids = psi_obj.search(cr, SUPERUSER_ID, [
#            ('name', '=', rit.supplier_partner_id.id),
#            ('supplier_product_id', 'in', supplier_product_ids)
#        ], context=context)
#    ctx = context.copy()
#    ctx['active_test'] = False
#    for psi in psi_obj.browse(cr, SUPERUSER_ID, psi_ids, context=context):
#        pp_ids = psi.product_tmpl_id.product_variant_ids.ids
#        psi_vals = rit_obj._prepare_product_supplierinfo(
#            cr, SUPERUSER_ID, intercompany_trade_id,
#            psi.supplier_product_id.id, pp_ids[0], context=context)
#        psi_obj.write(
#            cr, SUPERUSER_ID, [psi.id], psi_vals, context=context)


def _get_other_product_info(
        pool, cr, uid, rit, product_id, direction, context=None):
    """
        Deliver a product id from another product id.
        Usefull to call when create (sale / purchase / invoice) line to
        create according line with correct product;

        Realize correct check if the product is not referenced.

        :param @rit : model of intercompany.trade.config
            current trade;
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
    res = {}

    pp_obj = pool['product.product']
    ppl_obj = pool['product.pricelist']
    psi_obj = pool['product.supplierinfo']

    # Get current Product
    pp = pp_obj.browse(cr, uid, product_id, context=context)

    if direction == 'in':
        # Get product supplier info (if any)
        psi_ids = psi_obj.search(cr, uid, [
            ('product_tmpl_id', '=', pp.product_tmpl_id.id),
            ('name', '=', rit.supplier_partner_id.id),
            ('company_id', '=', rit.customer_company_id.id),
        ], context=context)
        if len(psi_ids) == 0:
            raise except_osv(
                _("Product Selection Error!"),
                _("You can not add '%s' to the current Order or Invoice"
                    " because you didn't linked the product to any Supplier"
                    " Product. Please do it in the 'Intercompany Trade'"
                    " menu.") % (pp.name))

        psi = psi_obj.browse(cr, uid, psi_ids[0], context=context)
        res['product_id'] = psi.supplier_product_id.id

        # Get Supplier Sale Price
        supplier_pp = pp_obj.browse(
            cr, rit.supplier_user_id.id, psi.supplier_product_id.id,
            context=context)
        res['price_unit'] = ppl_obj._compute_intercompany_trade_prices(
            cr, rit.supplier_user_id.id, supplier_pp,
            rit.supplier_partner_id, rit.sale_pricelist_id,
            context=None)['supplier_sale_price']

    else:
        psi_ids = psi_obj.search(cr, rit.customer_user_id.id, [
            ('supplier_product_id', '=', product_id),
            ('name', '=', rit.supplier_partner_id.id),
            ('company_id', '=', rit.customer_company_id.id),
        ], context=context)
        if len(psi_ids) == 0:
            raise except_osv(
                _("Product Selection Error!"),
                _("You can not add the product '%s' to the"
                    " current Order or Invoice because the customer didn't"
                    " referenced your product. Please contact him and"
                    " say him to do it.") % (pp.name))
        psi = psi_obj.browse(
            cr, rit.customer_user_id.id, psi_ids[0], context=context)
        customer_pp_ids = pp_obj.search(cr, rit.customer_user_id.id, [
            ('company_id', '=', rit.customer_company_id.id),
            ('product_tmpl_id', '=', psi.product_tmpl_id.id),
        ], context=context)
        if len(customer_pp_ids) == 0:
            # TODO improve me with V8.0 ORM, using variants fields
            # psi.product_tmpl_id.product_variant_ids.ids
            customer_pp_ids = pp_obj.search(cr, rit.customer_user_id.id, [
                ('company_id', '=', rit.customer_company_id.id),
                ('product_tmpl_id', '=', psi.product_tmpl_id.id),
                ('active', '=', False),
            ], context=context)
        if len(customer_pp_ids) != 1:
            raise except_osv(
                _("Product Selection Error!"),
                _("You can not add '%s' to the current Order or Invoice"
                    " because the customer referenced many variants of"
                    "  this template. Please contact him and say him to add"
                    "  the product manually to his Order or Invoice .") % (
                        pp.name))
        res['product_id'] = customer_pp_ids[0]
    return res
