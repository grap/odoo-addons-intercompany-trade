# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv.orm import Model


class intercompany_trade_config(Model):
    _inherit = 'intercompany.trade.config'

    # Custom Section
    def _prepare_product_supplierinfo(
            self, cr, uid, id, supplier_product_id, customer_product_id,
            context=None):
        res = super(
            intercompany_trade_config, self)._prepare_product_supplierinfo(
                cr, uid, id, supplier_product_id, customer_product_id,
                context=context)
        res['indicative_package'] = True
        res['package_qty'] = 1

        return res
