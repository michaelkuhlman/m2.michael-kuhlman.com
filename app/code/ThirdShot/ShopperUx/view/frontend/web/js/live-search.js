/**
 * Live search: as you type, the header search shows matching products (photo, price), matching categories and
 * a "See all results" link, after ~120 ms and without leaving the page. Arrow keys move through the results,
 * Enter opens one (or searches), Escape closes. An empty box shows recent searches and popular categories.
 * Replaces Magento's plain term suggestions (form-mini mixin turns those off).
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    var RECENT = 'ts-ux-searches';

    return function () {
        var input = document.getElementById('search'),
            form = document.getElementById('search_mini_form');
        if (!input || !form || input.dataset.tsUx) {
            return;
        }
        input.dataset.tsUx = '1';
        var cfg = util.config(),
            panel = document.createElement('div'),
            cache = {},
            timer = null,
            ctrl = null,
            active = -1,
            lastQuery = null;

        panel.className = 'ts-ux-search';
        panel.id = 'ts-ux-search';
        panel.hidden = true;
        panel.setAttribute('role', 'listbox');
        panel.setAttribute('aria-label', 'Search suggestions');
        form.appendChild(panel);
        input.setAttribute('aria-controls', 'ts-ux-search');
        input.setAttribute('aria-autocomplete', 'list');

        function recent() {
            try {
                return JSON.parse(localStorage.getItem(RECENT) || '[]').slice(0, 5);
            } catch (e) {
                return [];
            }
        }

        function remember(q) {
            q = $.trim(q);
            if (q.length < 2) {
                return;
            }
            var list = recent().filter(function (x) { return x.toLowerCase() !== q.toLowerCase(); });
            list.unshift(q);
            try {
                localStorage.setItem(RECENT, JSON.stringify(list.slice(0, 5)));
            } catch (e) { /* ignore */ }
        }

        function highlight(text, q) {
            var safe = util.escape(text), words = q.trim().split(/\s+/).filter(function (w) { return w.length > 1; });
            words.forEach(function (w) {
                var re = new RegExp('(' + util.escape(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
                safe = safe.replace(re, '<mark>$1</mark>');
            });
            return safe;
        }

        function open(html) {
            panel.innerHTML = html;
            panel.hidden = false;
            active = -1;
            input.setAttribute('aria-expanded', 'true');
            form.classList.add('ts-ux-search-open');
        }

        function close() {
            panel.hidden = true;
            active = -1;
            input.setAttribute('aria-expanded', 'false');
            input.removeAttribute('aria-activedescendant');
            form.classList.remove('ts-ux-search-open');
        }

        function options() {
            return panel.querySelectorAll('[role="option"]');
        }

        function move(dir) {
            var opts = options();
            if (!opts.length) {
                return;
            }
            if (active >= 0 && opts[active]) {
                opts[active].classList.remove('is-active');
            }
            active += dir; // -1 = back in the text box
            if (active >= opts.length) {
                active = -1;
            } else if (active < -1) {
                active = opts.length - 1;
            }
            if (active >= 0) {
                opts[active].classList.add('is-active');
                opts[active].scrollIntoView({block: 'nearest'});
                input.setAttribute('aria-activedescendant', opts[active].id);
            } else {
                input.removeAttribute('aria-activedescendant');
            }
        }

        function idle() {
            var r = recent(), cats = cfg.categories || [], html = '';
            if (r.length) {
                html += '<div class="ts-ux-search__group"><p class="ts-ux-search__label">Recent searches</p><div class="ts-ux-search__chips">' +
                    r.map(function (q, i) {
                        return '<a role="option" id="ts-ux-s-r' + i + '" class="ts-ux-chip" href="' +
                            util.escape(cfg.searchUrl + '?q=' + encodeURIComponent(q)) + '">' + util.escape(q) + '</a>';
                    }).join('') + '</div></div>';
            }
            if (cats.length) {
                html += '<div class="ts-ux-search__group"><p class="ts-ux-search__label">Popular categories</p><div class="ts-ux-search__chips">' +
                    cats.map(function (c, i) {
                        return '<a role="option" id="ts-ux-s-c' + i + '" class="ts-ux-chip" href="' + util.escape(c.url) + '">' +
                            util.escape(c.name) + '</a>';
                    }).join('') + '</div></div>';
            }
            if (html) {
                open(html);
            } else {
                close();
            }
        }

        function render(data, q) {
            var html = '';
            if (data.categories && data.categories.length) {
                html += '<div class="ts-ux-search__group"><p class="ts-ux-search__label">Categories</p><div class="ts-ux-search__chips">' +
                    data.categories.map(function (c, i) {
                        return '<a role="option" id="ts-ux-s-k' + i + '" class="ts-ux-chip" href="' + util.escape(c.url) + '">' +
                            highlight(c.name, q) + '</a>';
                    }).join('') + '</div></div>';
            }
            if (data.products && data.products.length) {
                html += '<div class="ts-ux-search__group"><p class="ts-ux-search__label">Products</p><ul class="ts-ux-search__products">' +
                    data.products.map(function (p, i) {
                        return '<li><a role="option" id="ts-ux-s-p' + i + '" class="ts-ux-search__product" href="' + util.escape(p.url) + '">' +
                            '<img src="' + util.escape(p.image) + '" alt="" width="48" height="60" loading="lazy">' +
                            '<span class="ts-ux-search__name">' + highlight(p.name, q) + '</span>' +
                            '<span class="ts-ux-search__price">' + p.price_html + '</span></a></li>';
                    }).join('') + '</ul></div>';
                html += '<a role="option" id="ts-ux-s-all" class="ts-ux-search__all" href="' + util.escape(data.all_url) + '">' +
                    'See all results for “' + util.escape(q) + '”</a>';
            }
            if (!html) {
                html = '<p class="ts-ux-search__empty">No matches for “' + util.escape(q) + '” yet. Try “paddle”, “balls” or “grip”.</p>';
            }
            open(html);
            panel.classList.remove('is-loading');
        }

        function query(q) {
            if (cache[q]) {
                render(cache[q], q);
                return;
            }
            if (ctrl) {
                ctrl.abort();
            }
            ctrl = window.AbortController ? new AbortController() : null;
            panel.classList.add('is-loading');
            fetch(cfg.suggestUrl + '?q=' + encodeURIComponent(q), {
                credentials: 'same-origin',
                signal: ctrl ? ctrl.signal : undefined,
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            }).then(function (r) {
                return r.json();
            }).then(function (data) {
                cache[q] = data;
                if ($.trim(input.value) === q) {
                    render(data, q);
                }
            }).catch(function () {
                panel.classList.remove('is-loading');
            });
        }

        function onInput() {
            var q = $.trim(input.value);
            if (q === lastQuery) {
                return;
            }
            lastQuery = q;
            clearTimeout(timer);
            if (q.length < 2) {
                idle();
                return;
            }
            timer = setTimeout(function () { query(q); }, cache[q] ? 0 : 120);
        }

        input.addEventListener('input', onInput);
        input.addEventListener('focus', function () {
            lastQuery = null;
            onInput();
        });
        input.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                if (panel.hidden) {
                    onInput();
                }
                e.preventDefault();
                move(e.key === 'ArrowDown' ? 1 : -1);
            } else if (e.key === 'Enter') {
                var opts = options();
                if (active >= 0 && opts[active]) {
                    e.preventDefault();
                    remember(input.value);
                    location.href = opts[active].href;
                } else {
                    remember(input.value);
                }
            } else if (e.key === 'Escape') {
                if (!panel.hidden) {
                    e.stopPropagation();
                    close();
                }
            }
        });
        form.addEventListener('submit', function () { remember(input.value); });
        panel.addEventListener('mousedown', function (e) { e.preventDefault(); }); // keep focus in the input
        panel.addEventListener('click', function (e) {
            if (e.target.closest('a')) {
                remember(input.value);
            }
        });
        document.addEventListener('click', function (e) {
            if (!form.contains(e.target)) {
                close();
            }
        });
        input.addEventListener('blur', function () {
            setTimeout(function () {
                if (!form.contains(document.activeElement)) {
                    close();
                }
            }, 150);
        });
        // "/" focuses search from anywhere (not while typing in a field)
        document.addEventListener('keydown', function (e) {
            var t = e.target;
            if (e.key === '/' && !e.ctrlKey && !e.metaKey && !/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) && !t.isContentEditable) {
                e.preventDefault();
                var label = document.querySelector('.block-search .label');
                if (label && window.getComputedStyle(input).visibility === 'hidden') {
                    label.click();
                }
                input.focus();
            }
        });
    };
});
