#!/usr/bin/env bash
# Frontend-track project prep: copy the skill's shared utilities into the
# project's src/utils/ and strip the Astro starter cruft that ships with the
# blank template. This is local-project (frontend) work, not backend seeding —
# the orchestrator only runs it in scaffold mode (integrate mode has no
# skill-written frontend to prep, so it is never invoked there).
#
# Usage (both modes work):
#   bash <SKILL_ROOT>/scripts/seed-utilities.sh --template astro
#   bash <(curl -s https://dev.wix.com/skills/wix-headless/scripts/seed-utilities.sh) --template astro
#
# --template (optional, default astro): astro
#   Astro is the only frontend the skill scaffolds and preps, so the value is
#   always "astro". Custom (non-astro) frontends route to the not-available stub
#   (references/custom/INSTRUCTIONS.md) and never reach this script.
#
# Run from the project directory (CWD = <scaffold>/). The script auto-detects
# whether shared-utilities is available on disk (tgz install) and falls back
# to fetching from the well-known URL when streamed via process substitution
# (BASH_SOURCE is /dev/fd/N, so the on-disk lookup naturally falls through).
#
# Behavior:
#   - Copies the three shared utility files into src/utils/ for both templates —
#     never overwrites an existing file (users can drop in their own version).
#   - On --template=astro, removes Astro starter cruft (Welcome.astro + marketing
#     SVGs) that ships with the blank template but is never imported by the build
#     skill.
#
# Shared utilities copied:
#   - wix-image.ts  — media URL resolver (used by stores, blog, cms)
#   - analytics.ts  — event tracking (used by stores, ecom, blog)
#   - ricos.ts      — Ricos JSON to HTML renderer for SSR Astro pages

set -euo pipefail

SKILL_URL="https://dev.wix.com/skills/wix-headless"
UTILS=(analytics.ts ricos.ts wix-image.ts)

TEMPLATE="astro"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    --template=*)
      TEMPLATE="${1#--template=}"
      shift
      ;;
    *)
      echo "seed-utilities.sh: unexpected arg: $1" >&2
      exit 2
      ;;
  esac
done

case "$TEMPLATE" in
  astro) ;;
  *)
    echo "seed-utilities.sh: --template must be 'astro' (the only supported frontend); got $TEMPLATE" >&2
    echo "(Custom non-astro frontends route to the stub and never reach this script.)" >&2
    exit 2
    ;;
esac

# Mode detection: prefer on-disk skill root if the sibling dir exists, else
# fetch over HTTP. Covers both tgz install and `bash <(curl ...)` streaming.
SHARED_UTILS_DIR=""
script_path="${BASH_SOURCE[0]}"
if [[ -f "$script_path" ]]; then
  candidate="$(dirname "$script_path")/../shared-utilities"
  if [[ -d "$candidate" ]]; then
    SHARED_UTILS_DIR="$(cd "$candidate" && pwd)"
  fi
fi

mkdir -p src/utils

for f in "${UTILS[@]}"; do
  dest="src/utils/$f"
  if [[ -e "$dest" ]]; then continue; fi
  if [[ -n "$SHARED_UTILS_DIR" ]]; then
    cp "$SHARED_UTILS_DIR/$f" "$dest"
  else
    curl -fsSL "$SKILL_URL/shared-utilities/$f" -o "$dest"
  fi
done

# Astro starter cruft cleanup — astro template only.
if [[ "$TEMPLATE" == "astro" ]]; then
  rm -f src/components/Welcome.astro
  rm -f src/assets/astro.svg src/assets/wix.svg src/assets/background.svg
fi
