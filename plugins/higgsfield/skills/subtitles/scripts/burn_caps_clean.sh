#!/usr/bin/env bash
# burn_caps_clean.sh — burn CLEAN CAPS subtitles onto a finished video from an .srt,
# using ffmpeg + libass. Explainer-style but PLATELESS: bold WHITE text, black
# OUTLINE + soft drop shadow, bottom-centre. No paper, NO background box.
# Text is forced to UPPERCASE (Unicode-aware: works for Cyrillic etc. via python3).
# Exact timing (from a Whisper-built srt), zero jitter.
#
# Sizing: ffmpeg converts SRT with a 384x288 subtitle grid (PlayResY=288), so values
# are fractions of 288: fontsize 13 ≈ 4.5% of frame height (small), marginv 34 ≈
# bottom 12%. Do NOT pass marginv ≥ 90 — that parks captions mid-frame.
#
# Usage:
#   scripts/burn_caps_clean.sh --in video.mp4 --srt caps.srt --out final_subbed.mp4
#     [--font "Poppins"] [--fontsdir DIR] [--fontsize 13] [--marginv 34]
#     [--outline 2] [--shadow 1]
#
# Font: put a bold face at scripts/fonts/ (e.g. Poppins-Bold.ttf — SIL OFL, Google
# Fonts). Binaries are not committed; without a .ttf libass falls back to a system
# font (the script warns — the look will differ).
# Requires: ffmpeg (with libass); python3 recommended for non-ASCII uppercasing.
set -euo pipefail

IN=""; SRT=""; OUT="final_subbed.mp4"; FONT="Poppins"; FONTSDIR=""; FSIZE=13; MV=34; OUTLINE=2; SHADOW=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --in) IN="$2"; shift 2 ;;
    --srt) SRT="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --font) FONT="$2"; shift 2 ;;
    --fontsdir) FONTSDIR="$2"; shift 2 ;;
    --fontsize) FSIZE="$2"; shift 2 ;;
    --marginv) MV="$2"; shift 2 ;;
    --outline) OUTLINE="$2"; shift 2 ;;
    --shadow) SHADOW="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
[[ -n "$IN"  && -f "$IN"  ]] || { echo "ERROR: --in video not found" >&2; exit 1; }
[[ -n "$SRT" && -f "$SRT" ]] || { echo "ERROR: --srt file not found" >&2; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg not found" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$FONTSDIR" && -d "$SCRIPT_DIR/fonts" ]] && FONTSDIR="$SCRIPT_DIR/fonts"
if [[ -n "$FONTSDIR" ]] && ! ls "$FONTSDIR"/*.[to]tf >/dev/null 2>&1; then
  echo "WARN: no .ttf/.otf in $FONTSDIR — libass will fall back to a system font (look may differ). Drop Poppins-Bold.ttf there." >&2
fi

# Force UPPERCASE in the srt copy. python3 = Unicode-correct (Cyrillic etc.);
# awk toupper is ASCII-only on mawk/BSD awk, so it is only the last-resort fallback.
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import sys; sys.stdout.write(open(sys.argv[1], encoding="utf-8", errors="replace").read().upper())' "$SRT" > "$TMP/caps_upper.srt"
else
  echo "WARN: python3 not found — using awk toupper (ASCII-only: non-Latin text may stay lowercase)." >&2
  awk 'BEGIN{RS="";FS="\n"} {print toupper($0) "\n"}' "$SRT" > "$TMP/caps_upper.srt" 2>/dev/null || cp "$SRT" "$TMP/caps_upper.srt"
fi

# ASS colours are &HAABBGGRR. White fill, black outline, semi-soft shadow.
# BorderStyle=1 => outline+shadow (NO opaque box). No BackColour plate.
STYLE="FontName=${FONT},Fontsize=${FSIZE},PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,BorderStyle=1,Outline=${OUTLINE},Shadow=${SHADOW},Alignment=2,MarginV=${MV},Bold=1"

FONTS_ARG=""; [[ -n "$FONTSDIR" ]] && FONTS_ARG=":fontsdir=${FONTSDIR}"
ffmpeg -y -loglevel error -i "$IN" -vf "subtitles=${TMP}/caps_upper.srt${FONTS_ARG}:force_style='${STYLE}'" \
  -c:v libx264 -preset veryfast -crf 20 -c:a copy "$OUT"
echo "DONE -> $OUT  (clean CAPS, no plate, small bottom captions)"
