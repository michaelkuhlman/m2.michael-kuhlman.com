<?php
/**
 * Order confirmation page: the order just placed (items, totals, ship-to), so the success page confirms what was
 * bought instead of showing only the order number. Reads the checkout session's last order; the page is never
 * full-page cached.
 */
declare(strict_types=1);

namespace ThirdShot\ShopperUx\ViewModel;

use Magento\Checkout\Model\Session as CheckoutSession;
use Magento\Framework\Pricing\PriceCurrencyInterface;
use Magento\Framework\View\Element\Block\ArgumentInterface;
use Magento\Sales\Model\Order;
use Magento\Sales\Model\Order\Address\Renderer as AddressRenderer;
use Magento\Sales\Model\Order\Item;

class LastOrder implements ArgumentInterface
{
    public function __construct(
        private readonly CheckoutSession $checkoutSession,
        private readonly PriceCurrencyInterface $priceCurrency,
        private readonly AddressRenderer $addressRenderer
    ) {
    }

    public function getOrder(): ?Order
    {
        $order = $this->checkoutSession->getLastRealOrder();
        return $order && $order->getId() ? $order : null;
    }

    public function formatPrice(float $amount, Order $order): string
    {
        return $this->priceCurrency->format($amount, false, PriceCurrencyInterface::DEFAULT_PRECISION, null, $order->getOrderCurrencyCode());
    }

    /** Address as HTML from the store's address template (values escaped by the renderer). */
    public function shippingAddressHtml(Order $order): string
    {
        $address = $order->getShippingAddress();
        return $address ? (string) $this->addressRenderer->format($address, 'html') : '';
    }

    /**
     * Chosen options of a line, e.g. ["Color" => "Glacier"] or a bundle's ["Balls" => "1 x Tour 40 ..."].
     *
     * @return array<string,string>
     */
    public function itemOptions(Item $item): array
    {
        $options = $item->getProductOptions() ?: [];
        $out = [];
        foreach ($options['attributes_info'] ?? [] as $opt) {
            $out[(string) ($opt['label'] ?? '')] = (string) ($opt['value'] ?? '');
        }
        foreach ($options['bundle_options'] ?? [] as $opt) {
            $values = array_map(
                static fn (array $v): string => ((int) ($v['qty'] ?? 1)) . ' x ' . ($v['title'] ?? ''),
                $opt['value'] ?? []
            );
            $out[(string) ($opt['label'] ?? '')] = implode(', ', $values);
        }
        return array_filter($out, static fn (string $v, string $k): bool => $k !== '' && $v !== '', ARRAY_FILTER_USE_BOTH);
    }
}
