/**
 * Magento's own search suggestions (plain query terms) are replaced by the live product search
 * (ThirdShot_ShopperUx/js/live-search); the widget keeps its other duties (mobile toggle, empty-submit guard).
 *
 * Phones: the theme keeps the field hidden until the magnifier label is "active", but core only activates it when
 * the input gains focus, and a hidden input cannot gain focus. So the label opens (and closes) the field itself.
 */
define(['jquery'], function ($) {
    'use strict';

    return function (widget) {
        $.widget('mage.quickSearch', widget, {
            _create: function () {
                this._super();
                var self = this;
                this.searchLabel.on('click.tsUx', function (e) {
                    if (!window.matchMedia('(max-width: 767px)').matches) {
                        return;
                    }
                    e.preventDefault();
                    if (self.isActive()) {
                        self.setActiveState(false);
                        self.element.trigger('blur');
                    } else {
                        self.setActiveState(true);
                        self.element.trigger('focus');
                    }
                });
            },
            _onPropertyChange: function () {},
            _onKeyDown: function () {
                return true;
            }
        });

        return $.mage.quickSearch;
    };
});
