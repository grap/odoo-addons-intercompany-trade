# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _logger.info("Create Intercompany Trade Fiscal Position ...")
    env["res.company"].with_context(active_test=False).search(
        [("fiscal_type", "=", "fiscal_mother")]
    )._create_intercompany_trade_fiscal_position_id()
