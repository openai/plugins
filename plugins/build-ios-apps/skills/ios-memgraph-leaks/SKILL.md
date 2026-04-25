---
name: ios-memgraph-leaks
description: Capture, inspect, compare, and root-cause iOS memory graph leaks using Apple's leaks and memgraph tools. Use when debugging leaked iOS objects, simulator memgraphs, retain-cycle suspicions, memory growth after navigation/logout/account changes, or when asked to prove an iOS leak fix with before/after memgraph evidence.
---

# iOS Memgraph Leaks

Use this skill to prove iOS leaks from a live simulator process or an existing `.memgraph`. Pair it with `../ios-debugger-agent/SKILL.md` when the task also needs simulator build, install, launch, UI driving, logs, or screenshots.

## Core Workflow

1. Build, launch, and drive the exact flow that should release objects.
2. Capture a memgraph from the running simulator process with `scripts/capture_sim_memgraph.sh`.
3. Summarize leaks with `scripts/summarize_memgraph_leaks.py`.
4. For each app-owned leaked type, inspect ownership with `leaks --traceTree=<address> <file.memgraph>` and grouped leak evidence.
5. Make the smallest root-cause patch, then recapture the same flow on the same simulator when possible.
6. Report proof: before/after leak counts, disappeared root types, remaining leaks, memgraph paths, and test/build results.

Do not claim a leak fix from a smaller memgraph alone. A credible fix explains the ownership path that kept the object alive and shows that the same path or type disappears after the patch.

## Capture

Prefer capturing from the simulator already used for the reproduction. Resolve the simulator UDID and app bundle identifier, then capture the running app:

```bash
SKILL_DIR="<absolute path to this loaded skill folder>"
SIM="<simulator-udid>"
BUNDLE_ID="<app.bundle.identifier>"
MEMGRAPH_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-ios-memgraph.XXXXXX")"

"$SKILL_DIR/scripts/capture_sim_memgraph.sh" \
  --udid "$SIM" \
  --bundle-id "$BUNDLE_ID" \
  --out-dir "$MEMGRAPH_DIR"
```

Do not derive `SKILL_DIR` from the target app repo's `pwd`; installed plugins usually live outside the app being debugged. Store captures in a run-specific temp or user-chosen folder, not under `SKILL_DIR`.

If the process cannot be found, confirm the bundle identifier and use `xcrun simctl spawn "$SIM" launchctl list` to inspect running labels.

## Summarize

Summarize an existing memgraph:

```bash
"$SKILL_DIR/scripts/summarize_memgraph_leaks.py" \
  /path/to/app.memgraph \
  --trace-limit 5 \
  --out /path/to/leak-summary.md
```

Use `--trace-limit` sparingly. Trace trees are useful root-cause evidence, but large memgraphs can produce noisy output. If a trace tree says `Found 0 roots referencing`, treat it as an unreachable/self-retained leak candidate and use the summary's grouped leak tree or `leaks --groupByType <file.memgraph>` to identify the retained fields and payload chain.

## Root Cause Rules

- Identify the first app-owned leaked type in the leak output or trace.
- Determine the intended lifetime: process, session, account, view, request, or task.
- Treat lazy or deferred allocation as a scope reduction, not a leak fix, unless the original eager allocation itself violated the intended lifetime.
- Prove retain-cycle claims with either a `traceTree` ownership path or an isolated reproduction.
- For unreachable/self-cycle leaks, `traceTree` may have no root path; use `leaks --groupByType` plus source verification to find the self-retaining edge.
- Do not claim success just because total leak count went down; prove the specific type or path disappeared.
- Separate real root-cause branches from candidate/noise branches.
- Prefer deleting the retaining edge over adding broad cleanup code.

## Report

A useful leak report includes:

- the exact flow and simulator/app build
- the memgraph and summary paths
- app-owned leaked types and counts
- at least one ownership path, or grouped leak tree evidence when the object is unreachable from roots
- the smallest proposed or applied retaining-edge fix
- before/after evidence when a fix was made

If the memgraph shows only framework/runtime noise, say that and recommend the next narrower capture rather than inventing an app leak.
