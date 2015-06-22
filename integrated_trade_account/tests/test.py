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

        # Get ids from xml_ids
        self.rit_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_base', 'integrated_trade')[1]

    def test_01_vat_association_bad(self):
        """[Functional Test] Associate products with incompatible VAT"""
        """ must fail"""
        pass

    def test_02_vat_association_good(self):
        """[Functional Test] Associate products with incompatible VAT"""
        """ must succeed"""
        pass


    def test_03_create_invoice_in(self):
        """Create an In Invoice with correct VAT, must create """

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
