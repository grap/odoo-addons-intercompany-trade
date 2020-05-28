# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _intercompany_trade_allowed_fields(self):
        """allow basic user to change pricelist"""
        res = super(ResPartner, self)._intercompany_trade_allowed_fields()
        res.append('property_product_pricelist')
        return res
