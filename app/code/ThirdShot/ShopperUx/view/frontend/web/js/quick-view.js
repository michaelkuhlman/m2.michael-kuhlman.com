/**
 * Quick view: the product page (photos, options, add to bag) in a dialog over the listing, without losing your
 * place. The product page renders in an iframe with a stripped "quick view" layout (?ts_qv=1, full-page cached);
 * after an add to bag the frame tells this page, which refreshes the bag and opens the added-to-bag drawer.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    var dialog = null, frame = null, lastFocus = null;

    function build() {
        dialog = document.createElement('div');
        dialog.className = 'ts-ux-qv';
        dialog.hidden = true;
        dialog.innerHTML = '<div class="ts-ux-qv__backdrop" data-close></div>' +
            '<div class="ts-ux-qv__panel" role="dialog" aria-modal="true" aria-label="Quick view">' +
            '<button type="button" class="ts-ux-qv__close" data-close aria-label="Close quick view"></button>' +
            '<div class="ts-ux-qv__loader" aria-hidden="true"></div>' +
            '<iframe class="ts-ux-qv__frame" title="Product quick view"></iframe></div>';
        document.body.appendChild(dialog);
        frame = dialog.querySelector('iframe');
        frame.addEventListener('load', function () {
            if (frame.getAttribute('src')) {
                dialog.classList.add('is-ready');
            }
        });
        $(dialog).on('click', '[data-close]', close);
        dialog.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                close();
            } else if (e.key === 'Tab') { // keep focus inside: close button <-> frame
                var btn = dialog.querySelector('.ts-ux-qv__close');
                if (e.shiftKey && document.activeElement === btn) {
                    e.preventDefault();
                    frame.focus();
                }
            }
        });
        window.addEventListener('message', function (e) {
            if (e.origin !== location.origin || !e.data || typeof e.data !== 'object') {
                return;
            }
            if (e.data.type === 'ts-ux-qv-added') {
                close();
                require(['Magento_Customer/js/customer-data'], function (customerData) {
                    customerData.reload(['cart'], true);
                });
                $(document).trigger('ts-ux:added', [{productIds: e.data.productIds || []}]);
            } else if (e.data.type === 'ts-ux-qv-close') {
                close();
            }
        });
    }

    function frameUrl(url) {
        var u = new URL(url, location.href);
        u.searchParams.set('ts_qv', '1');
        return u.toString();
    }

    function open(url) {
        if (!dialog) {
            build();
        }
        lastFocus = document.activeElement;
        dialog.classList.remove('is-ready');
        frame.setAttribute('src', frameUrl(url));
        dialog.hidden = false;
        document.documentElement.classList.add('ts-ux-lock');
        requestAnimationFrame(function () {
            dialog.classList.add('is-open');
            dialog.querySelector('.ts-ux-qv__close').focus();
        });
    }

    function close() {
        if (!dialog || dialog.hidden) {
            return;
        }
        dialog.classList.remove('is-open');
        document.documentElement.classList.remove('ts-ux-lock');
        setTimeout(function () {
            dialog.hidden = true;
            frame.setAttribute('src', 'about:blank');
            frame.removeAttribute('src');
        }, util.reducedMotion() ? 0 : 220);
        if (lastFocus && lastFocus.focus) {
            lastFocus.focus({preventScroll: true});
        }
    }

    $(document).on('click', '[data-ts-qv]', function (e) {
        e.preventDefault();
        var url = this.getAttribute('data-ts-qv-url');
        if (url) {
            open(url);
        }
    });

    return {open: open, close: close};
});
