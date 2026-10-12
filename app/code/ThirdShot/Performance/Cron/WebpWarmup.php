<?php
/**
 * Every minute: delete WebP siblings whose source changed or disappeared (so the next request regenerates them),
 * convert media images that have no WebP yet, and refresh the full page cache when product cache images were
 * converted (pages rendered before those images existed still point at the JPEG).
 */
declare(strict_types=1);

namespace ThirdShot\Performance\Cron;

use Magento\Framework\App\Cache\TypeListInterface;
use Magento\Framework\App\Filesystem\DirectoryList;
use Magento\Framework\Filesystem;
use Psr\Log\LoggerInterface;
use ThirdShot\Performance\Model\WebpConverter;

class WebpWarmup
{
    private const TIME_BUDGET = 45;

    public function __construct(
        private readonly Filesystem $filesystem,
        private readonly WebpConverter $converter,
        private readonly TypeListInterface $cacheTypeList,
        private readonly LoggerInterface $logger
    ) {
    }

    public function execute(): void
    {
        $root = rtrim($this->filesystem->getDirectoryRead(DirectoryList::MEDIA)->getAbsolutePath(), '/');
        $start = time();
        $removed = $converted = $productConverted = 0;

        foreach (WebpConverter::DIRS as $dir) {
            if (!is_dir("$root/$dir")) {
                continue;
            }
            $files = new \RecursiveIteratorIterator(
                new \RecursiveDirectoryIterator("$root/$dir", \FilesystemIterator::SKIP_DOTS)
            );
            foreach ($files as $file) {
                if (time() - $start > self::TIME_BUDGET) {
                    break 2;
                }
                $path = $file->getPathname();
                if (str_ends_with($path, '.webp')) {
                    $source = (string)preg_replace('~(\.w\d{3,4})?\.webp$~', '', $path);
                    if (!is_file($source) || filemtime($source) > $file->getMTime()) {
                        $removed += (int)@unlink($path);
                    }
                    continue;
                }
                if (!preg_match('~\.(jpe?g|png)$~i', $path) || is_file($path . '.webp')) {
                    continue;
                }
                if ($this->converter->convert($path, $path . '.webp')) {
                    $converted++;
                    $productConverted += (int)($dir === 'catalog/product/cache');
                }
            }
        }
        if ($productConverted > 0) {
            $this->cacheTypeList->cleanType('full_page');
        }
        if ($removed || $converted) {
            $this->logger->info(sprintf(
                'ThirdShot WebP warmup: %d converted (%d product cache), %d stale removed',
                $converted,
                $productConverted,
                $removed
            ));
        }
    }
}
