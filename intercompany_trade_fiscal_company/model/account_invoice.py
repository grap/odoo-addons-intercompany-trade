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

from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class AccountInvoice(Model):
    _inherit = 'account.invoice'

    def create(self, cr, uid, vals, context=None):
        rp_obj = self.pool['res.partner']
        aj_obj = self.pool['account.journal']
        rp = rp_obj.browse(cr, uid, vals['partner_id'], context=context)

        if rp.intercompany_trade:
            transaction_type = False
            aj = aj_obj.browse(
                cr, uid, int(vals['journal_id']), context=context)
            if aj.type in ('sale'):
                transaction_type = 'out'
            elif aj.type in ('purchase'):
                transaction_type = 'in'
            rit = self._get_intercompany_trade_by_partner_company_type(
                cr, uid, rp.id, rp.company_id.id, transaction_type,
                context=context)
            if rit.same_fiscal_mother_company:

                if aj.type in ('sale'):
                    vals['journal_id'] = rit.sale_journal_id.id
                elif aj.type in ('purchase'):
                    vals['journal_id'] = rit.purchase_journal_id.id

        return super(AccountInvoice, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('journal_id', False):
            for ai in self.browse(cr, uid, ids, context=context):
                if ai.intercompany_trade:
                    rit = self._get_intercompany_trade_by_partner_company_type(
                        cr, uid, ai.partner_id.id, ai.company_id.id, ai.type,
                        context=context)
                    if rit.same_fiscal_mother_company:
                        raise except_osv(
                            _("Incorrect Changes!"),
                            _("You can not change journal of invoice '%s'"
                                " because of intercompany Trade rules." % (
                                    ai.name)))
        # Call to super
        return super(AccountInvoice, self).write(
            cr, uid, ids, vals, context=context)
