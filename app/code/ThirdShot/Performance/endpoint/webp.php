<?php
/**
 * nginx fallback for a missing media WebP sibling (`/media/<path>.jpg.webp`, `/media/<path>.jpg.w800.webp`).
 * Converts from the source file on disk, stores the result next to it (nginx serves it directly from then on)
 * and streams it. Only reachable through the `@m2_webp` named location; does not bootstrap Magento.
 */
declare(strict_types=1);

require __DIR__ . '/../Model/WebpConverter.php';

$mediaRoot = rtrim((string)($_SERVER['M2_MEDIA_ROOT'] ?? dirname(__DIR__, 5) . '/pub/media'), '/');
$uri = (string)parse_url((string)($_SERVER['REQUEST_URI'] ?? ''), PHP_URL_PATH);
$converter = new \ThirdShot\Performance\Model\WebpConverter();
$parsed = str_starts_with($uri, '/media/') ? $converter->parse(substr($uri, 7)) : null;

if ($parsed === null || !is_file($mediaRoot . '/' . $parsed[0])) {
    http_response_code(404);
    header('Cache-Control: no-store');
    exit;
}
[$source, $width] = $parsed;
$target = $mediaRoot . '/' . \ThirdShot\Performance\Model\WebpConverter::webpName($source, $width);

if (!is_file($target) && !$converter->convert($mediaRoot . '/' . $source, $target, $width)) {
    http_response_code(500);
    header('Cache-Control: no-store');
    exit;
}
header('Content-Type: image/webp');
header('Content-Length: ' . filesize($target));
header('Cache-Control: public, max-age=31536000');
header('X-Frame-Options: SAMEORIGIN');
readfile($target);
