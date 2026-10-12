<?php
/**
 * "Pairs well with" ids for a product: cross-sells first, then related, then up-sells.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Model;

use Magento\Catalog\Api\ProductRepositoryInterface;
use Magento\Framework\Exception\NoSuchEntityException;

class Recommendations
{
    public function __construct(private readonly ProductRepositoryInterface $productRepository)
    {
    }

    /**
     * @param int[] $exclude
     * @return int[]
     */
    public function idsFor(int $productId, array $exclude = [], int $limit = 4): array
    {
        try {
            $product = $this->productRepository->getById($productId);
        } catch (NoSuchEntityException) {
            return [];
        }
        $ids = array_merge(
            array_map('intval', (array)$product->getCrossSellProductIds()),
            array_map('intval', (array)$product->getRelatedProductIds()),
            array_map('intval', (array)$product->getUpSellProductIds())
        );
        $exclude = array_map('intval', $exclude);
        $exclude[] = $productId;
        $ids = array_values(array_diff(array_unique($ids), $exclude));
        return array_slice($ids, 0, max(1, $limit * 2)); // spare ids in case some are hidden / out of stock
    }
}
