#!/usr/bin/env bash
# Close lingering legacy Playwright CLI browser sessions and upload pending Replay recordings.

set -euo pipefail

have_npx=0
have_replayio=0
command -v npx >/dev/null 2>&1 && have_npx=1
command -v replayio >/dev/null 2>&1 && have_replayio=1

if [ "$have_npx" -eq 1 ]; then
  listing="$(npx --yes --package @playwright/cli playwright-cli list 2>/dev/null || true)"
  if [ -n "$listing" ]; then
    sessions="$(printf '%s\n' "$listing" \
      | awk '/Browser servers available for attach/{next} /^\s+[A-Za-z0-9_-]+/{print $1}' \
      | tr -d ' ' \
      | sort -u || true)"
    for s in $sessions; do
      [ -z "$s" ] && continue
      echo "[replayio hook] Closing lingering browser session: $s" >&2
      npx --yes --package @playwright/cli playwright-cli --session="$s" close >/dev/null 2>&1 || true
    done
  fi
fi

if [ "$have_replayio" -eq 1 ]; then
  echo "[replayio hook] Uploading pending Replay recordings..." >&2
  replayio upload-all >/dev/null 2>&1 || replayio upload >/dev/null 2>&1 || true
else
  echo "[replayio hook] replayio CLI not found on PATH, skipping upload." >&2
fi

exit 0
