# -*- encoding: utf-8 -*-
##############################################################################
#
#    Fiscal Company for Fiscal Company Module for Odoo
#    Copyright (C) 2015 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model


class account_account(Model):
    _inherit = 'account.account'

    _columns = {
        'is_intercompany_trade_fiscal_company': fields.boolean(
            string='Is an Internal Account for Intercompany Trade')
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
