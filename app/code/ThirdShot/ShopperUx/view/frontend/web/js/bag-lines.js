/**
 * Bag drawer lines: renders the cart section's items as editable rows (photo, name, options, -/qty/+ stepper,
 * Remove, line total) and sends the changes through Magento's own mini-cart endpoints
 * (checkout/sidebar/updateItemQty, checkout/sidebar/removeItem). Those URLs invalidate the cart section, so
 * customer-data reloads it and the drawer repaints from the fresh data.
 *
 * The stepper is optimistic: the number and the line total change at once, the request follows 350 ms after the
 * last tap (so +,+,+ is one request), and lines with a request in flight keep the shopper's number until it lands.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util', 'Magento_Customer/js/customer-data'], function ($, util, customerData) {
    'use strict';

    var MAX = 99, pending = {}, root = null, base = '';

    function url(path) {
        return base + path;
    }

    function unitPrice(item) {
        var v = item.product_price_value;
        if (v && typeof v === 'object') {
            v = v.incl_tax !== undefined ? v.incl_tax : v.excl_tax;
        }
        v = Number(v);
        return isFinite(v) ? v : null;
    }

    function qtyOf(item) {
        var p = pending[item.item_id];
        return p ? p.qty : Number(item.qty);
    }

    function lineHtml(item, justAdded) {
        var id = util.escape(item.item_id), qty = qtyOf(item), unit = unitPrice(item),
            name = String(item.product_name || ''), // already HTML-escaped by Magento (DefaultItem)
            link = item.product_has_url !== false && item.product_url ? util.escape(item.product_url) : '',
            opts = (item.options || []).map(function (o) {
                return '<span>' + String(o.value) + '</span>'; // escaped by the configuration helper
            }).join(''),
            img = item.product_image && item.product_image.src
                ? '<img src="' + util.escape(item.product_image.src) + '" alt="" width="80" height="100" decoding="async">' : '',
            total = unit !== null ? util.money(unit * qty) : (item.product_price || ''),
            each = unit !== null && qty > 1 ? '<span class="ts-bag-line__each">' + util.money(unit) + ' each</span>' : '',
            edit = (item.options || []).length && item.configure_url
                ? '<a class="ts-bag-line__link" href="' + util.escape(item.configure_url) + '">Edit</a>' : '';
        return '<li class="ts-bag-line' + (justAdded ? ' is-new' : '') + (pending[item.item_id] ? ' is-pending' : '') +
            '" data-item="' + id + '">' +
            (link ? '<a class="ts-bag-line__img" href="' + link + '" tabindex="-1" aria-hidden="true">' + img + '</a>'
                : '<span class="ts-bag-line__img">' + img + '</span>') +
            '<div class="ts-bag-line__main">' +
            '<div class="ts-bag-line__top"><p class="ts-bag-line__name">' +
            (link ? '<a href="' + link + '">' + name + '</a>' : name) + '</p>' +
            '<p class="ts-bag-line__price"><strong>' + total + '</strong>' + each + '</p></div>' +
            (opts ? '<p class="ts-bag-line__opts">' + opts + '</p>' : '') +
            (justAdded ? '<p class="ts-bag-line__tag">Just added</p>' : '') +
            '<div class="ts-bag-line__row">' +
            '<div class="ts-bag-qty" role="group" aria-label="Quantity for ' + name + '">' +
            '<button type="button" class="ts-bag-qty__btn ts-bag-qty__minus" data-step="-1" aria-label="One less"' +
            (qty <= 1 ? ' disabled' : '') + '></button>' +
            '<output class="ts-bag-qty__val" aria-live="polite">' + qty + '</output>' +
            '<button type="button" class="ts-bag-qty__btn ts-bag-qty__plus" data-step="1" aria-label="One more"' +
            (qty >= MAX ? ' disabled' : '') + '></button></div>' +
            '<div class="ts-bag-line__links">' + edit +
            '<button type="button" class="ts-bag-line__link ts-bag-line__remove" aria-label="Remove ' + name + '">Remove</button>' +
            '</div></div><p class="ts-bag-line__err" role="alert" hidden></p></div></li>';
    }

    function find(id) {
        var items = (customerData.get('cart')() || {}).items || [];
        for (var i = 0; i < items.length; i++) {
            if (String(items[i].item_id) === String(id)) {
                return items[i];
            }
        }
        return null;
    }

    function error(line, msg) {
        var e = line && line.querySelector('.ts-bag-line__err');
        if (e) {
            e.textContent = msg || 'That did not work. Please try again.';
            e.hidden = false;
        }
    }

    function post(path, data) {
        data.form_key = util.formKey();
        return $.ajax({url: url(path), type: 'POST', dataType: 'json', data: data, global: true});
    }

    /** Repaint one line in place from the data we have (keeps focus on the button that was tapped). */
    function refreshLine(line, item) {
        var qty = qtyOf(item), unit = unitPrice(item);
        line.querySelector('.ts-bag-qty__val').textContent = qty;
        line.querySelector('.ts-bag-qty__minus').disabled = qty <= 1;
        line.querySelector('.ts-bag-qty__plus').disabled = qty >= MAX;
        if (unit !== null) {
            line.querySelector('.ts-bag-line__price').innerHTML = '<strong>' + util.money(unit * qty) + '</strong>' +
                (qty > 1 ? '<span class="ts-bag-line__each">' + util.money(unit) + ' each</span>' : '');
        }
        line.classList.toggle('is-pending', !!pending[item.item_id]);
    }

    function step(line, delta) {
        var id = line.getAttribute('data-item'), item = find(id);
        if (!item) {
            return;
        }
        var p = pending[id] || (pending[id] = {qty: Number(item.qty), confirmed: Number(item.qty), timer: null, req: null});
        p.qty = Math.max(1, Math.min(MAX, p.qty + delta));
        p.landed = undefined;
        line.querySelector('.ts-bag-line__err').hidden = true;
        refreshLine(line, item);
        $(root).trigger('ts-bag:estimate');
        clearTimeout(p.timer);
        p.timer = setTimeout(function () {
            p.timer = null;
            send(id);
        }, 350);
    }

    /** Send the shopper's number; compare with what the SERVER last confirmed, never with a possibly stale section. */
    function send(id) {
        var p = pending[id];
        if (!p || p.timer) {
            return;
        }
        if (p.req) { // one request per line at a time; the newest number goes when this one lands
            p.again = true;
            return;
        }
        if (p.qty === p.confirmed) { // back where the server is: nothing to send
            var item = find(id), line = lineEl(id);
            if (item && Number(item.qty) === p.confirmed) {
                delete pending[id];
                if (line) { refreshLine(line, item); }
            } else {
                p.landed = dataId(); // the section is behind: release on its next update
            }
            return;
        }
        var qty = p.qty;
        p.req = post('checkout/sidebar/updateItemQty/', {item_id: id, item_qty: qty}).done(function (res) {
            if (res && res.success) {
                p.confirmed = qty;
                $(root).trigger('ts-bag:changed');
            } else {
                fail(id, res && res.error_message);
            }
        }).fail(function () {
            fail(id);
        }).always(function () {
            if (pending[id] !== p) {
                return;
            }
            p.req = null;
            if (p.again || p.qty !== p.confirmed) {
                p.again = false;
                send(id);
            } else {
                // released by the first cart section newer than this (see paint): the section is the truth then
                p.landed = dataId();
            }
        });
    }

    function fail(id, msg) {
        delete pending[id];
        error(lineEl(id), msg);
        customerData.reload(['cart'], true);
    }

    function dataId() {
        return (customerData.get('cart')() || {}).data_id;
    }

    function lineEl(id) {
        return root && root.querySelector('.ts-bag-line[data-item="' + String(id).replace(/"/g, '') + '"]');
    }

    function remove(line) {
        var id = line.getAttribute('data-item');
        if (pending[id]) {
            clearTimeout(pending[id].timer);
            delete pending[id];
        }
        line.style.height = line.offsetHeight + 'px';
        line.classList.add('is-removing');
        // focus somewhere sensible before the row (and the button inside it) goes away
        var next = line.nextElementSibling || line.previousElementSibling;
        var target = next ? next.querySelector('.ts-bag-line__remove') : root.closest('[tabindex="-1"]');
        if (target) {
            target.focus({preventScroll: true});
        }
        requestAnimationFrame(function () {
            line.style.height = '0px';
        });
        post('checkout/sidebar/removeItem/', {item_id: id}).done(function (res) {
            if (res && res.success) {
                $(root).trigger('ts-bag:changed');
            } else {
                line.classList.remove('is-removing');
                line.style.height = '';
                error(line, res && res.error_message);
            }
        }).fail(function () {
            line.classList.remove('is-removing');
            line.style.height = '';
            error(line);
        });
    }

    return {
        /** list = the <ol>; baseUrl = store base URL with trailing slash. */
        bind: function (list, baseUrl) {
            root = list;
            base = baseUrl;
            $(list).on('click', '.ts-bag-qty__btn', function () {
                step(this.closest('.ts-bag-line'), Number(this.getAttribute('data-step')));
            }).on('click', '.ts-bag-line__remove', function () {
                remove(this.closest('.ts-bag-line'));
            });
        },

        /**
         * Paint the list from the cart section. Lines already on screen are updated in place (no flicker, focus
         * stays put); new ones are added, gone ones dropped.
         */
        paint: function (items, newIds) {
            newIds = (newIds || []).map(String);
            // release an optimistic number once a cart section newer than the server's answer has arrived
            var current = dataId();
            Object.keys(pending).forEach(function (id) {
                var p = pending[id], here = items.some(function (i) { return String(i.item_id) === id; });
                if (!here || (!p.req && !p.timer && p.landed !== undefined && current !== p.landed)) {
                    delete pending[id];
                }
            });
            var have = {}, order = items.map(function (i) { return String(i.item_id); });
            Array.prototype.forEach.call(root.querySelectorAll('.ts-bag-line'), function (li) {
                var id = li.getAttribute('data-item');
                if (order.indexOf(id) === -1 && !li.classList.contains('is-removing')) {
                    li.remove();
                } else if (order.indexOf(id) === -1) {
                    setTimeout(function () { li.remove(); }, 260);
                } else {
                    have[id] = li;
                }
            });
            var prev = null;
            items.forEach(function (item) {
                var id = String(item.item_id), li = have[id], fresh = newIds.indexOf(String(item.product_id)) !== -1;
                if (li && (!fresh || li.classList.contains('is-new')) && li.getAttribute('data-sig') === sig(item)) {
                    refreshLine(li, item);
                } else {
                    var tmp = document.createElement('ol');
                    tmp.innerHTML = lineHtml(item, fresh);
                    var n = tmp.firstChild;
                    n.setAttribute('data-sig', sig(item));
                    if (li) {
                        var a = li.contains(document.activeElement) ? document.activeElement : null,
                            sel = !a ? '' : a.hasAttribute('data-step') ? '[data-step="' + a.getAttribute('data-step') + '"]'
                                : a.classList.contains('ts-bag-line__remove') ? '.ts-bag-line__remove'
                                : a.tagName === 'A' ? 'a.ts-bag-line__link, .ts-bag-line__name a' : '';
                        li.replaceWith(n);
                        var f = sel && n.querySelector(sel);
                        if (f) { f.focus({preventScroll: true}); }
                    } else {
                        root.insertBefore(n, prev ? prev.nextSibling : root.firstChild);
                    }
                    li = n;
                }
                prev = li;
            });
        },

        /** Subtotal as the shopper sees it right now (optimistic quantities included). */
        estimate: function (items) {
            var sum = 0, ok = true;
            items.forEach(function (item) {
                var u = unitPrice(item);
                if (u === null) { ok = false; }
                sum += (u || 0) * qtyOf(item);
            });
            return ok ? sum : null;
        },

        count: function (items) {
            return items.reduce(function (n, i) { return n + qtyOf(i); }, 0);
        },

        busy: function () {
            return Object.keys(pending).length > 0;
        }
    };

    function sig(item) {
        return [item.product_id, item.product_name, (item.options || []).map(function (o) { return o.value; }).join('|'),
            item.product_image && item.product_image.src].join('~');
    }
});
