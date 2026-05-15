# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    "account_account": [
        ("is_intercompany_trade_fiscal_company", "is_intercompany_trade"),
    ],
    "account_journal": [
        ("is_intercompany_trade_fiscal_company", "is_intercompany_trade"),
    ],
    "account_fiscal_position": [
        ("is_intercompany_trade_fiscal_company", "is_intercompany_trade"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
