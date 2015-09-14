# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - Product module for Odoo
#    Copyright (C) 2014-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv.orm import TransientModel
from openerp.addons import decimal_precision as dp

from .custom_tools import _check_taxes


class IntercompanyTradeWizardLinkProduct(TransientModel):
    _inherit = 'intercompany.trade.wizard.link.product'

    # Column Section
    _columns = {
        'supplier_sale_price_vat_excl': fields.float(
            'Supplier Sale Price VAT Excluded', readonly=True,
            digits_compute=dp.get_precision(
                'Intercompany Trade Product Price')),
        'supplier_sale_price_vat_incl': fields.float(
            'Supplier Sale Price VAT Included', readonly=True,
            digits_compute=dp.get_precision(
                'Intercompany Trade Product Price')),
        # The Following Field are used to display external information
        # And avoir ACL problem
        'supplier_vat_name': fields.char(
            'Supplier VAT Name', readonly=True),
    }

    # Button Section
    def link_product(self, cr, uid, ids, context=None):
        pp_obj = self.pool['product.product']

        for itwlp in self.browse(cr, uid, ids, context=context):
            sup_pp = pp_obj.browse(
                cr, SUPERUSER_ID, itwlp.supplier_product_id.id,
                context=context)
            cus_pp = pp_obj.browse(
                cr, uid, itwlp.customer_product_id.id,
                context=context)
            _check_taxes(
                self.pool, cr, uid, sup_pp, cus_pp,
                context=context)

        return super(IntercompanyTradeWizardLinkProduct, self).link_product(
            cr, uid, ids, context=context)
