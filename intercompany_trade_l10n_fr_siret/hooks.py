# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Populate SIREN / NIC field for the 'intercompany trade' partners")
    cr.execute(
        """
        UPDATE res_partner rp
            SET siren = rpc.siren,
            nic = rpc.nic,
            siret=rpc.siret
            FROM res_company rc,
            res_partner rpc
            WHERE rc.intercompany_trade_partner_id = rp.id
            AND rpc.id = rc.partner_id;"""
    )
