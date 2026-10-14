<?php
declare(strict_types=1);

namespace ThirdShot\Headless\Model;

use Magento\Framework\App\DeploymentConfig;
use Magento\Framework\HTTP\Client\CurlFactory;
use Psr\Log\LoggerInterface;

/**
 * POSTs {"tags":[...]} to the headless storefront's /api/revalidate, signed with HMAC-SHA256 (X-Signature).
 * URL and secret live in app/etc/env.php under 'headless' => ['revalidate_url' => ..., 'revalidate_secret' => ...]
 * (not in git); without them this is a no-op. Never throws: a slow or down storefront must not break an admin save.
 */
class Notifier
{
    /** @var array<string, true> tag sets already sent in this request */
    private array $sent = [];

    public function __construct(
        private readonly DeploymentConfig $deploymentConfig,
        private readonly CurlFactory $curlFactory,
        private readonly LoggerInterface $logger
    ) {
    }

    /**
     * @param string[] $tags Magento cache tags; an empty list means "everything".
     */
    public function notify(array $tags): void
    {
        try {
            $url = (string)$this->deploymentConfig->get('headless/revalidate_url');
            $secret = (string)$this->deploymentConfig->get('headless/revalidate_secret');
            if ($url === '' || $secret === '') {
                return;
            }
            $tags = array_values(array_unique(array_filter(array_map('strval', $tags))));
            sort($tags);
            $tags = array_slice($tags ?: ['config'], 0, 500);
            $key = implode(',', $tags);
            if (isset($this->sent[$key])) {
                return;
            }
            $this->sent[$key] = true;

            $body = (string)json_encode(['tags' => $tags]);
            $curl = $this->curlFactory->create();
            $curl->setTimeout(4);
            $curl->addHeader('Content-Type', 'application/json');
            $curl->addHeader('X-Signature', hash_hmac('sha256', $body, $secret));
            $curl->post($url, $body);
            if ($curl->getStatus() !== 200) {
                $this->logger->warning('ThirdShot_Headless: revalidate answered ' . $curl->getStatus());
            }
        } catch (\Throwable $e) {
            $this->logger->warning('ThirdShot_Headless: revalidate failed: ' . $e->getMessage());
        }
    }
}
