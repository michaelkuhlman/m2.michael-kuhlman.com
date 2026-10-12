# Third Shot Supply Co. - Magento 2 demo store (https://m2.michael-kuhlman.com)

Portfolio demo for Michael Kuhlman (Magento 2 / Adobe Commerce developer). A fictional premium pickleball brand
on **Mage-OS 3.5.0** (open-source distribution of Magento Open Source, core = Magento 2.4.9), custom Luma child
theme, catalogue seeded by a custom module, product photography rendered in Blender. Written entirely by Claude.
Deep context: `/home/kai/vault/kai-brain/projects/m2-demo-store.md`. Working state: `memory/active/mk.md` in the vault.

**It is a demo: no real orders, payments or shipping.** Email sending is disabled (`system/smtp/disable=1`),
the only payment method is Check / Money order, and a site-wide notice says so. Keep it that way.

## Git and GitHub
The store is written entirely by AI (Claude Code sessions on this server and on Michael's laptop); no human edits
files or runs git. So git is the only record of what changed and why: every change is a commit, every commit is on
GitHub within seconds.

- **GitHub**: private `michaelkuhlman/m2.michael-kuhlman.com` (https://github.com/michaelkuhlman/m2.michael-kuhlman.com),
  one branch `main`, no PRs, no CI (the hooks below run the checks). It is the off-site copy and the channel to the
  laptop clone.
- **On this server git is `m2git`** (`~/bin/m2git`): `GIT_DIR=/home/kai/backups/m2/site.git`, this directory as the
  work tree, so nothing under `/var/www` can serve repository internals. Plain `git` here says "not a git
  repository": expected, never `git init`. Push/pull use the repo-only deploy key `~/.ssh/id_m2_github` via the ssh
  alias `github.com-m2` (`ssh -T git@github.com-m2` answers "Hi michaelkuhlman/m2.michael-kuhlman.com!").
- **The work tree IS the live store's source.** A change is live only after its Magento step (see Common tasks) and
  done only when it is committed.
- **Every change, in order:**
  1. `m2git pull --ff-only` before you start (if the laptop pushed, run `~/bin/m2-deploy` instead: it merges AND runs
     the Magento steps the new commits need).
  2. Edit, run the Magento step for what you touched, check it in a browser (Quality gates below).
  3. `m2git add <the files you touched>` **by name**, then `m2git commit -m "<what changed and why>"` with the trailer
     your harness gives you. Never `add -A` / `add .` / `commit -a`: other sessions keep live, uncommitted work in
     this same tree, and it is theirs to commit.
  4. The post-commit hook pushes to GitHub by itself and prints `pushed to GitHub`. If it prints `AUTO-PUSH FAILED`
     (the laptop pushed first), run `~/bin/m2-deploy`: it merges GitHub's commits, pushes, and deploys them.
- **Hooks** live in `.githooks/` (tracked; active through `core.hooksPath` here and in every clone):
  - `pre-commit` checks the STAGED files and blocks: token-shaped secrets and the real values from `~/.config/m2/*`
    and the Cloudflare env (DB/admin password, admin path, API token); `env.php` / `auth.json` / keys / `*.sql` dumps;
    leftovers (`.bak .old .orig .rej .save .swp .tmp .pre-*`); anything under `vendor/ generated/ pub/static/
    pub/media/ var/ setup/ lib/ dev/`; files over 5 MB; PHP/PHTML syntax errors (`php -l`); invalid XML (layout,
    di.xml, module.xml, SVG) or JSON; Python, shell and JavaScript syntax errors. Fix, re-stage, commit again.
    Never `--no-verify`. Whole-tree audit: `M2_PRECOMMIT_ALL=1 m2git hook run pre-commit`.
  - `post-commit` / `post-merge` / `post-rewrite` push `main`; `M2_NO_AUTOPUSH=1` skips once.
  - `pre-push` refuses force-pushes and branch deletions. GitHub's free plan has no branch protection for private
    repos, so this hook is the protection.
- **Never** `--force`, never amend or rebase a pushed commit, never `stash` / `reset --hard` / `checkout -- <file>` /
  `restore` / `clean` in this tree. Undo with `m2git revert <sha>` (then its Magento step).
- **`.gitignore` is a whitelist**: tracked are `composer.json/.lock`, `app/code/`, `app/design/`, `app/i18n/`,
  `app/etc/config.php` (the module list), `_build/` (minus render PNGs, previews, texture/brand outputs), `.githooks/`,
  this file and `README.md`. To track something new outside those, add a `!` line there (the comments show how).
  `css/critical.css` in the theme is generated from the live store after every theme deploy and stays untracked.
- **Not in git, back it up another way if it matters**: the database `m2_store` (catalogue, CMS, orders: rebuildable
  with `thirdshot:demo:seed`), `pub/media/` (seeder output + editorial images), `app/etc/env.php` (DB creds,
  crypt key), nginx/php-fpm live config (mirrors in `_build/server/`), the docker containers, cron.
- **Never commit a credential.** DB credentials live only in `app/etc/env.php` (ignored, mode 600, owner m2) and
  `~/.config/m2/db.env`; admin login in `~/.config/m2/admin.txt` (600). Neither belongs in git or the vault.
- **`~/bin/m2-deploy`** (symlink to the tracked `_build/scripts/m2-deploy`) brings the live store up to GitHub main:
  fetch, `php -l` the incoming PHP, fast-forward (or push the server's own commits, or merge when both moved), then
  ONLY the Magento steps the new files need: `setup:upgrade` (module list / schema / patches, in maintenance mode),
  `setup:di:compile` (PHP, di.xml), `deploy_theme.sh` (theme, view/, i18n), `thirdshot:demo:seed --step=cms`
  (`_build/cms`), `cache:flush`, then checks the main pages answer 200. composer changes, product data/photos and
  `_build/server/` are reported, never run. It holds `/tmp/m2-deploy.lock`, refuses the Magento steps while app/ or
  `_build/cms/` has someone's uncommitted edits (`M2_DEPLOY_ANYWAY=1` overrides), and keeps unfinished steps pending
  in `$GIT_DIR/m2-deploy.pending` so a rerun finishes them. `m2-deploy --dry-run` shows the plan and changes nothing.
- **Laptop clone** (Windows): `C:\xampp\htdocs\m2.michael-kuhlman.com`, origin `git@github.com:michaelkuhlman/m2.michael-kuhlman.com.git`,
  `core.hooksPath .githooks`. It has no vendor/ or database, so Magento does not run there: it is for reading, editing
  and committing source. Workflow: `git pull --rebase origin main`, edit, commit by name (the hooks check and push;
  the laptop's PHP 8.2 lint findings are warnings only), then `ssh atlas bin/m2-deploy` to bring it live. If the
  laptop's Bash tool has no network, run git and ssh from PowerShell.

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
  images are attached only to products without a gallery; `--fresh` resets the galleries of all `TS-*` products first.
  **Never delete and re-create products with the same SKUs**: MSI queues a source-item cleanup by SKU on delete, and the
  cron consumer then wipes the stock of the re-created products ("There are no source items with the in stock status").
  The seeder writes MSI source items explicitly. The CMS step never overwrites an existing `pub/media/wysiwyg/thirdshot/*.jpg`.
- `_build/` - everything that produced the content: `brand/brand.py` (logo SVGs from font outlines),
  `textures/` (PIL paddle face art, labels), `render/` (Blender scripts: `studio.py`, `models_*.py`, `shots.py`,
  `scenes.py`), `scripts/` (`render_all.sh`, `render_scenes.sh`, `export_jpg.py`, `deploy_theme.sh`).

### Common tasks
- **CSS/LESS or template change**: edit under the theme, then `_build/scripts/deploy_theme.sh` (static deploy for the
  theme + cache flush; the static version stamp changes, so Cloudflare and browsers fetch the new files).
- **PHP change in app/code**: `sudo -u m2 php bin/magento setup:di:compile` then `cache:flush`.
- **Product photos: Blender rendering is PAUSED at Michael's request (2026-10-11); do not start render jobs unless he
  asks.** 61 renders exist (paddles, balls, bags, covers); 22 products show the branded placeholder
  (`Magento_Catalog/web/images/product/placeholder/*.jpg` in the theme). When new images exist: put
  `<SKU>_<n>.jpg` in `_build/renders/jpg/`, then `thirdshot:demo:seed --step=products,composite` (products without a
  gallery pick them up; `--fresh` to replace existing galleries). Pipeline if resumed: `_build/scripts/render_all.sh SKU`
  then `export_jpg.py` (Blender 4.4 Cycles CPU, no AVX here: ~75 s per 800x1000 frame, always niced).
- **Editorial images**: home hero = `pub/media/wysiwyg/thirdshot/hero.jpg`, built from `_build/hero/` (cut-outs of the
  renders on an HTML/CSS court, screenshotted) - do not regenerate it from anything else. Category banners, story,
  spotlight and about images: `python3 _build/scripts/compose_editorial.py` (PIL composites of the renders), then copy
  the changed files into `pub/media/...` and **purge them on Cloudflare** (zone michael-kuhlman.com
  `854fec09adbc07d0567da5511541656f`, token in `~/.config/cloudflare/kuhlmanpickleball.env`): CF caches media.
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
