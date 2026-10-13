/**
 * Magento only shows the checkout summary totals once the shipping step is done
 * (isFullMode = step "shipping" processed), so on step 1 the sidebar says
 * "1 item" and nothing else. Show the totals as soon as they are loaded; the
 * shipping row still waits for a chosen method (summary/shipping.js checks that).
 */
define([], function () {
    'use strict';

    return function (AbstractTotal) {
        return AbstractTotal.extend({
            isFullMode: function () {
                return !!this.getTotals();
            }
        });
    };
});
