#!/usr/bin/env bash
# Recompile the storefront theme's static assets (LESS -> CSS), flush caches, then regenerate the inlined
# critical CSS in the background. Runs Magento as the m2 user. Always call it under the shared lock:
#   flock /tmp/m2-deploy.lock _build/scripts/deploy_theme.sh            (theme only, quick)
#   flock /tmp/m2-deploy.lock _build/scripts/deploy_theme.sh --all      (all themes/areas)
#   ... --no-critical                                                   (skip the critical CSS refresh)
#
# No downtime:
#  - only the LESS preprocessing cache (var/view_preprocessed/pub/static/<area>) is cleared. The minified templates
#    under var/view_preprocessed/pub/static/{vendor,app} are rewritten in place by the deploy; deleting them first
#    made every page 500 until the deploy finished (production mode includes root.phtml from there).
#  - Magento only publishes static files that do not exist yet, so the theme build must start empty: the live
#    build is moved to en_US.prev and nginx (snippets/m2_magento.conf) serves any file not rebuilt yet from there,
#    uncacheable, until the new build is complete. en_US.prev is removed at the end.
set -euo pipefail
cd "$(dirname "$0")/../.."
ALL=0; CRITICAL=1
for a in "$@"; do
  case "$a" in
    --all) ALL=1 ;;
    --no-critical) CRITICAL=0 ;;
  esac
done
LIVE=pub/static/frontend/ThirdShot/court/en_US
sudo -u m2 bash -c "rm -rf $LIVE.prev; if [ -d $LIVE ]; then mv $LIVE $LIVE.prev; fi"
DEPLOYED=0
# success: drop the previous build; failure: put it back so the site keeps working
trap 'if [ $DEPLOYED = 1 ]; then sudo -u m2 rm -rf "$LIVE.prev"; elif [ -d "$LIVE.prev" ]; then sudo -u m2 bash -c "rm -rf $LIVE; mv $LIVE.prev $LIVE"; echo "deploy FAILED, previous build restored" >&2; fi' EXIT
if [ $ALL = 1 ]; then
  sudo -u m2 bash -c 'umask 002; rm -rf var/view_preprocessed/pub/static/frontend var/view_preprocessed/pub/static/adminhtml pub/static/adminhtml pub/static/frontend/Magento; php bin/magento setup:static-content:deploy -f en_US -j 2'
else
  sudo -u m2 bash -c 'umask 002; rm -rf var/view_preprocessed/pub/static/frontend/ThirdShot; php bin/magento setup:static-content:deploy -f en_US --area=frontend --theme=ThirdShot/court -j 2 | tail -3'
fi
DEPLOYED=1
sudo -u m2 php bin/magento cache:flush >/dev/null
echo "theme deployed"
if [ $CRITICAL = 1 ]; then
  _build/perf/critical-css.sh --bg
fi
