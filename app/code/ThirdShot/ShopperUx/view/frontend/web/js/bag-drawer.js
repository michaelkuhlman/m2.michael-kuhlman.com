/**
 * Added-to-bag drawer: slides in after any add to bag (listing quick add, product page, quick view, Saved,
 * recommendations) with the item, the bag subtotal, the free-shipping meter, View bag / Checkout, and
 * "Pairs well with" picks you can add in one click.
 */
define([
    'jquery',
    'ThirdShot_ShopperUx/js/util',
    'ThirdShot_ShopperUx/js/free-shipping',
    'Magento_Customer/js/customer-data'
], function ($, util, freeShipping, customerData) {
    'use strict';

    var el = null, lastFocus = null, pending = null, recsFor = null, hideTimer = null, seen = [];

    function build() {
        var cfg = util.config();
        el = document.createElement('div');
        el.className = 'ts-ux-drawer';
        el.hidden = true;
        el.innerHTML = '<div class="ts-ux-drawer__backdrop" data-close></div>' +
            '<aside class="ts-ux-drawer__panel" role="dialog" aria-modal="true" aria-labelledby="ts-ux-drawer-title" tabindex="-1">' +
            '<header class="ts-ux-drawer__head"><h2 id="ts-ux-drawer-title" class="ts-ux-drawer__title">Added to your bag</h2>' +
            '<button type="button" class="ts-ux-drawer__close" data-close aria-label="Close"></button></header>' +
            '<div class="ts-ux-drawer__body"><div class="ts-ux-drawer__items" aria-live="polite"></div>' +
            '<div class="ts-ux-drawer__ship"></div>' +
            '<div class="ts-ux-drawer__totals"></div>' +
            '<div class="ts-ux-drawer__actions"><a class="action primary" href="' + util.escape(cfg.checkoutUrl) + '">Checkout</a>' +
            '<a class="action secondary" href="' + util.escape(cfg.cartUrl) + '">View bag</a>' +
            '<button type="button" class="ts-ux-drawer__keep" data-close>Keep shopping</button></div>' +
            '<section class="ts-ux-drawer__recs" hidden><h3>Pairs well with</h3><ol class="product-items ts-ux-mini-grid"></ol></section>' +
            '</div></aside>';
        document.body.appendChild(el);
        $(el).on('click', '[data-close]', close);
        el.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                close();
            } else {
                util.trapTab(e, el.querySelector('.ts-ux-drawer__panel'));
            }
        });
    }

    function open() {
        if (!el) {
            build();
        }
        clearTimeout(hideTimer); // an add to bag right after closing: cancel the pending hide
        if (el.hidden || !el.classList.contains('is-open')) {
            if (el.hidden) {
                lastFocus = document.activeElement;
            }
            el.hidden = false;
            util.modal(el, true);
            document.documentElement.classList.add('ts-ux-lock');
            requestAnimationFrame(function () {
                el.classList.add('is-open');
                el.querySelector('.ts-ux-drawer__panel').focus({preventScroll: true});
            });
        }
    }

    function close() {
        if (!el || el.hidden || !el.classList.contains('is-open')) {
            return;
        }
        el.classList.remove('is-open');
        util.modal(el, false);
        document.documentElement.classList.remove('ts-ux-lock');
        hideTimer = setTimeout(function () { el.hidden = true; }, util.reducedMotion() ? 0 : 260);
        if (lastFocus && lastFocus.focus && document.contains(lastFocus)) {
            lastFocus.focus({preventScroll: true});
        }
    }

    function itemHtml(item) {
        var opts = (item.options || []).map(function (o) {
            return util.escape(o.label) + ': ' + util.escape(o.value);
        }).join(' · ');
        return '<div class="ts-ux-drawer__item">' +
            (item.product_image && item.product_image.src
                ? '<img src="' + util.escape(item.product_image.src) + '" alt="" width="72" height="90">' : '') +
            '<div><p class="ts-ux-drawer__name"><a href="' + util.escape(item.product_url || '#') + '">' + util.escape(item.product_name) + '</a></p>' +
            (opts ? '<p class="ts-ux-drawer__opts">' + opts + '</p>' : '') +
            '<p class="ts-ux-drawer__qty"><span>Qty ' + Number(item.qty) + '</span>' + (item.product_price || '') + '</p></div></div>';
    }

    function paint(productIds) {
        var data = customerData.get('cart')() || {}, items = data.items || [], ids = (productIds || []).map(String);
        var match = items.filter(function (i) { return ids.indexOf(String(i.product_id)) !== -1; });
        if (!match.length && items.length) {
            match = [items[0]]; // most recent first
        }
        el.querySelector('.ts-ux-drawer__items').innerHTML = match.slice(0, 3).map(itemHtml).join('');
        el.querySelector('.ts-ux-drawer__ship').innerHTML = freeShipping.html(data.subtotalAmount);
        var count = Number(data.summary_count || 0);
        el.querySelector('.ts-ux-drawer__totals').innerHTML = count
            ? '<span>Bag subtotal (' + count + (count === 1 ? ' item' : ' items') + ')</span><strong>' +
                util.money(data.subtotalAmount || 0) + '</strong>'
            : '';
        el.classList.remove('is-loading');
        var pid = parseInt(ids[0] || (match[0] && match[0].product_id), 10);
        if (pid && pid !== recsFor) {
            recs(pid, items.map(function (i) { return i.product_id; }));
        }
    }

    function recs(pid, exclude) {
        recsFor = pid;
        var box = el.querySelector('.ts-ux-drawer__recs'), list = box.querySelector('ol');
        box.hidden = true;
        $.getJSON(util.config().cardsUrl, {related_to: pid, exclude: exclude.join(','), limit: 4}).done(function (res) {
            // the bag may have changed while this was on its way: never suggest what is already in it
            var inBag = ((customerData.get('cart')() || {}).items || []).map(function (i) { return Number(i.product_id); }),
                cards = (res.cards || []).filter(function (c) { return inBag.indexOf(Number(c.id)) === -1; }).slice(0, 2);
            if (recsFor !== pid || !cards.length) {
                return;
            }
            list.innerHTML = cards.map(function (c) { return c.html; }).join('');
            util.fixFormKeys(list);
            box.hidden = false;
            util.applyWidgets();
            $(document).trigger('ts-ux:products-added', [list.children]);
        });
    }

    /** Show the drawer now, fill it once the cart section reflects the new item. */
    function added(productIds) {
        open();
        el.classList.add('is-loading');
        var cart = customerData.get('cart'), before = (cart() || {}).data_id;
        if (pending) {
            pending.dispose();
        }
        pending = cart.subscribe(function (data) {
            if (data && data.data_id !== before) {
                pending.dispose();
                pending = null;
                paint(productIds);
            }
        });
        setTimeout(function () {
            if (pending) {
                pending.dispose();
                pending = null;
                paint(productIds);
            }
        }, 4000);
    }

    return {
        init: function () {
            $(document).on('ajax:addToCart', function (e, data) {
                if (data && data.response && data.response.backUrl) {
                    return;
                }
                // core reuses one productInfo array for the whole page, so productIds keeps every earlier add
                // too: keep only what is new since the last event (or the last id when the same item is re-added)
                var ids = ((data && data.productIds) || []).map(String),
                    fresh = ids.filter(function (id) { return seen.indexOf(id) === -1; });
                seen = ids;
                added(fresh.length ? fresh : ids.slice(-1));
            });
            $(document).on('ts-ux:added', function (e, data) {
                added((data && data.productIds) || []);
            });
        },
        close: close
    };
});
