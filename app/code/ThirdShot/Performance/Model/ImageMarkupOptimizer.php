<?php
/**
 * Rewrites storefront HTML so media images are delivered as WebP, editorial images get a responsive srcset
 * and intrinsic size, and the likely LCP images get fetchpriority="high".
 *
 * A URL is only switched to WebP when its source file exists on disk: nginx then serves the `.webp` sibling,
 * or hands a miss to endpoint/webp.php, which converts from that source. Product cache images that Magento
 * has not generated yet keep their JPEG URL; the WebpWarmup cron converts them and refreshes the page cache.
 */
declare(strict_types=1);

namespace ThirdShot\Performance\Model;

use Magento\Framework\App\Filesystem\DirectoryList;
use Magento\Framework\Filesystem;
use Magento\Framework\UrlInterface;
use Magento\Store\Model\StoreManagerInterface;

class ImageMarkupOptimizer
{
    private const DIR_RE = '(?:catalog/product/cache|catalog/category|wysiwyg)';
    private const END_RE = '(?=["\'\s),\\\\?&;<]|$)';

    private ?string $mediaUrl = null;
    private ?string $mediaPath = null;
    /** @var array<string,bool> */
    private array $exists = [];

    public function __construct(
        private readonly StoreManagerInterface $storeManager,
        private readonly Filesystem $filesystem,
        private readonly WebpConverter $converter
    ) {
    }

    public function optimize(string $html): string
    {
        if ($html === '' || strpos($html, '/media/') === false && strpos($html, '\/media\/') === false) {
            return $html;
        }
        $this->mediaUrl ??= (string)$this->storeManager->getStore()->getBaseUrl(UrlInterface::URL_TYPE_MEDIA);
        $this->mediaPath ??= rtrim($this->filesystem->getDirectoryRead(DirectoryList::MEDIA)->getAbsolutePath(), '/');

        $html = (string)preg_replace_callback('~<img\b[^>]*>~i', fn (array $m) => $this->img($m[0]), $html);

        $plain = preg_quote($this->mediaUrl, '~');
        $html = (string)preg_replace_callback(
            '~(' . $plain . ')(' . self::DIR_RE . '/[A-Za-z0-9_\-./]+?\.(?:jpe?g|png))' . self::END_RE . '~i',
            fn (array $m) => $m[1] . $this->webpIfAvailable($m[2]),
            $html
        );
        $escaped = preg_quote(str_replace('/', '\/', $this->mediaUrl), '~');
        $escDir = str_replace('/', '\\\\/', self::DIR_RE);
        return (string)preg_replace_callback(
            '~(' . $escaped . ')(' . $escDir . '\\\\/[A-Za-z0-9_\-.\\\\/]+?\.(?:jpe?g|png))' . self::END_RE . '~i',
            fn (array $m) => $m[1] . str_replace('/', '\/', $this->webpIfAvailable(str_replace('\/', '/', $m[2]))),
            $html
        );
    }

    private function img(string $tag): string
    {
        if (strpos($tag, 'gallery-placeholder__image') !== false) {
            return $this->addAttr($tag, 'fetchpriority', 'high');
        }
        $re = '~\ssrc="' . preg_quote($this->mediaUrl, '~') . '((?:catalog/category|wysiwyg)/[A-Za-z0-9_\-./]+?\.(?:jpe?g|png))"~i';
        if (!preg_match($re, $tag, $m) || !$this->sourceExists($m[1])) {
            return $tag;
        }
        $path = $m[1];
        $size = $this->converter->size($this->mediaPath . '/' . $path);
        if ($size === null) {
            return $tag;
        }
        [$w, $h] = $size;
        if (!preg_match('~\swidth=~i', $tag)) {
            $tag = $this->addAttr($tag, 'width', (string)$w);
            $tag = $this->addAttr($tag, 'height', (string)$h);
        }
        if (!preg_match('~\ssrcset=~i', $tag) && $w > WebpConverter::WIDTHS[0]) {
            $set = [];
            foreach (WebpConverter::WIDTHS as $cw) {
                if ($cw < $w * 0.9) {
                    $set[] = $this->mediaUrl . WebpConverter::webpName($path, $cw) . ' ' . $cw . 'w';
                }
            }
            $set[] = $this->mediaUrl . WebpConverter::webpName($path) . ' ' . $w . 'w';
            $tag = $this->addAttr($tag, 'srcset', implode(', ', $set));
            if (!preg_match('~\ssizes=~i', $tag)) {
                $tag = $this->addAttr($tag, 'sizes', '100vw');
            }
        }
        // Category banner: first thing on a category page and usually its LCP element.
        if (str_starts_with($path, 'catalog/category/') && !preg_match('~\sloading=~i', $tag)) {
            $tag = $this->addAttr($tag, 'fetchpriority', 'high');
        }
        return $tag;
    }

    private function addAttr(string $tag, string $name, string $value): string
    {
        if (preg_match('~\s' . $name . '=~i', $tag)) {
            return $tag;
        }
        return (string)preg_replace('~^<img\b~i', '<img ' . $name . '="' . htmlspecialchars($value) . '"', $tag, 1);
    }

    private function webpIfAvailable(string $path): string
    {
        return $this->sourceExists($path) ? WebpConverter::webpName($path) : $path;
    }

    private function sourceExists(string $path): bool
    {
        return $this->exists[$path] ??= (strpos($path, '..') === false && is_file($this->mediaPath . '/' . $path));
    }
}
