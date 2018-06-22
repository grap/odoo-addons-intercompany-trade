# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import Warning as UserError
from openerp.tests.common import TransactionCase

from ..custom_tools import _get_other_product_info


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

        # Get Registries
        self.imd_obj = self.registry('ir.model.data')
        self.rit_obj = self.registry('intercompany.trade.config')
        self.rp_obj = self.registry('res.partner')
        self.pitc_obj = self.registry('product.intercompany.trade.catalog')
        self.pp_obj = self.registry('product.product')
        self.itwlp_obj = self.registry(
            'intercompany.trade.wizard.link.product')

        # Get ids from xml_ids
        self.rit_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_base', 'intercompany_trade')[1]
        self.supplier_banana_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_product', 'product_supplier_banana')[1]
        self.supplier_apple_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_product', 'product_supplier_apple')[1]
        self.customer_apple_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_product', 'product_customer_apple')[1]
        self.pricelist_discount_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_product', 'pricelist_discount')[1]

        self.customer_user_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_base', 'customer_user')[1]
        self.supplier_user_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_base', 'supplier_user')[1]

        self.precision = self.env['decimal.precision'].precision_get(
            'Intercompany Trade Product Price')

    # Test Section
    def test_01_product_association(self):
        """[Functional Test] Check if associate a product create a
        product supplierinfo"""
        cr, uid = self.cr, self.customer_user_id

        # Associate with bad product (customer apple - supplier banana)
        active_id = self.pitc_obj.search(cr, uid, [
            ('supplier_product_id', '=', self.supplier_banana_id)])[0]

        itwlp_id = self.itwlp_obj.create(cr, uid, {
            'customer_product_id': self.customer_apple_id,
        }, context={'active_id': active_id})
        self.itwlp_obj.link_product(cr, uid, [itwlp_id])

        pp_customer_apple = self.pp_obj.browse(
            cr, uid, self.customer_apple_id)

        pp_supplier_banana = self.pp_obj.browse(
            cr, self.supplier_user_id, self.supplier_banana_id)

        self.assertEqual(
            len(pp_customer_apple.seller_ids), 1,
            """Associate a Customer Product to a Supplier Product must"""
            """ create a Product Supplierinfo.""")

        self.assertEqual(
            pp_customer_apple.seller_ids[0].intercompany_trade_price,
            round(pp_supplier_banana.list_price, self.precision),
            """Associate a Customer Product to a Supplier Product must"""
            """ set as intercompany trade price in customer database the"""
            """ sale price of the supplier product.""")

        self.assertEqual(
            pp_customer_apple.seller_ids[0].pricelist_ids[0].price,
            round(pp_supplier_banana.list_price, self.precision),
            """Associate a Customer Product to a Supplier Product must"""
            """ set as intercompany trade price in customer database the"""
            """ sale price of the supplier product in items list.""")

        # Reassociate with correct product (customer apple - supplier apple)
        # Must Fail
        active_id_2 = self.pitc_obj.search(cr, uid, [
            ('supplier_product_id', '=', self.supplier_apple_id)])[0]

        itwlp_id = self.itwlp_obj.create(cr, uid, {
            'customer_product_id': self.customer_apple_id,
        }, context={'active_id': active_id_2})
        with self.assertRaises(UserError):
            # this must fail
            self.itwlp_obj.link_product(cr, uid, [itwlp_id])

        # Remove association
        self.pitc_obj.button_unlink_product(cr, uid, [active_id])
        pp_customer_apple = self.pp_obj.browse(
            cr, uid, self.customer_apple_id)
        self.assertEqual(
            len(pp_customer_apple.seller_ids), 0,
            """Unlink a Customer Product must delete"""
            """ The Product Supplierinfo.""")

#    def test_02_pricelist_change(self):
#        """[Functional Test] Check if change pricelist in supplier database
#        change price in customer database"""
#        cr, uid = self.cr, self.customer_user_id

#        # Associate with product (customer apple - supplier apple)
#        active_id = self.pitc_obj.search(cr, uid, [
#            ('supplier_product_id', '=', self.supplier_apple_id)])[0]

#        itwlp_id = self.itwlp_obj.create(cr, uid, {
#            'customer_product_id': self.customer_apple_id,
#        }, context={'active_id': active_id})
#        self.itwlp_obj.link_product(cr, uid, [itwlp_id])

#        # Change customer pricelist
#        rit = self.rit_obj.browse(cr, self.supplier_user_id, self.rit_id)
#        self.rp_obj.write(
#            cr, self.supplier_user_id, [rit.customer_partner_id.id], {
#                'property_product_pricelist': self.pricelist_discount_id})

#        # check if price has changed
#        pp_customer_apple = self.pp_obj.browse(
#            cr, uid, self.customer_apple_id)

#        pp_supplier_apple = self.pp_obj.browse(
#            cr, self.supplier_user_id, self.supplier_apple_id)

#        self.assertEqual(
#            pp_customer_apple.seller_ids[0].intercompany_trade_price,
#            pp_supplier_apple.list_price - 0.1,
#            """Change pricelist in supplier database must change prices"""
#            """ in customer database.""")

#    def test_03_price_change(self):
#        """[Functional Test] Check if change price in supplier database
#        change price in customer database"""
#        cr, uid = self.cr, self.customer_user_id

#        # Associate with product (customer apple - supplier apple)
#        active_id = self.pitc_obj.search(cr, uid, [
#            ('supplier_product_id', '=', self.supplier_apple_id)])[0]

#        itwlp_id = self.itwlp_obj.create(cr, uid, {
#            'customer_product_id': self.customer_apple_id,
#        }, context={'active_id': active_id})
#        self.itwlp_obj.link_product(cr, uid, [itwlp_id])

#        # Change Price in supplier database
#        self.pp_obj.write(
#            cr, self.supplier_user_id, [self.supplier_apple_id], {
#                'list_price': 10})

#        # check if price has changed
#        pp_customer_apple = self.pp_obj.browse(
#            cr, uid, self.customer_apple_id)

#        self.assertEqual(
#            pp_customer_apple.seller_ids[0].intercompany_trade_price,
#            10,
#            """Change price in supplier database must change prices"""
#            """ in customer database.""")

#    def test_04_product_update(self):
#        """[Functional Test] Check if change a supplier product update the
#        product supplierinfo in the customer database"""
#        cr, uid = self.cr, self.uid

#        # Associate with product (customer apple - supplier apple)
#        active_id = self.pitc_obj.search(cr, uid, [
#            ('supplier_product_id', '=', self.supplier_apple_id)])[0]

#        itwlp_id = self.itwlp_obj.create(cr, uid, {
#            'customer_product_id': self.customer_apple_id,
#        }, context={'active_id': active_id})
#        self.itwlp_obj.link_product(cr, uid, [itwlp_id])

#        # Change name in the supplier product
#        new_name = 'Supplier New Name'
#        self.pp_obj.write(cr, uid, [self.supplier_apple_id], {
#            'name': new_name})

#        pp_c_apple = self.pp_obj.browse(cr, uid, self.customer_apple_id)
#        self.assertEqual(
#            pp_c_apple.seller_ids[0].product_name,
#            new_name,
#            """Update the name of the supplier product must update the"""
#            """ Supplier Info of the customer Product.""")

#        # Change code in the supplier product
#        new_code = '[SUPPLIER-NEW-CODE]'
#        self.pp_obj.write(cr, uid, [self.supplier_apple_id], {
#            'default_code': new_code})

#        pp_c_apple = self.pp_obj.browse(cr, uid, self.customer_apple_id)
#        self.assertEqual(
#            pp_c_apple.seller_ids[0].product_code,
#            new_code,
#            """Update the code of the supplier product must update the"""
#            """ Supplier Info of the customer Product.""")

    def test_05_product_association_recovery(self):
        """
            - Get supplier product from customer product
            - Get Customer Product from supplier Product"""
        cr, cus_uid, sup_uid =\
            self.cr, self.customer_user_id, self.supplier_user_id
        rit = self.rit_obj.browse(cr, cus_uid, self.rit_id)

        # Associate a product
        active_id = self.pitc_obj.search(cr, cus_uid, [
            ('supplier_product_id', '=', self.supplier_apple_id)])[0]

        itwlp_id = self.itwlp_obj.create(cr, cus_uid, {
            'customer_product_id': self.customer_apple_id,
        }, context={'active_id': active_id})
        self.itwlp_obj.link_product(cr, cus_uid, [itwlp_id])

        res = _get_other_product_info(
            self.pp_obj.pool, cr, cus_uid, rit, self.customer_apple_id, 'in',
            context=None)
        self.assertEqual(
            self.supplier_apple_id,
            res['product_id'],
            """Function to recovery supplier product info from customer"""
            """ product doesn't work.""")

        res = _get_other_product_info(
            self.pp_obj.pool, cr, sup_uid, rit, self.supplier_apple_id, 'out',
            context=None)
        self.assertEqual(
            self.customer_apple_id,
            res['product_id'],
            """Function to recovery customer product info from supplier"""
            """ product doesn't work.""")
