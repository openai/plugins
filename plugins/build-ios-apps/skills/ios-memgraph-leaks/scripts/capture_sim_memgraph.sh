#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Capture a memory graph from a running iOS simulator app.

Required:
  --udid UDID                 Simulator UDID
  --bundle-id ID              App bundle identifier, e.g. com.example.app

Optional:
  --out-dir DIR               Output directory for the memgraph and leaks output

Example:
  capture_sim_memgraph.sh --udid "$SIM" --bundle-id com.example.app --out-dir /tmp/codex-ios-memgraph
USAGE
}

require_value() {
  local flag="$1"
  local value="${2:-}"
  if [[ -z "$value" ]]; then
    echo "$flag requires a value" >&2
    usage >&2
    exit 2
  fi
}

bundle_id=""
out_dir=""
udid=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bundle-id)
      require_value "$1" "${2:-}"
      bundle_id="$2"
      shift 2
      ;;
    --out-dir)
      require_value "$1" "${2:-}"
      out_dir="$2"
      shift 2
      ;;
    --udid)
      require_value "$1" "${2:-}"
      udid="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$udid" ]]; then
  echo "--udid is required" >&2
  usage >&2
  exit 2
fi

if [[ -z "$bundle_id" ]]; then
  echo "--bundle-id is required" >&2
  usage >&2
  exit 2
fi

if [[ -z "$out_dir" ]]; then
  out_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-ios-memgraph.XXXXXX")"
fi

matching_processes="$(
  xcrun simctl spawn "$udid" launchctl list |
    awk -v bundle_id="$bundle_id" '
      $1 == "-" {
        next
      }
      $3 == bundle_id {
        print $1 "\t" $3
        next
      }
      index($3, "UIKitApplication:" bundle_id "[") == 1 {
        print $1 "\t" $3
      }
    '
)"

if [[ -z "$matching_processes" ]]; then
  echo "Could not find a running PID for $bundle_id on $udid" >&2
  exit 1
fi

if [[ "$(printf '%s\n' "$matching_processes" | wc -l | tr -d ' ')" -ne 1 ]]; then
  echo "Found multiple running PIDs for $bundle_id on $udid:" >&2
  printf '%s\n' "$matching_processes" >&2
  exit 1
fi

pid="$(printf '%s\n' "$matching_processes" | awk '{ print $1 }')"
process_label="$(printf '%s\n' "$matching_processes" | cut -f2-)"

mkdir -p "$out_dir"

timestamp="$(date +%Y%m%d-%H%M%S)"
safe_bundle="$(printf '%s' "$bundle_id" | tr -c 'A-Za-z0-9_.-' '_')"
memgraph="$out_dir/$safe_bundle-$pid-$timestamp.memgraph"
leaks_output="$out_dir/$safe_bundle-$pid-$timestamp.leaks.txt"
metadata="$out_dir/$safe_bundle-$pid-$timestamp.metadata.txt"

{
  echo "date: $(date)"
  echo "udid: $udid"
  echo "bundle_id: $bundle_id"
  echo "process_label: $process_label"
  echo "pid: $pid"
  echo "memgraph: $memgraph"
  echo "leaks_output: $leaks_output"
} > "$metadata"

set +e
leaks "--outputGraph=$memgraph" "$pid" > "$leaks_output" 2>&1
leaks_status=$?
set -e

echo "leaks_exit_status: $leaks_status" >> "$metadata"

if [[ ! -f "$memgraph" ]]; then
  echo "memgraph_missing: true" >> "$metadata"
  echo "leaks failed to create a memgraph; see: $leaks_output" >&2
  echo "metadata: $metadata" >&2
  exit 1
fi

echo "memgraph: $memgraph"
echo "leaks output: $leaks_output"
echo "metadata: $metadata"
