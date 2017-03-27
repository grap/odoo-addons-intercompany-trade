# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_intercompany_trade_fiscal_company = fields.Boolean(
        string='Integrated Trade : Receivable / Payable Account',
        help="Check this box for integrated Trade into 2 companies of"
        " the same cooperative for customer and supplier.")

    # Constraints Section
    @api.constrains('is_intercompany_trade_fiscal_company', 'type')
    def _check_is_intercompany_trade_fiscal_company(self):
        for account in self:
            if account.type != 'receivable' and\
                    account.is_intercompany_trade_fiscal_company:
                raise UserError(_(
                    "Only Accounts type 'Receivable' can be flaged as"
                    " 'Internal Account for Intercompany Trade'"))
