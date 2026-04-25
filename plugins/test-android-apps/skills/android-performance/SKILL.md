---
name: android-performance
description: Gather and interpret Android performance evidence on an adb target using Simpleperf CPU profiles, Perfetto or Compose traces, gfxinfo frame data, dumpsys meminfo snapshots, Java heap dumps, and native allocation traces. Use when asked to profile an Android app flow, find CPU-heavy functions, diagnose jank, capture startup or frame timing evidence, compare before/after performance, explain what code is taking time, or gather memory/leak profiling artifacts.
---

# Android Performance

Use this skill to capture Android performance evidence for adb-installable apps. CPU sampling usually requires a debuggable or profileable build; frame stats, Perfetto, and logcat can still help when an app cannot be sampled. Compose with `../android-emulator-qa/SKILL.md` for device selection, build/install/launch, UI driving, screenshots, UI trees, and logcat capture.

## Core Workflow

1. Pick one focused user-visible flow.
2. Choose the trace type that matches the question.
3. Record the flow with clear start and stop boundaries.
4. Pull or copy the trace produced by that run, then generate reports from that file.
5. Interpret reports with caveats about device, build type, sample count, and profiler limits.

Avoid broad "use the app for a while" captures. They make traces hard to attribute and usually hide the functions that matter.

Use a local adb target for meaningful timing. Store outputs in a run-specific artifact folder outside the skill directory:

```bash
if [ -z "${ARTIFACT_DIR:-}" ]; then
  ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-android-perf.XXXXXX")"
fi
mkdir -p "$ARTIFACT_DIR"
```

Do not put `ARTIFACT_DIR` under `SKILL_DIR`; the skill folder is for bundled instructions and scripts, not run artifacts.

## Choosing A Trace

- Use **Simpleperf** when the question is "what functions are taking CPU time?" or when you need a sampled profile of Kotlin, Java, native, or framework execution.
- Use **Perfetto** when the question is frame timing, startup timeline, scheduler gaps, binder work, lock contention, main-thread stalls, Compose recomposition, or why a flow felt janky.
- Use **gfxinfo framestats** for a quick manual frame/jank snapshot. Pair it with Perfetto when you need root cause.
- Use **meminfo / heap dumps** when the question is retained Java/Kotlin objects, PSS, native heap, or object counts after a focused flow.

## Simpleperf CPU Profiles

Simpleperf `--app` works best when the installed package is debuggable or profileable from shell. Preflight before recording:

```bash
SERIAL="<adb-serial>"
PACKAGE="<app package>"

adb -s "$SERIAL" shell dumpsys package "$PACKAGE" | grep -Ei 'DEBUGGABLE|profileable|isProfileable' || true
```

If the package is not debuggable/profileable and `simpleperf record --app` fails, install a debug/profileable build when possible. If that is not possible, use Perfetto or `gfxinfo` instead of treating missing CPU samples as evidence.

Start recording in one terminal or as a long-running Codex command session:

```bash
SERIAL="<adb-serial>"
PACKAGE="<app package>"
MAX_DURATION_SECONDS=60

adb -s "$SERIAL" shell rm -f /data/local/tmp/perf.data
adb -s "$SERIAL" logcat -c

adb -s "$SERIAL" shell simpleperf record \
  --app "$PACKAGE" \
  -o /data/local/tmp/perf.data \
  -e cpu-clock -f 4000 -g \
  --duration "$MAX_DURATION_SECONDS"
```

While that command is running, perform exactly one focused flow with adb input, UI automation, or `android-emulator-qa`.

Stop Simpleperf from another command and wait for the recording command to exit:

```bash
adb -s "$SERIAL" shell 'pid="$(pidof simpleperf 2>/dev/null || true)"; [ -n "$pid" ] && kill -INT $pid'
```

If that returns `Operation not permitted`, send Ctrl-C to the original `adb shell simpleperf record` command session and wait for it to exit.

Pull and report the capture:

```bash
adb -s "$SERIAL" pull /data/local/tmp/perf.data "$ARTIFACT_DIR/perf.data"
adb -s "$SERIAL" logcat -d > "$ARTIFACT_DIR/logcat.txt"

SKILL_DIR="<absolute path to this loaded skill folder>"
FIRST_PARTY_REGEX="$(printf '%s' "$PACKAGE" | sed 's/\./\\./g')"
"$SKILL_DIR/scripts/simpleperf_hotspots.sh" \
  "$ARTIFACT_DIR/perf.data" \
  "$ARTIFACT_DIR" \
  --serial "$SERIAL" \
  --first-party-regex "$FIRST_PARTY_REGEX"
```

Do not derive `SKILL_DIR` from the target app repo's `pwd`; installed plugins usually live outside the app being profiled. Keep `FIRST_PARTY_REGEX` scoped to the app's package or app-owned module prefixes; avoid broad framework patterns such as `kotlin`, `Compose`, or `androidx.compose` when reporting app-owned rows.

The helper writes:

- `$ARTIFACT_DIR/simpleperf-self.txt`
- `$ARTIFACT_DIR/simpleperf-children.txt`
- `$ARTIFACT_DIR/simpleperf.csv` when supported by the installed Simpleperf

If host Simpleperf is not installed, the helper searches Android Studio and Android SDK/NDK locations. If unavailable, it falls back to device-side `adb shell simpleperf report` when the device still has `/data/local/tmp/perf.data`.

## Reading Simpleperf

Simpleperf reports sampled CPU execution. It does not directly measure suspended coroutines, network latency, lock wait time, or other wall-clock waits. If a flow feels slow but Simpleperf shows little app CPU, capture Perfetto to inspect scheduler gaps, binder work, locks, frame timing, and app trace sections.

Read reports this way:

- **Self/Overhead**: samples where the function itself was executing. Use this for hot leaf work such as parsing, formatting, diffing, sorting, allocation-heavy iteration, or JSON/protobuf processing.
- **Children/inclusive**: samples in the function and its callees. Use this for expensive entry points such as repositories, use cases, view models, Composables, startup initializers, or feature coordinators.
- **Shared Object / Symbol**: prefer app-owned package frames, feature modules, domain/data/UI modules, and generated app code. Treat Android framework, Kotlin runtime, Compose, and native/runtime frames as context unless the app-owned caller is visible.
- **Percentages**: useful for ranking functions inside one capture. For user-facing timing claims, pair with Perfetto, `gfxinfo`, or repeated wall-clock measurements.

When interpreting a hotspot, note symbol/function name, self or inclusive percentage, approximate sampled CPU time when available, caller stack or owning source file, flow steps, artifact paths, and whether the capture is single-run or repeated.

## Perfetto / Compose Trace

If the app repo already documents a Perfetto/System Trace command for that project, use it. Otherwise use Perfetto directly. The light command below captures scheduler/frequency/Android atrace categories and app `Trace` sections for `PACKAGE`; it is not a substitute for a full project-specific Perfetto config when you need detailed frame timeline or Compose runtime internals.

```bash
SERIAL="<adb-serial>"
PACKAGE="<app package>"
TRACE_DURATION_SECONDS=30
TRACE_BASENAME="app-flow-$(date +%Y%m%d-%H%M%S).pftrace"
TRACE_DEVICE="/data/misc/perfetto-traces/$TRACE_BASENAME"

PERFETTO_PID="$(adb -s "$SERIAL" shell perfetto \
  --background-wait \
  -o "$TRACE_DEVICE" \
  -t "${TRACE_DURATION_SECONDS}s" \
  --app "$PACKAGE" \
  sched freq idle am wm gfx view binder_driver hal dalvik | tr -d '\r' | tail -n 1)"
printf 'Perfetto PID: %s\n' "$PERFETTO_PID"
```

Run exactly one focused flow before `TRACE_DURATION_SECONDS` expires. To stop early, gracefully terminate the background Perfetto process and give it a moment to flush:

```bash
adb -s "$SERIAL" shell kill -TERM "$PERFETTO_PID" 2>/dev/null || true
adb -s "$SERIAL" shell "
  last_size=-1
  stable_count=0
  i=0
  while [ \$i -lt 30 ]; do
    size=\$(ls -l '$TRACE_DEVICE' 2>/dev/null | awk '{ print \$5 }')
    if [ -n \"\$size\" ] && [ \"\$size\" -gt 0 ] && [ \"\$size\" = \"\$last_size\" ]; then
      stable_count=\$((stable_count + 1))
      [ \$stable_count -ge 2 ] && exit 0
    else
      stable_count=0
    fi
    last_size=\"\${size:-0}\"
    i=\$((i + 1))
    sleep 1
  done
  exit 1
"
```

Prefer letting `TRACE_DURATION_SECONDS` expire instead of stopping early. If the stop command fails because the trace already ended, still wait until the output file exists and its size is stable before pulling. If the direct command is too coarse, use Android Studio System Trace or a project-specific Perfetto config. Only report frame timeline or Compose recomposition details when those tracks/events are actually present in the captured trace; the light command above does not guarantee them.

Pull the exact on-device trace from this run:

```bash
adb -s "$SERIAL" pull "$TRACE_DEVICE" "$ARTIFACT_DIR/$TRACE_BASENAME"
```

In Perfetto, inspect:

- main-thread slices around missed frames or long startup sections
- frame scheduling, frame timeline, and render thread lanes
- Compose runtime tracing sections for recomposition work when enabled
- binder transactions, monitor contention, scheduler gaps, and app log markers

## gfxinfo Framestats

Use this for a quick manual frame snapshot:

```bash
SERIAL="<adb-serial>"
PACKAGE="<app package>"

adb -s "$SERIAL" shell pidof "$PACKAGE"
adb -s "$SERIAL" shell dumpsys window | grep -F "$PACKAGE"
adb -s "$SERIAL" shell dumpsys gfxinfo "$PACKAGE" reset
# Perform the focused flow.
adb -s "$SERIAL" shell dumpsys gfxinfo "$PACKAGE" > "$ARTIFACT_DIR/gfxinfo.txt"
adb -s "$SERIAL" shell dumpsys gfxinfo "$PACKAGE" framestats > "$ARTIFACT_DIR/gfxinfo-framestats.txt"
```

Capture from a stable, responsive screen. If `dumpsys gfxinfo` fails to dump the process, or the device shows an ANR/dialog/splash screen instead of the flow, discard that capture and use Perfetto for root cause.

Read the headline summary first: total frames, janky frames, frame percentiles, slow UI thread, slow draw commands, and frame deadline misses. On emulators, absolute smoothness numbers are noisy; percentile spikes and slow draw/UI counters are still useful for deciding whether to take a Perfetto trace.

## Memory / Leak Artifacts

Use this on an adb target after narrowing the investigation to one flow. Exercise the flow, return to a stable screen, then capture memory artifacts from that state.

For quick Java/native/PSS/object-count snapshots:

```bash
SERIAL="<adb-serial>"
PACKAGE="<app package>"

adb -s "$SERIAL" shell am force-stop "$PACKAGE"
adb -s "$SERIAL" shell monkey -p "$PACKAGE" 1
# Exercise the focused flow, then navigate back to a stable idle screen.
adb -s "$SERIAL" shell dumpsys meminfo "$PACKAGE" > "$ARTIFACT_DIR/meminfo-flow.txt"
```

Read `TOTAL PSS`, Java heap, native heap, graphics, `Views`, `Activities`, binder counts, and object counts. Treat one noisy sample as a lead, not a conclusion.

For retained Kotlin/Java objects, prefer Shark CLI when it is available. It works with Android heap dumps and produces text output the agent can inspect and cite.

```bash
HEAP="/data/local/tmp/app-flow.hprof"
HPROF="$ARTIFACT_DIR/app-flow.hprof"

if ! command -v shark-cli >/dev/null; then
  echo "Install Shark CLI, or analyze the HPROF with Android Studio Profiler / MAT." >&2
fi

adb -s "$SERIAL" shell am dumpheap -g "$PACKAGE" "$HEAP"
adb -s "$SERIAL" pull "$HEAP" "$HPROF"
adb -s "$SERIAL" shell rm -f "$HEAP"

if command -v shark-cli >/dev/null; then
  shark-cli --hprof "$HPROF" analyze | tee "$ARTIFACT_DIR/shark-analysis.txt"
fi
```

Read `shark-analysis.txt` first when it exists. Report suspected leaking objects, retained sizes, and reference chains. Look for retained feature objects, activities, fragments, view models, Compose state holders, repositories, listeners, callbacks, and caches that should have been released after leaving the flow. If Shark CLI is unavailable, still preserve the HPROF path and inspect it with the best available heap analyzer; do not claim leak roots from `meminfo` alone.

For native allocation growth, capture a Perfetto trace with heapprofd enabled. Keep the duration in the config; current Android `perfetto` rejects `-t` together with `--config`.

```bash
TRACE_DEVICE="/data/misc/perfetto-traces/native-alloc.pftrace"

adb -s "$SERIAL" shell perfetto -o "$TRACE_DEVICE" \
  --txt -c - <<EOF
duration_ms: 60000
buffers { size_kb: 262144 fill_policy: RING_BUFFER }
data_sources {
  config {
    name: "android.heapprofd"
    heapprofd_config {
      sampling_interval_bytes: 65536
      shmem_size_bytes: 8388608
      block_client: true
      process_cmdline: "$PACKAGE"
    }
  }
}
EOF

adb -s "$SERIAL" pull "$TRACE_DEVICE" "$ARTIFACT_DIR/native-alloc.pftrace"
```

Analyze the trace with `trace_processor_shell` and save the outputs:

```bash
SKILL_DIR="<absolute path to this loaded skill folder>"
"$SKILL_DIR/scripts/heapprofd_reports.sh" \
  "$ARTIFACT_DIR/native-alloc.pftrace" \
  "$ARTIFACT_DIR"
```

Read `heapprofd-summary.txt`, `heapprofd-top-allocations.txt`, `heapprofd-top-stack.txt`, `heapprofd-health.txt`, and `meminfo` together. Report net native allocation size, top allocating frames/mappings, the expanded stack for the largest callsite, and whether trace stats show heapprofd health issues such as client errors, packet loss, or buffer overruns. Prefer Java heap dumps for retained app objects; heapprofd is for native allocation behavior.

## Report

Report:

- exact flow, device/emulator, Android version, build variant, and run count
- artifact paths for every trace/report used
- top hotspots or frame/jank evidence with percentages, durations, or counts
- whether evidence is CPU samples, frame timeline, frame stats, or memory artifacts
- caveats such as emulator noise, low sample count, cold-start compilation, or missing symbols
- next smallest trace or code change when current evidence is insufficient
