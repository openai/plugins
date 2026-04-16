#!/usr/bin/env bash
set -euo pipefail

if ! command -v render &>/dev/null; then
  echo "[render plugin] Render CLI not found. Install it to validate render.yaml:"
  echo "  macOS:  brew install render"
  echo "  Linux:  curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh"
  exit 0
fi

render blueprints validate
