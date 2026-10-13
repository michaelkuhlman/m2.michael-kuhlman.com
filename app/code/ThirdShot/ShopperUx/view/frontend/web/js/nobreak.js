/**
 * Product names never break at their hyphen ("12- / Pack"): each hyphenated word in a card / drawer / search name
 * is wrapped in a nowrap span. Inter (our subset) has no U+2011 non-breaking hyphen, so a span it is. Runs on load
 * and on whatever the page adds later (infinite scroll, strips, the bag drawer, live search).
 */
define([], function () {
    'use strict';

    var NAMES = '.product-item-name, .ts-ux-drawer__name, .ts-ux-search__name, .product-name',
        WORD = /[^\s-]+(?:-[^\s-]+)+/g,
        queued = false;

    function wrapText(node) {
        var text = node.nodeValue;
        WORD.lastIndex = 0;
        if (!WORD.test(text)) {
            return;
        }
        var frag = document.createDocumentFragment(), last = 0, m;
        WORD.lastIndex = 0;
        while ((m = WORD.exec(text))) {
            if (m.index > last) {
                frag.appendChild(document.createTextNode(text.slice(last, m.index)));
            }
            var span = document.createElement('span');
            span.className = 'ts-nobr';
            span.textContent = m[0];
            frag.appendChild(span);
            last = m.index + m[0].length;
        }
        if (last < text.length) {
            frag.appendChild(document.createTextNode(text.slice(last)));
        }
        node.parentNode.replaceChild(frag, node);
    }

    function run(root) {
        var els = (root || document).querySelectorAll(NAMES);
        Array.prototype.forEach.call(els, function (el) {
            if (el.hasAttribute('data-ts-nobr') || el.textContent.indexOf('-') < 0) {
                return;
            }
            el.setAttribute('data-ts-nobr', '');
            var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null), nodes = [], n;
            while ((n = walker.nextNode())) {
                if (!(n.parentNode.classList && n.parentNode.classList.contains('ts-nobr'))) {
                    nodes.push(n);
                }
            }
            nodes.forEach(wrapText);
        });
    }

    return function () {
        run(document);
        if (!window.MutationObserver) {
            return;
        }
        new MutationObserver(function () {
            if (queued) {
                return;
            }
            queued = true;
            requestAnimationFrame(function () {
                queued = false;
                run(document);
            });
        }).observe(document.body, {childList: true, subtree: true});
    };
});
