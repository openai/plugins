#!/usr/bin/env bash
# prepare.sh — one-command pre-processing for a captions project.
#
#   bash prepare.sh <project-dir>
#
# Runs the three deterministic pre-steps with maximum parallelism:
#   matte.cjs (CPU-heavy ONNX)  ∥  transcribe.cjs (whisper)   → then safe-zones.cjs
# (matte and transcribe are independent; safe-zones needs the matte's frames_fg.)
# Replaces hand-running steps 2 / 3 / 3b — one call, nothing forgotten, ~the cost
# of the slower of the two instead of their sum.
#
# After this completes the project has: frames_bg/ frames_fg/ matte.fps
# transcript.json safe-zones.json — everything the authoring step needs.
set -euo pipefail

PROJECT="${1:?usage: prepare.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"
SD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[prepare] matte ∥ transcribe ∥ envelope …"
MLOG="$PROJECT/_prepare_matte.log"; TLOG="$PROJECT/_prepare_transcribe.log"; ELOG="$PROJECT/_prepare_envelope.log"
node "$SD/matte.cjs" "$PROJECT"      > "$MLOG" 2>&1 &  MPID=$!
node "$SD/transcribe.cjs" "$PROJECT" > "$TLOG" 2>&1 &  TPID=$!
node "$SD/audio-envelope.cjs" "$PROJECT" > "$ELOG" 2>&1 &  EPID=$!

MRC=0; TRC=0
wait "$MPID" || MRC=$?
wait "$TPID" || TRC=$?
wait "$EPID" || echo "[prepare] (envelope skipped — hero amplitude falls back to neutral)" >&2
# surface both logs (they contain the guards' warnings — near-silent audio, tail trim)
sed 's/^/  [matte] /'      "$MLOG" | tail -6
sed 's/^/  [transcribe] /' "$TLOG" | tail -12
if (( MRC != 0 )); then echo "[prepare] matte FAILED (rc=$MRC) — see $MLOG" >&2; exit "$MRC"; fi
if (( TRC != 0 )); then echo "[prepare] transcribe FAILED (rc=$TRC) — see $TLOG" >&2; exit "$TRC"; fi

echo "[prepare] safe-zones …"
node "$SD/safe-zones.cjs" "$PROJECT"

echo "[prepare] ✅ ready: frames_fg/ transcript.json safe-zones.json — author next (see SKILL.md step 4)"
