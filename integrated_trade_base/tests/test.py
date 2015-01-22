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

from openerp.tests.common import TransactionCase


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

#        # Get Registries
        self.imd_obj = self.registry('ir.model.data')
        self.rit_obj = self.registry('res.integrated.trade')
        self.rc_obj = self.registry('res.company')

        # Get ids from xml_ids
        self.integrated_trade_id = self.imd_obj.get_object_reference(
            self.cr, self.uid, 'integrated_trade_base', 'integrated_trade')[1]
        self.customer_company_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_base', 'customer_company')[1]
        self.supplier_company_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'integrated_trade_base', 'supplier_company')[1]

    # Test Section
    def test_01_create_reverse_integrated_trade(self):
        """[Functional Test] Check if create integrated trade with companies
        inverse of an existing integrated trade affect correctly partners"""
        cr, uid = self.cr, self.uid
        rit_id = self.rit_obj.create(cr, uid, {
            'name': 'Reverse Integrated Trade',
            'customer_company_id': self.supplier_company_id,
            'supplier_company_id': self.customer_company_id,
        })
        old_rit = self.rit_obj.browse(cr, uid, self.integrated_trade_id)
        new_rit = self.rit_obj.browse(cr, uid, rit_id)

        self.assertEqual(
            old_rit.customer_partner_id.id, new_rit.supplier_partner_id.id,
            "Create a Reverse Integrated Trade must reuse existing customer.")

        self.assertEqual(
            old_rit.supplier_partner_id.id, new_rit.customer_partner_id.id,
            "Create a Reverse Integrated Trade must reuse existing supplier.")

    # Test Section
    def test_02_update_company_update_partner(self):
        """[Functional Test] Check if update company data change the data
        of the partner associated"""
        cr, uid = self.cr, self.uid
        new_street = 'NEW STREET'
        self.rc_obj.write(cr, uid, [self.customer_company_id], {
            'street': new_street})
        rit = self.rit_obj.browse(cr, uid, self.integrated_trade_id)

        self.assertEqual(
            rit.supplier_partner_id.street, new_street,
            "Update a company must change the associated partner.")
