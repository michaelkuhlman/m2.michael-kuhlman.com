<?php
/**
 * Lowest and highest price a price slider should span. Category pages: every visible product in the category,
 * so the slider keeps its full width while a price range is applied. Search pages: the current results.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Model;

use Magento\Catalog\Model\Layer;
use Magento\Catalog\Model\Layer\Category as CategoryLayer;
use Magento\Catalog\Model\Product\Visibility;
use Magento\Catalog\Model\ResourceModel\Product\CollectionFactory;

class PriceBounds
{
    public function __construct(
        private readonly CollectionFactory $collectionFactory,
        private readonly Visibility $visibility
    ) {
    }

    /**
     * @return array{0: float, 1: float}|null
     */
    public function forLayer(Layer $layer): ?array
    {
        try {
            if ($layer instanceof CategoryLayer) {
                $collection = $this->collectionFactory->create();
                $collection->addCategoryFilter($layer->getCurrentCategory())
                    ->setVisibility($this->visibility->getVisibleInCatalogIds())
                    ->addPriceData();
                $min = (float)$collection->getMinPrice();
                $max = (float)$collection->getMaxPrice();
            } else {
                $collection = $layer->getProductCollection();
                $min = (float)$collection->getMinPrice();
                $max = (float)$collection->getMaxPrice();
            }
        } catch (\Throwable) {
            return null;
        }
        if ($max <= 0 || $max < $min) {
            return null;
        }
        return [floor($min), ceil($max)];
    }
}
