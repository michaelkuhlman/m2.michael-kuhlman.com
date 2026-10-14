/**
 * Product-card extras on every grid (category, search, home widgets, related, Saved, Recently viewed):
 * a heart to save the product without an account, and a Quick view button.
 * Plus the product-page "Save" button and the header Saved counter.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    var KEY = 'ts-ux-saved', MAX = 48;

    function saved() {
        return util.list(KEY);
    }

    function isSaved(id) {
        return saved().indexOf(Number(id)) !== -1;
    }

    function toggle(id) {
        id = Number(id);
        var list = saved(), on = list.indexOf(id) === -1;
        list = list.filter(function (x) { return x !== id; });
        if (on) {
            list.unshift(id);
        }
        util.setList(KEY, list.slice(0, MAX));
        toast(on);
        return on;
    }

    function toast(on) {
        var t = document.querySelector('.ts-ux-toast');
        if (!t) {
            t = document.createElement('div');
            t.className = 'ts-ux-toast';
            t.setAttribute('role', 'status');
            document.body.appendChild(t);
        }
        t.innerHTML = on
            ? 'Saved. <a href="' + util.escape(util.config().savedUrl) + '">View saved</a>'
            : 'Removed from saved';
        t.classList.add('is-on');
        clearTimeout(t._h);
        t._h = setTimeout(function () { t.classList.remove('is-on'); }, 2600);
    }

    function productId(info) {
        var el = info.querySelector('[data-product-id]');
        if (el) {
            return Number(el.getAttribute('data-product-id'));
        }
        el = info.querySelector('input[name="product"]');
        if (el) {
            return Number(el.value);
        }
        var m = /(\d+)$/.exec(info.id || '');
        return m ? Number(m[1]) : 0;
    }

    function heartLabel(on, name) {
        return (on ? 'Remove ' : 'Save ') + name + (on ? ' from saved' : ' for later');
    }

    function enhance(root) {
        $(root || document).find('.product-item-info').each(function () {
            var info = this, item = info.closest('.product-item');
            if (!item || item.querySelector('.ts-ux-card-tools') || document.body.classList.contains('ts-ux-qv-frame')) {
                return;
            }
            var id = productId(info), link = info.querySelector('.product-item-link');
            if (!id || !link) {
                return;
            }
            var name = $.trim(link.textContent), on = isSaved(id);
            var tools = document.createElement('div');
            tools.className = 'ts-ux-card-tools';
            tools.innerHTML = '<button type="button" class="ts-ux-heart" data-ts-save="' + id + '" aria-pressed="' + on + '"' +
                ' aria-label="' + util.escape(heartLabel(on, name)) + '" title="' + (on ? 'Saved' : 'Save for later') + '"></button>' +
                '<button type="button" class="ts-ux-eye" data-ts-qv="' + id + '" data-ts-qv-url="' + util.escape(link.href) + '"' +
                ' aria-label="Quick view: ' + util.escape(name) + '" title="Quick view"><span>Quick view</span></button>';
            tools.querySelector('.ts-ux-heart').dataset.name = name;
            // core list.phtml gives configurable products a plain add form, and Magento answers it with a redirect
            // to the product page: send those to quick view (options first) like the ShopperUx cards do
            var add = info.querySelector('form[data-role="tocart-form"] .action.tocart');
            if (add && !add.hasAttribute('data-ts-qv') && info.querySelector('[class*="swatch-opt"]')) {
                add.setAttribute('data-ts-qv', id);
                add.setAttribute('data-ts-qv-url', link.href);
                add.title = 'Choose options';
                var label = add.querySelector('span');
                if (label) { label.textContent = 'Choose options'; }
            }
            item.classList.add('ts-ux-has-tools');
            info.appendChild(tools);
        });
    }

    function paintHearts() {
        var list = saved();
        $('[data-ts-save]').each(function () {
            var on = list.indexOf(Number(this.getAttribute('data-ts-save'))) !== -1;
            this.setAttribute('aria-pressed', String(on));
            if (this.dataset.name) {
                this.setAttribute('aria-label', heartLabel(on, this.dataset.name));
            }
            this.title = on ? 'Saved' : 'Save for later';
            var txt = this.querySelector('.ts-ux-save-text');
            if (txt) {
                txt.textContent = on ? 'Saved' : 'Save for later';
            }
        });
        var n = list.length;
        $('.ts-ux-saved-link').toggleClass('has-items', n > 0).find('.ts-ux-saved-count').text(n ? String(n) : '');
        $('.ts-ux-saved-link').attr('aria-label', 'Saved items' + (n ? ' (' + n + ')' : ''));
    }

    function pdpSave() {
        if (!document.body.classList.contains('catalog-product-view') || document.querySelector('.ts-ux-save')) {
            return;
        }
        var form = document.getElementById('product_addtocart_form'),
            id = form && form.querySelector('input[name="product"]'),
            title = document.querySelector('.product-info-main .page-title');
        var box = document.querySelector('.product-info-main .product-social-links') ||
            document.querySelector('.product-info-main .box-tocart');
        if (!id || !box) {
            return;
        }
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'ts-ux-save';
        b.setAttribute('data-ts-save', id.value);
        b.dataset.name = title ? $.trim(title.textContent) : 'this product';
        b.innerHTML = '<span class="ts-ux-save-text">Save for later</span>';
        if (box.classList.contains('product-social-links')) {
            box.insertBefore(b, box.firstChild);
        } else {
            box.parentNode.insertBefore(b, box.nextSibling);
        }
    }

    return {
        saved: saved,
        enhance: enhance,
        init: function () {
            enhance(document);
            pdpSave();
            paintHearts();
            $(document).on('ts-ux:listing-updated contentUpdated', function () {
                enhance(document);
                paintHearts();
            });
            $(document).on('ts-ux:products-added', function () {
                enhance(document);
                paintHearts();
            });
            $(document).on('ts-ux:list-changed', function (e, key) {
                if (key === KEY) {
                    paintHearts();
                }
            });
            window.addEventListener('storage', function (e) {
                if (e.key === KEY) {
                    paintHearts();
                }
            });
            $(document).on('click', '[data-ts-save]', function (e) {
                e.preventDefault();
                e.stopPropagation();
                var on = toggle(this.getAttribute('data-ts-save'));
                if (on) {
                    this.classList.remove('is-pop');
                    void this.offsetWidth;
                    this.classList.add('is-pop');
                }
            });
        }
    };
});
