#!/usr/bin/env bash
# Install mixpanel_headless and pandas for CodeMode analytics
set -euo pipefail

echo "=== mixpanel-headless — CodeMode Setup ==="
echo ""

# Find Python 3.10+
python_cmd=""
for cmd in python3 python; do
  if command -v "$cmd" &>/dev/null; then
    major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo 0)
    minor=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo 0)
    if [ "$major" -gt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -ge 10 ]); then
      version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
      python_cmd="$cmd"
      echo "✓ Python $version ($cmd)"
      break
    fi
  fi
done

if [ -z "$python_cmd" ]; then
  echo "✗ Python 3.10+ required but not found."
  echo "  Install from https://python.org or via your package manager."
  exit 1
fi

# Install packages
MIXPANEL_HEADLESS_PKG="mixpanel-headless"
DEPS=(pandas numpy matplotlib seaborn 'networkx>=3.0' 'anytree>=2.8.0' scipy)

# pyarrow is only needed on Python 3.11+ (for pandas 3.x Arrow-backed dtypes)
if [ "$minor" -ge 11 ]; then
  DEPS+=('pyarrow>=17.0')
fi

echo ""
echo "Installing mixpanel-headless (import name: mixpanel_headless) and dependencies..."
if command -v uv &>/dev/null; then
  echo "  (using uv)"
  uv pip install --python "$python_cmd" "$MIXPANEL_HEADLESS_PKG" "${DEPS[@]}" || { echo "  ⚠ Virtualenv install failed, trying system install..."; uv pip install --system --python "$python_cmd" "$MIXPANEL_HEADLESS_PKG" "${DEPS[@]}"; }
elif "$python_cmd" -m pip --version &>/dev/null; then
  echo "  (using pip via $python_cmd)"
  "$python_cmd" -m pip install "$MIXPANEL_HEADLESS_PKG" "${DEPS[@]}"
else
  echo "✗ No package manager found. Install pip or uv."
  echo "  Recommended: https://docs.astral.sh/uv/"
  exit 1
fi

# Verify imports
echo ""
echo "Verifying installation..."
"$python_cmd" -c "
import sys
import mixpanel_headless as mp
import pandas as pd
import numpy as np
import matplotlib
import seaborn as sns
import networkx as nx
import anytree
import scipy
print(f'✓ mixpanel_headless installed')
print(f'✓ pandas {pd.__version__}')
if sys.version_info >= (3, 11):
    import pyarrow as pa
    print(f'✓ pyarrow {pa.__version__}')
print(f'✓ numpy {np.__version__}')
print(f'✓ matplotlib {matplotlib.__version__}')
print(f'✓ seaborn {sns.__version__}')
print(f'✓ networkx {nx.__version__}')
print(f'✓ anytree {anytree.__version__}')
print(f'✓ scipy {scipy.__version__}')
" || { echo "✗ Import verification failed"; exit 1; }

# Check credentials
echo ""
echo "Checking Mixpanel credentials..."
"$python_cmd" -c "
import os, sys

# 1) Service-account env quad
sa_quad = ['MP_USERNAME', 'MP_SECRET', 'MP_PROJECT_ID', 'MP_REGION']
sa_set = [v for v in sa_quad if os.environ.get(v)]
if len(sa_set) == len(sa_quad):
    print('✓ Service-account env quad is fully set (MP_USERNAME + MP_SECRET + MP_PROJECT_ID + MP_REGION)')
    sys.exit(0)
elif sa_set:
    missing = [v for v in sa_quad if not os.environ.get(v)]
    print(f'⚠ Partial service-account env config — missing: {\", \".join(missing)}')

# 2) OAuth-token env triple
oauth_triple = ['MP_OAUTH_TOKEN', 'MP_PROJECT_ID', 'MP_REGION']
oauth_set = [v for v in oauth_triple if os.environ.get(v)]
if len(oauth_set) == len(oauth_triple):
    print('✓ OAuth-token env triple is fully set (MP_OAUTH_TOKEN + MP_PROJECT_ID + MP_REGION)')
    sys.exit(0)

# 3) Persisted accounts in ~/.mp/config.toml
try:
    import mixpanel_headless as mp
    accounts = mp.accounts.list()
    if accounts:
        active = next((a for a in accounts if a.is_active), None)
        names = ', '.join(a.name for a in accounts)
        print(f'✓ {len(accounts)} account(s) in ~/.mp/config.toml: {names}')
        if active:
            print(f'  Active: {active.name} ({active.type}, {active.region})')
        else:
            print('⚠ No active account selected. Run: mp account use <name>')
    else:
        print('⚠ No accounts configured yet.')
        print('  Recommended:      mp login                                   # one-shot frictionless login')
        print('  Service account:  mp account add team --type service_account --username sa_xxx --project 12345 --region us')
except Exception as e:
    print(f'⚠ Could not read ~/.mp/config.toml: {e}')
    print('  Run `mp login`, set env vars (service-account quad or OAuth triple), or run mp account add ...')
"

# Remote-session detection: check for bridge file
if [ -d "/sessions" ] || [ -n "${CODEX_CLOUD:-}" ]; then
  echo ""
  echo "Remote environment detected."
  BRIDGE_FOUND=""
  for f in "$HOME/.claude/mixpanel/auth.json"; do
    if [ -f "$f" ]; then
      echo "✓ Auth bridge file found: $f"
      "$python_cmd" -c "
import json, sys
try:
    with open(sys.argv[1]) as fh:
        bridge = json.load(fh)
    if bridge.get('version') != 2:
        print(f'  ⚠ Unexpected bridge version: {bridge.get(\"version\")} (expected 2)')
    account = bridge.get('account', {})
    print(f'  Account: {account.get(\"name\", \"?\")} ({account.get(\"type\", \"?\")}, {account.get(\"region\", \"?\")})')
    project = bridge.get('project') or account.get('default_project')
    if project:
        print(f'  Project: {project}')
    if bridge.get('workspace'):
        print(f'  Workspace: {bridge[\"workspace\"]}')
    headers = bridge.get('headers') or {}
    if headers:
        print(f'  Custom headers: {len(headers)} entr{\"y\" if len(headers) == 1 else \"ies\"} ✓')
    tokens = bridge.get('tokens')
    if tokens and tokens.get('expires_at'):
        print(f'  Token expires: {tokens[\"expires_at\"]}')
except Exception as e:
    print(f'  Error reading bridge file: {e}')
" "$f"
      BRIDGE_FOUND=1
      break
    fi
  done
  if [ -z "$BRIDGE_FOUND" ]; then
    echo "⚠ No auth bridge file found."
    echo "  On your HOST machine, run:"
    echo "    mp account export-bridge --to ~/.claude/mixpanel/auth.json"
    echo "  Then start a new remote session."
  fi
fi

echo ""
echo "=== Setup complete ==="
