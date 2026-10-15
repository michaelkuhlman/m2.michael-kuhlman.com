/**
 * Picking a swatch after a failed "Add to bag" left core's "This is a required field." under the swatches:
 * the hidden swatch input gets its value, but nothing re-validates it. Re-check that input on every pick.
 */
define(['jquery'], function ($) {
    'use strict';

    return function (widget) {
        $.widget('mage.SwatchRenderer', widget, {
            _OnClick: function ($this, $widget) {
                var result = this._super($this, $widget),
                    $input = $this.parents('.' + this.options.classes.attributeClass)
                        .find('.' + this.options.classes.attributeInput);

                if ($input.length && $input.val() && $input.hasClass('mage-error')) {
                    if ($input.closest('form').data('validator')) {
                        $input.valid();
                    } else {
                        $input.removeClass('mage-error').attr('aria-invalid', 'false');
                        $input.siblings('div.mage-error').remove();
                    }
                    $input.siblings('[role="listbox"]').attr('aria-invalid', 'false');
                }

                return result;
            }
        });

        return $.mage.SwatchRenderer;
    };
});
