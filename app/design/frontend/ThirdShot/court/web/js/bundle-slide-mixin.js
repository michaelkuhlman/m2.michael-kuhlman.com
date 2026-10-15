/**
 * "Customize and add to bag" scrolled the options panel to the very top of the window, under the sticky header,
 * so its heading was hidden. Stop below the header and move focus to the panel heading.
 */
define(['jquery'], function ($) {
    'use strict';

    return function (widget) {
        $.widget('mage.slide', widget, {
            _show: function () {
                var $panel = $(this.options.bundleOptionsContainer),
                    header = document.querySelector('.page-header'),
                    offset = (header ? header.getBoundingClientRect().height : 0) + 16;

                $panel.slideDown(800);
                $('html, body').animate({scrollTop: Math.max(0, $panel.offset().top - offset)}, 600);
                $panel.find('#customizeTitle').attr('tabindex', '-1').trigger('focus');
            }
        });

        return $.mage.slide;
    };
});
