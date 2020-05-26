/*
    Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
    @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/


odoo.define('intercompany_trade_point_of_sale.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    // load new field 'has_image' for 'res.partner' model
    models.load_fields("res.partner", ['intercompany_trade']);
});
