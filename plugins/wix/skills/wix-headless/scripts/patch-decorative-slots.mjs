#!/usr/bin/env node
// Inject Image-Phase-1 decorative URLs into the page shells.
//
// The design-system Composer (index.astro) and the Phase 4 page designers write
// `<div data-decorative-slot="<key>">…</div>` placeholders in src/pages/*.astro. Image Phase 1 returns a slot→URL map
// in its JSON return; the orchestrator pipes that map (as JSON) into this
// script's stdin. This script reads the map + walks src/pages/*.astro,
// then injects an <img> as the first child of each matching slot div —
// pure string substitution, no LLM, no file rewrites.
//
// Usage:
//   echo '{"hero":"https://...","about":"https://..."}' \
//     | node patch-decorative-slots.mjs <scaffold-dir>
//
// <scaffold-dir> is the dir that contains src/pages/. The orchestrator
// passes the scaffold subdir explicitly — no eval-dir vs scaffold-dir
// auto-detection is needed for the URL map (it's on stdin), but src/pages
// is still resolved per-input since the orchestrator may call this from
// either the scaffold subdir or the eval root.
//
// Behavior:
//   - Empty stdin or no slot→URL pairs → exit 0 status="skipped" (themed-
//     blocks mode or Image Phase 1 had no URLs to publish).
//   - src/pages missing at <scaffold-dir> and in any single subdir one
//     level down → exit 2 status="error".
//   - For each `data-decorative-slot="<key>"` in src/pages/*.astro:
//       * Key has no URL in the input map → leave the div alone.
//       * Div already has a non-comment child → skip with a warning.
//       * Otherwise inject <img …> as the first child.
//   - Output JSON summary of patches/skips/warnings to stdout.

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const projectDir = process.argv[2] ?? process.cwd();

let urlMap = {};
if (!process.stdin.isTTY) {
  const raw = readFileSync(0, "utf8").trim();
  if (raw) {
    try {
      urlMap = JSON.parse(raw);
    } catch (e) {
      console.error(JSON.stringify({ status: "error", reason: `stdin is not valid JSON (${e.message})` }));
      process.exit(2);
    }
    if (!urlMap || typeof urlMap !== "object" || Array.isArray(urlMap)) {
      console.error(JSON.stringify({ status: "error", reason: "expected a JSON object mapping slot keys to URLs" }));
      process.exit(2);
    }
  }
}

if (Object.keys(urlMap).length === 0) {
  console.log(JSON.stringify({ status: "skipped", reason: "no slot→URL pairs on stdin (themed-blocks mode or Image Phase 1 produced none)" }));
  process.exit(0);
}

function findPagesDir() {
  const direct = join(projectDir, "src/pages");
  if (existsSync(direct)) return { path: direct, source: "projectDir" };
  const hits = [];
  for (const entry of readdirSync(projectDir, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
    const candidate = join(projectDir, entry.name, "src/pages");
    if (existsSync(candidate)) hits.push(candidate);
  }
  if (hits.length === 1) return { path: hits[0], source: "scaffold-subdir" };
  if (hits.length > 1) return { path: null, source: "ambiguous", hits };
  return { path: null, source: "missing" };
}

const pagesResolved = findPagesDir();
if (!pagesResolved.path) {
  console.error(JSON.stringify({
    status: "error",
    reason: "src/pages not found at <projectDir>/src/pages or in any scaffold subdir; pass the scaffold dir explicitly",
    projectDir,
    pagesSearchedAt: pagesResolved.source === "ambiguous" ? pagesResolved.hits : [join(projectDir, "src/pages")],
  }, null, 2));
  process.exit(2);
}

const pagesDir = pagesResolved.path;

const candidates = [];
const walk = (dir) => {
  if (!existsSync(dir)) return;
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) walk(full);
    else if (stat.isFile() && entry.endsWith(".astro")) candidates.push(full);
  }
};
walk(pagesDir);

const patched = [];
const skipped = [];
const warnings = [];

const SLOT_DIV_REGEX = /(<div[^>]*\bdata-decorative-slot="([^"]+)"[^>]*>)([\s\S]*?)(<\/div>)/g;

for (const file of candidates) {
  const original = readFileSync(file, "utf8");
  let modified = original;
  let fileChanged = false;

  modified = modified.replace(SLOT_DIV_REGEX, (match, openTag, slotKey, inner, closeTag) => {
    const url = urlMap[slotKey];
    if (!url) {
      skipped.push({ file, slot: slotKey, reason: "no URL for this slot in input map" });
      return match;
    }

    const stripped = inner.replace(/<!--[\s\S]*?-->/g, "").trim();

    if (/<img\b/i.test(stripped)) {
      skipped.push({ file, slot: slotKey, reason: "div already contains an <img> tag (idempotent skip)" });
      return match;
    }

    if (stripped.length > 0) {
      warnings.push({ file, slot: slotKey, reason: "div has existing non-image child content; not patching to avoid clobber" });
      return match;
    }

    fileChanged = true;
    const img = `<img src="${url}" alt="" loading="lazy" decoding="async" class="decorative-slot-img" />`;
    patched.push({ file, slot: slotKey });
    return `${openTag}\n      ${img}${inner}${closeTag}`;
  });

  if (fileChanged) {
    writeFileSync(file, modified);
  }
}

const summary = {
  status: warnings.length > 0 ? "partial" : "ok",
  slots: Object.keys(urlMap),
  filesScanned: candidates.length,
  patched,
  skipped,
  warnings,
  pagesFrom: pagesResolved.source,
};
console.log(JSON.stringify(summary, null, 2));
