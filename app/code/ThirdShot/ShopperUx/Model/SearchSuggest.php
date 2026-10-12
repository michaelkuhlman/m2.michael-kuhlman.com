<?php
/**
 * Live search: the top products (with photo and price) and matching categories for a partial query.
 * Products come from the same OpenSearch quick-search request as the results page; when the engine finds
 * nothing for a half-typed word ("padd"), a name/SKU prefix match on the catalogue fills in.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Model;

use Magento\Catalog\Helper\Image as ImageHelper;
use Magento\Catalog\Model\Product;
use Magento\Catalog\Model\Product\Attribute\Source\Status;
use Magento\Catalog\Model\Product\Visibility;
use Magento\Catalog\Model\ResourceModel\Category\CollectionFactory as CategoryCollectionFactory;
use Magento\Catalog\Model\ResourceModel\Product\CollectionFactory;
use Magento\Framework\UrlInterface;
use Magento\Store\Model\StoreManagerInterface;

class SearchSuggest
{
    private const LIMIT = 6;

    public function __construct(
        private readonly CollectionFactory $searchCollectionFactory,
        private readonly CollectionFactory $productCollectionFactory,
        private readonly CategoryCollectionFactory $categoryCollectionFactory,
        private readonly Visibility $visibility,
        private readonly ImageHelper $imageHelper,
        private readonly CardRenderer $renderer,
        private readonly StoreManagerInterface $storeManager,
        private readonly UrlInterface $url
    ) {
    }

    /**
     * @return array{query: string, total: int, all_url: string, products: array<int, array<string, mixed>>,
     *     categories: array<int, array{name: string, url: string}>}
     */
    public function suggest(string $query): array
    {
        [$products, $total] = $this->engineMatches($query);
        $categories = $this->categories($query);
        if (!$products) {
            // a half-typed word ("padd"): complete it from category / product names and ask the engine again
            [$like, $likeTotal] = $this->prefixMatches($query);
            $word = $this->completion($query, array_merge(
                array_column($categories, 'name'),
                array_map(static fn (Product $p) => (string)$p->getName(), $like)
            ));
            if ($word !== null) {
                [$products, $total] = $this->engineMatches($word);
            }
            if (!$products) {
                [$products, $total] = [$like, $likeTotal];
            }
        }
        return [
            'query' => $query,
            'total' => $total,
            'all_url' => $this->url->getUrl('catalogsearch/result', ['_query' => ['q' => $query]]),
            'products' => array_map(fn (Product $p) => $this->productData($p), $products),
            'categories' => $categories,
        ];
    }

    /**
     * The shortest word in $texts that starts with the last word of $query, as a full query ("padd" -> "paddle").
     *
     * @param string[] $texts
     */
    private function completion(string $query, array $texts): ?string
    {
        $words = preg_split('/\s+/u', mb_strtolower($query)) ?: [];
        $last = (string)array_pop($words);
        if (mb_strlen($last) < 2) {
            return null;
        }
        $best = null;
        foreach ($texts as $text) {
            foreach (preg_split('/[^\p{L}\p{N}]+/u', mb_strtolower($text)) ?: [] as $w) {
                if ($w !== $last && str_starts_with($w, $last) && ($best === null || mb_strlen($w) < mb_strlen($best))) {
                    $best = $w;
                }
            }
        }
        return $best === null ? null : trim(implode(' ', $words) . ' ' . $best);
    }

    /**
     * @return array{0: Product[], 1: int}
     */
    private function engineMatches(string $query): array
    {
        /** @var \Magento\CatalogSearch\Model\ResourceModel\Fulltext\Collection $collection */
        $collection = $this->searchCollectionFactory->create();
        $collection->addSearchFilter($query);
        $collection->setVisibility($this->visibility->getVisibleInSearchIds());
        $this->prepare($collection);
        $collection->setOrder('relevance', 'DESC');
        return [array_values($collection->getItems()), (int)$collection->getSize()];
    }

    /**
     * @return array{0: Product[], 1: int}
     */
    private function prefixMatches(string $query): array
    {
        $like = '%' . addcslashes($query, '%_\\') . '%';
        $collection = $this->productCollectionFactory->create();
        $collection->addStoreFilter((int)$this->storeManager->getStore()->getId())
            ->setVisibility($this->visibility->getVisibleInSearchIds())
            ->addAttributeToFilter('status', Status::STATUS_ENABLED)
            ->addAttributeToFilter([
                ['attribute' => 'name', 'like' => $like],
                ['attribute' => 'sku', 'like' => $like],
            ]);
        $this->prepare($collection);
        $collection->setOrder('name', 'ASC');
        return [array_values($collection->getItems()), (int)$collection->getSize()];
    }

    private function prepare(\Magento\Catalog\Model\ResourceModel\Product\Collection $collection): void
    {
        $collection->addAttributeToSelect(['name', 'thumbnail', 'small_image', 'url_key', 'special_price',
            'special_from_date', 'special_to_date', 'price_type', 'price_view'])
            ->addMinimalPrice()
            ->addFinalPrice()
            ->addTaxPercents()
            ->addUrlRewrite()
            ->setPageSize(self::LIMIT)
            ->setCurPage(1);
    }

    /**
     * @return array<string, mixed>
     */
    private function productData(Product $product): array
    {
        return [
            'id' => (int)$product->getId(),
            'name' => (string)$product->getName(),
            'url' => $product->getProductUrl(),
            'image' => $this->imageHelper->init($product, 'mini_cart_product_thumbnail')->getUrl(),
            'price_html' => $this->renderer->priceHtml($product),
        ];
    }

    /**
     * @return array<int, array{name: string, url: string}>
     */
    private function categories(string $query): array
    {
        $rootId = (int)$this->storeManager->getStore()->getRootCategoryId();
        $collection = $this->categoryCollectionFactory->create();
        $collection->addAttributeToSelect(['name', 'url_key'])
            ->addAttributeToFilter('name', ['like' => '%' . addcslashes($query, '%_\\') . '%'])
            ->addAttributeToFilter('is_active', 1)
            ->addPathFilter('^1/' . $rootId . '/')
            ->addUrlRewriteToResult()
            ->setPageSize(4);
        $out = [];
        foreach ($collection as $category) {
            $out[] = ['name' => (string)$category->getName(), 'url' => (string)$category->getUrl()];
        }
        return $out;
    }
}
