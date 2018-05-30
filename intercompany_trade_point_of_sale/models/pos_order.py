# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models
from openerp.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    @api.constrains('partner_id')
    def _check_partner_integrated_trade(self):
        for order in self:
            if order.partner_id.intercompany_trade:
                raise ValidationError(_(
                    "You can not select a partner marked as 'integrated Trade'"
                    " in a Point of sale context. Please use the sale or"
                    " the invoice module instead."))
