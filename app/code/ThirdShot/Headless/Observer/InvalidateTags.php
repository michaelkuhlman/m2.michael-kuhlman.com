<?php
declare(strict_types=1);

namespace ThirdShot\Headless\Observer;

use Magento\Framework\App\Cache\Tag\Resolver;
use Magento\Framework\Event\Observer;
use Magento\Framework\Event\ObserverInterface;
use ThirdShot\Headless\Model\Notifier;

/** Same tag resolution as Magento's Varnish purge (InvalidateVarnishObserver), sent to the headless storefront. */
class InvalidateTags implements ObserverInterface
{
    public function __construct(
        private readonly Resolver $tagResolver,
        private readonly Notifier $notifier
    ) {
    }

    public function execute(Observer $observer): void
    {
        $object = $observer->getEvent()->getObject();
        if (!is_object($object)) {
            return;
        }
        $tags = $this->tagResolver->getTags($object);
        if ($tags) {
            $this->notifier->notify($tags);
        }
    }
}
