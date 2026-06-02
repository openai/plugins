#!/usr/bin/env node
// Finalize and write .wix/run.json at the end of the build.
//
// The orchestrator collects agent returns, timings, and outcome data over the
// run. This script takes the orchestrator's draft as a JSON blob via stdin,
// runs the timing-completeness gate (every required phase MUST have non-null
// seconds, otherwise emit MISSING_TIMING errors), computes totalSeconds from
// started/ended, writes the canonical .wix/run.json, and prints the perf
// one-liner the orchestrator shows in the final message.
//
// Usage:
//   echo "$DRAFT_JSON" | node finalize-run-json.mjs <project-dir>
//
// Input shape (via stdin):
//   {
//     "run":   { started, ended, brand, prompt, verticals, packs },
//     "outcome": { build, previewUrl, dashboardUrl, ... },
//     "phases":  [ { phase, status, seconds, data?, errors? }, ... ],
//     "recoveries": [ ... ],   // optional; from manifest-check script outputs
//     "errors":     [ ... ],   // optional; from agent returns / orchestrator
//     "notes":      [ ... ],   // optional
//     "requiredPhases": ["scaffold","app-install-Wix Stores","env-pull",...]
//   }
//
// `requiredPhases` is the orchestrator's set of skill-invoked phases that MUST
// have a captured duration (scaffold, every app-install-*, env-pull,
// seed-utilities, npm-install, build, release|preview, etc.). The set is
// run-specific (number of app-install-* depends on loaded packs), so the
// orchestrator passes it in rather than the script guessing.
//
// Output:
//   - Writes .wix/run.json (full shape, with timing-completeness gate applied).
//   - Prints to stdout: a JSON object with { perfLine, missingTiming, totalSeconds }.

import { writeFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const projectDir = process.argv[2];

if (!projectDir) {
  console.error("usage: cat draft.json | finalize-run-json.mjs <project-dir>");
  process.exit(2);
}

let draft;
try {
  draft = JSON.parse(readFileSync(0, "utf8"));
} catch (e) {
  console.error(`finalize-run-json: stdin is not valid JSON (${e.message})`);
  process.exit(2);
}

const run = draft.run ?? {};
const phases = Array.isArray(draft.phases) ? [...draft.phases] : [];
const errors = Array.isArray(draft.errors) ? [...draft.errors] : [];
const recoveries = Array.isArray(draft.recoveries) ? draft.recoveries : [];
const notes = Array.isArray(draft.notes) ? draft.notes : [];
const outcome = draft.outcome ?? {};
const requiredPhases = Array.isArray(draft.requiredPhases) ? draft.requiredPhases : [];

// ---- 1. Timing completeness gate ------------------------------------------
const phasesByName = new Map();
for (const p of phases) {
  phasesByName.set(p.phase, p);
}

const missingTiming = [];

for (const required of requiredPhases) {
  const existing = phasesByName.get(required);
  if (!existing) {
    // Missing entry entirely.
    const entry = { phase: required, status: "unknown", seconds: null };
    phases.push(entry);
    phasesByName.set(required, entry);
    errors.push({ code: "MISSING_TIMING", phase: required });
    missingTiming.push(required);
  } else if (existing.seconds === null || existing.seconds === undefined) {
    existing.seconds = null;
    if (!errors.some((e) => e.code === "MISSING_TIMING" && e.phase === required)) {
      errors.push({ code: "MISSING_TIMING", phase: required });
    }
    missingTiming.push(required);
  }
}

// ---- 2. totalSeconds derivation -------------------------------------------
if (!run.totalSeconds && run.started && run.ended) {
  const started = Date.parse(run.started);
  const ended = Date.parse(run.ended);
  if (!Number.isNaN(started) && !Number.isNaN(ended) && ended >= started) {
    run.totalSeconds = Math.round((ended - started) / 1000);
  }
}

// ---- 3. Compose final shape -----------------------------------------------
const final = {
  version: "1.0",
  run,
  outcome,
  phases,
  ...(recoveries.length > 0 ? { recoveries } : {}),
  ...(errors.length > 0 ? { errors } : {}),
  ...(notes.length > 0 ? { notes } : { notes: [] }),
};

const wixDir = join(projectDir, ".wix");
mkdirSync(wixDir, { recursive: true });
const runJsonPath = join(wixDir, "run.json");
writeFileSync(runJsonPath, JSON.stringify(final, null, 2) + "\n");

// ---- 4. Perf one-liner ----------------------------------------------------
// Format: "Built in <Nm Ss> — design-system <n>s · images (phase 1 + phase 2) <n>s · build+release <n>s"
const fmtSeconds = (sec) => (sec === null || sec === undefined ? "–" : `${sec}s`);
const fmtTotal = (sec) => {
  if (sec === null || sec === undefined) return "–";
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s}s`;
};
const phaseSeconds = (name) => {
  const p = phasesByName.get(name);
  return p && p.seconds !== null && p.seconds !== undefined ? p.seconds : null;
};
const designSystem = phaseSeconds("design-system");
const img1 = phaseSeconds("image-phase-1-decorative");
const img2 = phaseSeconds("image-phase-2-entity");
const imgTotal = img1 !== null && img2 !== null ? img1 + img2 : null;
const build = phaseSeconds("build");
const release = phaseSeconds("release") ?? phaseSeconds("preview");
const buildPlusRelease = build !== null && release !== null ? build + release : null;

const perfLine = `Built in ${fmtTotal(run.totalSeconds)} — design-system ${fmtSeconds(designSystem)} · images (phase 1 + phase 2) ${fmtSeconds(imgTotal)} · build+release ${fmtSeconds(buildPlusRelease)}`;

console.log(JSON.stringify({
  status: missingTiming.length > 0 ? "partial" : "ok",
  path: runJsonPath,
  totalSeconds: run.totalSeconds ?? null,
  missingTiming,
  perfLine,
}, null, 2));
