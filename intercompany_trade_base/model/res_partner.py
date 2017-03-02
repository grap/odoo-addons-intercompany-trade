# -*- coding: utf-8 -*-
# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class ResPartner(Model):
    _inherit = 'res.partner'

    # Columns section
    _columns = {
        'intercompany_trade': fields.boolean(
            'Intercompany Trade', readonly=True,
            help="Indicate that this partner is a company in Odoo."),
    }

    def _intercompany_tradefields_allowed(self):
        """Overload this function to allow basic users to change
        some fields for intercompany trade partner"""
        return []

    def _check_intercompany_trade_access(
            self, cr, uid, ids, fields, context=None):
        """Restrict access of partner set as intercompany_trade for only
        'intercompany_trade_manager' users."""
        context = context and context or {}
        if context.get('ignore_intercompany_trade_check', False):
            return
        unallowed_fields =\
            set(fields) - set(self._intercompany_tradefields_allowed())
        ru_obj = self.pool['res.users']
        if not ru_obj.has_group(
                cr, uid,
                'intercompany_trade_base.intercompany_trade_manager'):
            for rp in self.browse(cr, uid, ids, context=context):
                if rp.intercompany_trade and unallowed_fields:
                    raise except_osv(
                        _("Access Denied!"),
                        _(
                            """Error: You have no right to create or"""
                            """ update a partner that is set as"""
                            """ 'Intercompany Trade'"""))

    def create(self, cr, uid, vals, context=None):
        res = super(ResPartner, self).create(
            cr, uid, vals, context=context)
        self._check_intercompany_trade_access(
            cr, uid, [res], vals.keys(), context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        self._check_intercompany_trade_access(
            cr, uid, ids, vals.keys(), context=context)
        return super(ResPartner, self).write(
            cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        self._check_intercompany_trade_access(
            cr, uid, ids, [0], context=context)
        return super(ResPartner, self).unlink(
            cr, uid, ids, context=context)
