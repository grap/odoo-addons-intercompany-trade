/*
    Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
    @author: Sylvain LE GAL
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define("intercompany_trade_point_of_sale.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");

    const OverloadPaymentScreen = (PaymentScreen) =>
        class OverloadPaymentScreen extends PaymentScreen {
            async validateOrder() {
                const partner = this.currentOrder.get_partner();
                console.log(partner);
                console.log(partner && partner.intercompany_trade );
                console.log(partner && partner.intercompany_trade && !this.currentOrder.to_invoice);
                if (partner && partner.intercompany_trade && !this.currentOrder.to_invoice) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("Order to invoice"),
                        body:
                            this.env._t(
                                "When the customer is flagged as 'Intercompany Trade', the order has to be invoiced."
                            ) +
                            "\n\n" +
                            this.env._t(
                                "Please check the box 'To invoice'."
                            ),
                    });
                    return;
                }

                return super.validateOrder(...arguments);
            }
        };

    Registries.Component.extend(PaymentScreen, OverloadPaymentScreen);

    return PaymentScreen;
});
