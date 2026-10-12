/**
 * Back to top: a small round button after two screens of scrolling.
 */
define(['ThirdShot_ShopperUx/js/util'], function (util) {
    'use strict';

    return {
        init: function () {
            var b = document.createElement('button'), ticking = false;
            b.type = 'button';
            b.className = 'ts-ux-top';
            b.setAttribute('aria-label', 'Back to top');
            b.tabIndex = -1;
            document.body.appendChild(b);
            b.addEventListener('click', function () {
                window.scrollTo({top: 0, behavior: util.reducedMotion() ? 'auto' : 'smooth'});
                var skip = document.querySelector('.logo') || document.body;
                if (skip.focus) {
                    skip.focus({preventScroll: true});
                }
            });
            window.addEventListener('scroll', function () {
                if (ticking) {
                    return;
                }
                ticking = true;
                requestAnimationFrame(function () {
                    var on = window.pageYOffset > window.innerHeight * 2;
                    b.classList.toggle('is-on', on);
                    b.tabIndex = on ? 0 : -1;
                    ticking = false;
                });
            }, {passive: true});
        }
    };
});
