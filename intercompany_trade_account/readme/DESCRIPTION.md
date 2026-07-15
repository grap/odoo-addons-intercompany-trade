This module implements intercompany trade features for account module.

* It adds a checkbox named 'Intercompany Trade'
  at journal, account and fiscal position models.
  if checked, that item can only be used in an intercompany trade account moves.
  (An error will be raised otherwise).

* Once configured, when creating an 'Intercompany trade' accounting move
  the journal, fiscal position and accounts will be set automatically.

* Check are done when confirming to avoid misconfiguration.

* When creating a supplier invoices,
