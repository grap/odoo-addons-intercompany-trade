# Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    intercompany_trade = fields.Boolean(
        string='Intercompany Trade', related='partner_id.intercompany_trade')
