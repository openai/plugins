#!/usr/bin/env bash
# Build the project and release to production. Unlike preview.sh, this populates
# the Frontend link in dashboard → Settings → Headless Settings → Manage URLs,
# which Wix injects into transactional emails (order confirmations, password
# resets, member invites). Use release.sh for production deploys.
#
# Usage:
#   bash <SKILL_ROOT>/scripts/release.sh
#
# Run from the project directory (CWD = <project>/). Requires wix.config.json.
#
# Output: stdout is the released URL that `npx @wix/cli@latest release` printed
# (extracted from the line `Site published on <url>`); the orchestrator
# captures it as outcome.releaseUrl in run.json. All other CLI output goes
# to stderr.
#
# Exit codes:
#   0 — ok; release URL on stdout
#   <other> — build or release failed; stderr surfaces the underlying error.
#             Build failures are code bugs (TypeScript / Astro / missing
#             module) — the orchestrator does NOT retry. Release auth failures
#             surface as `Run npx @wix/cli@latest login and retry.`
#             Known transient release failures are retried by this script.

set -euo pipefail

npx @wix/cli@latest build 1>&2

RELEASE_OUTPUT="$(mktemp)"
trap 'rm -f "$RELEASE_OUTPUT"' EXIT

release_is_retryable() {
  grep -Eiq 'ECONNRESET|ETIMEDOUT|EAI_AGAIN|STATE_MISMATCH|temporary system error|temporarily unavailable|try again shortly' "$RELEASE_OUTPUT"
}

MAX_RELEASE_ATTEMPTS="${WIX_RELEASE_ATTEMPTS:-3}"
RELEASE_STATUS=1

for ((attempt = 1; attempt <= MAX_RELEASE_ATTEMPTS; attempt++)); do
  : >"$RELEASE_OUTPUT"
  set +e
  npx @wix/cli@latest release 2>&1 | tee "$RELEASE_OUTPUT" 1>&2
  RELEASE_STATUS=${PIPESTATUS[0]}
  set -e

  if [[ "$RELEASE_STATUS" -eq 0 ]]; then
    break
  fi

  if [[ "$attempt" -lt "$MAX_RELEASE_ATTEMPTS" ]] && release_is_retryable; then
    sleep_seconds=$((attempt * 5))
    echo "release.sh: release attempt $attempt failed with a retryable Wix error; retrying in ${sleep_seconds}s" >&2
    sleep "$sleep_seconds"
    continue
  fi

  exit "$RELEASE_STATUS"
done

# CLI prints `Site published on <url>` — extract the URL after that marker.
# Fall back to the first Wix-hosted URL if the marker line is not found
# (CLI wording may vary between versions).
RELEASE_URL="$(sed -nE 's/.*Site published on ([^[:space:]]+).*/\1/p' "$RELEASE_OUTPUT" | head -n 1 || true)"
if [[ -z "$RELEASE_URL" ]]; then
  RELEASE_URL="$(grep -oE 'https://[A-Za-z0-9.-]+\.wix-(site-)?host\.com[^[:space:]]*' "$RELEASE_OUTPUT" | head -n 1 || true)"
fi

if [[ -z "$RELEASE_URL" ]]; then
  echo "release.sh: could not extract a release URL from release output" >&2
  exit 1
fi

echo "$RELEASE_URL"
