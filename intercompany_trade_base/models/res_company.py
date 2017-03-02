# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class res_company(Model):
    _inherit = 'res.company'

    def write(self, cr, uid, ids, vals, context=None):
        """update partners that are flagged as 'intercompany_trade' and
           are associated to the companies"""
        context = context and context or {}
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
