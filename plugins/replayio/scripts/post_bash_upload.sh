#!/usr/bin/env bash
# Upload pending Replay recordings after a shell/Bash command closes a legacy Playwright CLI session.
# Reads hook event JSON from stdin when the host provides it.

set -euo pipefail

input="$(cat || true)"

cmd=""
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | jq -r '
    .tool_input.command //
    .tool_input.args.command //
    .command //
    .shell_command //
    .args.command //
    empty
  ' 2>/dev/null || true)"
else
  cmd="$(printf '%s' "$input" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
fi

case "$cmd" in
  *playwright*close*|*pwcli*close*|*PWCLI*close*)
    ;;
  *)
    exit 0
    ;;
esac

if ! command -v replayio >/dev/null 2>&1; then
  echo "[replayio hook] replayio CLI not found on PATH, skipping upload." >&2
  exit 0
fi

echo "[replayio hook] Browser close detected; uploading pending recordings..." >&2
replayio upload-all >/dev/null 2>&1 || replayio upload >/dev/null 2>&1 || true
exit 0
