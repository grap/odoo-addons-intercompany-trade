# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Intercompany Trade",
    "version": "16.0.2.0.1",
    "category": "Intercompany Trade",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-intercompany-trade",
    "license": "AGPL-3",
    "depends": [
        # GRAP
        "fiscal_company_base",
    ],
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "views/view_res_company.xml",
        "views/view_res_partner.xml",
    ],
    "post_init_hook": "post_init_hook",
    "demo": ["demo/res_users.xml"],
    "installable": True,
}
