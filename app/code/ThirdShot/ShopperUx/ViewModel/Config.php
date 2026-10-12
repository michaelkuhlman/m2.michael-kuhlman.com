<?php
/**
 * Storefront config for the shopper-UX scripts. Store-wide values only (FPC-safe).
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\ViewModel;

use Magento\Catalog\Model\ResourceModel\Category\CollectionFactory as CategoryCollectionFactory;
use Magento\Framework\App\Config\ScopeConfigInterface;
use Magento\Framework\Locale\FormatInterface;
use Magento\Framework\UrlInterface;
use Magento\Framework\View\Element\Block\ArgumentInterface;
use Magento\Store\Model\ScopeInterface;
use Magento\Store\Model\StoreManagerInterface;

class Config implements ArgumentInterface
{
    public function __construct(
        private readonly UrlInterface $url,
        private readonly ScopeConfigInterface $scopeConfig,
        private readonly FormatInterface $localeFormat,
        private readonly StoreManagerInterface $storeManager,
        private readonly CategoryCollectionFactory $categoryCollectionFactory
    ) {
    }

    /**
     * @return array<string, mixed>
     */
    public function getConfig(): array
    {
        $free = 0.0;
        if ($this->scopeConfig->isSetFlag('carriers/freeshipping/active', ScopeInterface::SCOPE_STORE)) {
            $free = (float)$this->scopeConfig->getValue('carriers/freeshipping/free_shipping_subtotal', ScopeInterface::SCOPE_STORE);
        }
        $format = $this->localeFormat->getPriceFormat();
        return [
            'suggestUrl' => $this->url->getUrl('shopux/search/suggest'),
            'cardsUrl' => $this->url->getUrl('shopux/product/cards'),
            'searchUrl' => $this->url->getUrl('catalogsearch/result'),
            'savedUrl' => $this->url->getUrl('saved'),
            'cartUrl' => $this->url->getUrl('checkout/cart'),
            'checkoutUrl' => $this->url->getUrl('checkout'),
            'updateCartUrl' => $this->url->getUrl('checkout/cart/updatePost'),
            'freeShipping' => $free,
            'priceFormat' => (string)($format['pattern'] ?? '$%s'),
            'categories' => $this->topCategories(),
        ];
    }

    /**
     * @return array<int, array{name: string, url: string}>
     */
    private function topCategories(): array
    {
        $rootId = (int)$this->storeManager->getStore()->getRootCategoryId();
        $collection = $this->categoryCollectionFactory->create();
        $collection->addAttributeToSelect(['name', 'url_key'])
            ->addAttributeToFilter('is_active', 1)
            ->addAttributeToFilter('include_in_menu', 1)
            ->addFieldToFilter('parent_id', $rootId)
            ->addUrlRewriteToResult()
            ->addOrder('position', 'ASC')
            ->setPageSize(8);
        $out = [];
        foreach ($collection as $category) {
            $out[] = ['name' => (string)$category->getName(), 'url' => (string)$category->getUrl()];
        }
        return $out;
    }
}
