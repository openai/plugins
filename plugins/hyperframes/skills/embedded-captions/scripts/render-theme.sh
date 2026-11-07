#!/usr/bin/env bash
# render-theme.sh — compile + render + plate-reaction for THEME mode projects.
#   bash render-theme.sh <project-dir>
# Project needs: theme.json, transcript.json, source.mp4, frames_fg/, matte.fps
# Output: final_fx.mp4 (final.mp4 = before plate reaction)
set -euo pipefail
PROJECT="${1:?usage: render-theme.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"
SD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

node "$SD/make-theme.cjs" "$PROJECT"
# Gate honesty (cold-start E2E finding): theme mode enforces word timing at
# COMPILE time (sequential transcript matcher + verbatim completeness gate in
# make-theme.cjs — a mistimed/missing word is a compile error, not a render
# warning). The pixel occlusion gate is Cinematic-only; themes place heroes
# scene-aware (safe-zones) and are covered by overflow + rail-climax + the
# PAGEERROR gate below.
echo "[render-theme] gates: timing PASS (compile-enforced verbatim matcher)"
echo "[render-theme] gates: occlusion = scene-aware placement (pixel gate is Cinematic-only)"
RLOG="$PROJECT/_render-theme.log"
bash "$SD/render-and-composite.sh" "$PROJECT" 2>&1 | tee "$RLOG"
# GATE: a JS error in either generated layer silently yields a blank caption
# layer while every downstream gate still passes — fail loudly instead.
if grep -q "PAGEERROR" "$RLOG"; then
  echo "[render-theme] FAIL — Browser PAGEERROR in a generated layer (see $RLOG)." >&2
  echo "               The caption timeline did not build; the output is missing captions." >&2
  exit 2
fi
if [[ -f "$PROJECT/_postfx.sh" ]]; then
  bash "$PROJECT/_postfx.sh"
else
  cp "$PROJECT/final.mp4" "$PROJECT/final_fx.mp4"
fi
echo "[render-theme] done → $PROJECT/final_fx.mp4   (DELIVERABLE: final_fx.mp4; final.mp4 is the pre-plate-reaction cut)"
