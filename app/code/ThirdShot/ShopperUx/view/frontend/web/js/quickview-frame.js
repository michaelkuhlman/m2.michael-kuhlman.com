/**
 * Runs inside the quick-view iframe: links open in the main window, a successful add to bag is reported to it.
 */
define(['jquery'], function ($) {
    'use strict';

    return function () {
        if (window.parent === window) {
            return;
        }
        function post(msg) {
            window.parent.postMessage(msg, location.origin);
        }
        $(document).on('click', 'a[href]', function (e) {
            var href = this.getAttribute('href');
            if (!href || href.charAt(0) === '#' || /^javascript:/i.test(href) || this.closest('.fotorama')) {
                return;
            }
            e.preventDefault();
            window.top.location.href = this.href;
        });
        $(document).on('ajax:addToCart', function (e, data) {
            if (data && data.response && data.response.backUrl) {
                return; // Magento sends the shopper to the product page (e.g. an option is missing)
            }
            post({type: 'ts-ux-qv-added', productIds: (data && data.productIds) || []});
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                post({type: 'ts-ux-qv-close'});
            }
        });
    };
});
