/**
 * Third Shot shopper UX entry point (x-magento-init "*" on every storefront page): wires up the features the
 * current page needs. See the module's etc/module.xml for the list.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    return function (config) {
        util.setConfig(config);
        var body = document.body, cls = body.classList;

        if (cls.contains('ts-ux-qv-frame')) {
            require(['ThirdShot_ShopperUx/js/quickview-frame'], function (frame) { frame(); });
            return;
        }

        require(['ThirdShot_ShopperUx/js/cards', 'ThirdShot_ShopperUx/js/quick-view'], function (cards) {
            cards.init();
        });
        require(['ThirdShot_ShopperUx/js/live-search'], function (live) { live(); });
        require(['ThirdShot_ShopperUx/js/bag-drawer', 'ThirdShot_ShopperUx/js/free-shipping'], function (drawer, ship) {
            drawer.init();
            ship.init();
        });
        require(['ThirdShot_ShopperUx/js/recent'], function (recent) { recent.init(); });
        require(['ThirdShot_ShopperUx/js/nobreak'], function (nobreak) { nobreak(); });
        require(['ThirdShot_ShopperUx/js/back-to-top'], function (top) { top.init(); });

        if (cls.contains('page-products')) {
            require(['ThirdShot_ShopperUx/js/listing'], function (listing) { listing.init(); });
        }
        if (cls.contains('checkout-cart-index')) {
            require(['ThirdShot_ShopperUx/js/cart-qty'], function (qty) { qty.init(); });
        }
    };
});
