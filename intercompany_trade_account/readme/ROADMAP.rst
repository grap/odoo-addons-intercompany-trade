* For the time being, invoices validation process is quite hard because
  Odoo uses workflow, where context can not be passed easily.
  To do in V10 : simplify this module, removing _CUSTOMER_ALLOWED_FIELDS
  system.
* In V16, allow to generate intercompany trade 'In' invoices with section
  and notes, as it is well handled in both 'Customers' and 'Vendors' parts.
