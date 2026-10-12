/**
 * Two-handle price slider for layered navigation. Dragging updates the labels; letting go (or typing a value
 * and pressing Enter / leaving the field) applies the range through the instant listing navigation.
 */
define(['jquery', 'ThirdShot_ShopperUx/js/util'], function ($, util) {
    'use strict';

    return function (config, form) {
        var $f = $(form),
            from = form.querySelector('[data-role="from"]'),
            to = form.querySelector('[data-role="to"]'),
            fromIn = form.querySelector('[data-role="from-input"]'),
            toIn = form.querySelector('[data-role="to-input"]'),
            fill = form.querySelector('[data-role="fill"]'),
            min = Number(config.min),
            max = Number(config.max),
            applied = [Number(config.from), Number(config.to)];

        function clamp(v, lo, hi) {
            v = Math.round(Number(v));
            return isNaN(v) ? lo : Math.min(hi, Math.max(lo, v));
        }

        function paint() {
            var a = Number(from.value), b = Number(to.value), span = max - min || 1;
            fill.style.left = ((a - min) / span * 100) + '%';
            fill.style.right = (100 - (b - min) / span * 100) + '%';
            fromIn.value = a;
            toIn.value = b;
            from.setAttribute('aria-valuetext', util.money(a));
            to.setAttribute('aria-valuetext', util.money(b));
            // keep the lower thumb grabbable when both sit at the right end
            from.style.zIndex = a > max - (max - min) * 0.1 ? 5 : 3;
        }

        function apply() {
            var a = Number(from.value), b = Number(to.value), range;
            if (a === applied[0] && b === applied[1]) {
                return;
            }
            applied = [a, b];
            if (a <= min && b >= max) {
                range = null;
            } else {
                // Magento treats the upper bound as exclusive: +0.01 keeps an item priced exactly at the bound
                range = (a > min ? a : '') + '-' + (b < max ? (b + 0.01).toFixed(2) : '');
            }
            var url = config.url;
            url = range === null
                ? url.replace(new RegExp('([?&])' + config.param + '=__RANGE__&?'), '$1').replace(/[?&]$/, '')
                : url.replace('__RANGE__', encodeURIComponent(range));
            if (window.tsUxListing) {
                window.tsUxListing.navigate(url);
            } else {
                location.href = url;
            }
        }

        $(from).on('input', function () {
            if (Number(from.value) > Number(to.value)) {
                from.value = to.value;
            }
            paint();
        });
        $(to).on('input', function () {
            if (Number(to.value) < Number(from.value)) {
                to.value = from.value;
            }
            paint();
        });
        // pointer: apply on release. Keyboard: arrow keys fire change per step, so wait for a pause (or blur),
        // otherwise every step would rebuild the sidebar under the user's focus.
        var kbd = false, timer = null;
        function later() {
            clearTimeout(timer);
            timer = setTimeout(apply, 700);
        }
        $(from).add(to)
            .on('keydown', function () { kbd = true; })
            .on('pointerdown', function () { kbd = false; })
            .on('change', function () {
                if (kbd) {
                    later();
                } else {
                    apply();
                }
            })
            .on('blur', function () {
                if (timer) {
                    clearTimeout(timer);
                    timer = null;
                    apply();
                }
            });
        $(fromIn).on('change', function () {
            from.value = clamp(fromIn.value, min, Number(to.value));
            paint();
            apply();
        });
        $(toIn).on('change', function () {
            to.value = clamp(toIn.value, Number(from.value), max);
            paint();
            apply();
        });
        $f.on('submit', function (e) {
            e.preventDefault();
            fromIn.blur();
            toIn.blur();
            from.value = clamp(fromIn.value, min, max);
            to.value = clamp(toIn.value, Number(from.value), max);
            paint();
            apply();
        });
        paint();
    };
});
