<?php
/**
 * CMS pages and blocks from _build/cms/{pages,blocks}/*.html.
 * Each file starts with a JSON header comment, e.g.
 *   <!-- {"identifier":"about","title":"Our story","layout":"1column","meta_description":"..."} -->
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Cms\Model\BlockFactory;
use Magento\Framework\App\Filesystem\DirectoryList;
use Magento\Framework\Filesystem;
use Magento\Cms\Model\PageFactory;
use Magento\Framework\Exception\LocalizedException;

class CmsSetup
{
    public function __construct(
        private readonly PageFactory $pageFactory,
        private readonly BlockFactory $blockFactory,
        private readonly DataSource $data,
        private readonly Filesystem $filesystem
    ) {
    }

    /** Editorial images referenced from CMS content as {{media url='wysiwyg/thirdshot/<name>.jpg'}}. */
    private const MEDIA = ['hero', 'story', 'spotlight', 'workshop', 'cat_paddles', 'cat_balls', 'cat_bags',
        'cat_apparel', 'cat_training', 'cat_accessories'];

    public function install(callable $log): void
    {
        $media = $this->filesystem->getDirectoryWrite(DirectoryList::MEDIA);
        foreach (self::MEDIA as $name) {
            $src = $this->data->buildDir('renders/jpg/' . $name . '.jpg');
            if ($media->isExist('wysiwyg/thirdshot/' . $name . '.jpg')) {
                continue; // never overwrite: some editorial images are made outside this pipeline (e.g. _build/hero)
            }
            if (is_readable($src)) {
                $media->writeFile('wysiwyg/thirdshot/' . $name . '.jpg', (string) file_get_contents($src));
            } else {
                $log("WARNING: missing editorial image $name.jpg (render scenes + export_jpg first)");
            }
        }
        foreach (glob($this->data->buildDir('cms/blocks') . '/*.html') ?: [] as $file) {
            [$meta, $html] = $this->parse($file);
            $block = $this->blockFactory->create()->load($meta['identifier'], 'identifier');
            $block->setIdentifier($meta['identifier'])
                ->setTitle($meta['title'])
                ->setContent($html)
                ->setIsActive(1)
                ->setStores([0])
                ->save();
            $log('block ' . $meta['identifier']);
        }
        foreach (glob($this->data->buildDir('cms/pages') . '/*.html') ?: [] as $file) {
            [$meta, $html] = $this->parse($file);
            $page = $this->pageFactory->create()->load($meta['identifier'], 'identifier');
            $page->setIdentifier($meta['identifier'])
                ->setTitle($meta['title'])
                ->setContentHeading($meta['heading'] ?? '')
                ->setContent($html)
                ->setPageLayout($meta['layout'] ?? '1column')
                ->setMetaTitle($meta['meta_title'] ?? $meta['title'])
                ->setMetaDescription($meta['meta_description'] ?? '')
                ->setIsActive(1)
                ->setStores([0])
                ->save();
            $log('page ' . $meta['identifier']);
        }
    }

    /** @return array{0: array, 1: string} */
    private function parse(string $file): array
    {
        $raw = (string) file_get_contents($file);
        if (!preg_match('/^\s*<!--\s*(\{.*?\})\s*-->\s*/s', $raw, $m)) {
            throw new LocalizedException(__('Missing JSON header in %1', $file));
        }
        $meta = json_decode($m[1], true, 512, JSON_THROW_ON_ERROR);
        return [$meta, trim(substr($raw, strlen($m[0])))];
    }
}
