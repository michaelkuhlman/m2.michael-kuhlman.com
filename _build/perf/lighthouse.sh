#!/usr/bin/env bash
# Lighthouse benchmark of home / category / PDP, the way the 2026-10-12 perf pass measured it.
#   _build/perf/lighthouse.sh <label> [mobile_rounds=5] [desktop_rounds=3]   -> /tmp/m2-lighthouse/<label>/, median table
# Lighthouse CLI: ~/.npm-global/bin/lighthouse (13.x), Chrome from /opt/playwright. Simulated throttling (Moto G Power).
# The box is shared: runs are noisy and some mobile runs show a ~2 s first-frame stall that only happens under the
# Lighthouse harness here (also in the pre-optimisation baseline); judge by medians of >= 5 runs, interleaved.
label=${1:?label}; mr=${2:-5}; dr=${3:-3}
export CHROME_PATH=${CHROME_PATH:-/opt/playwright/browsers/chromium-1243/chrome-linux64/chrome}
out=/tmp/m2-lighthouse/$label; rm -rf "$out"; mkdir -p "$out"
declare -A P=([home]=/ [cat]=/paddles.html [pdp]=/kitchen-line-carbon-16.html)
for page in home cat pdp; do curl -s -o /dev/null "https://m2.michael-kuhlman.com${P[$page]}"; done   # warm FPC
for n in $(seq 1 "$mr"); do for page in home cat pdp; do
  lighthouse "https://m2.michael-kuhlman.com${P[$page]}" --only-categories=performance,accessibility,best-practices \
    --chrome-flags="--headless=new --no-sandbox" --output=json --output-path="$out/$page-mobile-$n.json" --quiet >/dev/null 2>&1
  if [ "$n" -le "$dr" ]; then
    lighthouse "https://m2.michael-kuhlman.com${P[$page]}" --preset=desktop --only-categories=performance,accessibility,best-practices \
      --chrome-flags="--headless=new --no-sandbox" --output=json --output-path="$out/$page-desktop-$n.json" --quiet >/dev/null 2>&1
  fi
done; done
python3 "$(dirname "$0")/lh-summary.py" "$out"
