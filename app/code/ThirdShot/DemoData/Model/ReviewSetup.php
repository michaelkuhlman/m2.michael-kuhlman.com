<?php
/**
 * Approved customer reviews with a 1-5 star "Rating" vote, spread over the last few months.
 */
declare(strict_types=1);

namespace ThirdShot\DemoData\Model;

use Magento\Catalog\Api\ProductRepositoryInterface;
use Magento\Framework\App\ResourceConnection;
use Magento\Review\Model\Rating;
use Magento\Review\Model\RatingFactory;
use Magento\Review\Model\Review;
use Magento\Review\Model\ReviewFactory;

class ReviewSetup
{
    public function __construct(
        private readonly ReviewFactory $reviewFactory,
        private readonly RatingFactory $ratingFactory,
        private readonly ProductRepositoryInterface $productRepository,
        private readonly ResourceConnection $resource,
        private readonly DataSource $data
    ) {
    }

    public function install(callable $log): void
    {
        $rating = $this->activeRating();
        $optionIds = $this->ratingOptions((int) $rating->getId());
        $c = $this->resource->getConnection();
        $reviewTable = $this->resource->getTableName('review');
        $count = 0;
        $seq = 0;
        foreach ($this->data->catalog()['products'] as $row) {
            if (empty($row['reviews'])) {
                continue;
            }
            $productId = (int) $this->productRepository->get($row['sku'])->getId();
            $already = (int) $c->fetchOne(
                $c->select()->from($reviewTable, 'COUNT(*)')->where('entity_pk_value = ?', $productId)
            );
            if ($already) {
                continue;
            }
            foreach ($row['reviews'] as $r) {
                $review = $this->reviewFactory->create();
                $review->setEntityId($review->getEntityIdByCode(Review::ENTITY_PRODUCT_CODE))
                    ->setEntityPkValue($productId)
                    ->setStatusId(Review::STATUS_APPROVED)
                    ->setTitle($r['title'])
                    ->setDetail($r['detail'])
                    ->setNickname($r['nickname'])
                    ->setStoreId(0)
                    ->setStores([1])
                    ->save();
                $this->ratingFactory->create()
                    ->setRatingId((int) $rating->getId())
                    ->setReviewId((int) $review->getId())
                    ->addOptionVote($optionIds[(int) $r['rating']], $productId);
                $review->aggregate();
                $days = 6 + (($seq * 37) % 150);
                $c->update($reviewTable, ['created_at' => date('Y-m-d H:i:s', strtotime("-$days days -" . ($seq % 9) . ' hours'))],
                    ['review_id = ?' => (int) $review->getId()]);
                $seq++;
                $count++;
            }
        }
        $log("$count reviews created");
    }

    private function activeRating(): Rating
    {
        $rating = $this->ratingFactory->create()->load('Rating', 'rating_code');
        if (!$rating->getId()) {
            $rating = $this->ratingFactory->create()->load('Quality', 'rating_code');
        }
        $rating->setIsActive(1)->setStores([0, 1])->save();
        return $rating;
    }

    /** @return array<int,int> star value => option id */
    private function ratingOptions(int $ratingId): array
    {
        $c = $this->resource->getConnection();
        $rows = $c->fetchPairs($c->select()
            ->from($this->resource->getTableName('rating_option'), ['value', 'option_id'])
            ->where('rating_id = ?', $ratingId));
        return array_map('intval', $rows);
    }
}
