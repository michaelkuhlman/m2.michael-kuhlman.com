<?php
/**
 * Boots the RequireJS chain after the first screen has painted, on storefront browsing pages.
 *
 * Runs after Magento's JsFooterPlugin (dev/js/move_script_to_bottom), which leaves every script at the end of
 * <body>, still parser-blocking. Here those scripts are taken out and replaced by one small loader that waits until
 * the page's high-priority image(s) (the LCP candidate: hero, category banner, product photo, all marked
 * fetchpriority="high") have loaded and a frame has been painted (capped at 2.5 s), then runs the original scripts
 * in their original order. The full stylesheets (made async by Magento's critical CSS path) are attached at the same
 * moment, so they do not take bandwidth from the LCP image either (<noscript> keeps them for no-JS clients). Scripts:
 * external files are inserted with async=false (downloaded in parallel, executed in
 * order) and inline code runs through indirect eval, i.e. as sloppy-mode global code exactly like a classic inline
 * script. The inline `var require = {...}` bootstrap stays a classic script. Nothing waits for user input: JS
 * starts as soon as the first screen is on the glass, instead of competing with it.
 * Indirect eval needs 'unsafe-eval' in script-src, which Magento's storefront CSP already allows (KnockoutJS).
 *
 * Checkout, cart and account pages are never touched.
 */
declare(strict_types=1);

namespace ThirdShot\Performance\Plugin;

use Magento\Framework\App\Config\ScopeConfigInterface;
use Magento\Framework\App\Request\Http as HttpRequest;
use Magento\Framework\App\ResponseInterface;
use Magento\Framework\View\Result\Layout;
use Magento\Store\Model\ScopeInterface;

class DeferScripts
{
    private const PAGES = [
        'cms_index_index', 'cms_page_view', 'cms_noroute_index',
        'catalog_category_view', 'catalog_product_view',
        'catalogsearch_result_index', 'catalogsearch_advanced_result', 'contact_index_index',
    ];

    public function __construct(
        private readonly ScopeConfigInterface $scopeConfig,
        private readonly HttpRequest $request
    ) {
    }

    public function afterRenderResult(Layout $subject, Layout $result, ResponseInterface $response): Layout
    {
        if (!in_array($this->request->getFullActionName(), self::PAGES, true)
            || !$this->scopeConfig->isSetFlag('dev/js/move_script_to_bottom', ScopeInterface::SCOPE_STORE)
            || !method_exists($response, 'getContent')
        ) {
            return $result;
        }
        $html = (string)$response->getContent();
        $converted = $this->convert($html);
        if ($converted !== null) {
            $response->setContent($converted);
        }
        return $result;
    }

    private function convert(string $html): ?string
    {
        $queue = [];
        $out = preg_replace_callback('~<script\b([^>]*)>(.*?)</script>~is', function (array $m) use (&$queue) {
            [$tag, $attrs, $code] = $m;
            $type = preg_match('~\stype\s*=\s*["\']([^"\']*)["\']~i', $attrs, $t)
                ? strtolower(html_entity_decode($t[1], ENT_QUOTES | ENT_HTML5)) : '';
            if ($type !== '' && $type !== 'text/javascript') {
                return $tag; // x-magento-init, speculationrules, templates, JSON...
            }
            if (preg_match('~\ssrc\s*=\s*["\']([^"\']+)["\']~i', $attrs, $src)) {
                $queue[] = ['s' => html_entity_decode($src[1], ENT_QUOTES | ENT_HTML5)];
                return '';
            }
            if (trim($code) === '' || preg_match('~^\s*var\s+(LOCALE|require)\s*=~', $code)) {
                return $tag; // RequireJS bootstrap globals: must exist before require.js loads
            }
            $queue[] = ['c' => $code];
            return '';
        }, $html);
        $pos = is_string($out) ? strrpos($out, '</body') : false;
        if ($pos === false || !$queue) {
            return null;
        }
        // Async stylesheets from Magento's AsyncCssPlugin: <link rel="stylesheet" media="print" onload="...media='X'">
        $css = [];
        $out = (string)preg_replace_callback(
            '~<link rel="stylesheet" media="print" onload="([^"]*)" href="([^"]+)">~',
            function (array $m) use (&$css) {
                $onload = html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5);
                if (!preg_match("~this\\.media='([^']+)'~", $onload, $media) || $media[1] === 'print') {
                    return $m[0];
                }
                $href = html_entity_decode($m[2], ENT_QUOTES | ENT_HTML5);
                $css[] = ['h' => $href, 'm' => $media[1]];
                return '<noscript><link rel="stylesheet" media="' . htmlspecialchars($media[1]) . '" href="'
                    . htmlspecialchars($href) . '"></noscript>';
            },
            $out
        );
        $queue = array_merge(array_map(fn ($c) => ['l' => $c['h'], 'm' => $c['m']], $css), $queue);
        $pos = strrpos($out, '</body');
        $json = json_encode($queue, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG
            | JSON_INVALID_UTF8_SUBSTITUTE);
        return substr_replace($out, '<script>' . str_replace('__QUEUE__', (string)$json, self::LOADER) . "</script>\n", $pos, 0);
    }

    private const LOADER = <<<'JS'
(function(q,d,w){var i=0,go=0;function next(){var last=null;while(i<q.length&&q[i].l){var c=d.createElement('link');
c.rel='stylesheet';c.media=q[i].m;c.href=q[i++].l;d.head.appendChild(c);}while(i<q.length&&q[i].s){var e=d.createElement('script');
e.src=q[i++].s;e.async=false;d.body.appendChild(e);last=e;}if(last){last.onload=last.onerror=next;return;}
while(i<q.length&&!q[i].s){try{(0,eval)(q[i].c);}catch(x){setTimeout(function(){throw x;});}i++;}if(i<q.length){next();}}
function start(){if(!go){go=1;next();}}
function painted(){w.requestAnimationFrame?w.requestAnimationFrame(function(){setTimeout(start,0);}):start();}
function ready(){var imgs=[].slice.call(d.querySelectorAll('img[fetchpriority="high"]')),n=imgs.length;
setTimeout(start,2500);if(d.visibilityState==='hidden'||!n){painted();return;}
imgs.forEach(function(im){if(im.complete){if(!--n)painted();}else{im.addEventListener('load',done);im.addEventListener('error',done);}});
function done(){if(!--n)painted();}}
d.readyState==='loading'?d.addEventListener('DOMContentLoaded',ready):ready();})(__QUEUE__,document,window);
JS;
}
