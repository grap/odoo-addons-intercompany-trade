# -*- coding: utf-8 -*-
# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class IntercompanyTradeConfig(models.Model):
    _inherit = 'intercompany.trade.config'

    # Columns Section
    same_fiscal_mother_company = fields.Boolean(
        compute='_compute_same_fiscal_mother_company',
        string='Same Fiscal Mother Company', store=True,
        help="If this field is checked, the intercompany"
        " trade is realized between two fiscal child companies"
        " that have the same mother company. Special rules"
        " will be applied.\n"
        " * VAT are deleted;\n"
        " * Sale and Purchase Accounts are updated using a"
        " transcoding table; ")

    sale_journal_id = fields.Many2one(
        comodel_name='account.journal', string='Journal in Supplier Company',
        help="Set a journal to use for intercompany trade. This setting is"
        " used only for trade between child companies of the same fiscal"
        " company.")

    purchase_journal_id = fields.Many2one(
        comodel_name='account.journal', string='Journal in Customer Company',
        help="Set a journal to use for intercompany trade. This setting is"
        " used only for trade between child companies of the same fiscal"
        " company.")

    fiscal_company_customer_account_id = fields.Many2one(
        related='customer_company_id.intercompany_trade_account_id',
        comodel_name='account.account', readonly=True,
        string='Receivable Account for the Customer')

    fiscal_company_supplier_account_id = fields.Many2one(
        related='supplier_company_id.intercompany_trade_account_id',
        comodel_name='account.account', readonly=True,
        string='Payable Account for the Supplier')

    # Compute Section
    @api.multi
    @api.depends('customer_company_id', 'supplier_company_id')
    def _compute_same_fiscal_mother_company(self):
        for config in self:
            config.same_fiscal_mother_company = (
                config.customer_company_id.fiscal_company.id ==
                config.supplier_company_id.fiscal_company.id)

    # Constraints Section
    @api.constrains('customer_company_id', 'supplier_company_id')
    def _check_account_settings_fiscal_company(self):
        for config in self:
            if config.same_fiscal_mother_company:
                if not config.fiscal_company_customer_account_id or\
                        not config.fiscal_company_supplier_account_id:
                    raise UserError(_(
                        " For Intercompany Trade between two child companies"
                        "  of the same fiscal company, please define first"
                        " Intercompany Trade account in Companies Form"))

    # Custom Section
    def _prepare_partner_from_company(self, company_id, inner_company_id):
        res =\
            super(IntercompanyTradeConfig, self)._prepare_partner_from_company(
                company_id, inner_company_id)
        company_obj = self.env['res.company']
        company = company_obj.browse(inner_company_id)
        if company.intercompany_trade_account_id:
            res.update({
                'property_account_receivable':
                    company.intercompany_trade_account_id.id,
                'property_account_payable':
                    company.intercompany_trade_account_id.id,
            })
        return res

    @api.multi
    def transcode_account_id(self, from_account_id, product_id):
        self.ensure_one()
        transcoding_obj = self.env['fiscal.company.transcoding.account']
        account_obj = self.env['account.account']
        product_obj = self.env['product.product']
        if not from_account_id:
            return False
        if not self.same_fiscal_mother_company:
            return from_account_id
        transcoding = transcoding_obj.search([
            ('company_id', '=', self.customer_company_id.fiscal_company.id),
            ('from_account_id', '=', from_account_id)])
        if transcoding:
            return transcoding.to_account_id.id
        else:
            account = account_obj.browse(from_account_id)
            product = product_obj.browse(product_id)
            raise UserError(_(
                "Unable to sell or purchase a product because the"
                " following account is not transcoded for the"
                " company %s. \n\n %s - %s\n\n.Please ask to your"
                " accountant to add a setting for this account."
                " \n\n Product Name : %s - %s" % (
                    self.customer_company_id.fiscal_company.name,
                    account.code, account.name, product.default_code,
                    product.name)))

    @api.multi
    def transcode_tax_ids(self, from_tax_ids):
        self.ensure_one()
        if not self.same_fiscal_mother_company:
            return from_tax_ids
        else:
            return False
