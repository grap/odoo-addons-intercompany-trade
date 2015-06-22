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

from openerp.osv.osv import except_osv
from openerp.tests.common import TransactionCase


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

        # Get Registries
        self.imd_obj = self.registry('ir.model.data')
        self.pitc_obj = self.registry('product.integrated.trade.catalog')
        self.itwlp_obj = self.registry('integrated.trade.wizard.link.product')

        # Get ids from xml_ids
#        self.rit_id = self.imd_obj.get_object_reference(
#            self.cr, self.uid,
#            'integrated_trade_base', 'integrated_trade')[1]

        self.product_supplier_service_25_incl =\
            self.imd_obj.get_object_reference(
                self.cr, self.uid, 'integrated_trade_account',
                'product_supplier_service_25_incl')[1]

        self.product_supplier_service_10_excl =\
            self.imd_obj.get_object_reference(
                self.cr, self.uid, 'integrated_trade_account',
                'product_supplier_service_10_excl')[1]

        self.product_customer_service_10_excl =\
            self.imd_obj.get_object_reference(
                self.cr, self.uid, 'integrated_trade_account',
                'product_customer_service_10_excl')[1]

        self.product_customer_apple =\
            self.imd_obj.get_object_reference(
                self.cr, self.uid, 'integrated_trade_product',
                'product_customer_apple')[1]

        self.customer_user_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_base', 'customer_user')[1]

    def test_01_vat_association_bad(self):
        """[Functional Test] Associate products with incompatible VAT"""
        """ must fail"""
        cr, uid = self.cr, self.customer_user_id

        # Associate with bad VAT 
        # (Customer Service VAT 10% EXCLUDED - Supplier Service VAT 25%)
        active_id = self.pitc_obj.search(cr, uid, [(
            'supplier_product_id', '=',
            self.product_supplier_service_25_incl)])[0]

        itwlp_id = self.itwlp_obj.create(cr, uid, {
            'customer_product_id': self.product_customer_service_10_excl,
        }, context={'active_id': active_id})
        with self.assertRaises(except_osv):
            self.itwlp_obj.link_product(cr, uid, [itwlp_id])

        # Associate with bad VAT 
        # (Customer Product with no VAT - Supplier Service VAT 25%)
        active_id = self.pitc_obj.search(cr, uid, [(
            'supplier_product_id', '=',
            self.product_supplier_service_25_incl)])[0]

        itwlp_id = self.itwlp_obj.create(cr, uid, {
            'customer_product_id': self.product_customer_apple,
        }, context={'active_id': active_id})
        with self.assertRaises(except_osv):
            self.itwlp_obj.link_product(cr, uid, [itwlp_id])

    def test_02_vat_association_good(self):
        """[Functional Test] Associate products with compatible VAT"""
        """ must succeed (excluded both)"""
        cr, uid = self.cr, self.customer_user_id
        # Associate with bad VAT 
        # (Customer Service VAT 10% EXCLUDED - Supplier Service VAT 10% EXCLUDED)
        active_id = self.pitc_obj.search(cr, uid, [(
            'supplier_product_id', '=',
            self.product_supplier_service_10_excl)])[0]

        itwlp_id = self.itwlp_obj.create(cr, uid, {
            'customer_product_id': self.product_customer_service_10_excl,
        }, context={'active_id': active_id})
        res = self.itwlp_obj.link_product(cr, uid, [itwlp_id])
        self.assertEqual(
            res, True,
            """Associate a Customer Product with 10% Excl VAT to """
            """ a supplier Product with 10% Excl VAT"""
            """ must succeed.""")

#    def test_03_create_invoice_in(self):
#        """Create an In Invoice must create Out Invoice"""

#    # Test Section
#    def test_XX_product_association(self):
#        """[Functional Test] Check if associate a product create a
#        product supplierinfo"""
#        cr, uid = self.cr, self.customer_user_id

#        self.assertEqual(
#            pp_c_apple.seller_ids[0].product_code,
#            new_code,
#            """Update the code of the supplier product must update the"""
#            """ Supplier Info of the customer Product.""")
