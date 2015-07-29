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


class ResIntegratedTrade(Model):
    _inherit = 'res.integrated.trade'

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
            store={'res.integrated.trade': (
                lambda self, cr, uid, ids, context=None: ids,
                [
                    'customer_company_id',
                    'supplier_company_id',
                ], 10)},
            help="""If this field is checked, the integrated"""
            """ trade is realized between two fiscal child companies"""
            """ that have the same mother company. Special rules"""
            """ willbe applied.\n"""
            """ * VAT are deleted;"""
            """ * Sale and Purchase Accounts are updated using a"""
            """ transcoding table; """),
    }
