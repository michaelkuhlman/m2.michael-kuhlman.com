<?php
/**
 * Reads the demo catalogue source files from <magento root>/_build.
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Framework\App\Filesystem\DirectoryList;
use Magento\Framework\Exception\LocalizedException;
use Magento\Framework\Serialize\Serializer\Json;

class DataSource
{
    private ?array $catalog = null;

    public function __construct(
        private readonly DirectoryList $directoryList,
        private readonly Json $json
    ) {
    }

    public function buildDir(string $sub = ''): string
    {
        return rtrim($this->directoryList->getRoot() . '/_build/' . ltrim($sub, '/'), '/');
    }

    /**
     * @return array{categories: array<int, array>, products: array<int, array>}
     */
    public function catalog(): array
    {
        if ($this->catalog === null) {
            $file = $this->buildDir('catalog/products.json');
            if (!is_readable($file)) {
                throw new LocalizedException(__('Catalogue file not found: %1', $file));
            }
            $this->catalog = $this->json->unserialize((string) file_get_contents($file));
        }
        return $this->catalog;
    }

    /** Search keywords of a category (products.json "keywords"): every product gets its category's, see ProductSetup. */
    public function categoryKeywords(string $code): string
    {
        foreach ($this->catalog()['categories'] as $category) {
            if (($category['code'] ?? null) === $code) {
                return (string) ($category['keywords'] ?? '');
            }
        }
        return '';
    }

    /**
     * All product rows including configurable children (children get parent defaults merged in).
     *
     * @return array<string, array>
     */
    public function flatProducts(): array
    {
        $rows = [];
        foreach ($this->catalog()['products'] as $p) {
            $rows[$p['sku']] = $p;
            foreach ($p['children'] ?? [] as $child) {
                $row = $child + [
                    'type' => 'simple',
                    'category' => $p['category'],
                    'price' => $p['price'],
                    'special_price' => $p['special_price'] ?? null,
                    'weight' => $p['weight'] ?? 1,
                    'parent' => $p['sku'],
                    'description' => $p['description'],
                    'short_description' => $p['short_description'],
                ];
                // own values (colour, grip size) win, the parent's specs fill the rest
                $row['attributes'] = ($child['attributes'] ?? []) + ($p['attributes'] ?? []);
                $rows[$child['sku']] = $row;
            }
        }
        return $rows;
    }

    /**
     * Rendered images for a SKU, ordered: <SKU>_1.jpg, <SKU>_2.jpg ...
     *
     * @return string[] absolute paths
     */
    public function images(string $sku): array
    {
        $dir = $this->buildDir('renders/jpg');
        $files = glob($dir . '/' . $sku . '_[0-9].jpg') ?: [];
        natsort($files);
        return array_values($files);
    }

    public function slug(string $text): string
    {
        $text = strtolower(trim($text));
        $text = (string) preg_replace('/[^a-z0-9]+/', '-', $text);
        return trim($text, '-');
    }
}
