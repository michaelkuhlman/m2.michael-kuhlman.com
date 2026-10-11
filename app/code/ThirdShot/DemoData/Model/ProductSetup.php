<?php
/**
 * Simple products, configurable children and configurable parents (with images).
 * Bundles, grouped products and product links are handled by CompositeSetup.
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Catalog\Api\Data\ProductInterface;
use Magento\Catalog\Api\Data\ProductInterfaceFactory;
use Magento\Catalog\Api\ProductRepositoryInterface;
use Magento\Catalog\Model\Product\Attribute\Source\Status;
use Magento\Catalog\Model\Product\Type;
use Magento\Catalog\Model\Product\Visibility;
use Magento\ConfigurableProduct\Helper\Product\Options\Factory as ConfigOptionsFactory;
use Magento\ConfigurableProduct\Model\Product\Type\Configurable;
use Magento\Eav\Model\Config as EavConfig;
use Magento\Framework\Exception\NoSuchEntityException;

class ProductSetup
{
    private const SELECTS = ['color', 'grip_size', 'core_thickness', 'face_material', 'paddle_shape', 'play_style',
        'surface'];

    /** @var array<string,array<string,int>> */
    private array $options = [];

    public function __construct(
        private readonly ProductInterfaceFactory $productFactory,
        private readonly ProductRepositoryInterface $productRepository,
        private readonly ConfigOptionsFactory $configOptionsFactory,
        private readonly EavConfig $eavConfig,
        private readonly AttributeSetup $attributes,
        private readonly DataSource $data
    ) {
    }

    /**
     * @param array<string,int> $categoryIds
     */
    public function install(array $categoryIds, callable $log): void
    {
        foreach (self::SELECTS as $code) {
            $this->options[$code] = $this->attributes->optionMap($code);
        }
        $rows = $this->data->flatProducts();
        // pass 1: simple products and configurable children
        foreach ($rows as $sku => $row) {
            if ($row['type'] === 'simple') {
                $this->saveSimple($row, $categoryIds, $rows, $log);
            }
        }
        // pass 2: configurable parents
        foreach ($rows as $row) {
            if ($row['type'] === 'configurable') {
                $this->saveConfigurable($row, $categoryIds, $log);
            }
        }
    }

    public function base(array $row, array $categoryIds, string $type): ProductInterface
    {
        try {
            $product = $this->productRepository->get($row['sku'], true, 0, true);
        } catch (NoSuchEntityException) {
            $product = $this->productFactory->create();
            $product->setSku($row['sku']);
        }
        $isChild = isset($row['parent']);
        $product->setTypeId($type)
            ->setAttributeSetId(4)
            ->setName($row['name'])
            ->setWebsiteIds([1])
            ->setStatus(Status::STATUS_ENABLED)
            ->setVisibility($isChild ? Visibility::VISIBILITY_NOT_VISIBLE : Visibility::VISIBILITY_BOTH)
            ->setWeight((float) ($row['weight'] ?? 1))
            ->setTaxClassId(2)
            ->setUrlKey($this->data->slug($row['name']) . ($isChild ? '-' . strtolower(substr(md5($row['sku']), 0, 4)) : ''));
        if ($row['price'] !== null) {
            $product->setPrice((float) $row['price']);
        }
        $product->setSpecialPrice(isset($row['special_price']) ? (float) $row['special_price'] : null);
        $product->setData('description', $row['description'] ?? '');
        $product->setData('short_description', $row['short_description'] ?? '');
        $product->setData('meta_title', $row['meta_title'] ?? $row['name']);
        $product->setData('meta_description', $row['meta_description'] ?? '');
        $product->setData('category_ids', isset($categoryIds[$row['category']]) ? [$categoryIds[$row['category']]] : []);
        if (in_array('new', $row['flags'] ?? [], true)) {
            $product->setData('news_from_date', date('Y-m-d', strtotime('-12 days')));
        }
        $qty = (int) ($row['qty'] ?? 50);
        $product->setStockData([
            'use_config_manage_stock' => 1,
            'qty' => $qty,
            'is_in_stock' => in_array($type, ['configurable', 'bundle', 'grouped'], true) ? 1 : (int) ($qty > 0),
        ]);
        foreach ($row['attributes'] ?? [] as $code => $value) {
            if (in_array($code, self::SELECTS, true)) {
                if (!isset($this->options[$code][$value])) {
                    continue;
                }
                $value = $this->options[$code][$value];
            }
            $product->setData($code, $value);
        }
        return $product;
    }

    /**
     * Attach images once (skips products that already have a gallery).
     *
     * @param string[] $files
     */
    public function addImages(ProductInterface $product, array $files): void
    {
        if (!$files || $product->getMediaGalleryEntries()) {
            return;
        }
        $tmpDir = sys_get_temp_dir() . '/ts-seed';
        if (!is_dir($tmpDir)) {
            mkdir($tmpDir, 0775, true);
        }
        foreach (array_values($files) as $i => $file) {
            // addImageToMediaGallery moves/renames, so hand it a throwaway copy named after the product
            $copy = $tmpDir . '/' . $this->data->slug($product->getName()) . '-' . ($i + 1) . '.jpg';
            copy($file, $copy);
            $roles = $i === 0 ? ['image', 'small_image', 'thumbnail', 'swatch_image'] : null;
            $product->addImageToMediaGallery($copy, $roles, true, false);
        }
        $gallery = $product->getData('media_gallery');
        foreach ($gallery['images'] ?? [] as $k => $img) {
            $gallery['images'][$k]['label'] = $product->getName();
        }
        $product->setData('media_gallery', $gallery);
    }

    private function saveSimple(array $row, array $categoryIds, array $rows, callable $log): void
    {
        $product = $this->base($row, $categoryIds, Type::TYPE_SIMPLE);
        $files = $this->data->images($row['sku']);
        if (!$files && isset($row['parent'])) {
            $files = array_slice($this->data->images($row['parent']), 0, 1);
        }
        $this->addImages($product, $files);
        $this->productRepository->save($product);
        $log(sprintf('simple %s (%d images)', $row['sku'], count($files)));
    }

    private function saveConfigurable(array $row, array $categoryIds, callable $log): void
    {
        $attrCode = $row['configurable_attribute'];
        $attribute = $this->eavConfig->getAttribute('catalog_product', $attrCode);
        $childIds = [];
        $values = [];
        foreach ($row['children'] as $child) {
            $childIds[] = (int) $this->productRepository->get($child['sku'])->getId();
            $values[] = ['value_index' => $this->options[$attrCode][$child['attributes'][$attrCode]]];
        }
        $product = $this->base($row, $categoryIds, Configurable::TYPE_CODE);
        $files = $this->data->images($row['children'][0]['sku']);
        $own = $this->data->images($row['sku']);
        if (!$files) {
            $files = $own;
        } else {
            $files = array_merge(array_slice($files, 0, 2), $own);
        }
        $this->addImages($product, $files);
        $options = $this->configOptionsFactory->create([[
            'attribute_id' => $attribute->getId(),
            'code' => $attrCode,
            'label' => $attribute->getStoreLabel() ?: $attribute->getFrontendLabel(),
            'position' => 0,
            'values' => $values,
        ]]);
        $ext = $product->getExtensionAttributes();
        $ext->setConfigurableProductOptions($options);
        $ext->setConfigurableProductLinks($childIds);
        $product->setExtensionAttributes($ext);
        $this->productRepository->save($product);
        $log(sprintf('configurable %s (%d children, %d images)', $row['sku'], count($childIds), count($files)));
    }
}
