# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

# pylint: disable=W8150

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    ResCompany = env["res.company"].with_context(active_test=False)
    ResPartner = env["res.partner"].with_context(
        active_test=False, ignore_intercompany_trade_check=True
    )
    MergeModel = env["base.partner.merge.automatic.wizard"].with_context(
        ignore_intercompany_trade_check=True
    )
    _logger.info("Create all intercompany trade partners ...")
    env["res.company"].with_context(active_test=False).search(
        []
    )._manage_intercompany_trade_partners()

    for cae_company in ResCompany.search([("fiscal_type", "=", "fiscal_mother")]):
        for child_company in ResCompany.search([("parent_id", "=", cae_company.id)]):
            # Get all customer partners
            env.cr.execute(
                """
                SELECT customer_partner_id
                FROM intercompany_trade_config
                WHERE customer_company_id = %s;
                """,
                (child_company.id,),
            )
            customer_partner_ids = [x[0] for x in env.cr.fetchall()]
            env.cr.execute(
                """
                SELECT supplier_partner_id
                FROM intercompany_trade_config
                WHERE supplier_company_id = %s;
                """,
                (child_company.id,),
            )
            supplier_partner_ids = [x[0] for x in env.cr.fetchall()]

            partner_ids = list(set(customer_partner_ids + supplier_partner_ids))

            if len(partner_ids) == 0:
                _logger.info("No intercompany trade partners found.")
                continue

            _logger.info(
                f"{len(partner_ids)} intercompany trade partners to merge found."
                f" {partner_ids}."
            )

            main_partner = child_company.intercompany_trade_partner_id.with_context(
                ignore_intercompany_trade_check=True
            )

            for partner_id in partner_ids[::-1]:
                partner = ResPartner.browse(partner_id)
                _logger.info(
                    f"Merging the partner #{partner_id} - {partner.name}"
                    f" of company {partner.company_id.code} {partner.company_id.name}"
                    f" with main partner (#{main_partner.id})"
                )
                MergeModel._merge(
                    [partner_id, main_partner.id],
                    dst_partner=main_partner,
                    extra_checks=False,
                )
