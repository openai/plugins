#!/usr/bin/env bash
# speech_metrics.sh — measure what actually matters about a TTS take, so a
# narration line can be gated WITHOUT guessing from the file length.
#
# A TTS file's duration lies: providers pad the head/tail with silence, so a
# 10.1s file can hold 9.2s of speech (and vice versa). Downstream assemblers
# centre the SPEECH inside its window, so the speech length — not the file
# length — is the number to check.
#
# Prints one line of KEY=VALUE pairs (and JSON with --json):
#   duration      file length (s)
#   speech_start  where speech begins (leading silence trimmed)
#   speech_end    where speech ends (trailing silence trimmed)
#   speech        speech_end - speech_start  <-- gate on this
#   pauses        number of internal silences >= --pause (default 0.8s)
#   longest_pause longest internal silence (s)
#
# Usage:
#   scripts/speech_metrics.sh voice01.wav [--pause 0.8] [--noise -45] [--json]
#
# Requires: ffmpeg, ffprobe, awk.
set -euo pipefail

FILE=""; PAUSE="0.8"; NOISE="-45"; JSON=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pause) PAUSE="$2"; shift 2 ;;
    --noise) NOISE="$2"; shift 2 ;;
    --json)  JSON=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) FILE="$1"; shift ;;
  esac
done
[[ -n "$FILE" && -f "$FILE" ]] || { echo "ERROR: pass an audio file" >&2; exit 1; }
for b in ffmpeg ffprobe awk; do command -v "$b" >/dev/null 2>&1 || { echo "ERROR: '$b' not found" >&2; exit 1; }; done

DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FILE")"
EVENTS="$(ffmpeg -i "$FILE" -af "silencedetect=noise=${NOISE}dB:d=0.25" -f null - 2>&1 \
          | grep -Eo 'silence_(start|end): *-?[0-9.]+' || true)"

# Speech bounds: ignore a leading silence that starts at ~0, and close the tail
# silence that EOF left open.
read -r SS SE <<< "$(awk -v A="$DUR" '
  /silence_start/ { s=$NF+0; if(first==""){first=s}; last=s; open=1; next }
  /silence_end/   { e=$NF+0; if(first!="" && first<0.1 && ssdone==""){ss=e; ssdone=1};
                    e_last=e; s_before=last; open=0 }
  END {
    if (open==1)                       se=last;
    else if (e_last>0 && A-e_last<0.2) se=s_before;
    else                               se=A;
    printf "%.3f %.3f", ss+0, se+0 }' <<< "$EVENTS")"
[[ -z "${SS:-}" ]] && SS=0; [[ -z "${SE:-}" || "$SE" == "0.000" ]] && SE="$DUR"
SPEECH="$(awk -v a="$SS" -v b="$SE" 'BEGIN{d=b-a; if(d<0)d=0; printf "%.3f", d}')"
# Degenerate detection (all-silence or no events) -> fall back to the whole file.
awk -v s="$SPEECH" 'BEGIN{exit (s<0.3)?0:1}' && { SS=0; SE="$DUR"; SPEECH="$DUR"; }

# Internal pauses strictly INSIDE the speech.
read -r PN PMAX <<< "$(awk -v lo="$SS" -v hi="$SE" -v thr="$PAUSE" '
  /silence_start/ { s=$NF+0; open=1; next }
  /silence_end/   { e=$NF+0; if(open==1 && s>lo+0.1 && e<hi-0.1 && e-s>=thr){n++; if(e-s>mx)mx=e-s}; open=0 }
  END{ printf "%d %.2f", n+0, mx+0 }' <<< "$EVENTS")"

if [[ "$JSON" == "1" ]]; then
  printf '{"file":"%s","duration":%.3f,"speech_start":%.3f,"speech_end":%.3f,"speech":%.3f,"pauses":%d,"longest_pause":%.2f}\n' \
    "$(basename "$FILE")" "$DUR" "$SS" "$SE" "$SPEECH" "${PN:-0}" "${PMAX:-0}"
else
  printf 'duration=%.3f speech_start=%.3f speech_end=%.3f speech=%.3f pauses=%d longest_pause=%.2f\n' \
    "$DUR" "$SS" "$SE" "$SPEECH" "${PN:-0}" "${PMAX:-0}"
fi
