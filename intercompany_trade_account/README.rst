.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Intercompany Trade - Account
============================

This module implements intercompany trade features for account module.

Features
--------

* Create link between:
    * customer 'account.invoice' and supplier 'account.invoice';
    * customer 'account.invoice.line' and supplier 'account.invoice.line';
* create or delete a customer / supplier invoice update the according
  customer / supplier invoice;
* create, update or delete a customer / supplier line update the according
  customer / supplier line;
* Add Tax management to avoid Tax Bug:
    * All invoices are Tax excluded allways;

* Customers doesn't have the possibility to change price_unit;
* Users doesn't the right to copy an 'intercompany_trade' invoice;

In intercompany trade context:

* Purchase orders can not be invoice
* Incoming Pickings can not be invoiced

Roadmap / Issues
----------------

* Some tests are disabled for the time being.
* Could be great to rename this module into intercompany_trade_transaction
  for generic, and depending officialy from purchase, sale, account and merging
  with intercompany_trade_stock.

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)
