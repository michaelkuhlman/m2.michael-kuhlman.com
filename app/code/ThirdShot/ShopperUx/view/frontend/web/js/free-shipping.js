/**
 * Free-shipping meter: "You're $12.00 away from free shipping" with a progress bar, from the bag subtotal.
 * Shown in the mini bag, on the bag page and in the added-to-bag drawer; follows the cart section live.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    function html(subtotal) {
        var cfg = util.config(), limit = Number(cfg.freeShipping || 0);
        if (!limit) {
            return '';
        }
        subtotal = Number(subtotal) || 0;
        var left = Math.max(0, limit - subtotal), pct = Math.min(100, subtotal / limit * 100), msg;
        if (left <= 0) {
            msg = '<strong>You’ve unlocked free shipping.</strong>';
        } else if (subtotal <= 0) {
            msg = 'Free shipping on orders over <strong>' + util.money(limit) + '</strong>';
        } else {
            msg = 'You’re <strong>' + util.money(left) + '</strong> away from free shipping';
        }
        return '<div class="ts-ux-ship' + (left <= 0 ? ' is-free' : '') + '">' +
            '<p class="ts-ux-ship__msg">' + msg + '</p>' +
            '<div class="ts-ux-ship__bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' +
            Math.round(pct) + '" aria-label="Progress to free shipping"><span style="width:' + pct.toFixed(1) + '%"></span></div></div>';
    }

    function mount(target, subtotal, where) {
        var $t = $(target);
        if (!$t.length) {
            return;
        }
        var $el = $t.children('.ts-ux-ship-slot');
        if (!$el.length) {
            $el = $('<div class="ts-ux-ship-slot"></div>');
            where === 'append' ? $t.append($el) : $t.prepend($el);
        }
        $el.html(html(subtotal));
    }

    return {
        html: html,
        /** Mini bag + bag page meters, kept in sync with the cart section. */
        init: function () {
            require(['Magento_Customer/js/customer-data'], function (customerData) {
                var cart = customerData.get('cart');
                function sync(data) {
                    data = data || {};
                    var sub = Number(data.subtotalAmount || 0), count = Number(data.summary_count || 0);
                    if (count > 0) {
                        mount('#minicart-content-wrapper .block-content', sub);
                    } else {
                        $('#minicart-content-wrapper .ts-ux-ship-slot').remove();
                    }
                    if (document.body.classList.contains('checkout-cart-index') && count > 0) {
                        mount('.cart-container .cart-summary', sub);
                    }
                }
                cart.subscribe(sync);
                sync(cart());
                // the mini bag content is (re)rendered by Knockout when it first opens
                $(document).on('click', '.minicart-wrapper .showcart', function () {
                    setTimeout(function () { sync(cart()); }, 50);
                });
                $('[data-block="minicart"]').on('contentUpdated', function () { sync(cart()); });
            });
        }
    };
});
