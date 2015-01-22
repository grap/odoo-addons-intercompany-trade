# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Base module for OpenERP
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


from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _


class res_integrated_trade(Model):
    _name = 'res.integrated.trade'
    _description = 'Integrated Trade'
    _order = 'customer_company_id, supplier_company_id'

    # Columns section
    _columns = {
        'name': fields.char(
            'Name', required=True, size=64),
        'active': fields.boolean(
            'Active',
            help="""By unchecking the active field you can disable """
            """the trading between the two company without deleting it."""),
        'customer_company_id': fields.many2one(
            'res.company', 'Customer Company', required=True,
            help="""Select the company that could purchase to the other."""),
        'supplier_company_id': fields.many2one(
            'res.company', 'Supplier Company', required=True,
            help="""Select the company that could sale to the other."""),
        'customer_partner_id': fields.many2one(
            'res.partner', 'Customer Partner in the Supplier Company',
            readonly=True),
        'supplier_partner_id': fields.many2one(
            'res.partner', 'Supplier Partner in the Customer Company',
            readonly=True),
    }

    _defaults = {
        'name': '/',
        'active': True,
    }

    _sql_constraints = [
        (
            'customer_supplier_company_uniq',
            'unique(customer_company_id, supplier_company_id)',
            'Customer and Supplier company must be uniq !'),
    ]

    # Custom Section
    def _prepare_partner_from_company(self, cr, uid, company_id, context=None):
        rc_obj = self.pool['res.company']
        rc = rc_obj.browse(cr, uid, company_id, context=context)
        return {
            'name': rc.name + ' ' + _('(Integrated Trade)'),
            'street': rc.street,
            'street2': rc.street2,
            'city': rc.city,
            'zip': rc.zip,
            'state_id': rc.state_id.id,
            'country_id': rc.country_id.id,
            'website': rc.website,
            'phone': rc.phone,
            'fax': rc.fax,
            'email': rc.email,
            'vat': rc.vat,
            'is_company': True,
            'image': rc.logo,
        }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create or update associated partner in each company"""
        rp_obj = self.pool['res.partner']
        res = super(res_integrated_trade, self).create(
            cr, uid, vals, context=context)
        rit_id = self.search(cr, uid, [
            ('customer_company_id', '=', vals['supplier_company_id']),
            ('supplier_company_id', '=', vals['customer_company_id']),
        ], context=context)
        if len(rit_id) == 0:
            # create supplier in customer company
            partner_vals = self._prepare_partner_from_company(
                cr, uid, vals['supplier_company_id'], context=context)
            partner_vals['customer'] = False
            partner_vals['supplier'] = True
            partner_vals['integrated_trade'] = True
            partner_vals['company_id'] = vals['customer_company_id']
            supplier_partner_id = rp_obj.create(
                cr, uid, partner_vals, context=context)

            # create customer in supplier company
            partner_vals = self._prepare_partner_from_company(
                cr, uid, vals['customer_company_id'], context=context)
            partner_vals['customer'] = True
            partner_vals['supplier'] = False
            partner_vals['integrated_trade'] = True
            partner_vals['company_id'] = vals['supplier_company_id']
            customer_partner_id = rp_obj.create(
                cr, uid, partner_vals, context=context)
            self.write(cr, uid, [res], {
                'customer_partner_id': customer_partner_id,
                'supplier_partner_id': supplier_partner_id,
            }, context=context)
        else:
            # Change the actual partners
            rit = self.browse(cr, uid, rit_id, context=context)[0]
            rp_obj.write(
                cr, uid, [rit.customer_partner_id.id], {'supplier': True},
                context=context)
            rp_obj.write(
                cr, uid, [rit.supplier_partner_id.id], {'customer': True},
                context=context)
            self.write(cr, uid, [res], {
                'customer_partner_id': rit.supplier_partner_id.id,
                'supplier_partner_id': rit.customer_partner_id.id,
            }, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """ Block possibility to change customer or supplier company"""
        if 'customer_company_id' in vals.keys()\
                or 'supplier_company_id' in vals.keys():
            if context.get('install_mode', False):
                vals.pop('customer_company_id')
                vals.pop('supplier_company_id')
            else:
                raise except_osv(
                    _("Error!"),
                    _("""You can not change customer or supplier company."""
                        """If you want to do so, please disable this"""
                        """ integrated trade and create a new one."""))
        return super(res_integrated_trade, self).write(
            cr, uid, ids, vals, context=context)
