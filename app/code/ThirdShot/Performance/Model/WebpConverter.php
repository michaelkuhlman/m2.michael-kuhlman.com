<?php
/**
 * Converts media JPEG/PNG files to WebP siblings (`file.jpg.webp`, resized `file.jpg.w800.webp`).
 *
 * Deliberately dependency-free: it is shared by the Magento cron job and by the tiny nginx fallback
 * endpoint (endpoint/webp.php), which must not bootstrap Magento.
 */
declare(strict_types=1);

namespace ThirdShot\Performance\Model;

class WebpConverter
{
    /** Media sub-trees whose images get WebP siblings. */
    public const DIRS = ['catalog/product/cache', 'catalog/category', 'wysiwyg'];

    /** Responsive widths offered in srcset for large editorial images (whitelist: no arbitrary resizes). */
    public const WIDTHS = [480, 800, 1200];

    private const QUALITY = 80;

    /** Matches a WebP request path relative to pub/media: [1] = source path, [2] = optional width. */
    private const PATH_PATTERN = '~^((?:catalog/product/cache|catalog/category|wysiwyg)/[A-Za-z0-9_\-./]+\.(?:jpe?g|png))'
        . '(?:\.w(\d{3,4}))?\.webp$~i';

    /**
     * @return array{0:string,1:?int}|null [source path relative to media root, width or null]
     */
    public function parse(string $webpPath): ?array
    {
        if (strpos($webpPath, '..') !== false || !preg_match(self::PATH_PATTERN, $webpPath, $m)) {
            return null;
        }
        $width = isset($m[2]) && $m[2] !== '' ? (int)$m[2] : null;
        if ($width !== null && !in_array($width, self::WIDTHS, true)) {
            return null;
        }
        return [$m[1], $width];
    }

    public static function webpName(string $source, ?int $width = null): string
    {
        return $source . ($width ? '.w' . $width : '') . '.webp';
    }

    /**
     * Write $target (WebP) from $source, optionally scaled down to $width. Atomic (temp file + rename).
     */
    public function convert(string $source, string $target, ?int $width = null): bool
    {
        $info = @getimagesize($source);
        if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG], true)) {
            return false;
        }
        $img = $info[2] === IMAGETYPE_PNG ? @imagecreatefrompng($source) : @imagecreatefromjpeg($source);
        if (!$img) {
            return false;
        }
        if ($info[2] === IMAGETYPE_PNG) {
            imagepalettetotruecolor($img);
            imagealphablending($img, false);
            imagesavealpha($img, true);
        }
        [$w, $h] = [$info[0], $info[1]];
        if ($width !== null && $width < $w) {
            $nh = (int)round($h * $width / $w);
            $scaled = imagecreatetruecolor($width, $nh);
            imagealphablending($scaled, false);
            imagesavealpha($scaled, true);
            imagecopyresampled($scaled, $img, 0, 0, 0, 0, $width, $nh, $w, $h);
            imagedestroy($img);
            $img = $scaled;
        }
        $tmp = $target . '.' . getmypid() . '.tmp';
        $ok = imagewebp($img, $tmp, self::QUALITY);
        imagedestroy($img);
        if (!$ok || !@rename($tmp, $target)) {
            @unlink($tmp);
            return false;
        }
        @chmod($target, 0664);
        return true;
    }

    /** Natural pixel size of an image, or null. */
    public function size(string $file): ?array
    {
        $info = @getimagesize($file);
        return $info ? [$info[0], $info[1]] : null;
    }
}
