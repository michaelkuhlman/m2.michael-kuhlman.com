#!/usr/bin/env bash
# Render every product shot, one Blender process per SKU (a crash only loses that SKU).
#   _build/scripts/render_all.sh [--preview] [--force] [SKU ...]
# Runs niced so the live sites on this box keep priority. Log: _build/renders/render.log
set -u
B=${BLENDER:-/home/kai/.local/bin/blender}
R="$(cd "$(dirname "$0")/../render" && pwd)"
LOG="$R/../renders/render.log"; mkdir -p "$R/../renders"
FLAGS=(); SKUS=()
for a in "$@"; do case "$a" in --*) FLAGS+=("$a");; *) SKUS+=("$a");; esac; done
if [ ${#SKUS[@]} -eq 0 ]; then
  read -r -a SKUS <<< "$("$B" -b --factory-startup -P "$R/render.py" -- --list 2>/dev/null | sed -n 's/^SKULIST //p')"
fi
for s in "${SKUS[@]}"; do
  echo "== $s $(date +%T)" >> "$LOG"
  nice -n 19 "$B" -b --factory-startup -P "$R/render.py" -- "${FLAGS[@]}" "$s" 2>&1 \
    | grep -E 'RENDERED|skip|Error|Traceback|line [0-9]+' >> "$LOG"
done
echo "== done $(date +%T)" >> "$LOG"
