/**
 * Third Shot theme RequireJS config.
 */
var config = {
    config: {
        mixins: {
            // checkout sidebar: show subtotal / shipping / order total on the shipping step too
            'Magento_Checkout/js/view/summary/abstract-total': {
                'js/summary-full-mode-mixin': true
            }
        }
    }
};
