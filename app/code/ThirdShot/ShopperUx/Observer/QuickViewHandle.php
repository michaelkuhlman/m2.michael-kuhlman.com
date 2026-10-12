<?php
/**
 * Product pages requested with ?ts_qv=1 (the quick-view iframe) get the stripped "shopux_quickview" layout.
 * The parameter is part of the URL, so the full-page cache keeps the two versions apart.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Observer;

use Magento\Framework\App\RequestInterface;
use Magento\Framework\Event\Observer;
use Magento\Framework\Event\ObserverInterface;

class QuickViewHandle implements ObserverInterface
{
    public function __construct(private readonly RequestInterface $request)
    {
    }

    public function execute(Observer $observer): void
    {
        if ($observer->getEvent()->getData('full_action_name') !== 'catalog_product_view'
            || $this->request->getParam('ts_qv') !== '1'
        ) {
            return;
        }
        $observer->getEvent()->getData('layout')->getUpdate()->addHandle('shopux_quickview');
    }
}
