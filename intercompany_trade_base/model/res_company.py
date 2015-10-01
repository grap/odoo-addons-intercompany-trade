# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Base module for OpenERP
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
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

from openerp.osv.orm import Model


class res_company(Model):
    _inherit = 'res.company'

    def write(self, cr, uid, ids, vals, context=None):
        """update partners that are flagged as 'intercompany_trade' and
           are associated to the companies"""
        res = super(res_company, self).write(
            cr, uid, ids, vals, context=context)
        rit_obj = self.pool['intercompany.trade.config']
        rp_obj = self.pool['res.partner']
        for rc in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx['ignore_intercompany_trade_check'] = True
            # Get customer partner created for this company
            rit_1 = rit_obj.browse(cr, uid, rit_obj.search(
                cr, uid, [('supplier_company_id', '=', rc.id)],
                context=context), context=context)

            for rit in rit_1:
                # Update all the partner with updated information
                data = rit_obj._prepare_partner_from_company(
                    cr, uid, rc.id, rit.customer_company_id.id,
                    context=context)
                rp_obj.write(
                    cr, rit.customer_user_id.id, [rit.supplier_partner_id.id],
                    data, context=ctx)

            # Get supplier partner created for this company
            rit_2 = rit_obj.browse(cr, uid, rit_obj.search(
                cr, uid, [('customer_company_id', '=', rc.id)],
                context=context), context=context)

            for rit in rit_2:
                # Update all the partner with updated information
                data = rit_obj._prepare_partner_from_company(
                    cr, uid, rc.id, rit.supplier_company_id.id,
                    context=context)
                rp_obj.write(
                    cr, rit.supplier_user_id.id, [rit.customer_partner_id.id],
                    data, context=ctx)
        return res
