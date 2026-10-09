#!/usr/bin/env node
/* check-timing.cjs — verify plan.json word timings vs transcript.json (1:1 port of check-timing.py).
 *   node check-timing.cjs <project-dir> [--strict]
 */
const path = require("path");
const fs = require("fs");

const DRIFT_TOL = 0.08;
const CREATIVE_SUBS = {
  "15%": ["fifteen", "percent"],
  "1/3": ["one", "third"],
  "2x": ["two", "times"],
};
const norm = (s) =>
  String(s)
    .replace(/^[ .,?!"']+|[ .,?!"']+$/g, "")
    .toLowerCase();
const splitPacked = (t) =>
  String(t)
    .split(/<br>|\s+/)
    .filter(Boolean);

function estimateVerticalBand(css, words, fw, fh) {
  const top = css.match(/top:\s*(-?[\d.]+)%/);
  if (!top) return null;
  const topPct = parseFloat(top[1]);
  const sizeM = css.match(/font-size:\s*calc\(\s*([\d.]+)\s*\*\s*var\(--h\)\s*\)/);
  const fontPx = sizeM ? parseFloat(sizeM[1]) * fh : 0.05 * fh;
  const lhM = css.match(/line-height:\s*([\d.]+)/);
  const lh = lhM ? parseFloat(lhM[1]) : 1.1;
  const charW = /uppercase/i.test(css) ? 0.72 : 0.6;
  let lineCount = 1,
    cur = 0;
  const spaceW = fontPx * 0.3;
  for (const w of words) {
    const parts = String(w.text).split(/<br>/);
    parts.forEach((part, i) => {
      const pw = part.length * fontPx * charW;
      if (i > 0) {
        lineCount++;
        cur = pw;
      } else {
        const test = cur + (cur > 0 ? spaceW : 0) + pw;
        if (test > fw && cur > 0) {
          lineCount++;
          cur = pw;
        } else cur = test;
      }
    });
  }
  return [topPct, topPct + (100 * (lineCount * fontPx * lh)) / fh];
}

function check(project, strict) {
  const plan = JSON.parse(fs.readFileSync(path.join(project, "plan.json"), "utf8"));
  const t = JSON.parse(fs.readFileSync(path.join(project, "transcript.json"), "utf8"));
  const seq = (t.words || [])
    .filter((w) => w.type === "word")
    .map((w) => [norm(w.text), w.start, w.end]);
  const issues = [];
  const fw = plan.width || 720,
    fh = plan.height || 1290;
  const groups = plan.groups || [];
  const bands = groups.map((g) =>
    g.plane
      ? [g.id || "?", g.in, g.out, null, true]
      : [
          g.id || "?",
          g.in,
          g.out,
          estimateVerticalBand(g.css || "", g.words || [], fw, fh),
          g.allow_overlap || false,
        ],
  );
  for (let i = 0; i < bands.length; i++) {
    const [gi, ai, bi, bbi, oki] = bands[i];
    if (!bbi) continue;
    for (let j = i + 1; j < bands.length; j++) {
      const [gj, aj, bj, bbj, okj] = bands[j];
      if (!bbj || oki || okj) continue;
      if (Math.min(bi, bj) - Math.max(ai, aj) <= 0.05) continue;
      if (Math.min(bbi[1], bbj[1]) - Math.max(bbi[0], bbj[0]) > 2.0)
        issues.push(
          `[${gi}↔${gj}] groups overlap in time (${Math.max(ai, aj).toFixed(2)}–${Math.min(bi, bj).toFixed(2)}s) AND vertically (band ${Math.max(bbi[0], bbj[0]).toFixed(0)}%–${Math.min(bbi[1], bbj[1]).toFixed(0)}%) — reposition one or add "allow_overlap": true if deliberate.`,
        );
    }
  }
  let ti = 0;
  for (const g of groups) {
    const gid = g.id || "?",
      gin = g.in,
      gout = g.out;
    const ws = (g.words || []).map((w) => w.start),
      we = (g.words || []).map((w) => w.end);
    if (ws.length && gin != null) {
      const e = Math.min(...ws);
      if (e < gin - 0.01)
        issues.push(
          `[${gid}] group.in=${gin.toFixed(2)} but earliest word starts at ${e.toFixed(2)} — word delayed by ${(gin - e >= 0 ? "+" : "") + (gin - e).toFixed(2)}s. Lower group.in.`,
        );
    }
    if (we.length && gout != null) {
      const l = Math.max(...we);
      if (l > gout + 0.01)
        issues.push(
          `[${gid}] group.out=${gout.toFixed(2)} but latest word ends at ${l.toFixed(2)} — word clipped. Raise group.out.`,
        );
    }
    for (const w of g.words || []) {
      // Exact pairing: a compiler that KNOWS the transcript index emits `ti` —
      // duplicate words then pair by POSITION, not text-search (which grabs the
      // first occurrence and reports a phantom drift). Sanity-check the text; on
      // mismatch fall back to the text matcher below.
      if (
        Number.isInteger(w.ti) &&
        seq[w.ti] &&
        seq[w.ti][0] === norm(splitPacked(w.text)[0] || "")
      ) {
        const drift = w.start - seq[w.ti][1];
        if (Math.abs(drift) > DRIFT_TOL)
          issues.push(
            `[${gid}] '${norm(w.text)}': plan=${w.start.toFixed(3)} transcript=${seq[w.ti][1].toFixed(3)} drift ${(drift >= 0 ? "+" : "") + drift.toFixed(3)}s`,
          );
        ti = w.ti + 1;
        continue;
      }
      const parts = splitPacked(w.text).map(norm);
      parts.forEach((part, pi) => {
        if (!part) return;
        if (part in CREATIVE_SUBS) {
          for (const sub of CREATIVE_SUBS[part]) {
            const j = seq.findIndex((s, k) => k >= ti && s[0] === sub);
            if (j >= 0) ti = j + 1;
          }
          return;
        }
        let found = seq.findIndex((s, k) => k >= ti && s[0] === part);
        if (found < 0) found = seq.findIndex((s) => s[0] === part);
        if (found < 0) {
          issues.push(`[${gid}] '${part}': NOT IN TRANSCRIPT (plan start=${w.start.toFixed(3)})`);
          return;
        }
        const ts = seq[found][1];
        ti = found + 1;
        if (pi === 0) {
          const drift = w.start - ts;
          if (Math.abs(drift) > DRIFT_TOL)
            issues.push(
              `[${gid}] '${part}': plan=${w.start.toFixed(3)} transcript=${ts.toFixed(3)} drift ${(drift >= 0 ? "+" : "") + drift.toFixed(3)}s`,
            );
        } else
          issues.push(
            `[${gid}] '${part}' packed with '${parts[0]}': transcript=${ts.toFixed(3)} but entry has no distinct timing — split into separate word entries`,
          );
      });
    }
  }
  const name = path.basename(project);
  if (!issues.length) {
    console.log(`${name}: timing OK ✓ (${seq.length} transcript words)`);
    return 0;
  }
  console.log(`${name}: ${issues.length} timing issue(s):`);
  for (const i of issues) console.log(`  ${i}`);
  return strict ? 1 : 0;
}

const args = process.argv.slice(2).filter((a) => a !== "--strict");
if (!args.length) {
  console.error("usage: check-timing.cjs <project-dir> [--strict]");
  process.exit(2);
}
process.exit(check(path.resolve(args[0]), process.argv.includes("--strict")));
