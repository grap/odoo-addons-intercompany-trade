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
        self.ai_obj = self.registry('account.invoice')
        self.ail_obj = self.registry('account.invoice.line')
        self.pitc_obj = self.registry('product.integrated.trade.catalog')
        self.rit_obj = self.registry('res.integrated.trade')
        self.itwlp_obj = self.registry('integrated.trade.wizard.link.product')

        # Get ids from xml_ids
        self.rit_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_base', 'integrated_trade')[1]
        self.rit = self.rit_obj.browse(self.cr, self.uid, self.rit_id)

        self.product_supplier_service_25_incl =\
            self.imd_obj.get_object_reference(
                self.cr, self.uid, 'integrated_trade_account',
                'product_supplier_service_25_incl')[1]

        self.product_supplier_service_10_incl =\
            self.imd_obj.get_object_reference(
                self.cr, self.uid, 'integrated_trade_account',
                'product_supplier_service_10_incl')[1]

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

        self.supplier_user_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_base', 'supplier_user')[1]

        self.purchase_journal_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_account', 'customer_journal_purchase')[1]

        self.customer_account_payable_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_account', 'customer_account_payable')[1]

        self.product_uom_unit_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'product', 'product_uom_unit')[1]

        

#    def test_01_vat_association_bad(self):
#        """[Functional Test] Associate products with incompatible VAT"""
#        """ must fail"""
#        cr, uid = self.cr, self.customer_user_id

#        # Associate with bad VAT 
#        # (Customer Service VAT 10% EXCLUDED - Supplier Service VAT 25%)
#        active_id = self.pitc_obj.search(cr, uid, [(
#            'supplier_product_id', '=',
#            self.product_supplier_service_25_incl)])[0]

#        itwlp_id = self.itwlp_obj.create(cr, uid, {
#            'customer_product_id': self.product_customer_service_10_excl,
#        }, context={'active_id': active_id})
#        with self.assertRaises(except_osv):
#            self.itwlp_obj.link_product(cr, uid, [itwlp_id])

#        # Associate with bad VAT 
#        # (Customer Product with no VAT - Supplier Service VAT 25%)
#        active_id = self.pitc_obj.search(cr, uid, [(
#            'supplier_product_id', '=',
#            self.product_supplier_service_25_incl)])[0]

#        itwlp_id = self.itwlp_obj.create(cr, uid, {
#            'customer_product_id': self.product_customer_apple,
#        }, context={'active_id': active_id})
#        with self.assertRaises(except_osv):
#            self.itwlp_obj.link_product(cr, uid, [itwlp_id])

#    def test_02_vat_association_good(self):
#        """[Functional Test] Associate products with compatible VAT"""
#        """ must succeed (Incl / excl)"""
#        cr, uid = self.cr, self.customer_user_id
#        # Associate with good VAT 
#        # (Customer Service VAT 10% EXCLUDED - Supplier Service VAT 10% INCLUDE)
#        active_id = self.pitc_obj.search(cr, uid, [(
#            'supplier_product_id', '=',
#            self.product_supplier_service_10_incl)])[0]

#        itwlp_id = self.itwlp_obj.create(cr, uid, {
#            'customer_product_id': self.product_customer_service_10_excl,
#        }, context={'active_id': active_id})
#        res = self.itwlp_obj.link_product(cr, uid, [itwlp_id])
#        self.assertEqual(
#            res, True,
#            """Associate a Customer Product with 10% Excl VAT to """
#            """ a supplier Product with 10% Incl VAT"""
#            """ must succeed.""")

    def test_03_create_invoice_in(self):
        """Create an In Invoice (Supplier Invoice) by the customer"""
        """ must create an Out Invoice"""
        cr, cus_uid = self.cr, self.customer_user_id #, self.supplier_user_id

        # Associate a product
        active_id = self.pitc_obj.search(cr, cus_uid, [(
            'supplier_product_id', '=',
            self.product_supplier_service_10_excl)])[0]

        itwlp_id = self.itwlp_obj.create(cr, cus_uid, {
            'customer_product_id': self.product_customer_service_10_excl,
        }, context={'active_id': active_id})
        res = self.itwlp_obj.link_product(cr, cus_uid, [itwlp_id])

        # Create a Invoice
        context = {'type': 'in_invoice'}
        vals = self.ai_obj.default_get(
            cr, cus_uid, ['currency_id', 'journal_id'],
            context=context)
        vals.update({
                'partner_id': self.rit.supplier_partner_id.id,
                'account_id': self.customer_account_payable_id,
            })

        cus_ai_id = self.ai_obj.create(cr, cus_uid, vals, context=context)

        # CHECKS
        SUPER_ai = self.ai_obj.browse(cr, self.uid, cus_ai_id)
        SUPER_ai_other = SUPER_ai.integrated_trade_account_invoice_id
        self.assertNotEqual(
            SUPER_ai_other.id, False,
            """Create a Invoice must create another invoice.""")

        self.assertEqual(
            SUPER_ai_other.type, 'out_invoice',
            """Create an In Invoice must create an Out invoice.""")

        # Create a Invoice Line
        vals = self.ail_obj.default_get(
            cr, cus_uid, ['account_id', 'quantity'],
            context=context)
        vals.update({
            'name': 'TEST',
            'product_id': self.product_customer_service_10_excl,
            'uos_id': self.product_uom_unit_id,
        })

        cus_ail_id = self.ail_obj.create(cr, cus_uid, vals, context=context)

        # CHECKS
        SUPER_ail = self.ail_obj.browse(cr, self.uid, cus_ail_id)
        SUPER_ail_other = SUPER_ail.integrated_trade_account_invoice_line_id
        self.assertNotEqual(
            SUPER_ail_other.id, False,
            """Create a Invoice Line must create another invoice Line.""")
