#!/usr/bin/env bash
# Build the project and deploy a rotating preview URL.
#
# Usage:
#   bash <SKILL_ROOT>/scripts/preview.sh
#
# Run from the project directory (CWD = <project>/). Requires wix.config.json.
#
# Output: stdout is the preview URL that `npx @wix/cli@latest preview` printed; the
# orchestrator captures it and records as outcome.previewUrl in run.json. All
# other CLI output goes to stderr.
#
# `preview` does NOT populate the Frontend link in headless settings — that's
# what `release.sh` is for. Use preview for fast iteration on a rotating URL;
# use release for production deploy + transactional-email URL stability.
#
# Exit codes:
#   0 — ok; preview URL on stdout
#   <other> — build or preview failed; stderr surfaces the underlying error
#             (TypeScript / Astro errors are code bugs, not endpoint drift —
#              the orchestrator's recovery ladder doesn't retry build).

set -euo pipefail

# Build first; surface compile errors verbatim if it fails.
npx @wix/cli@latest build 1>&2

# Preview captures the deployed URL on stdout. We tee its output to stderr for
# the user-visible log AND parse the URL out for the orchestrator's stdout.
PREVIEW_OUTPUT="$(mktemp)"
trap 'rm -f "$PREVIEW_OUTPUT"' EXIT

npx @wix/cli@latest preview 2>&1 | tee "$PREVIEW_OUTPUT" 1>&2

# Wix CLI prints `Site preview URL: <url>` (or similar) — extract the first
# https URL from the output. If multiple are printed, the first is the canonical
# preview URL.
PREVIEW_URL="$(grep -oE 'https://[A-Za-z0-9.-]+\.wix-host\.com[^[:space:]]*' "$PREVIEW_OUTPUT" | head -n 1 || true)"

if [[ -z "$PREVIEW_URL" ]]; then
  echo "preview.sh: could not extract a *.wix-host.com URL from preview output" >&2
  exit 1
fi

echo "$PREVIEW_URL"
