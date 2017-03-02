# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

        # Get Registries
        self.imd_obj = self.registry('ir.model.data')
        self.rit_obj = self.registry('intercompany.trade.config')
        self.rc_obj = self.registry('res.company')

        # Get ids from xml_ids
        self.intercompany_trade_id = self.imd_obj.get_object_reference(
            self.cr, self.uid, 'intercompany_trade_base',
            'intercompany_trade')[1]
        self.customer_company_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_base', 'customer_company')[1]
        self.supplier_company_id = self.imd_obj.get_object_reference(
            self.cr, self.uid,
            'intercompany_trade_base', 'supplier_company')[1]

    # Test Section
    def test_01_create_reverse_intercompany_trade(self):
        """[Functional Test] Check if create intercompany trade with companies
        inverse of an existing intercompany trade affect correctly partners"""
        cr, uid = self.cr, self.uid
        rit_id = self.rit_obj.create(cr, uid, {
            'name': 'Reverse Intercompany Trade',
            'customer_company_id': self.supplier_company_id,
            'supplier_company_id': self.customer_company_id,
        })
        old_rit = self.rit_obj.browse(cr, uid, self.intercompany_trade_id)
        new_rit = self.rit_obj.browse(cr, uid, rit_id)

        self.assertEqual(
            old_rit.customer_partner_id.id, new_rit.supplier_partner_id.id,
            "Create a Reverse Intercompany Trade must reuse customer.")

        self.assertEqual(
            old_rit.supplier_partner_id.id, new_rit.customer_partner_id.id,
            "Create a Reverse Intercompany Trade must reuse supplier.")

    # Test Section
    def test_02_update_company_update_partner(self):
        """[Functional Test] Check if update company data change the data
        of the partner associated"""
        cr, uid = self.cr, self.uid
        new_street = 'NEW STREET'
        self.rc_obj.write(cr, uid, [self.customer_company_id], {
            'street': new_street})
        rit = self.rit_obj.browse(cr, uid, self.intercompany_trade_id)

        self.assertEqual(
            rit.customer_partner_id.street, new_street,
            "Update a company must change the associated partner.")
