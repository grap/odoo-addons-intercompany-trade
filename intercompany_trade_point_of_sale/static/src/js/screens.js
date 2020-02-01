/*
    Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
    @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define('intercompany_trade_point_of_sale.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        validate_order: function(options) {
            if(this.pos.get_order().get_client().intercompany_trade){
                this.gui.show_popup('error',{
                    'title': _t('An order cannot be done for Intercompany Trade'),
                    'body':  _t('Please create a delivered order instead'),
                });
                return;
            }
            return this._super(options);
        }
    });
});
