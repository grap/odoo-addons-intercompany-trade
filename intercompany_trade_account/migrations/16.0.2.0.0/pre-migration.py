# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
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

queries = [
    """UPDATE account_account set code = '181' where code ilike '1810%';""",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)

    for query in queries:
        openupgrade.logged_query(env.cr, query)

    for company in env["res.company"].search([("fiscal_type", "=", "fiscal_mother")]):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_invoice ai
                SET account_id = (
                    SELECT id
                    FROM account_account aa
                    WHERE aa.code = '181'
                    AND company_id = %s
                )
                FROM res_company rc,
                    account_account aa_temp
                WHERE rc.id = ai.company_id
                AND rc.parent_id = %s
                AND aa_temp.id = ai.account_id
                AND aa_temp.code ilike '181%'
                AND aa_temp.code != '181';
            """,
            (
                company.id,
                company.id,
            ),
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_invoice_line ail
                SET account_id = (
                    SELECT id
                    FROM account_account aa
                    WHERE aa.code = '181'
                    AND company_id = %s
                )
                FROM res_company rc,
                    account_account aa_temp
                WHERE rc.id = ail.company_id
                AND rc.parent_id = %s
                AND aa_temp.id = ail.account_id
                AND aa_temp.code ilike '181%'
                AND aa_temp.code != '181';
            """,
            (
                company.id,
                company.id,
            ),
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_move_line aml
                SET account_id = (
                    SELECT id
                    FROM account_account aa
                    WHERE aa.code = '181'
                    AND company_id = %s
                )
                FROM res_company rc,
                    account_account aa_temp
                WHERE rc.id = aml.company_id
                AND rc.parent_id = %s
                AND aa_temp.id = aml.account_id
                AND aa_temp.code ilike '181%'
                AND aa_temp.code != '181';
            """,
            (
                company.id,
                company.id,
            ),
        )
