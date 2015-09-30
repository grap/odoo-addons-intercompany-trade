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


class res_ompany(Model):
    _inherit = 'res.company'

    _columns = {
        'intercompany_trade_account_id': fields.many2one(
            'account.account', domain="["
            "('company_id', '=', fiscal_company),"
            "('is_intercompany_trade_fiscal_company', '=', True)]",
            string='Account for Intercompany Trade',
            help="Set an account if there"
            " is Intercompany Trade with this company. This setting will have"
            " an effect only in trade between two company that belong to"
            " the same fiscal company."),
    }
