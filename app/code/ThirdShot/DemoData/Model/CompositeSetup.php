<?php
/**
 * Bundle and grouped products, then related / upsell / cross-sell links for every product.
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Bundle\Api\Data\LinkInterfaceFactory;
use Magento\Bundle\Api\Data\OptionInterfaceFactory;
use Magento\Catalog\Api\Data\ProductLinkInterfaceFactory;
use Magento\Catalog\Api\ProductRepositoryInterface;
use Magento\CatalogInventory\Api\StockRegistryInterface;
use Magento\GroupedProduct\Model\Product\Type\Grouped;

class CompositeSetup
{
    public function __construct(
        private readonly ProductSetup $products,
        private readonly ProductRepositoryInterface $productRepository,
        private readonly OptionInterfaceFactory $bundleOptionFactory,
        private readonly LinkInterfaceFactory $bundleLinkFactory,
        private readonly ProductLinkInterfaceFactory $linkFactory,
        private readonly StockRegistryInterface $stockRegistry,
        private readonly DataSource $data
    ) {
    }

    /**
     * @param array<string,int> $categoryIds
     */
    public function install(array $categoryIds, callable $log): void
    {
        foreach ($this->data->catalog()['products'] as $row) {
            if ($row['type'] === 'bundle') {
                $this->saveBundle($row, $categoryIds, $log);
            } elseif ($row['type'] === 'grouped') {
                $product = $this->products->base($row, $categoryIds, Grouped::TYPE_CODE);
                $this->products->addImages($product, $this->data->images($row['sku']));
                $this->productRepository->save($product);
                $log('grouped ' . $row['sku']);
            }
        }
        $this->saveLinks($log);
        // composite products carry no qty of their own; Magento can save them as out of stock
        foreach ($this->data->catalog()['products'] as $row) {
            if (in_array($row['type'], ['bundle', 'grouped', 'configurable'], true)) {
                $item = $this->stockRegistry->getStockItemBySku($row['sku']);
                $item->setIsInStock(true);
                $this->stockRegistry->updateStockItemBySku($row['sku'], $item);
            }
        }
        $log('composite stock status set');
    }

    private function saveBundle(array $row, array $categoryIds, callable $log): void
    {
        $product = $this->products->base($row, $categoryIds, 'bundle');
        $product->setPriceType(0)       // dynamic price
            ->setPriceView(0)           // "price range"
            ->setSkuType(0)
            ->setWeightType(0)
            ->setShipmentType(0);
        $product->setData('price_type', 0);
        $product->setData('sku_type', 0);
        $product->setData('weight_type', 0);
        $product->setData('price_view', 0);
        $product->setData('shipment_type', 0);
        $this->products->addImages($product, $this->data->images($row['sku']));

        $options = [];
        foreach ($row['bundle_options'] as $pos => $opt) {
            $option = $this->bundleOptionFactory->create();
            $option->setTitle($opt['title'])
                ->setType($opt['type'])
                ->setRequired((bool) $opt['required'])
                ->setPosition($pos + 1)
                ->setSku($row['sku']);
            $links = [];
            foreach ($opt['selections'] as $i => $sel) {
                $link = $this->bundleLinkFactory->create();
                $link->setSku($sel['sku'])
                    ->setQty((float) ($sel['qty'] ?? 1))
                    ->setCanChangeQuantity(0)
                    ->setIsDefault(!empty($sel['default']))
                    ->setPosition($i + 1)
                    ->setPrice(0)
                    ->setPriceType(0);
                $links[] = $link;
            }
            $option->setProductLinks($links);
            $options[] = $option;
        }
        $ext = $product->getExtensionAttributes();
        $ext->setBundleProductOptions($options);
        $product->setExtensionAttributes($ext);
        $this->productRepository->save($product);
        $log(sprintf('bundle %s (%d options)', $row['sku'], count($options)));
    }

    private function saveLinks(callable $log): void
    {
        $types = ['related' => 'related', 'upsell' => 'upsell', 'crosssell' => 'crosssell'];
        foreach ($this->data->catalog()['products'] as $row) {
            $links = [];
            foreach ($types as $key => $type) {
                foreach (array_values($row[$key] ?? []) as $pos => $target) {
                    $links[] = $this->link($row['sku'], $target, $type, $pos + 1);
                }
            }
            foreach (array_values($row['grouped_children'] ?? []) as $pos => $target) {
                $link = $this->link($row['sku'], $target, 'associated', $pos + 1, 'simple');
                $link->getExtensionAttributes()->setQty(0);
                $links[] = $link;
            }
            if (!$links) {
                continue;
            }
            $product = $this->productRepository->get($row['sku'], true, 0, true);
            $product->setProductLinks($links);
            $this->productRepository->save($product);
        }
        $log('product links saved');
    }

    private function link(string $sku, string $target, string $type, int $pos, ?string $targetType = null)
    {
        $targetType ??= $this->productRepository->get($target)->getTypeId();
        $link = $this->linkFactory->create();
        $link->setSku($sku)
            ->setLinkedProductSku($target)
            ->setLinkType($type)
            ->setLinkedProductType($targetType)
            ->setPosition($pos);
        return $link;
    }
}
