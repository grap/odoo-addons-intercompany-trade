This module extends the functionality of Odoo, to allow users for distinct
companies to make purchases and sales between us.

**Features**

* Add a New Model Intercompany Trade that define that two companies can
  realize purchases and sales between them with a supplier company and
  a customer company

* Add a new field ``intercompany_trade`` in ``res.partner`` model

* Add new groups to manage intercompany trade

* When we set a new intercompany trade, Odoo create a supplier in the
  customer company and a customer in the supplier company

* Intercompany trade partner can be accessed only by 'intercompany trade
  manager' members, except for specific fields, declared in
  ``_intercompany_trade_allowed_fields`` function

* Updating a company will update associated partners, in each company that
  has trade with the updated company

**Demo Data**

In demo mode, the module creates two new companies, and two users:

Login // password are the following :

* Supplier User: ``intercompany_trade_supplier`` // ``demo``
* Customer User: ``intercompany_trade_customer`` // ``demo``
