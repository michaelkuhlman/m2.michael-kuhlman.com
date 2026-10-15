/**
 * Sorting / per-page / view-mode changes go through the instant listing navigation instead of a page load.
 * A new sort order starts again from the first page; a new page size keeps the current first product in view.
 *
 * The theme's sorter offers "key~dir" values (Price: low to high / high to low) so phones, which have no
 * direction arrow, can sort both ways: such a value sets the order AND the direction in one navigation. Picking
 * a plain key (Featured, Name, Relevance) drops any direction, so it sorts the natural way.
 */
define(['jquery'], function ($) {
    'use strict';

    return function (widget) {
        $.widget('mage.productListToolbarForm', widget, {
            _processSelect: function (event) {
                var value = String(event.currentTarget.options[event.currentTarget.selectedIndex].value),
                    parts;

                if (event.data.paramName !== this.options.order) {
                    return this._super(event);
                }
                parts = value.split('~');
                this._tsGo(parts[0], parts[1] || null);
            },

            /** Navigate with a new sort order (and direction, or none = the default direction). */
            _tsGo: function (order, dir) {
                var base = this.options.url.split('?')[0],
                    params = this.getUrlParams(),
                    query;

                delete params[this.options.page];
                params[this.options.order] = order;
                if (order == this.options.orderDefault) { // eslint-disable-line eqeqeq
                    delete params[this.options.order];
                }
                if (dir) {
                    params[this.options.direction] = dir;
                } else {
                    delete params[this.options.direction];
                }
                query = $.param(params);
                query = base + (query.length ? '?' + query : '');
                if (this.options.post || !window.tsUxListing) {
                    location.href = query;
                    return;
                }
                window.tsUxListing.navigate(query);
            },

            changeUrl: function (paramName, paramValue, defaultValue) {
                if (this.options.post || !window.tsUxListing) {
                    return this._super(paramName, paramValue, defaultValue);
                }
                var base = this.options.url.split('?')[0],
                    params = this.getUrlParams(),
                    page = Number(this.getCurrentPage()),
                    newPage;

                delete params[this.options.page];
                // per page: like core, keep the first product of the current page in view
                if (paramName === this.options.limit && page > 1) {
                    newPage = Math.floor(this.getCurrentLimit() * (page - 1) / paramValue) + 1;
                    if (newPage > 1) {
                        params[this.options.page] = newPage;
                    }
                }
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
