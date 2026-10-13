<?php
/**
 * Shorter labels for the top-level categories in the main menu ("Apparel & Headwear" -> "Apparel"), so the
 * one-row desktop header keeps room for a proper search field. Only the menu changes: category pages, titles
 * and breadcrumbs keep the full names. Mapping (URL key => label) comes from di.xml.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Observer;

use Magento\Framework\Data\Tree\Node;
use Magento\Framework\Event\Observer;
use Magento\Framework\Event\ObserverInterface;

class ShortMenuLabels implements ObserverInterface
{
    /** @param array<string, string> $labels */
    public function __construct(private readonly array $labels = [])
    {
    }

    public function execute(Observer $observer): void
    {
        $menu = $observer->getEvent()->getData('menu');
        if (!$menu instanceof Node || $this->labels === []) {
            return;
        }
        foreach ($menu->getChildren() as $node) {
            $path = (string) parse_url((string) $node->getData('url'), PHP_URL_PATH);
            $key = basename($path, '.html');
            if (isset($this->labels[$key])) {
                $node->setData('name', $this->labels[$key]);
            }
        }
    }
}
