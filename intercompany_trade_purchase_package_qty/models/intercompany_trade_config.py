# coding: utf-8
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class IntercompanyTradeConfig(models.Model):
    _inherit = 'intercompany.trade.config'

    # Custom Section
    @api.multi
    def _prepare_product_supplierinfo(
            self, supplier_product_id, customer_product_id):
        self.ensure_one()
        vals = super(
            IntercompanyTradeConfig, self)._prepare_product_supplierinfo(
                supplier_product_id, customer_product_id)
        vals.update({
            'indicative_package': True,
            'package_qty': 1,
        })
        return vals
