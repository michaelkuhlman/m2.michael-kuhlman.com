/**
 * Third Shot shopper UX - shared helpers: config, localStorage lists, form keys, init-script hand-off for HTML
 * fetched from another page, and price formatting.
 */
define(['jquery', 'mage/cookies'], function ($) {
    'use strict';

    var config = {};

    function read(key) {
        try {
            var v = JSON.parse(window.localStorage.getItem(key) || '[]');
            return Array.isArray(v) ? v : [];
        } catch (e) {
            return [];
        }
    }

    function write(key, list) {
        try {
            window.localStorage.setItem(key, JSON.stringify(list));
        } catch (e) { /* private mode / quota: features degrade quietly */ }
    }

    return {
        setConfig: function (c) { config = $.extend(config, c || {}); },
        config: function () { return config; },

        /** Ordered id lists in localStorage ("ts-ux-saved", "ts-ux-recent"). */
        list: function (key) { return read(key).map(Number).filter(Boolean); },
        setList: function (key, ids) {
            write(key, ids);
            $(document).trigger('ts-ux:list-changed', [key, ids]);
        },

        formKey: function () {
            return $.mage.cookies.get('form_key') || $('input[name="form_key"]').first().val() || '';
        },

        /** Cached pages carry somebody else's form key: use this shopper's. */
        fixFormKeys: function (root) {
            var key = this.formKey();
            if (key) {
                $(root).find('input[name="form_key"]').val(key);
            }
        },

        /**
         * Magento moves every text/x-magento-init script to the end of <body>, so HTML lifted out of a fetched
         * page arrives without its widgets (listing swatches, price boxes...). Copy the scripts that target
         * elements inside `nodes` (selector keys only, never "*" or "body") into `container`, so mage.apply()
         * picks them up. `nodes` must be only the NEW elements, or old ones would get their widgets twice.
         */
        adoptInitScripts: function (doc, nodes, container) {
            nodes = Array.prototype.slice.call(nodes);
            var holder = document.createElement('div');
            holder.className = 'ts-ux-init';
            holder.hidden = true;
            Array.prototype.forEach.call(doc.querySelectorAll('script[type="text/x-magento-init"]'), function (s) {
                var data, keep = {}, n = 0;
                try {
                    data = JSON.parse(s.textContent);
                } catch (e) {
                    return;
                }
                Object.keys(data).forEach(function (sel) {
                    if (sel === '*' || sel === 'body') {
                        return;
                    }
                    try {
                        if (nodes.some(function (el) {
                            return el.nodeType === 1 && (el.matches(sel) || el.querySelector(sel));
                        })) {
                            keep[sel] = data[sel];
                            n++;
                        }
                    } catch (e) { /* not a valid selector here */ }
                });
                if (n) {
                    var copy = document.createElement('script');
                    copy.type = 'text/x-magento-init';
                    copy.textContent = JSON.stringify(keep);
                    holder.appendChild(copy);
                }
            });
            if (holder.firstChild) {
                container.appendChild(holder);
            }
        },

        /** Run data-mage-init / x-magento-init on freshly inserted HTML. */
        applyWidgets: function () {
            require(['mage/apply/main'], function (mage) {
                mage.apply();
                $(document).trigger('ts-ux:widgets-applied');
            });
        },

        money: function (amount) {
            var f = config.priceFormat || '$%s';
            var n = (Math.round(Number(amount) * 100) / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            return f.replace('%s', n);
        },

        reducedMotion: function () {
            return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        },

        /**
         * Modal mode for a dialog appended to <body>: everything else in <body> becomes inert (no focus, no
         * clicks, hidden from screen readers) while it is open.
         */
        modal: function (dialog, on) {
            Array.prototype.forEach.call(document.body.children, function (n) {
                if (n === dialog || n.tagName === 'SCRIPT') {
                    return;
                }
                if (on && !n.inert) {
                    n.inert = true;
                    n.setAttribute('data-ts-ux-inert', '');
                } else if (!on && n.hasAttribute('data-ts-ux-inert')) {
                    n.inert = false;
                    n.removeAttribute('data-ts-ux-inert');
                }
            });
        },

        /** Tab / Shift+Tab wrap around inside box (for browsers without inert, and so Tab never leaves it). */
        trapTab: function (e, box) {
            if (e.key !== 'Tab') {
                return;
            }
            var f = Array.prototype.filter.call(box.querySelectorAll(
                'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select, textarea, iframe, [tabindex]:not([tabindex="-1"])'
            ), function (n) { return n.offsetWidth || n.offsetHeight || n.getClientRects().length; });
            if (!f.length) {
                return;
            }
            var first = f[0], last = f[f.length - 1], a = document.activeElement;
            if (e.shiftKey && (a === first || a === box)) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && a === last) {
                e.preventDefault();
                first.focus();
            }
        },

        escape: function (s) {
            return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
                return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', '\'': '&#39;'}[c];
            });
        }
    };
});
