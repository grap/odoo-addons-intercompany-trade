[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# Integrated Trade Modules For Odoo
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/grap/odoo-addons-intercompany-trade/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/grap/odoo-addons-intercompany-trade/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/grap/odoo-addons-intercompany-trade/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/grap/odoo-addons-intercompany-trade/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/grap/odoo-addons-intercompany-trade/branch/16.0/graph/badge.svg)](https://codecov.io/gh/grap/odoo-addons-intercompany-trade)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

Roadmap:

* move modules into odoo-addons-cae folder, as now, the interocmpany-trade module are only usefull
  in a CAE context.
* FIX : remove `check_company = False` in many places, (and specially in `account_move.partner_id` field).
  We could replace by another property like, `check_fiscal_company`.

<!-- /!\ do not modify above this line -->

This project contains extra-addons modules for the project Odoo, to manage Intercompany Trade into Odoo.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[intercompany_trade](intercompany_trade/) | 16.0.2.0.1 |  | Intercompany Trade
[intercompany_trade_account](intercompany_trade_account/) | 16.0.3.0.0 |  | Intercompany Trade - Account
[intercompany_trade_account_edi](intercompany_trade_account_edi/) | 16.0.1.0.0 |  | Intercompany Trade - Account EDI
[intercompany_trade_account_usability](intercompany_trade_account_usability/) | 16.0.1.0.0 |  | Intercompany Trade - Account Usability
[intercompany_trade_l10n_fr_siret](intercompany_trade_l10n_fr_siret/) | 16.0.1.0.0 |  | Intercompany Trade - SIRET
[intercompany_trade_point_of_sale](intercompany_trade_point_of_sale/) | 16.0.1.0.0 |  | Intercompany Trade - Point Of Sale
[intercompany_trade_product](intercompany_trade_product/) | 16.0.1.0.0 |  | Intercompany Trade - Product


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[intercompany_trade_joint_buying_base](intercompany_trade_joint_buying_base/) | 16.0.1.0.0 (unported) |  | Intercompany Trade - Joint Buying Base

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to GRAP
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

## About GRAP

<p align="center">
   <img src="http://www.grap.coop/wp-content/uploads/2016/11/GRAP.png" width="200"/>
</p>

GRAP, [Groupement Régional Alimentaire de Proximité](http://www.grap.coop) is a
french company which brings together activities that sale food products in the
region Rhône Alpes. We promote organic and local food, social and solidarity
economy and cooperation.

The GRAP IT Team promote Free Software and developp all the Odoo modules under
AGPL-3 Licence.

You can find all these modules here:

* on the [OCA Apps Store](https://odoo-community.org/shop?&search=GRAP)
* on the [Odoo Apps Store](https://www.odoo.com/apps/modules/browse?author=GRAP).
* on [Odoo Code Search](https://odoo-code-search.com/ocs/search?q=author%3AOCA+author%3AGRAP)

You can also take a look on the following repositories:

* [grap-odoo-incubator](https://github.com/grap/grap-odoo-incubator)
* [grap-odoo-business](https://github.com/grap/grap-odoo-business)
* [grap-odoo-business-supplier-invoice](https://github.com/grap/grap-odoo-business-supplier-invoice)
* [odoo-addons-logistics](https://github.com/grap/odoo-addons-logistics)
* [odoo-addons-cae](https://github.com/grap/odoo-addons-cae)
* [odoo-addons-intercompany-trade](https://github.com/grap/odoo-addons-intercompany-trade)
* [odoo-addons-multi-company](https://github.com/grap/odoo-addons-multi-company)
* [odoo-addons-company-wizard](https://github.com/grap/odoo-addons-company-wizard)
