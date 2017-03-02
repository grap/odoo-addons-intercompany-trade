# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
