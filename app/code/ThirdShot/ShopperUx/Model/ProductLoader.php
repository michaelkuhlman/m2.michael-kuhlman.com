<?php
/**
 * Loads visible, enabled storefront products by id (keeping the requested order) with everything a product card
 * needs: name, URL, listing image, prices and the review summary.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Model;

use Magento\Catalog\Model\Product;
use Magento\Catalog\Model\Product\Attribute\Source\Status;
use Magento\Catalog\Model\Product\Visibility;
use Magento\Catalog\Model\ResourceModel\Product\CollectionFactory;
use Magento\Review\Model\ResourceModel\Review\Summary as ReviewSummary;
use Magento\Store\Model\StoreManagerInterface;

class ProductLoader
{
    public const MAX_IDS = 48; // = the Saved list's cap in js/cards.js

    public function __construct(
        private readonly CollectionFactory $collectionFactory,
        private readonly Visibility $visibility,
        private readonly StoreManagerInterface $storeManager,
        private readonly ReviewSummary $reviewSummary
    ) {
    }

    /**
     * @param int[] $ids
     * @return Product[] in the order of $ids, unknown/hidden ids dropped
     */
    public function load(array $ids): array
    {
        $ids = array_slice(array_values(array_unique(array_filter(array_map('intval', $ids)))), 0, self::MAX_IDS);
        if (!$ids) {
            return [];
        }
        $storeId = (int)$this->storeManager->getStore()->getId();
        $collection = $this->collectionFactory->create();
        $collection->addIdFilter($ids)
            ->addStoreFilter($storeId)
            ->setVisibility($this->visibility->getVisibleInCatalogIds())
            ->addAttributeToFilter('status', Status::STATUS_ENABLED)
            ->addAttributeToSelect(['name', 'small_image', 'thumbnail', 'url_key', 'special_price', 'special_from_date',
                'special_to_date', 'price_type', 'price_view', 'required_options', 'has_options', 'links_purchased_separately'])
            ->addMinimalPrice()
            ->addFinalPrice()
            ->addTaxPercents()
            ->addUrlRewrite();
        $this->reviewSummary->appendSummaryFieldsToCollection($collection, $storeId, 'product');

        $byId = [];
        foreach ($collection as $product) {
            $byId[(int)$product->getId()] = $product;
        }
        $out = [];
        foreach ($ids as $id) {
            if (isset($byId[$id])) {
                $out[] = $byId[$id];
            }
        }
        return $out;
    }
}
