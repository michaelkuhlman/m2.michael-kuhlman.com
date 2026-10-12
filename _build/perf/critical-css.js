#!/usr/bin/env node
/**
 * Generates the theme's critical (first-screen) CSS from the LIVE store and installs it as css/critical.css
 * (theme source + the deployed/minified copies Magento reads). Magento inlines it in <head>
 * (dev/css/use_css_critical_path=1) and loads styles-m / styles-l asynchronously.
 *
 * How: every page type is loaded at a phone (412x823) and a desktop (1440x900) viewport with the HTML rewritten
 * so the full stylesheets are render-blocking again (as without critical CSS). A rule is kept when one of its
 * selectors matches an element that intersects the first screen (plus a margin), or a box-less element
 * (display:none rules must survive, or hidden things flash). Then, self-correcting rounds: each page is rendered
 * with ONLY the candidate critical CSS (full sheets loaded as media="not all", readable but not applied) and rules
 * for everything visible in that layout are added, until nothing new appears (content that would float up into
 * the first screen without its rules, JS-built elements...). Kept rules are serialised from the CSSOM in original
 * order, so the cascade is unchanged. @font-face rules are kept, keyframes dropped.
 *
 * Deps: Playwright (/opt/playwright) and clean-css (/home/kai/m2perf-tools). Run via _build/perf/critical-css.sh.
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const CleanCSS = require('clean-css');

const BASE = 'https://m2.michael-kuhlman.com';
const ROOT = path.resolve(__dirname, '../..');
const STATIC = path.join(ROOT, 'pub/static/frontend/ThirdShot/court/en_US');
const THEME_OUT = path.join(ROOT, 'app/design/frontend/ThirdShot/court/web/css/critical.css');
const PAGES = ['/', '/paddles.html', '/balls.html', '/kitchen-line-carbon-16.html', '/court-ready-starter-set.html',
    '/tour-40-ball-packs.html', '/about', '/faq', '/no-such-page', '/catalogsearch/result/?q=paddle', '/checkout/cart/', '/contact'];
const VIEWPORTS = [[412, 823], [1440, 900]];
const FOLD_MARGIN = 1.25; // keep rules for elements down to 1.25 x viewport height

// Runs in the page: walk all same-origin stylesheets; keys = "sheet/rule/rule|selector".
function collect({foldPx, keepKeys: kk}) {
    const keepKeys = kk ? {V: new Set(kk.V), H: new Set(kk.H)} : null;
    const DYNAMIC = /::?(before|after|placeholder|selection|marker|backdrop|first-line|first-letter|-webkit-[\w-]+|-moz-[\w-]+|hover|focus|focus-within|focus-visible|active|visited)(\([^)]*\))?/g;
    const kept = [];
    const out = [];
    const splitSelectors = (text) => {
        const res = []; let depth = 0; let cur = '';
        for (const ch of text) {
            if (ch === '(' || ch === '[') depth++;
            if (ch === ')' || ch === ']') depth--;
            if (ch === ',' && depth === 0) { res.push(cur.trim()); cur = ''; } else { cur += ch; }
        }
        if (cur.trim()) res.push(cur.trim());
        return res;
    };
    const matches = (sel) => {
        let els = [];
        try { els = document.querySelectorAll(sel); } catch (e) { /* pseudo-element etc. */ }
        if (!els.length) {
            try { els = document.querySelectorAll(sel.replace(DYNAMIC, '').trim() || '*'); } catch (e) { return false; }
        }
        let hidden = false;
        for (const el of els) {
            const r = el.getBoundingClientRect();
            if (r.width === 0 && r.height === 0) { hidden = true; continue; }
            if (r.top < foldPx && r.bottom >= 0) return 'V';
        }
        return hidden ? 'H' : false;
    };
    const walk = (rules, prefix, sink) => {
        Array.from(rules).forEach((rule, i) => {
            const key = prefix + '/' + i;
            if (rule instanceof CSSStyleRule) {
                // V = matches something in the first screen: whole rule. H = only box-less (hidden) elements:
                // all that matters at first paint is that they stay hidden, so keep display/visibility only.
                const vis = []; const hid = [];
                splitSelectors(rule.selectorText).forEach((s) => {
                    const k = key + '|' + s;
                    if (keepKeys) {
                        if (keepKeys.V.has(k)) vis.push(s); else if (keepKeys.H.has(k)) hid.push(s);
                        return;
                    }
                    const m = matches(s);
                    if (m) kept.push(m + k);
                });
                if (vis.length && rule.style.cssText) sink.push(vis.join(',') + '{' + rule.style.cssText + '}');
                const dv = ['display', 'visibility'].filter((p) => rule.style.getPropertyValue(p))
                    .map((p) => p + ':' + rule.style.getPropertyValue(p)
                        + (rule.style.getPropertyPriority(p) ? ' !important' : '')).join(';');
                if (hid.length && dv) sink.push(hid.join(',') + '{' + dv + '}');
            } else if (rule instanceof CSSMediaRule || rule instanceof CSSSupportsRule) {
                const inner = [];
                walk(rule.cssRules, key, inner);
                if (inner.length) {
                    const cond = rule instanceof CSSMediaRule ? '@media ' + rule.media.mediaText : '@supports ' + rule.conditionText;
                    sink.push(cond + '{' + inner.join('') + '}');
                }
            } else if (rule instanceof CSSFontFaceRule) {
                sink.push(rule.cssText);
            }
        });
    };
    Array.from(document.styleSheets).forEach((sheet) => {
        if (!sheet.href || !/\/css\/styles-[ml]\.min\.css/.test(sheet.href)) return;
        const inner = [];
        walk(sheet.cssRules, sheet.href.includes('styles-l') ? 'L' : 'M', inner);
        const media = sheet.media.mediaText;
        if (inner.length) out.push(media && media !== 'all' ? '@media ' + media + '{' + inner.join('') + '}' : inner.join(''));
    });
    return keepKeys ? out.join('\n') : kept;
}

(async () => {
    const browser = await chromium.launch({args: ['--no-sandbox']});
    const keys = new Set();      // 'V…' / 'H…' prefixed selector keys
    // mode 'full': stylesheets render-blocking, inline critical CSS removed (layout as without critical CSS).
    // mode 'crit': stylesheets present but not applied (media="not all"), inline critical CSS = candidate.
    const open = async (url, width, height, mode, candidate, js = true) => {
        const ctx = await browser.newContext({viewport: {width, height}, javaScriptEnabled: js});
        const page = await ctx.newPage();
        await page.route(BASE + '/**', async (route) => {
            const req = route.request();
            if (req.resourceType() !== 'document') return route.continue();
            const resp = await route.fetch();
            let html = await resp.text();
            const style = mode === 'crit' ? '<style data-type="criticalCss">' + candidate.replace(/\$/g, '$$$$') + '</style>' : '';
            html = html.replace(/<style[^>]*data-type="criticalCss"[^>]*>[\s\S]*?<\/style>/, style)
                .replace(/<link rel="stylesheet" media="print" onload="[^"]*?media&#x3D;&#x27;([^"]*?)&#x27;"/g,
                    (m, media) => '<link rel="stylesheet" media="' + (mode === 'crit' ? 'not all' : media
                        .replace(/&#x20;/g, ' ').replace(/&#x28;/g, '(').replace(/&#x29;/g, ')').replace(/&#x3A;/g, ':')) + '"');
            // ThirdShot_Performance's loader attaches the full stylesheets itself ({"l": href, "m": media} entries)
            if (mode === 'crit') {
                html = html.replace(/("l":"[^"]+","m":")[^"]*(")/g, '$1not all$2');
            }
            return route.fulfill({response: resp, body: html});
        });
        await page.goto(url, {waitUntil: js ? 'networkidle' : 'load', timeout: 60000});
        await page.evaluate(() => document.fonts.ready);
        await page.waitForTimeout(300);
        return {ctx, page};
    };
    const capture = async (mode, candidate, js = true) => {
        let ok = 0;
        let added = 0;
        const jobs = [];
        PAGES.forEach((p) => VIEWPORTS.forEach(([w, h]) => jobs.push([p, w, h])));
        const worker = async () => {
            for (let job = jobs.shift(); job; job = jobs.shift()) {
                const [p, w, h] = job;
                try {
                    const {ctx, page} = await open(BASE + p, w, h, mode, candidate, js);
                    const kept = await page.evaluate(collect, {foldPx: h * FOLD_MARGIN, keepKeys: null});
                    kept.forEach((k) => { if (!keys.has(k)) { keys.add(k); added++; } });
                    ok++;
                    await ctx.close();
                } catch (e) {
                    process.stderr.write(`FAIL ${mode} ${p} ${w}: ${e.message}\n`);
                }
            }
        };
        await Promise.all([worker(), worker(), worker()]);
        if (ok < PAGES.length * VIEWPORTS.length - 2) {
            throw new Error('too many captures failed, keeping the previous critical.css');
        }
        process.stderr.write(`${mode}${js ? '' : ' (no JS)'} pass: +${added} selectors (${keys.size} total)\n`);
        return added;
    };
    const serialise = async () => {
        const {ctx, page} = await open(BASE + '/', 1440, 900, 'full');
        const V = []; const H = [];
        keys.forEach((k) => (k[0] === 'V' ? V : H).push(k.slice(1)));
        const css = await page.evaluate(collect, {foldPx: 0, keepKeys: {V, H}});
        await ctx.close();
        return new CleanCSS({level: 1}).minify(css).styles;
    };

    // Both states matter: before JS boots (it starts only after the LCP image, see ThirdShot_Performance
    // DeferScripts) and after (JS-built and JS-toggled elements).
    await capture('full', null, false);
    await capture('full');
    let out = await serialise();
    for (let round = 1; round <= 4; round++) {
        if (!(await capture('crit', out))) {
            break;
        }
        out = await serialise();
    }
    await browser.close();

    out += new CleanCSS({level: 1}).minify(fs.readFileSync(path.join(__dirname, 'critical-extra.css'), 'utf8')).styles;
    const banner = '/* critical CSS: generated by _build/perf/critical-css.js from the live store, do not edit */\n';
    // Magento reads css/critical.min.css (CSS minification is on) and caches it in pub/static and
    // var/view_preprocessed: refresh every copy so the next page render inlines the new file.
    const targets = [THEME_OUT, path.join(STATIC, 'css/critical.css'), path.join(STATIC, 'css/critical.min.css'),
        path.join(ROOT, 'var/view_preprocessed/pub/static/frontend/ThirdShot/court/en_US/css/critical.min.css')];
    for (const f of targets) {
        if (f === THEME_OUT || fs.existsSync(path.dirname(f))) {
            fs.writeFileSync(f + '.tmp', banner + out + '\n');
            fs.renameSync(f + '.tmp', f);
        }
    }
    process.stderr.write(`critical.css ${out.length} bytes, ${keys.size} selectors\n`);
})().catch((e) => { console.error(e); process.exit(1); });
