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

# from openerp import SUPERUSER_ID
# from openerp.osv.osv import except_osv
from openerp.osv.orm import Model
# from openerp.tools.translate import _


class StockPicking(Model):
    _inherit = 'stock.picking'

#    def _prepare_invoice_line(
#            self, cr, uid, group, picking, move_line, invoice_id,
#            invoice_vals, context=None):
#        rit_obj = self.pool['intercompany.trade.config']
#        aa_obj = self.pool['account.account']
#        fcta_obj = self.pool['fiscal.company.transcoding.account']
#        res = super(StockPicking, self)._prepare_invoice_line(
#            cr, uid, group, picking, move_line, invoice_id,
#            invoice_vals, context=None)
#        if picking.intercompany_trade:
#            SUPERUSER_picking = self.browse(
#                cr, SUPERUSER_ID, picking.id, context=context)
#            if SUPERUSER_picking.type == 'out':
#                customer_company_id =\
#                    SUPERUSER_picking.intercompany_trade_picking_in_id\
#                    .company_id.id
#                supplier_company_id = SUPERUSER_picking.company_id.id
#            elif SUPERUSER_picking.type == 'in':
#                supplier_company_id =\
#                    SUPERUSER_picking.intercompany_trade_picking_out_id\
#                    .company_id.id
#                customer_company_id = SUPERUSER_picking.company_id.id
#            else:
#                raise except_osv(_('Error!'), _(
#                    """ You can not invoice an internal Picking flaged as"""
#                    """ Internal Trade."""))
#            rit_id = rit_obj.search(cr, uid, [
#                ('customer_company_id', '=', customer_company_id),
#                ('supplier_company_id', '=', supplier_company_id),
#            ], context=context)[0]
#            rit = rit_obj.browse(cr, uid, rit_id, context=context)
#            if rit.same_fiscal_mother_company:
#                # Change VAT
#                # TODO FIXME if VAT are included
#                res['invoice_line_tax_id'] = False

#                # Transcode account
#                fcta_ids = fcta_obj.search(cr, uid, [
#                    ('company_id', '=',
#                        picking.company_id.fiscal_company.id),
#                    ('from_account_id', '=', res['account_id'])],
#                    context=context)
#                if len(fcta_ids) == 0:
#                    aa = aa_obj.browse(
#                        cr, uid, res['account_id'], context=context)
#                    raise except_osv(_('Missing Accounting Settings!'), _(
#                        """ You can not invoice this product %s because"""
#                        """ according account '%s - %s' is not transcoded."""
#                        """ Please ask your accountant to fix the"""
#                        """ problem.""" % (
#                            picking.product_id.name, aa.code, aa.name)))
#                else:
#                    fcta = fcta_obj.browse(
#                        cr, uid, fcta_ids[0], context=context)
#                    res['account_id'] = fcta.to_account_id.id
#        return res
