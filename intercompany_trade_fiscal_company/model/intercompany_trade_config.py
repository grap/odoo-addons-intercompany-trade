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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class ResIntercompanyTrade(Model):
    _inherit = 'intercompany.trade.config'

    def transcode_account_id(
            self, cr, uid, rit, from_account_id, product_name, context=None):
        fcta_obj = self.pool['fiscal.company.transcoding.account']
        aa_obj = self.pool['account.account']
        if not from_account_id:
            return False
        if not rit.same_fiscal_mother_company:
            return from_account_id
        fcta_ids = fcta_obj.search(cr, uid, [
            ('company_id', '=', rit.customer_company_id.fiscal_company.id),
            ('from_account_id', '=', from_account_id)], context=context)
        if fcta_ids:
            return fcta_obj.browse(
                cr, uid, fcta_ids[0], context=context).to_account_id.id
        else:
            aa = aa_obj.browse(cr, uid, from_account_id, context=context)
            raise except_osv(
                _("Missing Setting!"),
                _(
                    "Unable to sell or purchase a product because the"
                    " following account is not transcoded for the"
                    " company %s. \n\n %s - %s\n\n.Please ask to your"
                    "  accountant to add a setting for this account."
                    " \n\n Product Name : %s" % (
                        rit.customer_company_id.fiscal_company.name,
                        aa.code, aa.name, product_name)))

    # Fields Function Section
    def _same_fiscal_mother_company(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {x: False for x in ids}
        for rit in self.browse(cr, uid, ids, context=context):
            if (rit.customer_company_id.fiscal_type == 'fiscal_child' and
                rit.supplier_company_id.fiscal_type == 'fiscal_child' and
                rit.customer_company_id.fiscal_company.id ==
                    rit.supplier_company_id.fiscal_company.id):
                res[rit.id] = True
        return res

    # Columns Section
    _columns = {
        'same_fiscal_mother_company': fields.function(
            _same_fiscal_mother_company, type='boolean',
            string='Same Fiscal Mother Company',
            store={'intercompany.trade.config': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'customer_company_id',
                    'supplier_company_id',
                ], 10)},
            help="""If this field is checked, the intercompany"""
            """ trade is realized between two fiscal child companies"""
            """ that have the same mother company. Special rules"""
            """ will be applied.\n"""
            """ * VAT are deleted;\n"""
            """ * Sale and Purchase Accounts are updated using a"""
            """ transcoding table; """),
    }
