import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].with_context(active_test=False).search(
        []
    )._manage_intercompany_trade_partners()
