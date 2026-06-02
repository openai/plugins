#!/usr/bin/env node
// Post-phase manifest check + template-copy recovery.
//
// Verifies that every file declared in each loaded pack's `creates:` array
// for the named phase exists on disk. If a file is missing, attempts to
// recover by copying the canonical template from <SKILL_ROOT>/references/astro/templates/<pack>/.
// Outputs a JSON summary of present / recovered / errored files.
//
// Usage (both modes work):
//   node <SKILL_ROOT>/scripts/check-manifest.mjs <project-dir> <phase> <packs-csv>
//   curl -s https://dev.wix.com/skills/wix-headless/scripts/check-manifest.mjs \
//     | node --input-type=module - <project-dir> <phase> <packs-csv>
//
//   <phase> ∈ { "components", "pages" }
//   <packs-csv> = comma-separated pack names (loaded verticals), e.g. "stores,ecom,cms"
//
// Note: `node <(curl ...)` does NOT work for .mjs files — Node sees /dev/fd/N
// with no extension and rejects ESM syntax. Use the stdin form above.
//
// Skill-local file reads (vertical pack markdowns, template files) auto-detect
// whether they can resolve on disk (tgz install) and fall back to HTTP fetch
// otherwise (stream via stdin).
//
// Behavior:
//   - For each pack, parses `references/verticals/<pack>.md` to extract the
//     `creates:` array.
//   - For each `creates:` entry where phase matches:
//       * If file exists in the project → "present"
//       * If missing AND a template exists at `references/astro/templates/<pack>/<tail>`
//         (where <tail> is the path under src/pages/ for page files, or the
//         basename for everything else) → copy/fetch it; record as "recovered".
//       * Otherwise → record as "missing" with a remediation hint.
//   - Exit 0 on happy path or recoverable misses.
//   - Exit 1 if any file is unrecoverably missing.

import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync } from "node:fs";
import { join, dirname, basename, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SKILL_URL = "https://dev.wix.com/skills/wix-headless";

// Mode detection: prefer on-disk skill root if reachable, else use HTTP.
// When invoked as `node <(curl ...)`, import.meta.url is `file:///dev/fd/N`
// and the candidate root won't contain `references/verticals` — so we fall
// through to URL mode automatically.
let SKILL_ROOT_DISK = null;
try {
  const scriptDir = dirname(fileURLToPath(import.meta.url));
  const candidate = resolve(scriptDir, "..");
  if (existsSync(join(candidate, "references/verticals"))) {
    SKILL_ROOT_DISK = candidate;
  }
} catch {
  // fileURLToPath may fail on non-file URLs; fall through to URL mode.
}

// Read a skill-local file (relative path like "references/verticals/stores.md").
// Returns null when the file doesn't exist.
async function readSkillText(relPath) {
  if (SKILL_ROOT_DISK) {
    const p = join(SKILL_ROOT_DISK, relPath);
    if (!existsSync(p)) return null;
    return readFileSync(p, "utf8");
  }
  const url = `${SKILL_URL}/${relPath}`;
  const r = await fetch(url);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`fetch ${url}: HTTP ${r.status}`);
  return await r.text();
}

// Copy a skill-local file at relPath into destPath (in the user's project).
// Returns true on success, false if the source doesn't exist.
async function copySkillFile(relPath, destPath) {
  if (SKILL_ROOT_DISK) {
    const src = join(SKILL_ROOT_DISK, relPath);
    if (!existsSync(src)) return false;
    mkdirSync(dirname(destPath), { recursive: true });
    copyFileSync(src, destPath);
    return true;
  }
  const text = await readSkillText(relPath);
  if (text === null) return false;
  mkdirSync(dirname(destPath), { recursive: true });
  writeFileSync(destPath, text);
  return true;
}

const [, , projectDir, phase, packsCsv] = process.argv;

if (!projectDir || !phase || !packsCsv) {
  console.error("usage: check-manifest.mjs <project-dir> <phase> <packs-csv>");
  process.exit(2);
}

if (phase !== "components" && phase !== "pages") {
  console.error(`check-manifest: invalid phase "${phase}" — must be "components" or "pages"`);
  process.exit(2);
}

const packs = packsCsv.split(",").map((p) => p.trim()).filter(Boolean);

// Map a `creates:` file path to its template path (relative to skill root).
// Heuristic: `src/pages/<X>` preserves <X> under references/astro/templates/<pack>/;
// everything else uses basename only.
function templateRelPath(packName, srcPath) {
  const pagesMatch = srcPath.match(/^src\/pages\/(.+)$/);
  const tail = pagesMatch ? pagesMatch[1] : basename(srcPath);
  return `references/astro/templates/${packName}/${tail}`;
}

// Parse `creates:` block from a vertical pack's markdown frontmatter.
// Format (one per line):
//   - { file: src/utils/back-in-stock.ts,          phase: components }
function parseCreates(text) {
  const lines = text.split("\n");
  const entries = [];
  let inCreates = false;
  for (const line of lines) {
    if (/^creates:\s*$/.test(line)) {
      inCreates = true;
      continue;
    }
    if (inCreates) {
      // Block ends at a non-indented, non-blank line that doesn't start with `-`.
      if (/^[^\s-]/.test(line)) {
        inCreates = false;
        continue;
      }
      const m = line.match(/^\s*-\s*\{\s*file:\s*([^,]+?),\s*phase:\s*([\w-]+)\s*\}/);
      if (m) entries.push({ file: m[1].trim(), phase: m[2].trim() });
    }
  }
  return entries;
}

const present = [];
const recovered = [];
const missing = [];

for (const pack of packs) {
  const verticalRel = `references/verticals/${pack}.md`;
  const text = await readSkillText(verticalRel);
  if (text === null) {
    missing.push({
      pack,
      path: null,
      code: "PACK_NOT_FOUND",
      remediation: `vertical pack file not found at ${verticalRel} — pack "${pack}" may not be a valid loaded vertical`,
    });
    continue;
  }

  const entries = parseCreates(text).filter((e) => e.phase === phase);

  for (const { file } of entries) {
    const destPath = join(projectDir, file);
    if (existsSync(destPath)) {
      present.push({ pack, path: file });
      continue;
    }

    const templateRel = templateRelPath(pack, file);
    const ok = await copySkillFile(templateRel, destPath);
    if (ok) {
      recovered.push({
        pack,
        path: file,
        source: "template-copy",
        template: templateRel,
      });
      continue;
    }

    missing.push({
      pack,
      path: file,
      code: "PHASE_FILE_MISSING",
      remediation: `the ${pack} agent did not write this file and the pack ships no template at ${templateRel}. Re-dispatch the ${phase} scope, or report the gap to the pack maintainer.`,
    });
  }
}

const summary = {
  phase,
  packs,
  counts: {
    present: present.length,
    recovered: recovered.length,
    missing: missing.length,
  },
  present,
  recovered,
  missing,
};
console.log(JSON.stringify(summary, null, 2));

process.exit(missing.length > 0 ? 1 : 0);
