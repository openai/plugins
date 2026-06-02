#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: simpleperf_hotspots.sh <perf.data> [output-dir] [--serial SERIAL] [--first-party-regex REGEX]

Generates Simpleperf self-time, children/inclusive, and optional CSV reports
for a focused Android profiling capture.

Options:
  --serial SERIAL             adb serial for device-side fallback.
  --first-party-regex REGEX   Extra grep pattern for likely app-owned rows.

Environment:
  ANDROID_PERF_FIRST_PARTY_REGEX  Default first-party grep pattern
  ANDROID_PERF_SERIAL             adb serial for device-side fallback
  ANDROID_PERF_DEVICE_DATA        device perf.data path for fallback
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

perf_data=""
output_dir=""
first_party_regex="${ANDROID_PERF_FIRST_PARTY_REGEX:-}"
serial="${ANDROID_PERF_SERIAL:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --first-party-regex)
      if [[ -z "${2:-}" ]]; then
        echo "--first-party-regex requires a value" >&2
        usage
        exit 2
      fi
      first_party_regex="$2"
      shift 2
      ;;
    --serial)
      if [[ -z "${2:-}" ]]; then
        echo "--serial requires a value" >&2
        usage
        exit 2
      fi
      serial="$2"
      shift 2
      ;;
    -*)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -z "$perf_data" ]]; then
        perf_data="$1"
      elif [[ -z "$output_dir" ]]; then
        output_dir="$1"
      else
        echo "Unexpected argument: $1" >&2
        usage
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$perf_data" ]]; then
  usage
  exit 2
fi

if [[ -n "$first_party_regex" ]]; then
  set +e
  awk -v re="$first_party_regex" 'BEGIN { _ = ("" ~ re); exit 0 }' >/dev/null 2>&1
  regex_status=$?
  set -e
  if [[ $regex_status -ne 0 ]]; then
    echo "Invalid --first-party-regex: $first_party_regex" >&2
    exit 2
  fi
fi

perf_data_exists=0
if [[ -f "$perf_data" ]]; then
  perf_data_exists=1
fi

if [[ "$perf_data_exists" -eq 1 && "$perf_data" != /* ]]; then
  perf_data="$(cd "$(dirname "$perf_data")" && pwd)/$(basename "$perf_data")"
fi

output_dir="${output_dir:-$(dirname "$perf_data")}"
mkdir -p "$output_dir"
if [[ "$output_dir" != /* ]]; then
  output_dir="$(cd "$output_dir" && pwd)"
fi

search_roots=()
for env_var in ANDROID_NDK_HOME ANDROID_HOME ANDROID_SDK_ROOT; do
  value="${!env_var:-}"
  if [[ -n "$value" && -d "$value" ]]; then
    search_roots+=("$value")
  fi
done

default_sdk="$HOME/Library/Android/sdk"
if [[ -d "$default_sdk" ]]; then
  search_roots+=("$default_sdk")
fi

android_studio_simpleperf="/Applications/Android Studio.app/Contents/plugins/android/resources/simpleperf"
if [[ -d "$android_studio_simpleperf" ]]; then
  search_roots+=("$android_studio_simpleperf")
fi

simpleperf_bin=""
if command -v simpleperf >/dev/null 2>&1; then
  candidate_simpleperf="$(command -v simpleperf)"
  if [[ -x "$candidate_simpleperf" ]] && "$candidate_simpleperf" --version >/dev/null 2>&1; then
    simpleperf_bin="$candidate_simpleperf"
  fi
fi

if [[ -z "$simpleperf_bin" ]] && (( ${#search_roots[@]} > 0 )); then
  while IFS= read -r simpleperf_path; do
    if [[ -x "$simpleperf_path" ]] && "$simpleperf_path" --version >/dev/null 2>&1; then
      simpleperf_bin="$simpleperf_path"
      break
    fi
  done < <(
    {
      find "${search_roots[@]}" -path '*/darwin-*/simpleperf' -type f -print
      find "${search_roots[@]}" -path '*/simpleperf' -type f -print
    } 2>/dev/null | awk '!seen[$0]++'
  )
fi

print_report_summary() {
  local children_report="$1"

  printf '\nTop inclusive rows:\n'
  awk 'seen || /^(Overhead|Children)/ { seen = 1; print }' "$children_report" | sed -n '1,80p'

  printf '\nLikely first-party rows:\n'
  if [[ -n "$first_party_regex" ]]; then
    awk -v re="$first_party_regex" '
      function is_sample_row(columns) {
        return columns >= 7 && $1 ~ /%$/ && $2 ~ /%$/
      }
      {
        sub(/^[[:space:]]+/, "")
        columns = split($0, fields, /[[:space:]]{2,}/)
        if (is_sample_row(columns)) {
          shared_object = fields[6]
          symbol = fields[7]
          if ((shared_object " " symbol) ~ re) {
            print
            found = 1
          }
        }
      }
      END {
        if (!found) {
          print "No rows matched the first-party regex in Shared Object or Symbol columns."
        }
      }
    ' "$children_report" | sed -n '1,120p'
  else
    printf 'No first-party regex configured. Re-run with --first-party-regex scoped to the app package or app-owned modules.\n'
  fi
}

if [[ -z "$simpleperf_bin" ]]; then
  if ! command -v adb >/dev/null 2>&1; then
    echo "Host Simpleperf unavailable and adb is not installed or not on PATH." >&2
    echo "Install Android platform-tools, set PATH for adb, or install host Simpleperf." >&2
    exit 1
  fi

  if [[ -z "$serial" ]]; then
    connected_devices=()
    while IFS= read -r connected_device; do
      connected_devices+=("$connected_device")
    done < <(
      adb devices 2>/dev/null |
        awk 'NR > 1 && $2 == "device" { print $1 }'
    )
    if [[ ${#connected_devices[@]} -eq 1 ]]; then
      serial="${connected_devices[0]}"
    else
      echo "Host Simpleperf unavailable and no adb serial was provided." >&2
      echo "Pass --serial or set ANDROID_PERF_SERIAL so device-side fallback reads the intended target." >&2
      adb devices >&2 || true
      exit 1
    fi
  fi

  device_perf_data="${ANDROID_PERF_DEVICE_DATA:-/data/local/tmp/perf.data}"
  if [[ -n "$serial" ]] && adb -s "$serial" shell test -f "$device_perf_data" 2>/dev/null; then
    self_report="$output_dir/simpleperf-self.txt"
    children_report="$output_dir/simpleperf-children.txt"

    adb -s "$serial" shell simpleperf report -i "$device_perf_data" > "$self_report"
    adb -s "$serial" shell simpleperf report -i "$device_perf_data" --children > "$children_report"

    printf 'Simpleperf binary: device %s\n' "$serial"
    printf 'Wrote: %s\n' "$self_report"
    printf 'Wrote: %s\n' "$children_report"
    printf 'First-party regex: %s\n' "${first_party_regex:-<none>}"
    print_report_summary "$children_report"
    exit 0
  fi

  echo "Could not find host Simpleperf on PATH or under: ${search_roots[*]:-(no search roots)}" >&2
  echo "Also could not use device-side fallback. Set ANDROID_PERF_SERIAL and keep perf.data on the device, or install host Simpleperf." >&2
  exit 1
fi

if [[ "$perf_data_exists" -ne 1 ]]; then
  echo "perf.data not found: $perf_data" >&2
  exit 1
fi

self_report="$output_dir/simpleperf-self.txt"
children_report="$output_dir/simpleperf-children.txt"
csv_report="$output_dir/simpleperf.csv"

"$simpleperf_bin" report -i "$perf_data" > "$self_report"
"$simpleperf_bin" report -i "$perf_data" --children > "$children_report"

if "$simpleperf_bin" report -i "$perf_data" --children --csv > "$csv_report" 2>/dev/null; then
  :
else
  rm -f "$csv_report"
fi

printf 'Simpleperf binary: %s\n' "$simpleperf_bin"
printf 'Wrote: %s\n' "$self_report"
printf 'Wrote: %s\n' "$children_report"
[[ -f "$csv_report" ]] && printf 'Wrote: %s\n' "$csv_report"
printf 'First-party regex: %s\n' "${first_party_regex:-<none>}"
print_report_summary "$children_report"
