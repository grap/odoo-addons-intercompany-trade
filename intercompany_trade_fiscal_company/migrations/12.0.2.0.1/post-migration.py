# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_fiscal_position afp
        SET is_intercompany_trade_fiscal_company = true
        FROM res_company rc
        WHERE rc.id = afp.company_id
        AND rc.fiscal_type = 'fiscal_mother'
        AND afp.name ilike '%Interso%';
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company rc
        SET intercompany_trade_fiscal_position_id = afp.id
        FROM account_fiscal_position afp
        WHERE rc.id = afp.company_id
        AND afp.is_intercompany_trade_fiscal_company = true;
        """,
    )
