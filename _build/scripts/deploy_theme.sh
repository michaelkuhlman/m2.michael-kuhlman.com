#!/usr/bin/env bash
# Recompile the storefront theme's static assets (LESS -> CSS) and flush caches. Runs as the m2 user.
#   _build/scripts/deploy_theme.sh            (theme only, quick)
#   _build/scripts/deploy_theme.sh --all      (all themes/areas, as for production mode)
set -euo pipefail
cd "$(dirname "$0")/../.."
if [ "${1:-}" = "--all" ]; then
  sudo -u m2 bash -c 'umask 002; rm -rf var/view_preprocessed/* pub/static/frontend pub/static/adminhtml; php bin/magento setup:static-content:deploy -f en_US -j 2'
else
  sudo -u m2 bash -c 'umask 002; rm -rf var/view_preprocessed/* pub/static/frontend/ThirdShot; php bin/magento setup:static-content:deploy -f en_US --area=frontend --theme=ThirdShot/court -j 2 | tail -3'
fi
sudo -u m2 php bin/magento cache:flush >/dev/null
echo "theme deployed"
