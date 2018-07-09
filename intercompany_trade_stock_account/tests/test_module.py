# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
#        self.invoice_obj = self.env['account.invoice']
#        self.sale_order = self.env.ref('intercompany_trade_sale.sale_order')
#        self.config = self.env.ref(
#            'intercompany_trade_base.intercompany_trade')
#        self.supplier_user = self.env.ref(
#            'intercompany_trade_base.supplier_user')

#    def test_01_invoice_sale_order(self):
#        self.sale_order.sudo(self.supplier_user).write({
#            'partner_id': self.config.customer_partner_id.id,
#            'partner_invoice_id': self.config.customer_partner_id.id,
#        })
#        res = self.sale_order.sudo(self.supplier_user).action_invoice_create()
#        invoice = self.invoice_obj.browse(res)
#        line = invoice.invoice_line[0]
#        self.assertNotEqual(
#            line.intercompany_trade_account_invoice_line_id, False,
#            "Invoicing an Intercompany Trade sale order should generate"
#            " invoice lines with related invoice id.")
