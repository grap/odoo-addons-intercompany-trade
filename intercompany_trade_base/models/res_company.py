# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.multi
    def write(self, vals):
        """update partners that are flagged as 'intercompany_trade' and
           are associated to the companies
           TODO : check if sudo is necessary.
           """
        IntercompanyTradeConfig = self.env["intercompany.trade.config"]

        res = super(ResCompany, self).write(vals)

        for company in self:
            # Get customer partner created for this company
            configs = IntercompanyTradeConfig.search(
                [("supplier_company_id", "=", company.id)]
            )

            for config in configs:
                # Update all the partner with updated information
                data = IntercompanyTradeConfig._prepare_partner_from_company(
                    company.id, config.customer_company_id.id
                )
                config.supplier_partner_id.write(data)

            # Get supplier partner created for this company
            configs = IntercompanyTradeConfig.search(
                [("customer_company_id", "=", company.id)]
            )

            for config in configs:
                # Update all the partner with updated information
                data = IntercompanyTradeConfig._prepare_partner_from_company(
                    company.id, config.supplier_company_id.id
                )
                config.customer_partner_id.write(data)

        return res
