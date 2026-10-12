<?php
/**
 * Two-handle price slider in place of the layered-navigation price ranges. Without JS it still works: the
 * min/max number inputs submit as a GET form with the same "price=from-to" parameter Magento understands.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Block;

use Magento\Catalog\Model\Layer\Filter\FilterInterface;
use Magento\Framework\View\Element\Template;
use ThirdShot\ShopperUx\Model\PriceBounds;

class PriceSlider extends Template
{
    protected $_template = 'ThirdShot_ShopperUx::price-slider.phtml';

    private ?FilterInterface $filter = null;

    public function __construct(
        Template\Context $context,
        private readonly PriceBounds $priceBounds,
        array $data = []
    ) {
        parent::__construct($context, $data);
    }

    public function setFilter(FilterInterface $filter): self
    {
        $this->filter = $filter;
        return $this;
    }

    /**
     * @return array<string, mixed>|null null = fall back to Magento's range list
     */
    public function getConfig(): ?array
    {
        if (!$this->filter) {
            return null;
        }
        $bounds = $this->priceBounds->forLayer($this->filter->getLayer());
        if (!$bounds || $bounds[1] - $bounds[0] < 2) {
            return null;
        }
        [$min, $max] = $bounds;
        $from = $min;
        $to = $max;
        $applied = (string)$this->getRequest()->getParam($this->filter->getRequestVar(), '');
        if (preg_match('/^(\d*(?:\.\d+)?)-(\d*(?:\.\d+)?)$/', $applied, $m)) {
            $from = $m[1] !== '' ? max($min, min($max, (float)$m[1])) : $min;
            // the upper bound arrives as "to + 0.01" (Magento treats it as exclusive)
            $to = $m[2] !== '' ? max($from, min($max, (float)$m[2] - 0.01)) : $max;
        }
        $symbol = '$';
        try {
            $symbol = (string)$this->_storeManager->getStore()->getCurrentCurrency()->getCurrencySymbol() ?: '$';
        } catch (\Throwable) {
        }
        return [
            'min' => $min,
            'max' => $max,
            'from' => floor($from),
            'to' => round($to),
            'applied' => $applied !== '',
            'symbol' => $symbol,
            'param' => $this->filter->getRequestVar(),
            'url' => $this->getUrl('*/*/*', [
                '_current' => true,
                '_use_rewrite' => true,
                '_escape' => false,
                '_query' => [$this->filter->getRequestVar() => '__RANGE__', 'p' => null],
            ]),
        ];
    }

    /**
     * Query parameters to carry through the no-JS form (everything but the price and the page).
     *
     * @return array<string, string>
     */
    public function getCarriedParams(): array
    {
        $out = [];
        foreach ($this->getRequest()->getQueryValue() ?? [] as $k => $v) {
            if (is_string($v) && $k !== 'p' && $k !== $this->filter?->getRequestVar()) {
                $out[(string)$k] = $v;
            }
        }
        return $out;
    }
}
