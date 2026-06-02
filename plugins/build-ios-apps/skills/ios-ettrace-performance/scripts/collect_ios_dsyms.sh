#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: collect_ios_dsyms.sh --app App.app --out-dir DIR [options]

Collects UUID-matched dSYMs for a built iOS simulator app into DIR.

Required:
  --app PATH                 Built .app bundle
  --out-dir DIR              Destination dSYM directory

Optional:
  --search-root DIR          Directory to search for .dSYM bundles (repeatable)
  --extra-dsym DIR           Known .dSYM bundle to include in candidates (repeatable)
  --require-framework NAME   Require a matching dSYM for an embedded framework
  --require-all-frameworks   Require matching dSYMs for every embedded framework

Example:
  collect_ios_dsyms.sh --app build/Debug-iphonesimulator/MyApp.app \
    --out-dir /tmp/profile/dsyms \
    --search-root build \
    --search-root ~/Library/Developer/Xcode/DerivedData
USAGE
}

require_value() {
  local flag="$1"
  local value="${2:-}"
  if [[ -z "$value" ]]; then
    echo "$flag requires a value" >&2
    usage
    exit 2
  fi
}

app_path=""
out_dir=""
require_all_frameworks=false
search_roots=()
extra_dsyms=()
required_frameworks=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app)
      require_value "$1" "${2:-}"
      app_path="$2"
      shift 2
      ;;
    --out-dir)
      require_value "$1" "${2:-}"
      out_dir="$2"
      shift 2
      ;;
    --search-root)
      require_value "$1" "${2:-}"
      search_roots+=("$2")
      shift 2
      ;;
    --extra-dsym)
      require_value "$1" "${2:-}"
      extra_dsyms+=("$2")
      shift 2
      ;;
    --require-framework)
      require_value "$1" "${2:-}"
      required_frameworks+=("$2")
      shift 2
      ;;
    --require-all-frameworks)
      require_all_frameworks=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$app_path" || -z "$out_dir" ]]; then
  usage
  exit 2
fi

if [[ ! -d "$app_path" ]]; then
  echo "error: app bundle not found: $app_path" >&2
  exit 1
fi

app_path="$(cd "$(dirname "$app_path")" && pwd)/$(basename "$app_path")"
mkdir -p "$out_dir"
out_dir="$(cd "$out_dir" && pwd)"
candidates_file="$out_dir/dsym-candidates.txt"

if [[ -f "$app_path/Info.plist" ]]; then
  executable="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$app_path/Info.plist")"
else
  executable="$(basename "$app_path" .app)"
fi

app_binary="$app_path/$executable"
if [[ ! -f "$app_binary" ]]; then
  echo "error: app executable not found: $app_binary" >&2
  exit 1
fi

default_roots=(
  "$(dirname "$app_path")"
  "$PWD"
  "$PWD/build"
  "$PWD/bazel-bin"
  "$PWD/bazel-out"
)

for root in "${default_roots[@]}"; do
  if [[ -d "$root" ]]; then
    search_roots+=("$root")
  fi
done

if [[ -d "$HOME/Library/Developer/Xcode/DerivedData" ]]; then
  search_roots+=("$HOME/Library/Developer/Xcode/DerivedData")
fi

: > "$candidates_file"
if [[ ${#search_roots[@]} -gt 0 ]]; then
  find -L "${search_roots[@]}" -type d -name "*.dSYM" -prune -print 2>/dev/null >> "$candidates_file" || true
fi

if [[ ${#extra_dsyms[@]} -gt 0 ]]; then
  for dsym in "${extra_dsyms[@]}"; do
    if [[ -d "$dsym" ]]; then
      printf '%s\n' "$dsym" >> "$candidates_file"
    fi
  done
fi

awk '!seen[$0]++' "$candidates_file" > "$candidates_file.tmp"
mv "$candidates_file.tmp" "$candidates_file"

if [[ ! -s "$candidates_file" ]]; then
  echo "error: no dSYM candidates found. Add --search-root pointing at build output or DerivedData." >&2
  exit 1
fi

contains_required_framework() {
  local framework_name="$1"
  if [[ ${#required_frameworks[@]} -eq 0 ]]; then
    return 1
  fi

  for required in "${required_frameworks[@]}"; do
    if [[ "$required" == "$framework_name" || "$required" == "${framework_name%.framework}" ]]; then
      return 0
    fi
  done
  return 1
}

copy_matching_dsym() {
  local binary="$1"
  local label="$2"
  local required="$3"

  if [[ ! -f "$binary" ]]; then
    return 0
  fi

  local binary_uuids=()
  while IFS= read -r uuid; do
    [[ -n "$uuid" ]] && binary_uuids+=("$uuid")
  done < <(dwarfdump --uuid "$binary" 2>/dev/null | awk '{ print $2 }')

  if [[ ${#binary_uuids[@]} -eq 0 ]]; then
    if [[ "$required" == "required" ]]; then
      echo "error: could not read UUID for required $label: $binary" >&2
      return 1
    fi

    echo "warning: could not read UUID for $label: $binary" >&2
    return 0
  fi

  local match=""
  local candidate_uuids=""
  local has_all_uuids=""
  while IFS= read -r candidate; do
    candidate_uuids="$(dwarfdump --uuid "$candidate" 2>/dev/null | awk '{ print $2 }' || true)"
    if [[ -z "$candidate_uuids" ]]; then
      continue
    fi
    has_all_uuids=true
    for uuid in "${binary_uuids[@]}"; do
      if ! grep -Fxq "$uuid" <<< "$candidate_uuids"; then
        has_all_uuids=false
        break
      fi
    done

    if [[ "$has_all_uuids" == "true" ]]; then
      match="$candidate"
      break
    fi
  done < "$candidates_file"

  if [[ -z "$match" ]]; then
    if [[ "$required" == "required" ]]; then
      echo "error: missing required dSYM for $label UUIDs ${binary_uuids[*]}" >&2
      return 1
    fi

    echo "warning: missing dSYM for $label UUIDs ${binary_uuids[*]}" >&2
    return 0
  fi

  local dest="$out_dir/$(basename "$match")"
  rm -rf "$dest"
  cp -R "$match" "$dest"
  printf 'matched %s UUIDs %s -> %s\n' "$label" "${binary_uuids[*]}" "$dest"
}

copy_matching_dsym "$app_binary" "$executable.app" required

if [[ -d "$app_path/Frameworks" ]]; then
  for framework in "$app_path"/Frameworks/*.framework; do
    [[ -d "$framework" ]] || continue

    framework_name="$(basename "$framework")"
    framework_binary="$framework/${framework_name%.framework}"
    required="optional"

    if [[ "$require_all_frameworks" == "true" ]] || contains_required_framework "$framework_name"; then
      required="required"
    fi

    copy_matching_dsym "$framework_binary" "$framework_name" "$required"
  done
fi

cat <<EOF
DSYMS=$out_dir

Use:
  ettrace --simulator --launch --dsyms "$out_dir"
EOF
