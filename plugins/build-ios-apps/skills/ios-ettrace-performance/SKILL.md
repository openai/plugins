---
name: ios-ettrace-performance
description: Capture and interpret ETTrace profiles for iOS simulator apps, including symbolicated launch and runtime flamegraphs. Use when asked to profile an iOS app flow, gather simulator performance traces, identify CPU-heavy stacks, compare before/after traces, or produce flamegraph evidence for startup, scrolling, navigation, rendering, or other user-visible latency.
---

# iOS ETTrace Performance

Use this skill to capture a focused, symbolicated ETTrace profile from an iOS simulator app. Pair it with `../ios-debugger-agent/SKILL.md` when the task also needs simulator build, install, launch, UI driving, logs, or screenshots.

## Core Workflow

1. Pick one focused flow and write down the expected start and stop points.
2. Build the exact simulator app that will be installed and profiled.
3. Temporarily link ETTrace into that app target for simulator/debug profiling.
4. Collect UUID-matched dSYMs for the app executable and embedded dynamic frameworks.
5. Capture one launch or runtime trace.
6. Preserve the processed flamegraph JSON immediately after the run.
7. Analyze only the processed JSON and report the flow, artifacts, hotspots, and caveats.

Avoid broad "use the app for a while" captures. One trace should correspond to one user-visible flow.

## Setup

Use a writable run folder for each profiling session:

```bash
if [ -z "${RUN_DIR:-}" ]; then
  RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-ios-ettrace.XXXXXX")"
fi
mkdir -p "$RUN_DIR"
```

Install the ETTrace runner CLI if it is not already available:

```bash
brew install emergetools/homebrew-tap/ettrace
```

`ettrace` is the host-side macOS runner. The app must also link an `ETTrace.xcframework` for the iOS Simulator architecture.
This workflow is validated for ETTrace v1.1.0 processed `output_<thread>.json` files with top-level `nodes`.

## Link ETTrace Into The App

Wire ETTrace into the exact app target being profiled. Keep the integration in a clearly temporary patch and remove it when the profiling task is done unless the user explicitly asks to keep it.

Preferred options:

- Reuse an existing simulator-compatible `ETTrace.xcframework` if the repo already vendors one.
- If none exists, build a simulator-only copy into `RUN_DIR` from the upstream ETTrace package.
- Link the framework directly into the app target, not only into tests, resources, data files, or a nested launcher target.
- Confirm launch logs print `Starting ETTrace`.
- Profile only one ETTrace-instrumented simulator app at a time because simulator mode listens on a fixed localhost port.

Build a simulator framework when needed:

```bash
ETTRACE_TAG="${ETTRACE_TAG:-v1.1.0}" # Override to match the installed runner when Homebrew updates.
ETTRACE_SRC="$RUN_DIR/ETTrace-src"
if [ ! -d "$ETTRACE_SRC" ]; then
  git clone --depth 1 --branch "$ETTRACE_TAG" https://github.com/EmergeTools/ETTrace "$ETTRACE_SRC"
fi

rm -rf "$RUN_DIR/ETTrace-iphonesimulator.xcarchive" "$RUN_DIR/ETTrace.xcframework"
pushd "$ETTRACE_SRC" >/dev/null
xcodebuild archive \
  -scheme ETTrace \
  -archivePath "$RUN_DIR/ETTrace-iphonesimulator.xcarchive" \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES \
  INSTALL_PATH='Library/Frameworks' \
  SKIP_INSTALL=NO \
  CLANG_CXX_LANGUAGE_STANDARD=c++17

xcodebuild -create-xcframework \
  -framework "$RUN_DIR/ETTrace-iphonesimulator.xcarchive/Products/Library/Frameworks/ETTrace.framework" \
  -output "$RUN_DIR/ETTrace.xcframework"
popd >/dev/null
```

For Bazel apps, a temporary import usually looks like:

```python
load("@rules_apple//apple:apple.bzl", "apple_dynamic_xcframework_import")

package(default_visibility = ["//visibility:public"])

apple_dynamic_xcframework_import(
    name = "ETTrace",
    xcframework_imports = glob(["ETTrace.xcframework/**"]),
)
```

For Xcode projects, temporarily add the simulator `ETTrace.xcframework` to the app target's Link Binary With Libraries / Embed Frameworks phases for the debug simulator build you are profiling, then remove that wiring after profiling.

## Symbolication Gate

Do not draw conclusions from an unsymbolicated flamegraph. Before every capture, prepare a dSYM folder that includes the app dSYM and any embedded first-party dynamic framework dSYMs.

Collect dSYMs after the final build that produced the installed app:

```bash
SKILL_DIR="<absolute path to this loaded skill folder>"
APP="<path-to-built-simulator-App.app>"
DSYMS="$RUN_DIR/dsyms"

"$SKILL_DIR/scripts/collect_ios_dsyms.sh" \
  --app "$APP" \
  --out-dir "$DSYMS" \
  --search-root "$(dirname "$APP")" \
  --search-root "$PWD" \
  --extra-dsym "$RUN_DIR/ETTrace-iphonesimulator.xcarchive/dSYMs/ETTrace.framework.dSYM"
```

Add `--require-framework <FrameworkName>` for app-owned dynamic frameworks that must symbolicate; use `--require-all-frameworks` only when every embedded framework is app-owned or expected to have symbols. If the helper reports a missing required app or framework dSYM, rebuild the exact simulator app with dSYM generation before tracing, or add the build output directory that contains those dSYMs as another `--search-root`.

Verify important UUIDs before tracing when the report looks suspicious:

```bash
dwarfdump --uuid "$APP/$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$APP/Info.plist")"
find "$DSYMS" -maxdepth 1 -type d -name '*.dSYM' -print -exec dwarfdump --uuid {} \;
```

After ETTrace exits, read its symbolication summary. Treat meaningful first-party "have library but no symbol" lines as a failed trace unless they are tiny noise. Unsymbolicated system-framework or ETTrace internal buckets are usually acceptable.

## Capture

For launch traces:

```bash
cd "$RUN_DIR"
CAPTURE_MARKER="$RUN_DIR/.ettrace-capture-start"
: > "$CAPTURE_MARKER"
find "$RUN_DIR" -maxdepth 1 \( -name 'output.json' -o -name 'output_*.json' \) -delete
ettrace --simulator --launch --verbose --dsyms "$DSYMS"
```

Use `--launch` only when measuring startup or first render. The first launch connection can force quit the app; relaunch from the simulator home screen rather than Xcode if prompted. For first-launch-after-install traces, temporarily set `ETTraceRunAtStartup=YES` in the app Info.plist, then run `ettrace --simulator` and launch from the home screen.

For runtime flow traces:

```bash
cd "$RUN_DIR"
CAPTURE_MARKER="$RUN_DIR/.ettrace-capture-start"
: > "$CAPTURE_MARKER"
find "$RUN_DIR" -maxdepth 1 \( -name 'output.json' -o -name 'output_*.json' \) -delete
ettrace --simulator --verbose --dsyms "$DSYMS"
```

Start from a stable screen, start ETTrace, perform exactly one focused flow, wait until visible work is complete, then stop the runner. For wider attribution, add `--multi-thread`; otherwise start with the main thread.

In Codex, run `ettrace` with a TTY and answer prompts with `write_stdin`. Without a TTY, the runner can exit without a useful trace.

## Preserve Outputs

The next ETTrace run can overwrite processed flamegraph files, so preserve fresh `output_<thread-id>.json` files immediately. Do not analyze a saved `output.json`; ETTrace also serves a viewer route with that name, and raw `emerge-output/output.json` files are not the processed flamegraph artifacts this workflow expects.

```bash
PRESERVED_DIR="$(mktemp -d "$RUN_DIR/run-$(date +%Y%m%d-%H%M%S).XXXXXX")"
: > "$PRESERVED_DIR/summary.txt"
if [ ! -e "$CAPTURE_MARKER" ]; then
  echo "error: capture marker missing; start a fresh ETTrace capture before preserving outputs" >&2
  exit 1
fi
find "$RUN_DIR" -maxdepth 1 -name 'output_*.json' -newer "$CAPTURE_MARKER" -print | while IFS= read -r json; do
  preserved="$PRESERVED_DIR/${json##*/}"
  cp "$json" "$preserved"
  {
    echo "## ${preserved##*/}"
    python3 "$SKILL_DIR/scripts/analyze_flamegraph_json.py" "$preserved"
  } >> "$PRESERVED_DIR/summary.txt"
done
if [ ! -s "$PRESERVED_DIR/summary.txt" ]; then
  echo "error: no fresh processed ETTrace output JSON found in $RUN_DIR" >&2
  exit 1
fi
```

Analyze only processed `output_*.json` files in `RUN_DIR`. Ignore `output.json` and raw `emerge-output/output.json` files unless debugging ETTrace itself. If the analyzer rejects the JSON shape, capture again with the Homebrew ETTrace runner and matching app-side `ETTrace.xcframework` tag instead of trying to interpret the rejected file.

## Read The Profile

Start from `run-*/summary.txt`, then inspect processed JSON directly if needed.

Report:

- exact flow, app build, simulator model/runtime, and run count
- processed flamegraph JSON paths
- top active leaves and inclusive first-party stacks with sample weights or percentages
- whether symbols were complete for app-owned binaries
- caveats such as first-run setup, simulator-only cost, network variance, or low sample count
- before/after deltas only when the same flow was captured with comparable setup


## Cleanup

Remove temporary ETTrace app wiring when profiling is complete unless the user asked to keep it. Keep or discard run artifacts based on the active task.
