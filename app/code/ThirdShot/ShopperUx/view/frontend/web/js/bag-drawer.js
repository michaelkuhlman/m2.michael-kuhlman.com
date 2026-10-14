/**
 * The bag drawer: ONE panel for the whole bag, opened by the header bag icon and after any add to bag (product
 * page, listing quick add, quick view, Saved, recommendations). It replaces Luma's dropdown mini cart.
 *
 * Head: "Your bag" + item count. After an add, a confirmation strip names what went in and the new line is marked.
 * Body (scrolls): free-shipping meter, editable lines (see bag-lines.js), "Pairs well with" one-tap picks.
 * Foot (always visible): subtotal, Checkout, View bag. Empty bag: a short message and shop links.
 */
define([
    'jquery',
    'ThirdShot_ShopperUx/js/util',
    'ThirdShot_ShopperUx/js/free-shipping',
    'ThirdShot_ShopperUx/js/bag-lines',
    'Magento_Customer/js/customer-data'
], function ($, util, freeShipping, lines, customerData) {
    'use strict';

    var dirty = false, el = null, lastFocus = null, pending = null, recsFor = null, hideTimer = null, seen = [], newIds = [];

    function q(sel) {
        return el.querySelector(sel);
    }

    function build() {
        var cfg = util.config(), cats = (cfg.categories || []).slice(0, 3);
        el = document.createElement('div');
        el.className = 'ts-bag';
        el.hidden = true;
        el.innerHTML = '<div class="ts-bag__backdrop" data-close></div>' +
            '<aside class="ts-bag__panel" role="dialog" aria-modal="true" aria-labelledby="ts-bag-title" tabindex="-1">' +
            '<header class="ts-bag__head"><h2 id="ts-bag-title" class="ts-bag__title">Your bag <span class="ts-bag__count"></span></h2>' +
            '<button type="button" class="ts-bag__close" data-close aria-label="Close bag"></button></header>' +
            '<div class="ts-bag__added" role="status" aria-live="polite"></div>' +
            '<div class="ts-bag__body">' +
            '<div class="ts-bag__ship"></div>' +
            '<ol class="ts-bag__lines" aria-label="Items in your bag"></ol>' +
            '<div class="ts-bag__skeleton" aria-hidden="true"><span></span><span></span></div>' +
            '<div class="ts-bag__empty" hidden><span class="ts-bag__empty-icon" aria-hidden="true"></span>' +
            '<p class="ts-bag__empty-title">Your bag is empty</p><p>Start with a paddle, a sleeve of balls or something for the bag.</p>' +
            '<div class="ts-bag__empty-links">' + cats.map(function (c) {
                return '<a href="' + util.escape(c.url) + '">' + util.escape(c.name) + '</a>';
            }).join('') + '</div></div>' +
            '<section class="ts-bag__recs" hidden aria-labelledby="ts-bag-recs-title"><h3 id="ts-bag-recs-title">Pairs well with</h3>' +
            '<ol class="product-items ts-bag__picks"></ol></section>' +
            '</div>' +
            '<footer class="ts-bag__foot">' +
            '<p class="ts-bag__total"><span>Subtotal</span><strong></strong></p>' +
            '<p class="ts-bag__note">Shipping and taxes at checkout.</p>' +
            '<a class="action primary checkout ts-bag__checkout" href="' + util.escape(cfg.checkoutUrl) + '"><span>Checkout</span></a>' +
            '<a class="ts-bag__view" href="' + util.escape(cfg.cartUrl) + '">View bag</a>' +
            '</footer></aside>';
        document.body.appendChild(el);
        lines.bind(q('.ts-bag__lines'), String(cfg.cartUrl || '/checkout/cart/').replace(/checkout\/cart\/?$/, ''));
        $(el).on('click', '[data-close]', close);
        $(q('.ts-bag__lines')).on('ts-bag:estimate', totals).on('ts-bag:changed', function () { dirty = true; });
        el.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                close();
            } else {
                util.trapTab(e, q('.ts-bag__panel'));
            }
        });
        // a "Choose options" pick opens quick view: step aside for it (an add there reopens the drawer)
        $(el).on('click', '[data-ts-qv]', close);
    }

    function open(mode) {
        if (!el) {
            build();
        }
        clearTimeout(hideTimer); // an add right after closing: cancel the pending hide
        el.classList.toggle('is-added', mode === 'added');
        if (mode !== 'added') {
            q('.ts-bag__added').innerHTML = '';
        }
        if (el.hidden || !el.classList.contains('is-open')) {
            if (el.hidden) {
                lastFocus = document.activeElement;
            }
            el.hidden = false;
            q('.ts-bag__body').scrollTop = 0;
            util.modal(el, true);
            document.documentElement.classList.add('ts-ux-lock');
            requestAnimationFrame(function () {
                el.classList.add('is-open');
                q('.ts-bag__panel').focus({preventScroll: true});
            });
        }
        if (mode !== 'added') {
            paint();
        }
    }

    function close() {
        if (!el || el.hidden || !el.classList.contains('is-open')) {
            return;
        }
        el.classList.remove('is-open');
        util.modal(el, false);
        // the bag page's table and totals are rendered by the server: show the drawer's changes there
        if (dirty && document.body.classList.contains('checkout-cart-index')) {
            window.location.reload();
            return;
        }
        dirty = false;
        document.documentElement.classList.remove('ts-ux-lock');
        hideTimer = setTimeout(function () {
            el.hidden = true;
            newIds = [];
            clearNew();
        }, util.reducedMotion() ? 0 : 300);
        if (lastFocus && lastFocus.focus && document.contains(lastFocus)) {
            lastFocus.focus({preventScroll: true});
        }
    }

    function items() {
        return ((customerData.get('cart')() || {}).items || []);
    }

    function totals() {
        var data = customerData.get('cart')() || {}, list = items(),
            est = lines.estimate(list), sub = est !== null ? est : Number(data.subtotalAmount || 0),
            count = lines.busy() ? lines.count(list) : Number(data.summary_count || lines.count(list));
        q('.ts-bag__count').textContent = count ? '(' + count + ')' : '';
        q('.ts-bag__total strong').textContent = util.money(sub);
        q('.ts-bag__ship').innerHTML = count ? freeShipping.html(sub) : '';
    }

    function paint() {
        var list = items(), empty = !list.length;
        el.classList.remove('is-loading');
        el.classList.toggle('is-empty', empty);
        q('.ts-bag__empty').hidden = !empty;
        lines.paint(list, newIds);
        totals();
        if (empty) {
            q('.ts-bag__recs').hidden = true;
            recsFor = null;
            return;
        }
        var pid = parseInt(newIds[0] || list[0].product_id, 10);
        if (pid && pid !== recsFor) {
            recs(pid, list.map(function (i) { return i.product_id; }));
        } else {
            dropPicksInBag();
        }
    }

    function confirmAdded() {
        var list = items(), ids = newIds.map(String),
            hit = list.filter(function (i) { return ids.indexOf(String(i.product_id)) !== -1; })[0] || list[0];
        q('.ts-bag__added').innerHTML = hit
            ? '<p><span class="ts-bag__added-icon" aria-hidden="true"></span><span><strong>' +
                String(hit.product_name || '') + '</strong> is in your bag</span></p>'
            : '';
        if (!newIds.length && hit) {
            newIds = [String(hit.product_id)];
        }
    }

    function dropPicksInBag() {
        var inBag = items().map(function (i) { return String(i.product_id); }), left = 0;
        Array.prototype.forEach.call(el.querySelectorAll('.ts-bag__picks > li'), function (li) {
            var gone = inBag.indexOf(li.getAttribute('data-ts-pick')) !== -1;
            li.hidden = gone;
            left += gone ? 0 : 1;
        });
        q('.ts-bag__recs').hidden = !left;
    }

    function recs(pid, exclude) {
        recsFor = pid;
        var box = q('.ts-bag__recs'), list = box.querySelector('ol');
        $.getJSON(util.config().cardsUrl, {related_to: pid, exclude: exclude.join(','), limit: 5}).done(function (res) {
            // the bag may have changed while this was on its way: never suggest what is already in it
            var inBag = items().map(function (i) { return Number(i.product_id); }),
                cards = (res.cards || []).filter(function (c) { return inBag.indexOf(Number(c.id)) === -1; }).slice(0, 3);
            if (recsFor !== pid) {
                return;
            }
            if (!cards.length) {
                box.hidden = true;
                return;
            }
            list.innerHTML = cards.map(function (c) {
                return c.html.replace(/^<li\b/, '<li data-ts-pick="' + Number(c.id) + '"');
            }).join('');
            util.fixFormKeys(list);
            box.hidden = false;
            util.applyWidgets();
            $(document).trigger('ts-ux:products-added', [list.children]);
        });
    }

    /** Show the drawer now, fill it once the cart section reflects the new item. */
    function clearNew() {
        Array.prototype.forEach.call(el.querySelectorAll('.ts-bag-line.is-new'), function (n) {
            n.classList.remove('is-new');
            var tag = n.querySelector('.ts-bag-line__tag');
            if (tag) { tag.remove(); }
        });
    }

    function added(productIds) {
        dirty = true;
        newIds = (productIds || []).map(String);
        open('added');
        clearNew();
        q('.ts-bag__body').scrollTop = 0; // the new line and the confirmation sit at the top
        el.classList.add('is-loading');
        q('.ts-bag__added').innerHTML = '';
        var cart = customerData.get('cart'), before = (cart() || {}).data_id;
        if (pending) {
            pending.dispose();
        }
        function done() {
            if (pending) {
                pending.dispose();
                pending = null;
            }
            confirmAdded();
            paint();
            hideAddedMessage();
        }
        var mine = pending = cart.subscribe(function (data) {
            if (data && data.data_id !== before) {
                done();
            }
        });
        setTimeout(function () {
            if (pending && pending === mine) {
                done();
            }
        }, 4000);
    }

    /** The drawer already says it: drop Magento's "You added X to your shopping cart." page message. */
    function hideAddedMessage() {
        var messages = customerData.get('messages'), sub = null;
        function strip(data) {
            data = data || {};
            var list = (data.messages || []).filter(function (m) {
                return !(m.type === 'success' &&
                    /to your (shopping cart|bag)\.?$|is in your bag\.?$/i.test(String(m.text || '').replace(/<[^>]*>/g, '').trim()));
            });
            if (data.messages && list.length !== data.messages.length) {
                customerData.set('messages', $.extend({}, data, {messages: list}));
            }
        }
        strip(messages());
        // the messages section can land a moment after the cart section: catch it for a few seconds
        sub = messages.subscribe(strip);
        setTimeout(function () { sub.dispose(); }, 5000);
    }

    /** Header bag icon: open the drawer instead of Luma's dropdown (the link still works before JS loads). */
    function bindIcon() {
        document.addEventListener('click', function (e) {
            var t = e.target.closest && e.target.closest('.minicart-wrapper .action.showcart');
            if (!t || e.metaKey || e.ctrlKey || e.shiftKey || e.button > 0) {
                return;
            }
            e.preventDefault();
            e.stopPropagation();
            if (document.body.classList.contains('checkout-cart-index')) {
                window.scrollTo({top: 0, behavior: util.reducedMotion() ? 'auto' : 'smooth'});
                return;
            }
            open('browse');
        }, true);
        document.documentElement.classList.add('ts-bag-ready');
    }

    /** Small bump on the header badge whenever the count goes up. */
    function bindBadge() {
        var last = Number((customerData.get('cart')() || {}).summary_count || 0);
        customerData.get('cart').subscribe(function (data) {
            var n = Number((data || {}).summary_count || 0);
            if (n > last && !util.reducedMotion()) {
                var b = document.querySelector('.minicart-wrapper .counter.qty');
                if (b) {
                    b.classList.remove('ts-bump');
                    void b.offsetWidth;
                    b.classList.add('ts-bump');
                }
            }
            last = n;
        });
    }

    return {
        init: function () {
            bindIcon();
            bindBadge();
            customerData.get('cart').subscribe(function () {
                if (el && !el.hidden && !el.classList.contains('is-loading')) {
                    paint();
                }
            });
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
        open: open,
        close: close
    };
});
