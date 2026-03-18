#!/usr/bin/env bash
# Draft hook example for future plugin hook runtimes.
# Intention: nudge the agent to re-check Figma parity after UI-affecting writes.

set -euo pipefail

echo "[draft-hook] PostToolUse triggered after file write. If the change is UI-related, re-run screenshot-based Figma parity checks before finalizing."
