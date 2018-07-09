# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def prepare_intercompany_invoice(self, config, operation):
        self.ensure_one()
        partner_obj = self.env['res.partner']
        values, other_user = super(
            AccountInvoice, self).prepare_intercompany_invoice(
                config, operation)
        if 'property_product_pricelist_purchase' in partner_obj._fields:
            pricelist = config.sudo().with_context(
                force_company=config.supplier_company_id.id,
            ).supplier_partner_id.property_product_pricelist_purchase
            values['pricelist_id'] = pricelist.id
        return values, other_user
