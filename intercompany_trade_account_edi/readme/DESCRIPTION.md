This module implements intercompany trade features for `account_edi` module.

It basically disables EDI feature for Internal Trade for the time being,
to avoid messages like:

```text
Errors occured while creating the EDI document (format: Factur-x/XRechnung CII 2.2.0).
The receiver might refuse it.

Each invoice line should have at least one tax.
You should include at least one tax per invoice line.
LINE XXX shall be categorized with an Invoiced item VAT category code (BT-151).
The field 'Sanitized Account Number' is required on the Recipient Bank.
The field 'Compte bancaire destinataire' is required on MOVE YYY.
```
