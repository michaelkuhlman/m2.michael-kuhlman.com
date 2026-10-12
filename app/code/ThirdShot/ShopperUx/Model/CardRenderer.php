<?php
/**
 * Turns products into card HTML (and compact price HTML) outside a page layout, for the JSON endpoints.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Model;

use Magento\Catalog\Model\Product;
use Magento\Framework\Pricing\Render as PriceRender;
use Magento\Framework\View\LayoutInterface;
use ThirdShot\ShopperUx\Block\ProductCards;

class CardRenderer
{
    private ?ProductCards $cards = null;

    public function __construct(private readonly LayoutInterface $layout)
    {
    }

    /**
     * @param Product[] $products
     * @return array<int, array{id: int, html: string}>
     */
    public function cards(array $products): array
    {
        $block = $this->block();
        $out = [];
        foreach ($products as $product) {
            $out[] = ['id' => (int)$product->getId(), 'html' => trim($block->renderCard($product))];
        }
        return $out;
    }

    public function priceHtml(Product $product): string
    {
        return trim((string)$this->block()->getProductPrice($product));
    }

    private function block(): ProductCards
    {
        if ($this->cards === null) {
            if (!$this->layout->getBlock('product.price.render.default')) {
                $this->layout->createBlock(PriceRender::class, 'product.price.render.default', ['data' => [
                    'price_render_handle' => 'catalog_product_prices',
                    'use_link_for_as_low_as' => true,
                ]]);
            }
            /** @var ProductCards $cards */
            $cards = $this->layout->createBlock(ProductCards::class, 'ts.ux.cards');
            $this->cards = $cards;
        }
        return $this->cards;
    }
}
