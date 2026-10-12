<?php
/**
 * GET /shopux/search/suggest?q=padd -> {"query","total","all_url","products":[...],"categories":[...]}
 * Answers are cached per query (catalogue cache tags), so repeated keystrokes are cheap.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Controller\Search;

use Magento\Catalog\Model\Category;
use Magento\Catalog\Model\Product;
use Magento\Customer\Model\Session as CustomerSession;
use Magento\Framework\App\Action\HttpGetActionInterface;
use Magento\Framework\App\Cache\Type\Collection as CollectionCache;
use Magento\Framework\App\CacheInterface;
use Magento\Framework\App\RequestInterface;
use Magento\Framework\Controller\Result\Json;
use Magento\Framework\Controller\Result\JsonFactory;
use Magento\Framework\Serialize\SerializerInterface;
use Magento\Store\Model\StoreManagerInterface;
use ThirdShot\ShopperUx\Model\SearchSuggest;

class Suggest implements HttpGetActionInterface
{
    private const MIN = 2;
    private const MAX = 64;

    public function __construct(
        private readonly RequestInterface $request,
        private readonly JsonFactory $jsonFactory,
        private readonly SearchSuggest $suggest,
        private readonly CacheInterface $cache,
        private readonly SerializerInterface $serializer,
        private readonly StoreManagerInterface $storeManager,
        private readonly CustomerSession $customerSession
    ) {
    }

    public function execute(): Json
    {
        $result = $this->jsonFactory->create();
        $query = trim(preg_replace('/\s+/u', ' ', (string)$this->request->getParam('q', '')) ?? '');
        $query = mb_substr($query, 0, self::MAX);
        if (mb_strlen($query) < self::MIN) {
            return $result->setData(['query' => $query, 'total' => 0, 'products' => [], 'categories' => []]);
        }
        $key = 'ts_ux_suggest_' . sha1(implode('|', [
            mb_strtolower($query),
            $this->storeManager->getStore()->getId(),
            $this->customerSession->getCustomerGroupId(),
        ]));
        $cached = $this->cache->load($key);
        if ($cached) {
            $data = $this->serializer->unserialize($cached);
        } else {
            $data = $this->suggest->suggest($query);
            $this->cache->save($this->serializer->serialize($data), $key, [Product::CACHE_TAG, Category::CACHE_TAG, CollectionCache::CACHE_TAG], 3600);
        }
        $result->setHeader('Cache-Control', 'no-store', true);
        return $result->setData($data);
    }
}
