/**
 * Quick view: the product page (photos, options, add to bag) in a dialog over the listing, without losing your
 * place. The product page renders in an iframe with a stripped "quick view" layout (?ts_qv=1, full-page cached);
 * after an add to bag the frame tells this page, which refreshes the bag and opens the added-to-bag drawer.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    var dialog = null, frame = null, lastFocus = null, hideTimer = null, sizer = null;

    /**
     * Desktop / tablet: the panel takes the height of the product inside it (up to the CSS max), so a simple
     * product does not float in a tall empty box. Phones keep the fixed bottom sheet.
     */
    function fitHeight() {
        var panel = dialog.querySelector('.ts-ux-qv__panel'), doc, main;
        if (sizer) {
            sizer.disconnect();
            sizer = null;
        }
        panel.style.height = '';
        try {
            doc = frame.contentDocument;
            main = doc && doc.querySelector('.page-main');
        } catch (e) {
            return;
        }
        if (!main || !window.ResizeObserver || window.matchMedia('(max-width: 767px)').matches) {
            return;
        }
        sizer = new window.ResizeObserver(function () {
            var h = Math.ceil(main.getBoundingClientRect().height);
            if (h > 200) {
                panel.style.height = Math.min(h, 780, Math.floor(window.innerHeight * 0.9)) + 'px';
            }
        });
        sizer.observe(main);
    }

    function build() {
        dialog = document.createElement('div');
        dialog.className = 'ts-ux-qv';
        dialog.hidden = true;
        dialog.innerHTML = '<div class="ts-ux-qv__backdrop" data-close></div>' +
            '<div class="ts-ux-qv__panel" role="dialog" aria-modal="true" aria-label="Quick view">' +
            '<button type="button" class="ts-ux-qv__close" data-close aria-label="Close quick view"></button>' +
            '<div class="ts-ux-qv__loader" aria-hidden="true"></div>' +
            '<iframe class="ts-ux-qv__frame" title="Product quick view"></iframe>' +
            // Tab off the last control inside the frame lands here (the frame's own key events never reach this
            // page), and goes back to the close button instead of the page behind the dialog
            '<span class="ts-ux-qv__end" tabindex="0"></span></div>';
        document.body.appendChild(dialog);
        frame = dialog.querySelector('iframe');
        frame.addEventListener('load', function () {
            if (frame.getAttribute('src')) {
                dialog.classList.add('is-ready');
                fitHeight();
            }
        });
        $(dialog).on('click', '[data-close]', close);
        var closeBtn = dialog.querySelector('.ts-ux-qv__close');
        dialog.querySelector('.ts-ux-qv__end').addEventListener('focus', function () { closeBtn.focus(); });
        dialog.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                close();
            } else if (e.key === 'Tab' && e.shiftKey && document.activeElement === closeBtn) {
                e.preventDefault(); // close button <-> frame, both ways
                frame.focus();
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
        clearTimeout(hideTimer); // reopened while the last close was still animating
        if (dialog.hidden) {
            lastFocus = document.activeElement;
        }
        dialog.classList.remove('is-ready');
        frame.setAttribute('src', frameUrl(url));
        dialog.hidden = false;
        util.modal(dialog, true);
        document.documentElement.classList.add('ts-ux-lock');
        requestAnimationFrame(function () {
            dialog.classList.add('is-open');
            dialog.querySelector('.ts-ux-qv__close').focus();
        });
    }

    function close() {
        if (!dialog || dialog.hidden || !dialog.classList.contains('is-open')) {
            return;
        }
        dialog.classList.remove('is-open');
        util.modal(dialog, false);
        document.documentElement.classList.remove('ts-ux-lock');
        if (sizer) {
            sizer.disconnect();
            sizer = null;
        }
        hideTimer = setTimeout(function () {
            dialog.hidden = true;
            dialog.querySelector('.ts-ux-qv__panel').style.height = '';
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
