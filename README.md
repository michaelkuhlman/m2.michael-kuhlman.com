# Third Shot Supply Co. (Magento 2 demo store)

Live: **https://m2.michael-kuhlman.com**

A portfolio demo store for a fictional premium pickleball brand, built on **Mage-OS 3.5** (the open-source
distribution of Magento Open Source, core Magento 2.4.9). It is a demo: no real orders, payments, shipping or email.
The only payment method is Check / Money order and a site-wide notice says so.

## What is in this repository

Only the code and sources that are ours. Everything composer installs (`vendor/`, `lib/`, `setup/`, `pub/` entry
points) and everything Magento generates (`generated/`, `pub/static/`, `var/`) is rebuilt, never committed.

| Path | What it is |
|---|---|
| `app/design/frontend/ThirdShot/court/` | The storefront theme, a Luma child: brand tokens and LESS in `web/css/source/` (`ts/_header`, `_catalog`, `_product`, `_checkout`, ...), layout XML overrides, a few templates, self-hosted Fraunces + Inter fonts |
| `app/code/ThirdShot/DemoData/` | `bin/magento thirdshot:demo:seed`: builds the attributes, swatches, categories, all product types (simple, configurable, bundle, grouped), images, reviews and CMS content from `_build/`. Idempotent and MSI-safe |
| `app/code/ThirdShot/Performance/` | Front-end speed: WebP delivery with srcset, deferred script boot after first paint, native critical CSS path fixes, image cache warm-up cron |
| `app/etc/config.php` | The enabled module list |
| `_build/catalog/` | Product copy and specs (`products.json`) |
| `_build/cms/` | CMS pages and blocks (home, about, FAQ, shipping, 404) |
| `_build/renders/jpg/` | Product and editorial photography, named `<SKU>_<n>.jpg` |
| `_build/gemini/`, `_build/render/`, `_build/brand/`, `_build/hero/` | How the images and the logo were made (AI image shot list, earlier Blender scenes, logo SVG generator, hero composition) |
| `_build/scripts/` | `deploy_theme.sh` (theme static deploy without downtime), `m2-deploy` (bring the live store up to GitHub main) |
| `_build/perf/` | Generates the critical CSS from the live store (Playwright) |
| `_build/server/` | Reference copies of the nginx vhost and php-fpm pool |
| `.githooks/` | Commit guards (secrets, lint, leftovers) and auto-push |

## Stack

PHP 8.3, MariaDB 10.11, OpenSearch 2.19, Redis (cache, full page cache, sessions), nginx behind Cloudflare,
production mode with indexers on schedule. Catalogue: 45 products (62 SKUs) in 6 categories.

## How it is worked on

The store is designed, coded and maintained entirely by AI (Claude Code), with Michael Kuhlman directing. The
working rules for those sessions (git workflow, deploy steps, quality gates, coding standards) are in
[`CLAUDE.md`](CLAUDE.md). In short: one branch `main`, every change is a small commit that the hooks check and push
straight to GitHub, and `_build/scripts/m2-deploy` brings the live server up to date.
