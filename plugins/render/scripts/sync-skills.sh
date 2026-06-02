#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/render-oss/skills"
SKILLS_SUBDIR="skills"
PLUGIN_SKILLS_DIR="skills"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_URL="$2"
      shift 2
      ;;
    --subdir)
      SKILLS_SUBDIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Cloning $REPO_URL ..."
git clone --depth 1 --quiet "$REPO_URL" "$TMPDIR/skills-source"

SOURCE_DIR="$TMPDIR/skills-source/$SKILLS_SUBDIR"
TARGET_DIR="$REPO_ROOT/$PLUGIN_SKILLS_DIR"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Skills subdirectory '$SKILLS_SUBDIR' not found in $REPO_URL." >&2
  exit 1
fi

SKILLS=()
for dir in "$SOURCE_DIR"/*/; do
  if [[ -f "$dir/SKILL.md" ]]; then
    SKILLS+=("$(basename "$dir")")
  fi
done

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo "No skills found in $REPO_URL (no directories with SKILL.md)." >&2
  exit 1
fi

echo "Found ${#SKILLS[@]} skills: ${SKILLS[*]}"

rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"

for skill in "${SKILLS[@]}"; do
  cp -R "$SOURCE_DIR/$skill" "$TARGET_DIR/$skill"
  file_count="$(find "$TARGET_DIR/$skill" -type f | wc -l | tr -d ' ')"
  echo "  $skill ($file_count files)"
done

echo ""
echo "Synced ${#SKILLS[@]} skills into $PLUGIN_SKILLS_DIR/"
