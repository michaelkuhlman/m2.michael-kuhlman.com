<?php
/**
 * bin/magento thirdshot:demo:seed [--fresh] [--step=attributes,categories,products,composite,reviews,cms]
 *
 * Builds the Third Shot Supply Co. demo catalogue from _build/ (catalog JSON, rendered images, CMS HTML).
 * Idempotent: existing records are updated; images are only attached to products without a gallery.
 * --fresh deletes every TS-* product first (use after re-rendering images).
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Console\Command;

use Magento\Catalog\Api\ProductRepositoryInterface;
use Magento\Catalog\Model\ResourceModel\Product\CollectionFactory;
use Magento\Framework\App\Area;
use Magento\Framework\App\Cache\Manager as CacheManager;
use Magento\Framework\App\State;
use Magento\Framework\Registry;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use ThirdShot\DemoData\Model\AttributeSetup;
use ThirdShot\DemoData\Model\CategorySetup;
use ThirdShot\DemoData\Model\CmsSetup;
use ThirdShot\DemoData\Model\CompositeSetup;
use ThirdShot\DemoData\Model\ProductSetup;
use ThirdShot\DemoData\Model\ReviewSetup;

class SeedCommand extends Command
{
    private const STEPS = ['attributes', 'categories', 'products', 'composite', 'reviews', 'cms'];

    public function __construct(
        private readonly State $state,
        private readonly Registry $registry,
        private readonly AttributeSetup $attributes,
        private readonly CategorySetup $categories,
        private readonly ProductSetup $products,
        private readonly CompositeSetup $composite,
        private readonly ReviewSetup $reviews,
        private readonly CmsSetup $cms,
        private readonly CollectionFactory $productCollection,
        private readonly ProductRepositoryInterface $productRepository,
        private readonly CacheManager $cacheManager
    ) {
        parent::__construct();
    }

    protected function configure(): void
    {
        $this->setName('thirdshot:demo:seed')
            ->setDescription('Build the Third Shot Supply Co. demo catalogue and CMS content from _build/')
            ->addOption('fresh', null, InputOption::VALUE_NONE, 'Delete all TS-* products first')
            ->addOption('step', null, InputOption::VALUE_REQUIRED, 'Comma separated: ' . implode(',', self::STEPS));
        parent::configure();
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        try {
            $this->state->setAreaCode(Area::AREA_ADMINHTML);
        } catch (\Magento\Framework\Exception\LocalizedException) {
            // area already set
        }
        $log = static fn (string $m) => $output->writeln('  ' . $m);
        $steps = $input->getOption('step')
            ? array_values(array_filter(array_map('trim', explode(',', (string) $input->getOption('step')))))
            : self::STEPS;
        $unknown = array_diff($steps, self::STEPS);
        if ($unknown) {
            $output->writeln('<error>unknown step(s): ' . implode(', ', $unknown) . '</error>');
            return Command::FAILURE;
        }

        if ($input->getOption('fresh')) {
            $this->deleteProducts($log);
        }
        $categoryIds = [];
        $categories = function () use (&$categoryIds, $log): array {
            return $categoryIds ?: ($categoryIds = $this->categories->install($log));
        };
        foreach ($steps as $step) {
            $output->writeln("<info>$step</info>");
            match ($step) {
                'attributes' => $this->attributes->install($log),
                'categories' => $categories(),
                'products' => $this->products->install($categories(), $log),
                'composite' => $this->composite->install($categories(), $log),
                'reviews' => $this->reviews->install($log),
                'cms' => $this->cms->install($log),
            };
        }
        // swatch data is written with SQL and CMS/catalog changed: drop the affected caches
        $this->cacheManager->clean(['eav', 'config', 'block_html', 'full_page', 'collections']);
        $output->writeln('<info>done (caches eav, config, block_html, full_page, collections cleaned)</info>');
        return Command::SUCCESS;
    }

    private function deleteProducts(callable $log): void
    {
        $this->registry->register('isSecureArea', true, true);
        $collection = $this->productCollection->create()->addAttributeToFilter('sku', ['like' => 'TS-%']);
        // composites first so their links go cleanly
        $order = ['bundle' => 0, 'grouped' => 1, 'configurable' => 2, 'simple' => 3];
        $items = $collection->getItems();
        usort($items, static fn ($a, $b) => ($order[$a->getTypeId()] ?? 9) <=> ($order[$b->getTypeId()] ?? 9));
        foreach ($items as $item) {
            $this->productRepository->deleteById($item->getSku());
        }
        $log(sprintf('deleted %d products', count($items)));
    }
}
