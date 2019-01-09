# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # Due to bad design, some field are written on computed function
    # with account_invoice_triple_discount
    # To avoid error, the following fields are allowed for the time being
    # TODO V10. Check if it is required.
    # Alternatively, we could add a check on the user. (Block if user != admin)
    _CUSTOMER_ALLOWED_FIELDS = [
        'discount', 'price_unit']

    # Columns Section
    intercompany_trade = fields.Boolean(
        string='Intercompany Trade',
        related='invoice_id.intercompany_trade', store=True)

    intercompany_trade_account_invoice_line_id = fields.Integer(
        string='Intercompany Trade Account Invoice Line', readonly=True)

    price_subtotal = fields.Float(compute_sudo=True)

    # Overload Section
    @api.model
    def create(self, vals):
        # Call Super
        line = super(AccountInvoiceLine, self).create(vals)

        if not self.env.context.get(
                'intercompany_trade_do_not_propagate', False) and\
                line.intercompany_trade:

            # Block Customer Creation
            if line.invoice_id.type in ('in_invoice', 'in_refund'):
                raise UserError(_(
                    "Error!\nYou can not edit invoice lines."
                    " Please ask to your supplier to do it."))

            # Prepare and create associated Account Invoice Line
            line_other_vals = line._prepare_intercompany_vals()

            line_other = self.sudo().with_context(
                intercompany_trade_do_not_propagate=True).create(
                    line_other_vals)

            # if this is a supplier invoice and an intercompany trade, the user
            # doesn't have the right to change the unit price, so we will
            # erase the unit price, and recover the good one.
            if line.invoice_id.type in ('in_invoice', 'in_refund'):
                price_unit = line_other_vals['price_unit']
            else:
                price_unit = vals['price_unit']

            # Update Original Account Invoice Line
            line.with_context(
                intercompany_trade_do_not_propagate=True).write({
                    'intercompany_trade_account_invoice_line_id':
                    line_other.id,
                    'price_unit': price_unit})

            # Update Other Account Invoice Line
            line_other.sudo().with_context(
                intercompany_trade_do_not_propagate=True).write({
                    'intercompany_trade_account_invoice_line_id': line.id,
                    'price_unit': price_unit})

        return line

    @api.multi
    def write(self, vals):
        res = super(AccountInvoiceLine, self).write(vals)

        if not self.env.context.get(
                'intercompany_trade_do_not_propagate', False):

            for line in self.filtered(lambda x: x.intercompany_trade):

                # Block Customer Update
                if line.invoice_id.type in ['in_invoice', 'in_refund']:
                    copy_vals = vals.copy()
                    for key in self._CUSTOMER_ALLOWED_FIELDS:
                        copy_vals.pop(key, False)
                    if copy_vals:
                        raise UserError(_(
                            "You can not edit invoice lines."
                            " Please ask to your supplier to do it."
                            "\n\n %s") % ', '.join(
                                [x for x in copy_vals.keys()]))
                    continue

                # Block supplier changes for some fields.
                if 'product_id' in vals.keys():
                    raise UserError(_(
                        "Error!\nYou can not change the product %s."
                        "Please remove this line and create a"
                        " new one." % (line.product_id.name)))
                if 'uos_id' in vals.keys():
                    raise UserError(_(
                        "Error!\nYou can not change the UoM of the Product"
                        " %s." % (line.product_id.name)))

                # Prepare and update associated Account Invoice line
                line_other_vals = line._prepare_intercompany_vals()

                if 'price_unit' in vals.keys():
                    line_other_vals['price_unit'] = vals['price_unit']
                line_other = line.sudo().browse(
                    line.intercompany_trade_account_invoice_line_id)
                line_other.with_context(
                    intercompany_trade_do_not_propagate=True).write(
                        line_other_vals)

        return res

    @api.multi
    def unlink(self):
        if not self.env.context.get(
                'intercompany_trade_do_not_propagate', False):
            for line in self.filtered(lambda x: x.intercompany_trade):

                # Block Customer Deletion
                if line.invoice_id.type in ('in_invoice', 'in_refund'):
                    raise UserError(_(
                        "Error!\nYou can not delete invoice lines."
                        " Please ask to your supplier to do it."))

                # Delete according line
                line_other = line.sudo().browse(
                    line.intercompany_trade_account_invoice_line_id)
                line_other.with_context(
                    intercompany_trade_do_not_propagate=True).unlink()

        return super(AccountInvoiceLine, self).unlink()

    # Custom Section
    @api.multi
    def _prepare_intercompany_vals(self):
        self.ensure_one()
        invoice_obj = self.env['account.invoice']
        invoice = self.invoice_id
        config =\
            invoice_obj._get_intercompany_trade_by_partner_company_type(
                invoice.partner_id.id,
                invoice.company_id.id,
                invoice.type)
        if invoice.type in ['out_invoice', 'out_refund']:
            # A Purchase Invoice Line Create a Sale Invoice Line
            other_type = invoice.type.replace('out_', 'in_')
            other_user = config.customer_user_id
            other_company_id = config.customer_company_id.id
            other_partner_id = config.supplier_partner_id.id
        else:
            raise UserError(_(
                "Unimplemented Feature!\n"
                "You can not create an invoice Line %s with a"
                " partner flagged as Intercompany Trade." % (invoice.type)))

        # Create according account invoice line
        customer_product = config._get_product_in_customer_company(
            self.product_id)

        values = self.sudo(user=other_user).product_id_change(
            customer_product.id,
            False, type=other_type, company_id=other_company_id,
            partner_id=other_partner_id)['value']

        values.update({
            'invoice_id': invoice.intercompany_trade_account_invoice_id,
            'product_id': customer_product.id,
            'company_id': other_company_id,
            'partner_id': other_partner_id,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'uos_id': self.uos_id.id,
            'invoice_line_tax_id': (
                values.get('invoice_line_tax_id', False) and
                [[6, False, values['invoice_line_tax_id']]] or False),
        })

        return values
