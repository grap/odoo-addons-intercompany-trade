# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    for cae_company in env["res.company"].search(
        [("fiscal_type", "=", "fiscal_mother")]
    ):
        _logger.info(f">>>>>>>>>> Handle {cae_company.code} - {cae_company.name} ...")
        _logger.info("Create Intercompany Trade Fiscal Position (if required)...")
        cae_company._create_intercompany_trade_fiscal_position_id()

        account_181 = env["account.account"].search(
            [("code", "=", "181"), ("company_id", "=", cae_company.id)]
        )
        if not account_181:
            _logger.info("Creating missing 181 Account ...")
            account_181 = env["account.account"].create(
                {
                    "code": "181",
                    "name": "Comptes de liaison des établissements",
                    "is_intercompany_trade": True,
                    "account_type": "liability_non_current",
                    "reconcile": True,
                    "company_id": cae_company.id,
                }
            )
        else:
            account_181.write(
                {
                    "account_type": "liability_non_current",
                    "is_intercompany_trade": True,
                    "reconcile": True,
                }
            )
        env.cr.execute(
            """
            SELECT id as company_id, intercompany_trade_account_id
            FROM res_company
            WHERE fiscal_type = 'fiscal_child'"""
        )
        for fiscal_child_company_id, fiscal_child_account_181_id in env.cr.fetchall():
            fiscal_child_company = env["res.company"].browse(fiscal_child_company_id)
            if not fiscal_child_account_181_id:
                _logger.warning(
                    f"""No 181 account for the company
                     {fiscal_child_company.code} - {fiscal_child_company.name}...
                """
                )
                continue
            openupgrade.logged_query(
                env.cr,
                "update account_move_line set account_id = %s where account_id = %s",
                (
                    account_181.id,
                    fiscal_child_account_181_id,
                ),
            )
            openupgrade.logged_query(
                env.cr,
                "update account_invoice_line set account_id = %s where account_id = %s",
                (
                    account_181.id,
                    fiscal_child_account_181_id,
                ),
            )
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE ir_property set value_reference = 'account.account,%s'
                where value_reference = 'account.account,%s'""",
                (
                    account_181.id,
                    fiscal_child_account_181_id,
                ),
            )

        _logger.info("Configure res_company.intercompany_trade_account_id ...")
        cae_company.intercompany_trade_account_id = account_181

        _logger.info("Configure res_company.intercompany_trade_sale_journal_id ...")
        env.cr.execute(
            """
            SELECT id from account_journal
            WHERE company_id = %s and is_intercompany_trade and type = 'sale'""",
            (cae_company.id,),
        )
        sale_journal_id = env.cr.fetchall()[0][0]
        cae_company.intercompany_trade_sale_journal_id = sale_journal_id

        _logger.info("Configure res_company.intercompany_trade_purchase_journal_id ...")
        env.cr.execute(
            """
            SELECT id from account_journal
            WHERE company_id = %s and is_intercompany_trade and type = 'purchase'""",
            (cae_company.id,),
        )
        purchase_journal_id = env.cr.fetchall()[0][0]
        cae_company.intercompany_trade_purchase_journal_id = purchase_journal_id
