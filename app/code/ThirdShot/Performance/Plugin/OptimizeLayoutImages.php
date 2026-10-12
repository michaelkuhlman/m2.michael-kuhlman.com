<?php
declare(strict_types=1);

namespace ThirdShot\Performance\Plugin;

use Magento\Framework\View\Layout;
use ThirdShot\Performance\Model\ImageMarkupOptimizer;

/**
 * Applies the image markup optimisation to the rendered page body (storefront area only, see etc/frontend/di.xml).
 * Runs before the full page cache stores the response, so cached pages carry the optimised markup.
 */
class OptimizeLayoutImages
{
    public function __construct(private readonly ImageMarkupOptimizer $optimizer)
    {
    }

    public function afterGetOutput(Layout $subject, $result)
    {
        return is_string($result) ? $this->optimizer->optimize($result) : $result;
    }
}
