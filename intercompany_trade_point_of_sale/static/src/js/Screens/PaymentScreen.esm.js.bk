/*
    Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
    @author: Sylvain LE GAL
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

import PaymentScreen from "point_of_sale.PaymentScreen";

import Registries from "point_of_sale.Registries";

const IntercompanyTradePaymentScreen = (OriginalPaymentScreen) =>
    class extends OriginalPaymentScreen {
        /**
         * Overload function.
         *
         * If intercompany trade partner is selected, check if invoice is selected.
         *
         * @returns {Boolean} Whether the order is valid.
         */
        async validateOrder() {
            const partner = this.currentOrder.get_partner();
            console.log(this.currentOrder);
            console.log(partner);

            if (partner && partner.intercompany_trade) {
                if (payment_lines_qty > 0) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("No customer selected"),
                        body:
                            this.env._t(
                                "Cannot use a customer wallet payment method without selecting a customer."
                            ) +
                            "\n\n" +
                            this.env._t(
                                "Please select a customer or use a different payment method."
                            ),
                    });
                    return;
                }
                if (product_lines_qty > 0) {
                    const wallet_product_names =
                        this.find_customer_wallet_products().map(
                            (product) => product.display_name
                        );
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("No customer selected"),
                        body:
                            this.env._t(
                                "Cannot sell the following products without selecting a customer:"
                            ) +
                            " " +
                            wallet_product_names.join(", ") +
                            "\n\n" +
                            this.env._t(
                                "Please select a customer or remove the order lines."
                            ),
                    });
                    return;
                }
            } else if (this.is_balance_above_minimum(partner, wallet_amount)) {
                this.showPopup("ErrorPopup", {
                    title: this.env._t("Customer wallet balance not sufficient"),
                    body: this.env._t(
                        "There is not enough balance in the customer's wallet to validate this order."
                    ),
                });
                return;
            }

            if (payment_lines_qty > 0 && product_lines_qty > 0) {
                this.showPopup("ErrorPopup", {
                    title: this.env._t("Customer Wallet: Credit and Debit"),
                    body: this.env._t(
                        "You cannot credit and debit a customer wallet in the same order."
                    ),
                });
                return;
            }

            return super.validateOrder(...arguments);
        }

    };

Registries.Component.extend(PaymentScreen, IntercompanyTradePaymentScreen);
export default IntercompanyTradePaymentScreen;
