# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.rename_columns(
        cr,
        {
            "res_partner": [
                ("contact_mandate_id", "old_contact_mandate_id"),
            ]
        },
    )
