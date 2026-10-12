/**
 * Sorting / per-page / view-mode changes go through the instant listing navigation instead of a page load.
 * A new sort order starts again from the first page.
 */
define(['jquery'], function ($) {
    'use strict';

    return function (widget) {
        $.widget('mage.productListToolbarForm', widget, {
            changeUrl: function (paramName, paramValue, defaultValue) {
                if (this.options.post || !window.tsUxListing) {
                    return this._super(paramName, paramValue, defaultValue);
                }
                var base = this.options.url.split('?')[0],
                    params = this.getUrlParams();

                delete params[this.options.page];
                params[paramName] = paramValue;
                if (paramValue == defaultValue) { // eslint-disable-line eqeqeq
                    delete params[paramName];
                }
                params = $.param(params);
                window.tsUxListing.navigate(base + (params.length ? '?' + params : ''));
            }
        });

        return $.mage.productListToolbarForm;
    };
});
