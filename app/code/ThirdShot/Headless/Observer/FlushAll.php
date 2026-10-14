<?php
declare(strict_types=1);

namespace ThirdShot\Headless\Observer;

use Magento\Framework\Event\Observer;
use Magento\Framework\Event\ObserverInterface;
use ThirdShot\Headless\Model\Notifier;

/** A full cache flush (or a config save) in Magento drops every headless cache too. */
class FlushAll implements ObserverInterface
{
    public function __construct(private readonly Notifier $notifier)
    {
    }

    public function execute(Observer $observer): void
    {
        $this->notifier->notify([]);
    }
}
