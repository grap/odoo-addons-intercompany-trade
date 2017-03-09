.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
Intercompany Trade - Glue Module For Cooperative
================================================


New fields
----------

* On 'account.account' model:
    * Add a new check box 'Integrated Trade : Receivable / Payable Account'
      for accounts linked to customers and suppliers in cooperative.
      (181xxx accounts in french accounting) 

* On 'res.company' model:
    * Add a new field 'intercompany_trade_account_id' that will be used
      for each trade between two companies of the same cooperative.

* On 'intercompany.trade.config' model:
    * Add two fields 'purchase_journal_id' and 'sale_journal_id' that will
      be used for trade between two companies of the same cooperative, instead
      of the default ones

* Add 'fiscal.company.transcoding.account' model that will map accounts
  to be used instead of the default one for trades between two companies of
  the same cooperative in supplier and customer invoices lines.

Features
--------

* Remove VAT in trades between two companies of a same cooperative for the
  following models purchase.order.line, sale.order.line, account.invoice.line.

* When creating invoices, change journal if it is trade between two companies
  of the same cooperative.

Roadmap / Issues
----------------

* Add same concept as transoding account for journal. (simplify configuration)

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)
