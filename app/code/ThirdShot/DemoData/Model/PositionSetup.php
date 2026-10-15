<?php
/**
 * Category positions ("Featured" sort): each category lists its products in products.json order, so the flagship
 * paddles lead instead of whatever was saved first (configurables came last, after their simple siblings).
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Catalog\Api\CategoryLinkRepositoryInterface;
use Magento\Catalog\Api\Data\CategoryProductLinkInterfaceFactory;

class PositionSetup
{
    public function __construct(
        private readonly DataSource $data,
        private readonly CategoryLinkRepositoryInterface $linkRepository,
        private readonly CategoryProductLinkInterfaceFactory $linkFactory
    ) {
    }

    /**
     * @param array<string,int> $categoryIds category code => id
     */
    public function install(array $categoryIds, callable $log): void
    {
        $next = [];
        foreach ($this->data->flatProducts() as $sku => $row) {
            $code = $row['category'] ?? null;
            if (isset($row['parent']) || $code === null || !isset($categoryIds[$code])) {
                continue;
            }
            $position = $next[$code] = ($next[$code] ?? 0) + 1;
            $link = $this->linkFactory->create();
            $link->setSku((string) $sku);
            $link->setCategoryId((string) $categoryIds[$code]);
            $link->setPosition($position);
            $this->linkRepository->save($link);
        }
        foreach ($next as $code => $count) {
            $log(sprintf('positions %s: %d products', $code, $count));
        }
    }
}
