<?php
/**
 * Product attributes for the demo catalogue: select/text specs, colour as a visual swatch,
 * grip size as a text swatch, all grouped under "Third Shot Specs" in the Default set.
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Catalog\Model\Product;
use Magento\Catalog\Model\ResourceModel\Eav\Attribute as EavAttribute;
use Magento\Eav\Model\Config as EavConfig;
use Magento\Eav\Setup\EavSetupFactory;
use Magento\Framework\App\ResourceConnection;
use Magento\Framework\Setup\ModuleDataSetupInterface;

class AttributeSetup
{
    public const GROUP = 'Third Shot Specs';

    /** Visual swatch hex values for `color`. */
    public const COLOURS = [
        'Volt' => '#D9F24F', 'Optic' => '#D9F24F', 'Coral' => '#EC7A5C', 'Glacier' => '#9ED2E4',
        'Forest' => '#1F4A3C', 'Sand' => '#D9CDB4', 'Clay' => '#C9603A', 'Chalk' => '#EFEADF',
        'Charcoal' => '#2E3434', 'Navy' => '#1F3550',
    ];

    /** code => [label, input, options|null, filterable, comparable-on-front] */
    private const SPEC = [
        'grip_size' => ['Grip Size', 'select', ['4.00 in', '4.25 in', '4.50 in'], 1],
        'paddle_weight' => ['Weight', 'text', null, 0],
        'core_thickness' => ['Core Thickness', 'select', ['13 mm', '14 mm', '16 mm'], 1],
        'face_material' => ['Face Material', 'select', ['Raw T700 Carbon', 'Toray Carbon Fiber', 'Fiberglass',
            'Carbon/Fiberglass Hybrid', 'Polymer Composite', 'Ash Wood'], 1],
        'paddle_shape' => ['Shape', 'select', ['Standard', 'Elongated', 'Hybrid', 'Widebody'], 1],
        'play_style' => ['Play Style', 'select', ['Control', 'All-Court', 'Power'], 1],
        'grip_length' => ['Grip Length', 'text', null, 0],
        'surface' => ['Surface', 'select', ['Outdoor', 'Indoor', 'Indoor & Outdoor'], 1],
        'pack_size' => ['Pack Size', 'text', null, 0],
        'material' => ['Material', 'text', null, 0],
        'dimensions' => ['Dimensions', 'text', null, 0],
    ];

    public function __construct(
        private readonly EavSetupFactory $eavSetupFactory,
        private readonly ModuleDataSetupInterface $setup,
        private readonly EavConfig $eavConfig,
        private readonly ResourceConnection $resource
    ) {
    }

    public function install(callable $log): void
    {
        $eav = $this->eavSetupFactory->create(['setup' => $this->setup]);
        $entity = Product::ENTITY;
        $setId = (int) $eav->getDefaultAttributeSetId($entity);
        $eav->addAttributeGroup($entity, $setId, self::GROUP, 15);

        foreach (self::SPEC as $code => [$label, $input, $options, $filterable]) {
            if (!$eav->getAttributeId($entity, $code)) {
                $eav->addAttribute($entity, $code, [
                    'type' => $input === 'select' ? 'int' : 'varchar',
                    'label' => $label,
                    'input' => $input,
                    'source' => $input === 'select' ? \Magento\Eav\Model\Entity\Attribute\Source\Table::class : '',
                    'global' => \Magento\Eav\Model\Entity\Attribute\ScopedAttributeInterface::SCOPE_GLOBAL,
                    'required' => false,
                    'user_defined' => true,
                    'visible_on_front' => true,
                    'used_in_product_listing' => false,
                    'filterable' => $filterable,
                    'searchable' => true,
                    'comparable' => true,
                    'is_used_in_grid' => true,
                    'is_filterable_in_grid' => true,
                    'option' => $options ? ['values' => $options] : null,
                    'apply_to' => '',
                ]);
                $log("attribute $code created");
            }
            $eav->addAttributeToGroup($entity, $setId, self::GROUP, $code);
        }

        // meta_keyword (products.json "keywords") is searched with the top weight (10; name 5, SKU 6), see ShopperUx etc/search_request.xml
        $eav->updateAttribute($entity, 'meta_keyword', ['is_searchable' => 1, 'search_weight' => 10]);

        $this->setupColour($eav, $setId, $log);
        $this->eavConfig->clear();
        $this->makeSwatch('color', 'visual', self::COLOURS);
        $this->makeSwatch('grip_size', 'text', null);
        $log('swatches configured');
    }

    private function setupColour(\Magento\Eav\Setup\EavSetup $eav, int $setId, callable $log): void
    {
        $entity = Product::ENTITY;
        $attrId = (int) $eav->getAttributeId($entity, 'color');
        $existing = $this->optionLabels($attrId);
        $missing = array_values(array_diff(array_keys(self::COLOURS), $existing));
        if ($missing) {
            $eav->addAttributeOption(['attribute_id' => $attrId, 'values' => $missing]);
            $log('color options added: ' . implode(', ', $missing));
        }
        $eav->updateAttribute($entity, 'color', [
            'is_filterable' => 1,
            'is_filterable_in_search' => 1,
            'is_visible_on_front' => 1,
            'used_in_product_listing' => 1,
            'is_global' => \Magento\Eav\Model\Entity\Attribute\ScopedAttributeInterface::SCOPE_GLOBAL,
        ]);
        $eav->addAttributeToGroup($entity, $setId, self::GROUP, 'color');
    }

    /** @return string[] admin labels of an attribute's options */
    public function optionLabels(int $attributeId): array
    {
        $c = $this->resource->getConnection();
        $sql = $c->select()
            ->from(['o' => $this->resource->getTableName('eav_attribute_option')], [])
            ->join(['v' => $this->resource->getTableName('eav_attribute_option_value')],
                'v.option_id = o.option_id AND v.store_id = 0', ['value'])
            ->where('o.attribute_id = ?', $attributeId);
        return $c->fetchCol($sql);
    }

    /** @return array<string,int> label => option_id */
    public function optionMap(string $code): array
    {
        $attr = $this->eavConfig->getAttribute(Product::ENTITY, $code);
        $c = $this->resource->getConnection();
        $sql = $c->select()
            ->from(['o' => $this->resource->getTableName('eav_attribute_option')], ['option_id'])
            ->join(['v' => $this->resource->getTableName('eav_attribute_option_value')],
                'v.option_id = o.option_id AND v.store_id = 0', ['value'])
            ->where('o.attribute_id = ?', (int) $attr->getId());
        $map = [];
        foreach ($c->fetchAll($sql) as $row) {
            $map[$row['value']] = (int) $row['option_id'];
        }
        return $map;
    }

    /**
     * Turn a select attribute into a swatch (visual = hex colours, text = option labels).
     */
    private function makeSwatch(string $code, string $type, ?array $hex): void
    {
        /** @var EavAttribute $attr */
        $attr = $this->eavConfig->getAttribute(Product::ENTITY, $code);
        $c = $this->resource->getConnection();
        $c->update(
            $this->resource->getTableName('catalog_eav_attribute'),
            ['additional_data' => json_encode([
                'swatch_input_type' => $type,
                'update_product_preview_image' => $type === 'visual' ? 1 : 0,
                'use_product_image_for_swatch' => 0,
            ])],
            ['attribute_id = ?' => (int) $attr->getId()]
        );
        $table = $this->resource->getTableName('eav_attribute_option_swatch');
        foreach ($this->optionMap($code) as $label => $optionId) {
            $value = $type === 'visual' ? ($hex[$label] ?? '#cccccc') : $label;
            $c->delete($table, ['option_id = ?' => $optionId, 'store_id = ?' => 0]);
            $c->insert($table, [
                'option_id' => $optionId,
                'store_id' => 0,
                'type' => $type === 'visual' ? 1 : 0,
                'value' => $value,
            ]);
        }
    }
}
