<?php
declare(strict_types=1);

namespace ThirdShot\Performance\Plugin;

use Magento\Framework\View\Asset\Repository as AssetRepository;
use Magento\Theme\Block\Html\Header\CriticalCss;

/**
 * Inlined critical CSS keeps the relative url(../fonts/...) references of css/critical.css, which would resolve
 * against the page URL. Rewrite them to the versioned static theme URL so they hit the same files as the
 * <link rel="preload"> font hints (one download, no 404s).
 */
class AbsoluteCriticalCssUrls
{
    public function __construct(private readonly AssetRepository $assetRepository)
    {
    }

    public function afterGetCriticalCssData(CriticalCss $subject, $result)
    {
        if (!is_string($result) || $result === '') {
            return $result;
        }
        // getUrl() may return css/critical.min.css (CSS minification), so strip the file part by pattern.
        $themeBase = (string)preg_replace('~css/critical(\.min)?\.css$~', '', $this->assetRepository->getUrl('css/critical.css'));
        return (string)preg_replace('~url\(\s*([\'"]?)\.\./~', 'url($1' . $themeBase, $result);
    }
}
