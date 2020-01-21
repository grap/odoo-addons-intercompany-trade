# Copyright (C) 2019 - Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IntercompanyTradeConfigLine(models.Model):
    _name = "intercompany.trade.config.line"
    _order = "sequence,categ_id"

    # Columns section
    config_id = fields.Many2one(
        comodel_name="intercompany.trade.config",
        required=True,
        ondelete="cascade",
    )

    sequence = fields.Integer()

    categ_id = fields.Many2one(
        string="Category", comodel_name="product.category"
    )

    product_id = fields.Many2one(
        string="Customer Product",
        comodel_name="product.product",
        required=True,
    )

    @api.multi
    def match_rule(self, product):
        self.ensure_one()
        return self._match_rule_category(product)

    @api.multi
    def _match_rule_category(self, product):
        """
        Return True if the category of the product (or one of the parent
        category of the product) is the category of the current line.
        """
        self.ensure_one()
        if not self.categ_id:
            return True
        categ = product.categ_id
        while categ:
            if self.categ_id == categ:
                return True
            categ = categ.parent_id
        return False
