/**
 * Shipping step: with more than one rate (Free over $75 + Standard) core selected none, and "Next" on an untouched
 * form only said "The shipping method is missing". When nothing was chosen before, preselect the cheapest rate.
 */
define(['underscore', 'Magento_Checkout/js/model/quote', 'Magento_Checkout/js/action/select-shipping-method'],
    function (_, quote, selectShippingMethodAction) {
        'use strict';

        return function (resolver) {
            var original = resolver.resolveShippingRates;

            resolver.resolveShippingRates = function (ratesData) {
                original.call(this, ratesData);
                if (quote.shippingMethod() || !ratesData || !ratesData.length) {
                    return;
                }
                var available = _.filter(ratesData, function (rate) { return rate.available !== false; });
                if (available.length) {
                    selectShippingMethodAction(_.min(available, function (rate) { return Number(rate.amount); }));
                }
            };

            return resolver;
        };
    });
