.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================
Intercompany Trade - Glue Module for Product
============================================

Features
--------

* Give the possibility to customer to link a product to a supplier product
* Change the pricelist on customer change the pricelist on
  intercompany.trade.config object

* Change product information changes supplierinfo
* Change price information changes supplierinfo
* Change pricelist on partner changes supplierinfo

Roadmap / Issues
----------------
* Refactor this module.
    * set new api
    * maybe remove custom_tools

* Round sale price to make it compatible with purchase prices.

* add an extra ratio to have the possibility to link a supplier product
  'pack of 6 bottles' to a customer product 'bottle'. Link a product should
  divide prices by 6.

* Supplierinfo should be readonly in intercompany trade for customer, for
  consistency reason. (not a big deal, because only supplier can now
  create invoices)

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)
