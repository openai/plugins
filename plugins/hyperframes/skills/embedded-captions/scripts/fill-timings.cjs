#!/usr/bin/env node
/*
 * fill-timings.cjs — fill plan.json group/word times DIRECTLY from transcript.json,
 * by SEQUENCE (Cinematic mode). Kills the timing-drift + duplicate-word class of
 * occlusion/timing-gate re-tries: the agent only decides the GROUPING (which words form
 * each group, in spoken order); times come from the transcript by position, so the
 * second "and"/"actions" matches the right occurrence (text-matching pairs the wrong one).
 *
 *   node fill-timings.cjs <project-dir>
 *
 * Reads  <project>/plan.json (groups[].words[].text, in spoken order) + transcript.json.
 * Writes <project>/plan.json with each word's start/end and each group's in/out filled.
 * A group word that can't be matched keeps whatever time it had + is reported (so a typo
 * or an added word degrades gracefully instead of silently mis-timing).
 */
const path = require("path");
const fs = require("fs");

const norm = (s) =>
  String(s == null ? "" : s)
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");
const LOOKAHEAD = 40; // how far past the pointer to search for a group word (skips dropped fillers)

function fillGroup(g, tw, state) {
  const matched = [];
  const unmatched = [];
  for (const w of g.words || []) {
    const target = norm(w.text);
    if (!target) {
      unmatched.push(w.text);
      continue;
    }
    let found = -1;
    for (let j = state.p; j < Math.min(tw.length, state.p + LOOKAHEAD); j++) {
      if (norm(tw[j].text) === target) {
        found = j;
        break;
      }
    }
    if (found >= 0) {
      w.start = tw[found].start;
      w.end = tw[found].end;
      matched.push(w);
      state.p = found + 1;
    } else {
      unmatched.push(w.text);
    }
  }
  if (matched.length) {
    const firstStart = +matched[0].start.toFixed(3);
    const lastEnd = +matched[matched.length - 1].end.toFixed(3);
    // WORD start/end are filled above (deterministic). For the group's DISPLAY window we
    // only GUARANTEE it brackets the words (never clip a word) — we do NOT tighten it:
    // a deliberately later `out` is the apex HOLD / sentence ACCUMULATION the author set,
    // and an earlier `in` is a pre-entry. Preserve both; clamp only if they'd clip.
    g.in = g.in == null ? firstStart : Math.min(g.in, firstStart);
    g.out = g.out == null ? lastEnd : Math.max(g.out, lastEnd);
  }
  return { matched: matched.length, unmatched };
}

function main() {
  const project = path.resolve(process.argv[2] || "");
  if (!process.argv[2]) {
    console.error("usage: fill-timings.cjs <project-dir>");
    process.exit(1);
  }
  const planPath = path.join(project, "plan.json");
  const trPath = path.join(project, "transcript.json");
  let plan, trWordsRaw;
  try {
    plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
  } catch {
    console.error(`[fill-timings] no plan.json (Cinematic only) — skipping`);
    process.exit(0);
  }
  try {
    trWordsRaw = JSON.parse(fs.readFileSync(trPath, "utf8")).words || [];
  } catch {
    console.error(`[fill-timings] no transcript.json — skipping`);
    process.exit(0);
  }
  const tw = trWordsRaw.filter((w) => w && "start" in w && "end" in w);
  if (!tw.length) {
    console.error(`[fill-timings] transcript has no word timings — skipping`);
    process.exit(0);
  }

  const state = { p: 0 };
  let totalMatched = 0,
    totalUnmatched = 0;
  const groups = plan.groups || [];
  // crown_group (if any) is spoken last in the standard templates; process groups in order, crown after.
  const ordered = [...groups];
  for (const g of ordered) {
    const r = fillGroup(g, tw, state);
    totalMatched += r.matched;
    totalUnmatched += r.unmatched.length;
    if (r.unmatched.length)
      console.error(
        `[fill-timings] ⚠ ${g.id || "(group)"}: ${r.unmatched.length} word(s) not found in transcript from here: ${r.unmatched.join(" ")}`,
      );
  }
  if (plan.crown_group) {
    const r = fillGroup(plan.crown_group, tw, state);
    totalMatched += r.matched;
    totalUnmatched += r.unmatched.length;
    if (r.unmatched.length)
      console.error(`[fill-timings] ⚠ crown_group: ${r.unmatched.join(" ")} not found`);
  }

  fs.writeFileSync(planPath, JSON.stringify(plan, null, 2));
  console.log(
    `[fill-timings] filled ${totalMatched} word time(s) from transcript by sequence` +
      (totalUnmatched
        ? `; ${totalUnmatched} unmatched (kept prior time — check those words)`
        : `; all matched ✓`),
  );
  console.log(
    `[fill-timings] group windows now: ${ordered.map((g) => `${g.id || "?"}[${g.in}-${g.out}]`).join(" ")}`,
  );
}
main();
