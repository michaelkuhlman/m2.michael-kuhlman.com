<?php
/**
 * Renders products as native-looking listing cards (same markup as the category grid, so the theme styles them).
 * Used by the JSON endpoint behind "Saved", "Recently viewed" and the added-to-bag recommendations.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Block;

use Magento\Catalog\Block\Product\AbstractProduct;
use Magento\Catalog\Block\Product\Context;
use Magento\Catalog\Model\Product;
use Magento\Framework\App\ActionInterface;
use Magento\Framework\Url\Helper\Data as UrlHelper;

class ProductCards extends AbstractProduct
{
    protected $_template = 'ThirdShot_ShopperUx::cards.phtml';

    /** @var Product[] */
    private array $products = [];

    public function __construct(
        Context $context,
        private readonly UrlHelper $urlHelper,
        array $data = []
    ) {
        parent::__construct($context, $data);
    }

    /**
     * Same shape as ListProduct::getAddToCartPostParams(); the return URL is the product page.
     *
     * @return array{action: string, data: array<string, mixed>}
     */
    public function getAddToCartPostParams(Product $product): array
    {
        return [
            'action' => $this->getAddToCartUrl($product, ['_escape' => false]),
            'data' => [
                'product' => (int)$product->getEntityId(),
                ActionInterface::PARAM_NAME_URL_ENCODED => $this->urlHelper->getEncodedUrl($product->getProductUrl()),
            ],
        ];
    }

    /**
     * @param Product[] $products
     */
    public function setProducts(array $products): self
    {
        $this->products = $products;
        return $this;
    }

    /**
     * @return Product[]
     */
    public function getProducts(): array
    {
        return $this->products;
    }

    public function renderCard(Product $product): string
    {
        $this->setData('current_product', $product);
        return $this->fetchView($this->getTemplateFile());
    }

    public function getCurrentProduct(): ?Product
    {
        $product = $this->getData('current_product');
        return $product instanceof Product ? $product : null;
    }

    /**
     * Products a guest cannot add with one click (options to choose first) open quick view instead.
     */
    public function needsOptions(Product $product): bool
    {
        return in_array($product->getTypeId(), ['configurable', 'bundle', 'grouped'], true)
            || (bool)$product->getRequiredOptions();
    }

    public function toHtml(): string
    {
        return '';
    }
}
