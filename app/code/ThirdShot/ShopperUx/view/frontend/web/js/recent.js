/**
 * Recently viewed: product pages are remembered in this browser (ids only, newest first); any
 * [data-ts-ux-strip="recent"] or [data-ts-ux-strip="saved"] container renders those products as cards.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    var KEY = 'ts-ux-recent', MAX = 12;

    function track() {
        if (!document.body.classList.contains('catalog-product-view') || document.body.classList.contains('ts-ux-qv-frame')) {
            return;
        }
        var input = document.querySelector('#product_addtocart_form input[name="product"]');
        var id = input ? Number(input.value) : 0;
        if (!id) {
            return;
        }
        var list = util.list(KEY).filter(function (x) { return x !== id; });
        list.unshift(id);
        util.setList(KEY, list.slice(0, MAX));
    }

    function currentProductId() {
        var input = document.querySelector('#product_addtocart_form input[name="product"]');
        return input ? Number(input.value) : 0;
    }

    function render(box) {
        var kind = box.getAttribute('data-ts-ux-strip'),
            key = kind === 'saved' ? 'ts-ux-saved' : KEY,
            limit = Number(box.getAttribute('data-limit') || 12),
            skip = currentProductId(),
            ids = util.list(key).filter(function (x) { return x !== skip; }).slice(0, limit),
            list = box.querySelector('.product-items'),
            empty = box.querySelector('[data-role="empty"]');
        if (!ids.length) {
            box.classList.remove('is-filled');
            if (list) {
                list.innerHTML = '';
            }
            box.hidden = !empty;
            if (empty) {
                empty.hidden = false;
            }
            return;
        }
        $.getJSON(util.config().cardsUrl, {ids: ids.join(',')}).done(function (res) {
            var cards = (res && res.cards) || [];
            if (!cards.length) {
                box.hidden = !empty;
                if (empty) {
                    empty.hidden = false;
                }
                return;
            }
            list.innerHTML = cards.map(function (c) { return c.html; }).join('');
            util.fixFormKeys(list);
            box.hidden = false;
            box.classList.add('is-filled');
            if (empty) {
                empty.hidden = true;
            }
            var count = box.querySelector('[data-role="count"]');
            if (count) {
                count.textContent = cards.length === 1 ? '1 item' : cards.length + ' items';
            }
            util.applyWidgets();
            $(document).trigger('ts-ux:products-added', [list.children]);
        });
    }

    return {
        init: function () {
            track();
            $('[data-ts-ux-strip]').each(function () { render(this); });
            $(document).on('ts-ux:list-changed', function (e, key) {
                if (key === 'ts-ux-saved') {
                    $('[data-ts-ux-strip="saved"]').each(function () {
                        var box = this, ids = util.list('ts-ux-saved');
                        // unsaving on the Saved page: fade the card out instead of a full re-render
                        $(box).find('.product-item').each(function () {
                            var b = this.querySelector('[data-ts-save]');
                            if (b && ids.indexOf(Number(b.getAttribute('data-ts-save'))) === -1) {
                                $(this).addClass('ts-ux-gone');
                            }
                        });
                        setTimeout(function () { render(box); }, 280);
                    });
                }
            });
            $(document).on('click', '[data-ts-ux-clear]', function () {
                var key = this.getAttribute('data-ts-ux-clear') === 'saved' ? 'ts-ux-saved' : KEY;
                util.setList(key, []);
                $('[data-ts-ux-strip]').each(function () { render(this); });
            });
        }
    };
});
