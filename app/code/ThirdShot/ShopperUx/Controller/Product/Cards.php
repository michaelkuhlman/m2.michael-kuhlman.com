<?php
/**
 * GET /shopux/product/cards?ids=1,2,3            -> cards for "Saved" / "Recently viewed"
 * GET /shopux/product/cards?related_to=69&exclude=1,2&limit=4 -> "Pairs well with" for the added-to-bag drawer
 * Response: {"cards":[{"id":69,"html":"<li ...>"}]}. Not page-cached (contains the form key).
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Controller\Product;

use Magento\Framework\App\Action\HttpGetActionInterface;
use Magento\Framework\App\RequestInterface;
use Magento\Framework\Controller\Result\Json;
use Magento\Framework\Controller\Result\JsonFactory;
use ThirdShot\ShopperUx\Model\CardRenderer;
use ThirdShot\ShopperUx\Model\ProductLoader;
use ThirdShot\ShopperUx\Model\Recommendations;

class Cards implements HttpGetActionInterface
{
    public function __construct(
        private readonly RequestInterface $request,
        private readonly JsonFactory $jsonFactory,
        private readonly ProductLoader $loader,
        private readonly CardRenderer $renderer,
        private readonly Recommendations $recommendations
    ) {
    }

    public function execute(): Json
    {
        $result = $this->jsonFactory->create();
        $result->setHeader('Cache-Control', 'no-store', true);
        $relatedTo = (int)$this->request->getParam('related_to');
        $limit = min(12, max(1, (int)($this->request->getParam('limit') ?: 4)));
        if ($relatedTo > 0) {
            $ids = $this->recommendations->idsFor($relatedTo, $this->idList('exclude'), $limit);
            $products = array_slice(array_values(array_filter(
                $this->loader->load($ids),
                static fn ($p) => $p->isSaleable()
            )), 0, $limit);
        } else {
            $products = $this->loader->load($this->idList('ids'));
        }
        return $result->setData(['cards' => $this->renderer->cards($products)]);
    }

    /**
     * @return int[]
     */
    private function idList(string $param): array
    {
        $raw = (string)$this->request->getParam($param, '');
        return array_slice(array_filter(array_map('intval', explode(',', $raw))), 0, ProductLoader::MAX_IDS);
    }
}
