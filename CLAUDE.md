# Third Shot Supply Co. - Magento 2 demo store (https://m2.michael-kuhlman.com)

Portfolio demo for Michael Kuhlman (Magento 2 / Adobe Commerce developer). A fictional premium pickleball brand
on **Mage-OS 3.5.0** (open-source distribution of Magento Open Source, core = Magento 2.4.9), custom Luma child
theme, catalogue seeded by a custom module, product photography rendered in Blender. Written entirely by Claude.
Deep context: `/home/kai/vault/kai-brain/projects/m2-demo-store.md`. Working state: `memory/active/mk.md` in the vault.

**It is a demo: no real orders, payments or shipping.** Email sending is disabled (`system/smtp/disable=1`),
the only payment method is Check / Money order, and a site-wide notice says so. Keep it that way.

## Git
- Repo: `~/bin/m2git` (`GIT_DIR=/home/kai/backups/m2/site.git`, this directory as work tree). Plain `git` here
  says "not a git repository": expected, never `git init`. **Local only: no GitHub remote yet** (needs Michael to
  create `michaelkuhlman/m2-demo-store` (or similar) and a deploy key, as for the other sites).
- `.gitignore` is a whitelist: only `composer.json/.lock`, `app/code/`, `app/design/`, `app/etc/config.php`,
  `_build/` (minus renders PNG/previews/texture outputs) and this file are tracked. Everything composer installs
  is rebuilt with `composer install`.
- Commit the files you touched **by name** (no `add -A`), subject = what changed and why, with the trailer your
  harness gives you. Never `--force`, never rewrite history, never `stash` / `reset --hard` / `clean` here.
- **Never commit a credential.** DB credentials live only in `app/etc/env.php` (ignored, mode 600, owner m2) and
  `~/.config/m2/db.env`; admin login in `~/.config/m2/admin.txt` (600). Neither belongs in git or the vault.

## Runtime layout
| Piece | Where |
|---|---|
| Docroot / Magento root | `/var/www/m2.michael-kuhlman.com` (owner `m2`, ACLs give `kai` rw) |
| PHP | pool `[m2]` `/etc/php/8.3/fpm/pool.d/m2.conf`, runs as user `m2`, socket `/run/php/php8.3-fpm-m2.sock`, 1G memory_limit |
| nginx | `/etc/nginx/sites-available/m2.michael-kuhlman.com` + `/etc/nginx/snippets/m2_magento.conf` (copy of Magento's nginx.conf.sample, upstream renamed `m2_fastcgi`) |
| TLS | Let's Encrypt webroot `/var/www/letsencrypt`, cert `m2.michael-kuhlman.com`, deploy hook reloads nginx |
| DNS / edge | Cloudflare zone michael-kuhlman.com, `A m2 -> 64.7.64.210` proxied, SSL strict |
| Database | MariaDB 10.11, db + user `m2_store` |
| Search | docker `m2-opensearch` (opensearch 2.19.2, heap 768m, `127.0.0.1:9201`, restart unless-stopped, volume `m2-opensearch-data`) |
| Cache / FPC / sessions | docker `m2-redis` (`127.0.0.1:6390`, maxmemory 384mb): db 0 cache, db 1 page cache, db 2 sessions |
| Cron | `crontab -u m2 -l` (`bin/magento cron:run` every minute); indexers are "Update by Schedule" |
| Mode | production. Admin path and user: see `~/.config/m2/admin.txt`. 2FA module disabled for the demo. |

Always run Magento CLI as the owner: `sudo -u m2 php bin/magento ...` (with `umask 002`).
Reload, never restart, shared services: `sudo nginx -t && sudo systemctl reload nginx`, `sudo systemctl reload php8.3-fpm`.

## Code
- `app/design/frontend/ThirdShot/court/` - theme (parent Magento/luma). LESS in `web/css/source/`:
  `_theme.less` (Luma's file + brand variables at the end), `_typography.less` (self-hosted Fraunces + Inter,
  SIL OFL), `_extend.less` imports `ts/_base|_header|_home|_catalog|_product|_checkout|_footer|_cms.less`.
  `etc/view.xml` sets 4:5 product images. Layout overrides under `Magento_*/layout/`.
- `app/code/ThirdShot/DemoData/` - `bin/magento thirdshot:demo:seed [--step=attributes,categories,products,composite,reviews,cms] [--fresh]`.
  Reads `_build/catalog/products.json`, `_build/renders/jpg/*.jpg`, `_build/cms/{pages,blocks}/*.html`. Idempotent;
  images are attached only to products without a gallery (`--fresh` deletes all `TS-*` products first).
- `_build/` - everything that produced the content: `brand/brand.py` (logo SVGs from font outlines),
  `textures/` (PIL paddle face art, labels), `render/` (Blender scripts: `studio.py`, `models_*.py`, `shots.py`,
  `scenes.py`), `scripts/` (`render_all.sh`, `render_scenes.sh`, `export_jpg.py`, `deploy_theme.sh`).

### Common tasks
- **CSS/LESS or template change**: edit under the theme, then `_build/scripts/deploy_theme.sh` (static deploy for the
  theme + cache flush; the static version stamp changes, so Cloudflare and browsers fetch the new files).
- **PHP change in app/code**: `sudo -u m2 php bin/magento setup:di:compile` then `cache:flush`.
- **New/changed product photo**: edit `_build/render/*`, `_build/scripts/render_all.sh --force SKU`, then
  `python3 _build/scripts/export_jpg.py`, then re-seed (`--fresh` or remove that product's gallery first).
  Blender: `~/.local/bin/blender` 4.4, Cycles CPU (no AVX on this VM: ~75 s per 800x1000 frame), always niced.
- **CMS content**: edit `_build/cms/...html`, then `thirdshot:demo:seed --step=cms` and `cache:flush`.

## Quality gates
- `php -l` every changed PHP/PHTML file; `setup:di:compile` must pass; LESS must compile (deploy_theme.sh fails loudly).
- less.php evaluates `/` and some CSS functions: escape `font: 600 14px/1.3`, `aspect-ratio: 4 / 5`,
  `grid-column: 1 / -1`, `min()`/`max()`/`clamp()` as `~"..."`.
- Check desktop 1440 and mobile 390 in a real browser (Playwright: `NODE_PATH=/opt/playwright/node_modules
  PLAYWRIGHT_BROWSERS_PATH=/opt/playwright/browsers`), no horizontal overflow at 390, no 404s in the network log.
- Checkout must still work end to end (guest, flat rate or free shipping, Check / Money order).

## Coding standards
- Small, focused files (about 400 lines max); one responsibility per class; constructor DI with service contracts
  (repositories, interfaces), no ObjectManager in code; `declare(strict_types=1)`.
- Customise through the theme fallback, layout XML and CMS before touching templates; never edit `vendor/`.
- Escape all output in templates (`$escaper`); keep blocks FPC-safe (no per-customer data in cacheable blocks).
- Commit messages say what changed and why. Do not leave `*.bak`, `*.old`, `*.orig` copies anywhere in the docroot.
