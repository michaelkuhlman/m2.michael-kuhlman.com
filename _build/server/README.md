# Server config mirror (m2.michael-kuhlman.com)

Copies of the live config outside this tree. Change the live file and this copy together.

| File here | Live path |
|---|---|
| nginx-m2.michael-kuhlman.com.conf | /etc/nginx/sites-available/m2.michael-kuhlman.com (symlinked in sites-enabled) |
| nginx-snippet-m2_magento.conf | /etc/nginx/snippets/m2_magento.conf (Magento nginx.conf.sample, upstream m2_fastcgi, header include per location) |
| nginx-snippet-m2_headers.conf | /etc/nginx/snippets/m2_headers.conf |
| php-fpm-pool-m2.conf | /etc/php/8.3/fpm/pool.d/m2.conf |

Containers (both `--restart unless-stopped`, docker is enabled at boot):

    docker run -d --name m2-redis --restart unless-stopped -p 127.0.0.1:6390:6379 redis:alpine \
      redis-server --maxmemory 384mb --maxmemory-policy allkeys-lru --save "" --appendonly no
    docker run -d --name m2-opensearch --restart unless-stopped -p 127.0.0.1:9201:9200 \
      -e discovery.type=single-node -e DISABLE_SECURITY_PLUGIN=true -e DISABLE_INSTALL_DEMO_CONFIG=true \
      -e "OPENSEARCH_JAVA_OPTS=-Xms768m -Xmx768m" --memory 1600m \
      -v m2-opensearch-data:/usr/share/opensearch/data opensearchproject/opensearch:2.19.2

Host prerequisites: `vm.max_map_count=262144` in /etc/sysctl.d/90-opensearch.conf; php8.3-soap; composer.
Reload only: `sudo nginx -t && sudo systemctl reload nginx`, `sudo systemctl reload php8.3-fpm`.

## Performance pieces (2026-10-12)
- `nginx-snippet-m2_magento.conf` has three Third Shot additions, all marked in comments:
  - `/media/...(jpg|png)[.wNNN].webp` served from disk, misses go to `@m2_webp` ->
    `app/code/ThirdShot/Performance/endpoint/webp.php` (converts from the source file, no Magento bootstrap);
  - `/static/frontend/ThirdShot/court/en_US/...` falls back to `en_US.prev` (`@m2_static_prev`, `no-store`) while
    `_build/scripts/deploy_theme.sh` rebuilds the theme: deploys have no downtime.
- Critical CSS: `_build/perf/critical-css.sh` (Playwright from /opt/playwright, clean-css from
  `/home/kai/m2perf-tools/node_modules`: `cd /home/kai/m2perf-tools && npm i clean-css`). Run automatically in the
  background by every theme deploy; log `var/log/thirdshot-critical-css.log`.
- Locked in `app/etc/config.php`: `dev/js/move_script_to_bottom=1`, `dev/css/use_css_critical_path=1`.
