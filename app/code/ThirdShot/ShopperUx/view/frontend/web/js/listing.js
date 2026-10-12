/**
 * Category + search result pages without page reloads.
 *
 *  - Instant filtering / sorting / paging: filter links, swatches, "remove" chips, "Clear all", the sorter and
 *    the price slider fetch the next page in the background (full-page cached, ~100 ms) and swap only the
 *    product column and the filter sidebar. The URL follows (pushState), so Back/Forward, refresh and shared
 *    links all work. Hovering a filter prefetches it, so most clicks feel instant.
 *  - Infinite scroll: the next page's products are appended as you near the end of the grid (the first few
 *    pages automatically, then a "Load more" button so the footer stays reachable), with a "Showing 9 of 12"
 *    meter. Leaving for a product and pressing Back restores the loaded pages and the scroll position.
 *  - Phones: the filter drawer stays open while you filter and gets a "Show N items" button.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    var MAIN = '.columns .column.main',
        SIDE = '.sidebar.sidebar-main',
        AUTO_PAGES = 3,
        RESTORE_KEY = 'ts-ux-list:',
        cache = {},
        controller = null,
        autoLoaded = 0,
        observer = null,
        loadingMore = false,
        prevPage = null,
        api;

    function sameListing(url) {
        try {
            var u = new URL(url, location.href);
            return u.origin === location.origin && u.pathname === location.pathname;
        } catch (e) {
            return false;
        }
    }

    function fetchPage(url, signal) {
        if (cache[url]) {
            return cache[url];
        }
        var p = fetch(url, {credentials: 'same-origin', signal: signal}).then(function (r) {
            if (!r.ok) {
                throw new Error('HTTP ' + r.status);
            }
            return r.text();
        }).then(function (html) {
            return new DOMParser().parseFromString(html, 'text/html');
        });
        cache[url] = p;
        p.catch(function () { delete cache[url]; });
        return p;
    }

    function prefetch(url) {
        if (!url || !sameListing(url) || (navigator.connection && navigator.connection.saveData)) {
            return;
        }
        fetchPage(url).catch(function () {});
    }

    /* ---------- drawer / accordion state that must survive a swap ---------- */

    function uiState() {
        var open = [];
        $(SIDE).find('.filter-options-item').each(function () {
            if ($(this).hasClass('active')) {
                open.push($.trim($(this).find('.filter-options-title').first().text()));
            }
        });
        return {drawer: $(SIDE).find('.block.filter').hasClass('active'), open: open};
    }

    function restoreUi(state) {
        var $filter = $(SIDE).find('#layered-filter-block');
        setTimeout(function () { // widgets initialise a task or two after mage/apply
            if (state.drawer && $filter.length && $filter.data('mageCollapsible')) {
                $filter.collapsible('activate');
            }
            var $acc = $(SIDE).find('#narrow-by-list');
            if ($acc.length && $acc.data('mageAccordion')) {
                $acc.find('.filter-options-item').each(function (i) {
                    var t = $.trim($(this).find('.filter-options-title').first().text());
                    if (state.open.indexOf(t) !== -1) {
                        $acc.accordion('activate', i);
                    }
                });
            }
            decorateSidebar();
        }, 60);
    }

    /* ---------- navigation ---------- */

    function navigate(url, opts) {
        opts = opts || {};
        if (controller) {
            controller.abort();
        }
        controller = window.AbortController ? new AbortController() : null;
        var state = uiState();
        $('.swatch-option-tooltip').hide(); // its swatch is about to be replaced while hovered
        $('body').addClass('ts-ux-loading').attr('aria-busy', 'true');
        return fetchPage(url, controller ? controller.signal : undefined).then(function (doc) {
            var newMain = doc.querySelector(MAIN), main = document.querySelector(MAIN);
            if (!newMain || !main) {
                throw new Error('no listing');
            }
            var newSide = doc.querySelector(SIDE), side = document.querySelector(SIDE);
            main.innerHTML = newMain.innerHTML;
            var nodes = [main];
            if (side && newSide) {
                side.innerHTML = newSide.innerHTML;
                nodes.push(side);
            } else if (side) {
                side.innerHTML = '';
            }
            util.adoptInitScripts(doc, nodes, main);
            util.fixFormKeys(main);
            document.title = doc.title;
            if (opts.push !== false) {
                history.pushState({tsUx: 1}, '', url);
            }
            autoLoaded = 0;
            $(document).one('ts-ux:widgets-applied', function () { restoreUi(state); });
            util.applyWidgets();
            afterSwap();
            if (opts.scroll !== false && !state.drawer) {
                scrollToResults();
            }
            announce();
        }).catch(function (e) {
            if (e && e.name === 'AbortError') {
                return;
            }
            location.href = url; // anything odd: fall back to a normal page load
        }).then(function () {
            $('body').removeClass('ts-ux-loading').removeAttr('aria-busy');
        });
    }

    function scrollToResults(always) {
        var el = document.querySelector(MAIN + ' .toolbar-products') || document.querySelector(MAIN);
        if (!el) {
            return;
        }
        var header = document.querySelector('.page-header'),
            offset = (header ? header.offsetHeight : 0) + 16,
            top = el.getBoundingClientRect().top + window.pageYOffset - offset;
        if (always || window.pageYOffset > top) {
            window.scrollTo({top: top, behavior: util.reducedMotion() ? 'auto' : 'smooth'});
        }
    }

    function announce() {
        var live = document.getElementById('ts-ux-live');
        if (!live) {
            live = document.createElement('div');
            live.id = 'ts-ux-live';
            live.className = 'ts-ux-sr';
            live.setAttribute('aria-live', 'polite');
            document.body.appendChild(live);
        }
        live.textContent = totalText();
    }

    function total() {
        var nums = $(MAIN).find('.toolbar-products').first().find('.toolbar-amount .toolbar-number');
        return nums.length ? parseInt(nums.last().text().replace(/\D/g, ''), 10) || 0 : $(MAIN).find('.product-items > li').length;
    }

    function totalText() {
        var n = total();
        return n === 1 ? '1 item' : n + ' items';
    }

    /* ---------- infinite scroll ---------- */

    function list() {
        return document.querySelector(MAIN + ' .products.wrapper .product-items');
    }

    /** The bottom toolbar's pager is the live one (Luma prints a hidden copy in the top toolbar). */
    function pagerLink(scope, cls) {
        var pages = (scope || document).querySelectorAll(MAIN + ' .pages');
        var a = pages.length ? pages[pages.length - 1].querySelector('.action.' + cls) : null;
        return a ? a.href : null;
    }

    function nextUrl() {
        return pagerLink(document, 'next');
    }

    function shown() {
        var l = list();
        return l ? l.querySelectorAll(':scope > li.product-item').length : 0;
    }

    function buildMore() {
        var l = list(), wrap = l && l.closest('.products.wrapper');
        $(MAIN).find('.ts-ux-more, .ts-ux-prev').remove();
        if (!wrap) {
            return;
        }
        var more = document.createElement('div');
        more.className = 'ts-ux-more';
        more.innerHTML = '<p class="ts-ux-more__count" aria-live="polite"></p>' +
            '<div class="ts-ux-more__bar" aria-hidden="true"><span></span></div>' +
            '<button type="button" class="action secondary ts-ux-more__btn">Load more</button>' +
            '<div class="ts-ux-more__sentinel" aria-hidden="true"></div>';
        wrap.parentNode.insertBefore(more, wrap.nextSibling);
        more.querySelector('button').addEventListener('click', function () { loadMore(true); });
        prevPage = pagerLink(document, 'previous');
        if (prevPage) {
            var prev = document.createElement('div');
            prev.className = 'ts-ux-prev';
            prev.innerHTML = '<button type="button" class="action secondary">Show earlier items</button>';
            wrap.parentNode.insertBefore(prev, wrap);
            prev.querySelector('button').addEventListener('click', loadPrevious);
        }
        updateMore();
        if (observer) {
            observer.disconnect();
        }
        if ('IntersectionObserver' in window) {
            observer = new IntersectionObserver(function (entries) {
                if (entries[0].isIntersecting && autoLoaded < AUTO_PAGES && nextUrl()) {
                    loadMore(false);
                }
            }, {rootMargin: '0px 0px 700px 0px'});
            observer.observe(more.querySelector('.ts-ux-more__sentinel'));
        }
    }

    function updateMore() {
        var more = document.querySelector('.ts-ux-more');
        if (!more) {
            return;
        }
        var n = shown(), t = Math.max(total(), n), has = !!nextUrl();
        more.hidden = t <= 0 || (!has && t <= n && !document.querySelector('.ts-ux-prev'));
        more.querySelector('.ts-ux-more__count').textContent = has
            ? 'Showing ' + n + ' of ' + t
            : (t > 0 ? 'You’ve seen all ' + t + (t === 1 ? ' item' : ' items') : '');
        more.querySelector('.ts-ux-more__bar span').style.width = (t ? Math.min(100, n / t * 100) : 0) + '%';
        more.querySelector('button').hidden = !has;
        more.classList.toggle('is-done', !has);
    }

    function appendFrom(doc, where) {
        var src = doc.querySelector(MAIN + ' .product-items'), l = list();
        if (!src || !l) {
            return [];
        }
        var have = {};
        Array.prototype.forEach.call(l.querySelectorAll('[data-container="product-grid"]'), function (el) {
            have[el.id] = 1;
        });
        var items = Array.prototype.filter.call(src.querySelectorAll(':scope > li'), function (li) {
            var info = li.querySelector('[data-container]');
            return !(info && have[info.id]);
        }).map(function (li) {
            return document.importNode(li, true);
        });
        var frag = document.createDocumentFragment();
        items.forEach(function (li) {
            li.classList.add('ts-ux-new');
            frag.appendChild(li);
        });
        if (where === 'start') {
            l.insertBefore(frag, l.firstChild);
        } else {
            l.appendChild(frag);
        }
        util.adoptInitScripts(doc, items, l.parentNode);
        util.fixFormKeys(l);
        return items;
    }

    function swapPager(doc) {
        var theirs = doc.querySelectorAll(MAIN + ' .pages'), html = theirs.length ? theirs[theirs.length - 1].innerHTML : '';
        Array.prototype.forEach.call(document.querySelectorAll(MAIN + ' .pages'), function (el) {
            el.innerHTML = html;
        });
    }

    function loadMore(byUser) {
        var url = nextUrl();
        if (!url || loadingMore) {
            return Promise.resolve();
        }
        loadingMore = true;
        if (!byUser) {
            autoLoaded++;
        }
        var more = document.querySelector('.ts-ux-more');
        if (more) {
            more.classList.add('is-loading');
        }
        return fetchPage(url).then(function (doc) {
            var items = appendFrom(doc, 'end');
            swapPager(doc);
            util.applyWidgets();
            $(document).trigger('ts-ux:products-added', [items]);
            if (byUser && items[0]) {
                var link = items[0].querySelector('a.product-item-link');
                if (link) {
                    link.focus({preventScroll: true});
                }
            }
            loadedPages(1);
        }).catch(function () {
            location.href = url;
        }).then(function () {
            loadingMore = false;
            if (more) {
                more.classList.remove('is-loading');
            }
            updateMore();
        });
    }

    function loadPrevious() {
        var btn = document.querySelector('.ts-ux-prev');
        if (!prevPage) {
            return;
        }
        fetchPage(prevPage).then(function (doc) {
            var before = document.documentElement.scrollHeight;
            var items = appendFrom(doc, 'start');
            window.scrollBy(0, document.documentElement.scrollHeight - before);
            util.applyWidgets();
            $(document).trigger('ts-ux:products-added', [items]);
            prevPage = pagerLink(doc, 'previous');
            if (!prevPage && btn) {
                btn.remove();
            }
            updateMore();
        });
    }

    /* Remember how far the shopper got, so Back from a product page lands in the same place. */
    function loadedPages(add) {
        var st = readRestore() || {pages: 1};
        st.pages = (st.pages || 1) + (add || 0);
        st.y = window.pageYOffset;
        st.t = Date.now();
        try {
            sessionStorage.setItem(RESTORE_KEY + location.href, JSON.stringify(st));
        } catch (e) { /* ignore */ }
        return st.pages;
    }

    function readRestore() {
        try {
            var st = JSON.parse(sessionStorage.getItem(RESTORE_KEY + location.href) || 'null');
            return st && Date.now() - st.t < 30 * 60 * 1000 ? st : null;
        } catch (e) {
            return null;
        }
    }

    function clearRestore() {
        try {
            sessionStorage.removeItem(RESTORE_KEY + location.href);
        } catch (e) { /* ignore */ }
    }

    function restoreIfBack() {
        var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
        var st = readRestore();
        clearRestore();
        if (!st || !nav || nav.type !== 'back_forward') {
            return;
        }
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual';
        }
        var pages = st.pages || 1, y = st.y || 0;
        (function step() {
            if (pages > 1 && nextUrl()) {
                pages--;
                loadMore(true).then(step);
                return;
            }
            window.scrollTo(0, y);
            loadedPages(0);
        })();
    }

    /* ---------- sidebar extras ---------- */

    function decorateSidebar() {
        var $filter = $(SIDE).find('.block.filter');
        if (!$filter.length || $filter.find('.ts-ux-apply').length) {
            return;
        }
        var bar = $('<div class="ts-ux-apply"><button type="button" class="action primary"></button></div>');
        bar.find('button').text('Show ' + totalText()).on('click', function () {
            $filter.find('#layered-filter-block').addBack('#layered-filter-block').collapsible('deactivate');
            // the open drawer locks body scroll, so jump to the results once it has closed
            setTimeout(function () { scrollToResults(true); }, 60);
        });
        $filter.find('.filter-content').append(bar);
        var count = $filter.find('.filter-current .items > li').length;
        $filter.find('.filter-title strong').attr('data-ts-count', count || null);
    }

    // phones: Luma hides "Now shopping by", so mirror the active filters as removable chips under the toolbar
    function buildChips() {
        var main = document.querySelector(MAIN), old = main && main.querySelector('.ts-ux-chips');
        if (old) {
            old.parentNode.removeChild(old);
        }
        var items = document.querySelectorAll(SIDE + ' .filter-current .item'),
            toolbar = main && main.querySelector('.toolbar-products');
        if (!items.length || !toolbar) {
            return;
        }
        var box = document.createElement('div');
        box.className = 'ts-ux-chips';
        box.setAttribute('aria-label', 'Active filters');
        Array.prototype.forEach.call(items, function (li) {
            var remove = li.querySelector('a.remove, a.action.remove');
            if (!remove) {
                return;
            }
            var label = $.trim($(li).find('.filter-label').text()),
                value = $.trim($(li).find('.filter-value').text()),
                a = document.createElement('a');
            a.href = remove.href;
            a.className = 'ts-ux-chip';
            a.setAttribute('aria-label', 'Remove filter ' + label + ' ' + value);
            a.innerHTML = '<span>' + util.escape(label) + ':</span> ' + util.escape(value);
            box.appendChild(a);
        });
        var clear = document.querySelector(SIDE + ' .filter-actions a.filter-clear');
        if (clear && items.length > 1) {
            var c = document.createElement('a');
            c.href = clear.href;
            c.className = 'ts-ux-chip ts-ux-chip--clear';
            c.textContent = 'Clear all';
            box.appendChild(c);
        }
        toolbar.parentNode.insertBefore(box, toolbar.nextSibling);
    }

    function afterSwap() {
        $('body').addClass('ts-ux-listing');
        buildChips();
        buildMore();
        $(document).trigger('ts-ux:listing-updated');
    }

    /* ---------- event wiring ---------- */

    function isListingLink(a) {
        var href = a.getAttribute('href');
        return href && href.charAt(0) !== '#' && !a.target && sameListing(a.href);
    }

    function bind() {
        $(document).on('click', SIDE + ' .block.filter a, ' + MAIN + ' .block.filter a, ' + MAIN + ' .ts-ux-chips a', function (e) {
            if (e.ctrlKey || e.metaKey || e.shiftKey || e.button || !isListingLink(this)) {
                return;
            }
            e.preventDefault();
            navigate(this.href);
        });
        $(document).on('click', MAIN + ' .pages a', function (e) {
            if (e.ctrlKey || e.metaKey || e.shiftKey || e.button || !isListingLink(this)) {
                return;
            }
            e.preventDefault();
            navigate(this.href);
        });
        $(document).on('mouseenter focusin touchstart', SIDE + ' .block.filter a', function () {
            if (isListingLink(this)) {
                prefetch(this.href);
            }
        });
        // product clicks: remember pages + scroll for Back
        $(document).on('click', MAIN + ' .product-items a', function () {
            loadedPages(0);
        });
        window.addEventListener('pagehide', function () {
            if (shown() > 0) {
                loadedPages(0);
            }
        });
        window.addEventListener('popstate', function () {
            if (sameListing(location.href)) {
                navigate(location.href, {push: false, scroll: false});
            }
        });
    }

    api = {
        navigate: navigate,
        prefetch: prefetch,
        init: function () {
            if (!document.querySelector(MAIN + ' .products.wrapper') && !document.querySelector(SIDE + ' .block.filter')) {
                return;
            }
            window.tsUxListing = api;
            history.replaceState({tsUx: 1}, '', location.href);
            bind();
            afterSwap();
            restoreUi({drawer: false, open: []});
            restoreIfBack();
        }
    };

    return api;
});
