# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# flake8: noqa
# TODO FIXME


from openerp.exceptions import Warning as UserError
from openerp.tests.common import TransactionCase


class Test(TransactionCase):

    # Overload Section
    def setUp(self):
        super(Test, self).setUp()

        # Get Registries
        self.invoice_obj = self.env['account.invoice']
        self.invoice_line_obj = self.env['account.invoice.line']
        self.product_obj = self.env['product.product']
        self.catalog_obj = self.env['product.intercompany.trade.catalog']
        self.config_obj = self.env['intercompany.trade.config']
        self.link_obj = self.env['intercompany.trade.wizard.link.product']

        # Get ids from xml_ids
        self.config = self.env.ref(
            'intercompany_trade_base.intercompany_trade')

        self.customer_user = self.env.ref(
            'intercompany_trade_base.customer_user')
        self.supplier_user = self.env.ref(
            'intercompany_trade_base.supplier_user')

        self.product_uom_unit = self.env.ref(
            'product.product_uom_unit')

        self.product_customer_apple = self.env.ref(
            'intercompany_trade_product.product_customer_apple')

        self.customer_product = self.env.ref(
            'intercompany_trade_product.product_customer_ref')
        self.supplier_product = self.env.ref(
            'intercompany_trade_product.product_supplier_ref')


        self.product_supplier_service_25_incl = self.env.ref(
            'intercompany_trade_account.product_supplier_service_25_incl')
        self.product_supplier_service_10_incl = self.env.ref(
            'intercompany_trade_account.product_supplier_service_10_incl')
        self.product_supplier_service_10_excl = self.env.ref(
            'intercompany_trade_account.product_supplier_service_10_excl')
        self.product_customer_service_10_excl = self.env.ref(
            'intercompany_trade_account.product_customer_service_10_excl')
        self.purchase_journal = self.env.ref(
            'intercompany_trade_account.customer_journal_purchase')
        self.customer_account_payable = self.env.ref(
            'intercompany_trade_account.customer_account_payable')
        self.supplier_account_receivable = self.env.ref(
            'intercompany_trade_account.supplier_account_receivable')

    def test_01_vat_association_bad(self):
        """
            [Functional Test] Associate products with incompatible VAT
            must fail
        """
        # Associate with bad VAT
        # (Customer Service VAT 10% EXCLUDED - Supplier Service VAT 25%)
        catalog = self.catalog_obj.sudo(self.customer_user).search([(
            'supplier_product_id', '=',
            self.product_supplier_service_25_incl.id)])

        link = self.link_obj.with_context(active_id=catalog.id).sudo(
            self.customer_user).create({
                'customer_product_id':
                self.product_customer_service_10_excl.id})
        with self.assertRaises(UserError):
            link.sudo(self.customer_user).link_product()

        # Associate with bad VAT
        # (Customer Product with no VAT -> Supplier Service VAT 25%)
        catalog = self.catalog_obj.sudo(self.customer_user).search([(
            'supplier_product_id', '=',
            self.product_supplier_service_25_incl.id)])

        link = self.link_obj.with_context(active_id=catalog.id).sudo(
            self.customer_user).create({
                'customer_product_id': self.product_customer_apple.id})
        with self.assertRaises(UserError):
            link.sudo(self.customer_user).link_product()

    def test_02_vat_association_good(self):
        """
            [Functional Test] Associate products with compatible VAT
            must succeed (Incl / excl)
        """
        cr, uid = self.cr, self.customer_user.id
        # Associate with good VAT
        # (Customer Service VAT 10% EXCLUDED
        # -> Supplier Service VAT 10% INCLUDE)

        catalog = self.catalog_obj.sudo(self.customer_user).search([(
            'supplier_product_id', '=',
            self.product_supplier_service_10_incl.id)])

        link = self.link_obj.with_context(active_id=catalog.id).sudo(
            self.customer_user).create({
                'customer_product_id':
                self.product_customer_service_10_excl.id})
        try:
            link.sudo(self.customer_user).link_product()
        except:
            self.assertTrue(
                "Associate a Customer Product with 10% Excl VAT to  a supplier"
                " Product with 10% Incl VAT must succeed.")


    def test_03_create_invoice_out(self):
        """
            Create an Out Invoice (Customer Invoice) by the supplier
            must create an In Invoice
        """
        # Create a Out Invoice
        vals = self.invoice_obj.sudo(self.supplier_user).with_context(
            type='out_invoice', tracking_disable=True).default_get(
                ['currency_id', 'journal_id'])
        vals.update(self.invoice_obj.sudo(
            self.supplier_user).onchange_partner_id(
                'out_type', self.config.customer_partner_id.id)['value'])
        vals.update({
            'partner_id': self.config.customer_partner_id.id,
        })

        supplier_invoice = self.invoice_obj.sudo(
            self.supplier_user).with_context(
                type='out_invoice', tracking_disable=True).create(vals)

        customer_invoice = self.invoice_obj.sudo(self.customer_user).browse(
            supplier_invoice.intercompany_trade_account_invoice_id)

        self.assertNotEqual(
            customer_invoice.id, False,
            "Create an Out Invoice must create another Invoice.")

        self.assertEqual(
            customer_invoice.type, 'in_invoice',
            "Create an In Invoice must create an Out invoice.")

        # Create a Invoice Line
        vals = self.invoice_line_obj.sudo(self.supplier_user).with_context(
            type='out_invoice', tracking_disable=True).default_get(
                ['account_id', 'quantity'])
        vals.update({
            'invoice_id': supplier_invoice.id,
            'name': 'Supplier Invoice Line Test',
            'product_id': self.supplier_product.id,
            'uos_id': self.product_uom_unit.id,
            'price_unit': 50,
            'quantity': 1,
        })

        supplier_invoice_line = self.invoice_line_obj.sudo(
            self.supplier_user).create(vals)

        # Checks creation of the according Invoice Line
        customer_invoice_line = self.invoice_line_obj.sudo(
            self.customer_user).browse(
                supplier_invoice_line.
                intercompany_trade_account_invoice_line_id)

        self.assertNotEqual(
            supplier_invoice_line.id, False,
            "Create an Invoice Line must create another invoice Line.")

        # Update Customer Invoice Line (change price = must fail)
        with self.assertRaises(UserError):
            customer_invoice_line.sudo(
                self.customer_user).write({'price_unit': 10})

        # Update Supplier Invoice Line (change price should update other line)
        supplier_invoice_line.sudo(
            self.supplier_user).write({'price_unit': 200})

        self.assertNotEqual(
            customer_invoice_line.price_unit, 100,
            "Updating price unit on supplier invoice line should impact."
            " the according customer invoice line")

        # Update Supplier Invoice Line (change product = must fail)
        with self.assertRaises(UserError):
            supplier_invoice_line.sudo(
                self.supplier_user).write({
                    'product_id': self.product_supplier_service_25_incl.id})

        # Unlink Supplier Invoice line (must unlink according customer line)
        supplier_invoice_line.sudo(self.supplier_user).unlink()
        count = self.invoice_line_obj.search(
            [('invoice_id', '=', customer_invoice.id)])

        self.assertEqual(
            len(count), 0,
            "Delete supplier Invoice Line must delete according"
            " customer Invoice Line.")
