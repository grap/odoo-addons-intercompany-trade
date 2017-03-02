# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class account_account(Model):
    _inherit = 'account.account'

    _columns = {
        'is_intercompany_trade_fiscal_company': fields.boolean(
            string='Integrated Trade : Receivable / Payable Account',
            help="Check this box for integrated Trade into 2 companies of"
            " the same cooperative for customer and supplier.")
    }

    # Constraints Section
    def _check_is_intercompany_trade_fiscal_company(
            self, cr, uid, ids, context=None):
        for aa in self.browse(cr, uid, ids, context=context):
            if aa.type != 'receivable' and\
                    aa.is_intercompany_trade_fiscal_company:
                return False
        return True

    _constraints = [
        (
            _check_is_intercompany_trade_fiscal_company,
            "Only Accounts type 'Receivable' can be flaged as 'Internal"
            " Account for Intercompany Trade'",
            ['is_intercompany_trade_fiscal_company', 'type']),
    ]
