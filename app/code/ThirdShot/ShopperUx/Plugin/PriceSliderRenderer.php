<?php
/**
 * Swaps the price filter's range list for the slider; every other filter renders as before.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Plugin;

use Magento\Catalog\Model\Layer\Filter\FilterInterface;
use Magento\LayeredNavigation\Block\Navigation\FilterRenderer;
use ThirdShot\ShopperUx\Block\PriceSlider;

class PriceSliderRenderer
{
    public function aroundRender(FilterRenderer $subject, callable $proceed, FilterInterface $filter)
    {
        if ($filter->getRequestVar() !== 'price') {
            return $proceed($filter);
        }
        /** @var PriceSlider $slider */
        $slider = $subject->getLayout()->createBlock(PriceSlider::class);
        $html = $slider->setFilter($filter)->toHtml();
        return $html !== '' ? $html : $proceed($filter);
    }
}
