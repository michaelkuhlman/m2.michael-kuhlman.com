/**
 * Bag page: quantity steppers (- / +) that save on their own, no "Update Shopping Cart" button needed.
 * The change posts to Magento's own updatePost (errors arrive as normal store messages); then the item rows, the mini bag, the shipping
 * estimate and the totals refresh in place. Setting 0 (or Remove) takes the item out.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util', 'Magento_Customer/js/customer-data'], function ($, util, customerData) {
    'use strict';

    var timers = {}, pend = {}, busy = 0;

    function stepper(input) {
        if (input.closest('.ts-ux-qty')) {
            return;
        }
        var wrap = document.createElement('div');
        wrap.className = 'ts-ux-qty';
        input.parentNode.insertBefore(wrap, input);
        var minus = document.createElement('button'), plus = document.createElement('button');
        minus.type = plus.type = 'button';
        minus.className = 'ts-ux-qty__btn ts-ux-qty__minus';
        plus.className = 'ts-ux-qty__btn ts-ux-qty__plus';
        var name = $.trim($(input).closest('tbody').find('.product-item-name').text());
        minus.setAttribute('aria-label', 'Decrease quantity of ' + name);
        plus.setAttribute('aria-label', 'Increase quantity of ' + name);
        wrap.appendChild(minus);
        wrap.appendChild(input);
        wrap.appendChild(plus);
        function sync() {
            minus.classList.toggle('is-remove', Number(input.value) <= 1);
            minus.setAttribute('aria-label', (Number(input.value) <= 1 ? 'Remove ' : 'Decrease quantity of ') + name);
        }
        minus.addEventListener('click', function () {
            input.value = Math.max(0, (parseFloat(input.value) || 1) - 1);
            sync();
            queue(input);
        });
        plus.addEventListener('click', function () {
            input.value = (parseFloat(input.value) || 0) + 1;
            sync();
            queue(input);
        });
        input.addEventListener('change', function () { sync(); queue(input); });
        $(input).on('ts-ux:qty-synced', sync);
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                input.blur();
            }
        });
        sync();
    }

    function queue(input) {
        var id = input.name;
        clearTimeout(timers[id]);
        pend[id] = true;
        $(input).closest('tbody').addClass('ts-ux-pending');
        timers[id] = setTimeout(function () { save(input); }, 450);
    }

    function save(input) {
        var qty = Math.max(0, Math.round(parseFloat(input.value) || 0)),
            row = $(input).closest('tbody'),
            data = {form_key: util.formKey()};
        delete pend[input.name];
        if (String(qty) === String(input.getAttribute('data-item-qty'))) {
            row.removeClass('ts-ux-pending');
            return;
        }
        if (qty === 0) {
            var del = row.find('.action-delete[data-post]');
            if (del.length) {
                row.addClass('ts-ux-removing');
                del.trigger('click'); // Magento's own remove (posts and reloads the bag)
                return;
            }
        }
        data[input.name] = qty;
        data.update_cart_action = 'update_qty';
        busy++;
        $('body').addClass('ts-ux-cart-busy');
        watchCart();
        $.ajax({
            url: util.config().updateCartUrl,
            type: 'POST',
            dataType: 'html',
            data: data
        }).done(function (html) {
            refresh(html);
        }).fail(function () {
            location.reload();
        }).always(function () {
            busy--;
            if (!busy) {
                $('body').removeClass('ts-ux-cart-busy');
            }
        });
    }

    /** Swap in the fresh item rows from the bag page Magento answered with. */
    function refresh(html) {
        var doc = new DOMParser().parseFromString(html, 'text/html'),
            fresh = doc.getElementById('shopping-cart-table'),
            table = document.getElementById('shopping-cart-table');
        if (!fresh || !table) {
            location.reload(); // e.g. the bag is now empty
            return;
        }
        Array.prototype.forEach.call(table.querySelectorAll('tbody.cart.item'), function (tb) {
            var input = tb.querySelector('input.qty');
            var match = input && fresh.querySelector('input.qty[name="' + input.name + '"]');
            if (!match) {
                tb.remove();
                return;
            }
            var ftb = match.closest('tbody');
            ['.col.price', '.col.subtotal'].forEach(function (sel) {
                var a = tb.querySelector(sel), b = ftb.querySelector(sel);
                if (a && b) {
                    a.innerHTML = b.innerHTML;
                }
            });
            input.setAttribute('data-item-qty', match.getAttribute('data-item-qty'));
            if (pend[input.name]) {
                return; // another change is queued for this row: keep what the shopper typed
            }
            if (document.activeElement !== input) {
                input.value = match.value;
            }
            $(input).trigger('ts-ux:qty-synced');
            $(tb).removeClass('ts-ux-pending');
        });
    }

    /** When the cart section has the new totals, re-run the shipping estimate and totals. */
    function watchCart() {
        var cart = customerData.get('cart'), before = (cart() || {}).data_id, sub;
        sub = cart.subscribe(function (d) {
            if (d && d.data_id !== before) {
                sub.dispose();
                recalc();
            }
        });
    }

    function recalc() {
        require([
            'Magento_Checkout/js/model/quote',
            'Magento_Checkout/js/model/shipping-rate-registry',
            'Magento_Checkout/js/model/cart/totals-processor/default',
            'Magento_Checkout/js/model/cart/cache'
        ], function (quote, rateRegistry, totals, cartCache) {
            var addr = quote.shippingAddress();
            cartCache.clear('rates');
            cartCache.clear('totals');
            if (addr) {
                rateRegistry.set(addr.getCacheKey(), null);
                rateRegistry.set(addr.getKey && addr.getKey(), null);
                quote.shippingAddress(addr); // re-estimates rates (free shipping can switch on/off)
                totals.estimateTotals(addr);
            }
        });
    }

    return {
        init: function () {
            var table = document.getElementById('shopping-cart-table');
            if (!table || !util.config().updateCartUrl) {
                return;
            }
            document.body.classList.add('ts-ux-cart-live');
            Array.prototype.forEach.call(table.querySelectorAll('input.qty'), stepper);
        }
    };
});
