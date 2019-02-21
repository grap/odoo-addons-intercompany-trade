# coding: utf-8
# Copyright (C) 2019 - Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class IntercompanyTradeConfigLine(models.Model):
    _name = 'intercompany.trade.config.line'

    # Columns section
    config_id = fields.Many2one(
        comodel_name='intercompany.trade.config', required=True,
        ondelete='cascade')

    category_id = fields.Many2one(
        string='Category', comodel_name='product.category', required=True)

    product_id = fields.Many2one(
        string='Customer Product', comodel_name='product.product',
        required=True)
