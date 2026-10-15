/**
 * Third Shot theme RequireJS config.
 */
var config = {
    config: {
        mixins: {
            // checkout sidebar: show subtotal / shipping / order total on the shipping step too
            'Magento_Checkout/js/view/summary/abstract-total': {
                'js/summary-full-mode-mixin': true
            },
            // re-validate the swatch input on pick, so "This is a required field." goes away
            'Magento_Swatches/js/swatch-renderer': {
                'js/swatch-renderer-mixin': true
            },
            // bundle "Customize": scroll the options panel to just below the sticky header
            'Magento_Bundle/js/slide': {
                'js/bundle-slide-mixin': true
            },
            // checkout: preselect the cheapest shipping rate when nothing was chosen yet
            'Magento_Checkout/js/model/checkout-data-resolver': {
                'js/checkout-data-resolver-mixin': true
            }
        }
    }
};
