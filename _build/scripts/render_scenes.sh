#!/usr/bin/env bash
# Render editorial scenes (hero, category banners, story...). Niced. Log: _build/renders/scenes.log
set -u
B=${BLENDER:-/home/kai/.local/bin/blender}
R="$(cd "$(dirname "$0")/../render" && pwd)"
LOG="$R/../renders/scenes.log"
FLAGS=(); NAMES=()
for a in "$@"; do case "$a" in --*) FLAGS+=("$a");; *) NAMES+=("$a");; esac; done
[ ${#NAMES[@]} -eq 0 ] && NAMES=(hero cat_paddles cat_balls cat_bags cat_apparel cat_training cat_accessories story spotlight workshop)
for n in "${NAMES[@]}"; do
  echo "== $n $(date +%T)" >> "$LOG"
  nice -n 19 "$B" -b --factory-startup -P "$R/scenes.py" -- "${FLAGS[@]}" "$n" 2>&1 \
    | grep -E 'RENDERED|skip|Error|Traceback|line [0-9]+' >> "$LOG"
done
echo "== done $(date +%T)" >> "$LOG"
