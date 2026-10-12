<?php
/**
 * Top-level categories under the default root, with a banner image (category `image` attribute).
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Catalog\Api\CategoryRepositoryInterface;
use Magento\Catalog\Model\CategoryFactory;
use Magento\Catalog\Model\ResourceModel\Category\CollectionFactory;
use Magento\Framework\App\Filesystem\DirectoryList;
use Magento\Framework\Filesystem;
use Magento\Store\Model\StoreManagerInterface;

class CategorySetup
{
    public function __construct(
        private readonly CategoryFactory $categoryFactory,
        private readonly CategoryRepositoryInterface $categoryRepository,
        private readonly CollectionFactory $collectionFactory,
        private readonly StoreManagerInterface $storeManager,
        private readonly Filesystem $filesystem,
        private readonly DataSource $data
    ) {
    }

    /**
     * @return array<string,int> category code => id
     */
    public function install(callable $log): array
    {
        $rootId = (int) $this->storeManager->getStore(1)->getRootCategoryId();
        $media = $this->filesystem->getDirectoryWrite(DirectoryList::MEDIA);
        $media->create('catalog/category');
        $ids = [];
        foreach ($this->data->catalog()['categories'] as $pos => $row) {
            $urlKey = $this->data->slug($row['code'] === 'bags' ? 'bags-covers' :
                ($row['code'] === 'apparel' ? 'apparel-headwear' :
                    ($row['code'] === 'training' ? 'court-training' : $row['code'])));
            $existing = $this->collectionFactory->create()
                ->addAttributeToFilter('url_key', $urlKey)
                ->addAttributeToFilter('parent_id', $rootId)
                ->getFirstItem();
            $category = $existing->getId()
                ? $this->categoryFactory->create()->setStoreId(0)->load($existing->getId())
                : $this->categoryFactory->create();

            $image = null;
            // a dedicated wide crop for the category page header (16:7) wins over the 4:3 home tile image
            $banner = $this->data->buildDir('renders/jpg/catbanner_' . $row['code'] . '.jpg');
            if (!is_readable($banner)) {
                $banner = $this->data->buildDir('renders/jpg/cat_' . $row['code'] . '.jpg');
            }
            if (is_readable($banner)) {
                $image = 'ts-' . $row['code'] . '.jpg';
                $media->writeFile('catalog/category/' . $image, (string) file_get_contents($banner));
            }

            $category->setStoreId(0)
                ->setName($row['name'])
                ->setUrlKey($urlKey)
                ->setParentId($rootId)
                ->setIsActive(true)
                ->setIncludeInMenu(true)
                ->setIsAnchor(true)
                ->setPosition($pos + 1)
                ->setDescription($row['description'] ?? '')
                ->setMetaTitle($row['name'] . ' | Third Shot Supply Co.')
                ->setMetaDescription($row['meta_description'] ?? '')
                ->setDisplayMode('PRODUCTS')
                ->setAvailableSortBy(['position', 'name', 'price'])
                ->setDefaultSortBy('position');
            if (!$category->getId()) {
                $parent = $this->categoryRepository->get($rootId);
                $category->setPath($parent->getPath());
            }
            if ($image) {
                $category->setImage($image);
            }
            $category->save();
            $ids[$row['code']] = (int) $category->getId();
            $log(sprintf('category %s #%d', $row['name'], $category->getId()));
        }
        return $ids;
    }
}
