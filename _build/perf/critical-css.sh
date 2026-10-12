#!/usr/bin/env bash
# Regenerate the inlined critical CSS from the live store (see critical-css.js), then refresh the page cache.
#   _build/perf/critical-css.sh          run now (waits for nothing; skips if a run is already going, re-runs after it)
#   _build/perf/critical-css.sh --bg     same, detached (deploy_theme.sh uses this)
# Log: var/log/thirdshot-critical-css.log. Safe to run any time: on failure the previous critical.css stays.
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG=var/log/thirdshot-critical-css.log
if [ "${1:-}" = "--bg" ]; then
  nohup "$0" >>"$LOG" 2>&1 </dev/null &
  echo "critical CSS regeneration started in the background (log: $LOG)"
  exit 0
fi
exec 9>/tmp/m2-critical-css.lock
if ! flock -n 9; then
  touch /tmp/m2-critical-css.pending   # the running job picks this up when it finishes
  echo "$(date '+%F %T') busy, queued a re-run"
  exit 0
fi
while :; do
  rm -f /tmp/m2-critical-css.pending
  echo "$(date '+%F %T') generating critical CSS"
  if NODE_PATH=/opt/playwright/node_modules:/home/kai/m2perf-tools/node_modules \
     PLAYWRIGHT_BROWSERS_PATH=/opt/playwright/browsers nice -n 10 node _build/perf/critical-css.js; then
    sudo -u m2 php bin/magento cache:clean full_page >/dev/null && echo "$(date '+%F %T') done, page cache cleaned"
    # re-warm the full page cache: home, every page linked from it (nav, categories, products, CMS)
    curl -s https://m2.michael-kuhlman.com/ | grep -o 'href="https://m2.michael-kuhlman.com/[^"#?]*"' | cut -d'"' -f2 \
      | grep -vE '/(customer|checkout|wishlist|sales|catalog/product_compare|media|static)/' | sort -u | head -80 \
      | xargs -r -n1 -P3 curl -s -o /dev/null && echo "$(date '+%F %T') page cache warmed"
  else
    echo "$(date '+%F %T') FAILED, previous critical.css kept"
  fi
  [ -e /tmp/m2-critical-css.pending ] || break
done
