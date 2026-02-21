# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

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

            partner_ids = customer_partner_ids + supplier_partner_ids

            if len(partner_ids) == 0:
                _logger.info(
                    f"Company #{child_company.id} - {child_company.name}."
                    " No transaction partners found. Creating a new one"
                )
                child_company._create_intercompany_trade_partner()

            if len(partner_ids) == 1:
                main_partner = ResPartner.browse(partner_ids[0])
            else:
                # We search the older partner.
                # It will be the target partner during the merge process
                main_partner = ResPartner.search(
                    [("id", "in", partner_ids)], limit=1, order="create_date"
                )

            # We change the company of the main partner
            _logger.info(
                f"Partner #{main_partner.id} - {main_partner.name}: Link to CAE."
                f" (previously in {main_partner.company_id.name})"
            )
            main_partner.company_id = cae_company.id
            child_company.intercompany_trade_partner_id = main_partner

            partner_ids.remove(main_partner.id)

            for partner_id in partner_ids:
                MergeModel._merge(
                    [partner_id, main_partner.id],
                    dst_partner=main_partner,
                    extra_checks=False,
                )
