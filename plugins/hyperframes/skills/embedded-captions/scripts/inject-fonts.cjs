#!/usr/bin/env node
/*
 * inject-fonts.cjs — inline the @font-face blocks each HTML actually uses.
 *
 *   node inject-fonts.cjs <project-dir> [file.html ...]
 *
 * hyperframes' renderer only auto-supplies its ~18 CANONICAL_FONTS. Every other
 * family (Anton, Bangers, VT323, Press Start 2P, …) falls back to a generic font
 * unless the HTML ships a local @font-face — even when it "looks fine" locally,
 * because that only works when the font happens to be installed as a system font.
 * On a clean/offline/CI machine it silently degrades. (hyperframes' own font
 * linter flags exactly this: font_family_without_font_face.)
 *
 * This step reads the bundled font library (modes/standard/fonts/fonts.css —
 * base64 woff2, no sub-resources), finds which of those families the HTML uses,
 * and inlines just those @font-face blocks into a <style id="hf-embedded-fonts">.
 * Idempotent (re-running replaces the block). Families already declared in the
 * HTML, hyperframes-canonical families, and CSS generics are left untouched.
 *
 * Runs BEFORE the layout gates + render so measure-layout and the capture both
 * see the real glyph metrics, never a fallback.
 */
const fs = require("fs");
const path = require("path");

const SKILL_ROOT = path.resolve(__dirname, "..");
const FONTS_CSS = path.join(SKILL_ROOT, "modes", "standard", "fonts", "fonts.css");
const MARKER = "hf-embedded-fonts";

const GENERIC = new Set([
  "serif",
  "sans-serif",
  "monospace",
  "cursive",
  "fantasy",
  "system-ui",
  "ui-serif",
  "ui-sans-serif",
  "ui-monospace",
  "ui-rounded",
  "math",
  "emoji",
  "fangsong",
  "inherit",
  "initial",
  "unset",
  "revert",
  "revert-layer",
]);

// Parse fonts.css → Map<lowercased family, [ @font-face block strings ]>.
function loadFontLibrary() {
  let css;
  try {
    css = fs.readFileSync(FONTS_CSS, "utf8");
  } catch {
    console.error(
      `[inject-fonts] missing ${FONTS_CSS} — run modes/standard/fonts/build-fonts-css.cjs`,
    );
    process.exit(2);
  }
  const lib = new Map();
  // base64 data-URIs contain no "}", so [^}]* safely bounds a block.
  const blockRe = /@font-face\s*\{[^}]*\}/gi;
  const famRe = /font-family\s*:\s*(['"]?)([^;'"]+)\1/i;
  let m;
  while ((m = blockRe.exec(css)) !== null) {
    const fam = m[0].match(famRe);
    if (!fam) continue;
    const key = fam[2].trim().toLowerCase();
    if (!lib.has(key)) lib.set(key, []);
    lib.get(key).push(m[0]);
  }
  return lib;
}

// Families referenced anywhere in the HTML: CSS `font-family:` (in <style> or
// inline style="") and the data-font-family attribute hyperframes also honors.
function usedFamilies(html) {
  const out = new Set();
  const add = (stack) => {
    for (const part of String(stack).split(",")) {
      const name = part
        .trim()
        .replace(/^['"]|['"]$/g, "")
        .trim()
        .toLowerCase();
      if (name && !GENERIC.has(name) && !/^var\(/.test(name)) out.add(name);
    }
  };
  // strip existing @font-face so we don't re-list the family it declares
  const body = html.replace(/@font-face\s*\{[^}]*\}/gi, "");
  for (const mm of body.matchAll(/font-family\s*:\s*([^;}{]+)/gi)) add(mm[1]);
  for (const mm of html.matchAll(/data-font-family\s*=\s*["']([^"']+)["']/gi)) add(mm[1]);
  return out;
}

// Families the HTML ALREADY declares via @font-face — leave those alone.
function declaredFamilies(html) {
  const out = new Set();
  const famRe = /font-family\s*:\s*(['"]?)([^;'"]+)\1/i;
  for (const mm of html.matchAll(/@font-face\s*\{[^}]*\}/gi)) {
    const f = mm[0].match(famRe);
    if (f) out.add(f[2].trim().toLowerCase());
  }
  return out;
}

function injectInto(file, lib) {
  let html;
  try {
    html = fs.readFileSync(file, "utf8");
  } catch {
    return null;
  }
  // drop any previous injection so this is idempotent
  html = html.replace(new RegExp(`\\s*<style id="${MARKER}">[\\s\\S]*?</style>`, "i"), "");

  const used = usedFamilies(html);
  const already = declaredFamilies(html);
  const blocks = [];
  const inlined = [];
  for (const fam of used) {
    if (already.has(fam)) continue;
    const lb = lib.get(fam);
    if (!lb) continue; // canonical / system / unknown — not ours to supply
    blocks.push(...lb);
    inlined.push(fam);
  }
  if (!blocks.length) {
    fs.writeFileSync(file, html);
    return { file: path.basename(file), inlined: [] };
  }
  const style = `<style id="${MARKER}">\n/* auto-embedded by inject-fonts.cjs — deterministic template fonts */\n${blocks.join("\n")}\n</style>`;
  // Prefer right after <head...>; fall back to before </head>, then <html>, then prepend.
  if (/<head[^>]*>/i.test(html)) html = html.replace(/<head[^>]*>/i, (m0) => `${m0}\n${style}`);
  else if (/<\/head>/i.test(html)) html = html.replace(/<\/head>/i, `${style}\n</head>`);
  else if (/<html[^>]*>/i.test(html))
    html = html.replace(/<html[^>]*>/i, (m0) => `${m0}\n${style}`);
  else html = style + "\n" + html;

  fs.writeFileSync(file, html);
  return { file: path.basename(file), inlined };
}

function main() {
  const project = path.resolve(process.argv[2] || "");
  if (!process.argv[2]) {
    console.error("usage: inject-fonts.cjs <project-dir> [file.html ...]");
    process.exit(1);
  }
  const lib = loadFontLibrary();
  let files = process.argv.slice(3);
  if (!files.length) files = ["index.html", "rail.html", "index_fg.html"];
  files = files.map((f) => (path.isAbsolute(f) ? f : path.join(project, f)));

  let touched = 0;
  for (const f of files) {
    const r = injectInto(f, lib);
    if (r == null) continue;
    if (r.inlined.length) {
      console.log(`[inject-fonts] ${r.file}: embedded ${r.inlined.join(", ")}`);
      touched++;
    } else console.log(`[inject-fonts] ${r.file}: no non-canonical fonts to embed`);
  }
  if (!touched)
    console.log(`[inject-fonts] nothing embedded (all fonts canonical/system or already declared)`);
}
main();
