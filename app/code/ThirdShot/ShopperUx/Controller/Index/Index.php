<?php
/**
 * /saved - the guest "Saved" list. The page itself is static (full-page cacheable); the products come from
 * this browser's localStorage through /shopux/product/cards.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\Controller\Index;

use Magento\Framework\App\Action\HttpGetActionInterface;
use Magento\Framework\App\RequestInterface;
use Magento\Framework\Controller\Result\Forward;
use Magento\Framework\Controller\Result\ForwardFactory;
use Magento\Framework\View\Result\Page;
use Magento\Framework\View\Result\PageFactory;

class Index implements HttpGetActionInterface
{
    public function __construct(
        private readonly PageFactory $pageFactory,
        private readonly ForwardFactory $forwardFactory,
        private readonly RequestInterface $request
    ) {
    }

    public function execute(): Page|Forward
    {
        if ($this->request->getRouteName() !== 'saved') {
            return $this->forwardFactory->create()->forward('noroute');
        }
        $page = $this->pageFactory->create();
        $page->getConfig()->getTitle()->set(__('Saved items'));
        $page->getConfig()->setRobots('NOINDEX,NOFOLLOW');
        return $page;
    }
}
