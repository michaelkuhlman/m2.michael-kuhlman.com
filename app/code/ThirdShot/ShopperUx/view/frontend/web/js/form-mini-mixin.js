/**
 * Magento's own search suggestions (plain query terms) are replaced by the live product search
 * (ThirdShot_ShopperUx/js/live-search); the widget keeps its other duties (mobile toggle, empty-submit guard).
 */
define(['jquery'], function ($) {
    'use strict';

    return function (widget) {
        $.widget('mage.quickSearch', widget, {
            _onPropertyChange: function () {},
            _onKeyDown: function () {
                return true;
            }
        });

        return $.mage.quickSearch;
    };
});
