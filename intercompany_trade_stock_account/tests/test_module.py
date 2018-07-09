# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        self.module_obj = self.env['ir.module.module']
        self.partner_obj = self.env['res.partner']
        self.picking_obj = self.env['stock.picking']
        self.move_obj = self.env['stock.move']
        self.invoice_obj = self.env['account.invoice']
        self.wizard_obj = self.env['stock.invoice.onshipping']
        self.supplier_product = self.env.ref(
            'intercompany_trade_account.product_supplier_ref_stock')
        self.config = self.env.ref(
            'intercompany_trade_base.intercompany_trade')
        self.supplier_user = self.env.ref(
            'intercompany_trade_base.supplier_user')
        self.unit_uom = self.env.ref('product.product_uom_unit')
        self.warehouse = self.env.ref(
            'intercompany_trade_stock.supplier_stock_warehouse')
        self.pricelist = self.env.ref(
            'intercompany_trade_product.sale_pricelist')
        self.picking_type = self.warehouse.out_type_id

    def test_01_invoice_stock_picking(self):
        """[Functional Test] Check if invoicing stock picking
        create correct intercompany trade invoice"""
        # this test uses stock.picking.type
        # if product_fiscal_company is installed, company_id is added
        # and so ir.rule contains company_id, but at this step
        # this field is not in the model, so an error is raised
        # in openerp/osv/expression.py #830
        # to avoid this bug, we prevent running this this if
        # product_fiscal_company is installed.
        if not self.module_obj.search([
                ('name', '=', 'product_fiscal_company'),
                ('state', '=', 'installed')]):
            self._test_01_invoice_stock_picking()
        else:
            _logger.info(
                "test skipped, will be run later in"
                " intercompany_trade_fiscal_company")

    def _test_01_invoice_stock_picking(self):
        partner = self.partner_obj.sudo(self.supplier_user).browse(
            self.config.customer_partner_id.id)
        partner.property_product_pricelist = self.pricelist.id
        picking = self.picking_obj.sudo(self.supplier_user).create({
            'partner_id': self.config.customer_partner_id.id,
            'invoice_state': '2binvoiced',
            'picking_type_id': self.picking_type.id,
        })
        self.move_obj.sudo(self.supplier_user).create({
            'picking_id': picking.id,
            'product_id': self.supplier_product.id,
            'product_uom_qty': 10,
            'product_uom': self.unit_uom.id,
            'name': 'Move Line Test',
            'invoice_state': '2binvoiced',
            'location_id': self.picking_type.default_location_src_id.id,
            'location_dest_id': self.picking_type.default_location_dest_id.id,
        })
        wizard = self.wizard_obj.sudo(self.supplier_user).with_context(
            active_ids=[picking.id]).create({})
        res = wizard.create_invoice()
        invoice = self.invoice_obj.browse(res)
        line = invoice.invoice_line[0]
        self.assertNotEqual(
            line.intercompany_trade_account_invoice_line_id, False,
            "Invoicing an Intercompany Trade stock picking should generate"
            " invoice lines with related invoice id.")
        # TODO Test if journal is correct
