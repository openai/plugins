#!/usr/bin/env node
/*
 * fit-fonts.cjs — shrink any plan.json caption group whose single line would overflow
 * its box, BEFORE render (Cinematic mode). Kills the "font too big → off-frame → shrink
 * → re-render" overflow round. Estimates rendered width from character count × a
 * per-family advance × the group's font-size, compares to the group's box width (its
 * plane width, else the frame), and only ever SHRINKS to fit. Approximate by design —
 * it prevents gross overflow; check-overflow.cjs remains the exact terminal check.
 *
 *   node fit-fonts.cjs <project-dir>
 */
const path = require("path");
const fs = require("fs");

// rough per-family advance (em per char, caps-ish). Condensed faces are narrow; pixel
// faces wide. Default is conservative. (Estimate only — gate confirms.)
const ADV = {
  anton: 0.44,
  oswald: 0.45,
  teko: 0.4,
  "saira stencil one": 0.46,
  "bebas neue": 0.4,
  "press start 2p": 1.05,
  vt323: 0.52,
  monoton: 0.62,
  "special elite": 0.55,
  "jetbrains mono": 0.6,
  "space mono": 0.6,
  "ibm plex mono": 0.6,
  "source code pro": 0.6,
  "archivo black": 0.62,
  bangers: 0.5,
  "bodoni moda": 0.5,
  "playfair display": 0.52,
  cinzel: 0.62,
  "cormorant garamond": 0.45,
  fredoka: 0.55,
  "baloo 2": 0.55,
  "permanent marker": 0.55,
  caveat: 0.4,
  orbitron: 0.66,
  sora: 0.54,
  "space grotesk": 0.54,
};
const DEFAULT_ADV = 0.56;

const cssVal = (css, prop) => {
  const m = String(css || "").match(new RegExp(prop + "\\s*:\\s*([^;}]+)", "i"));
  return m ? m[1].trim() : null;
};
function familyOf(css) {
  const v = cssVal(css, "font-family");
  if (!v) return "inter";
  return v
    .split(",")[0]
    .trim()
    .replace(/^['"]|['"]$/g, "")
    .toLowerCase();
}
function sizePxOf(css, H) {
  const v = cssVal(css, "font-size");
  if (!v) return null;
  let m;
  if ((m = v.match(/calc\(\s*([\d.]+)\s*\*\s*var\(--h\)\s*\)/i))) return parseFloat(m[1]) * H;
  if ((m = v.match(/([\d.]+)\s*cqh/i))) return (parseFloat(m[1]) / 100) * H;
  if ((m = v.match(/([\d.]+)\s*vh/i))) return (parseFloat(m[1]) / 100) * H;
  if ((m = v.match(/([\d.]+)\s*px/i))) return parseFloat(m[1]);
  return null;
}
function planeWidthPx(plan, plane, W) {
  const p = plan.planes && plan.planes[plane];
  const css = p && (typeof p === "string" ? p : p.css);
  const v = cssVal(css, "width");
  if (!v) return null;
  let m;
  if ((m = v.match(/([\d.]+)\s*%/))) return (parseFloat(m[1]) / 100) * W;
  if ((m = v.match(/([\d.]+)\s*px/))) return parseFloat(m[1]);
  return null;
}
function setFontSize(css, fracOfH) {
  const decl = `font-size: calc(${fracOfH.toFixed(3)} * var(--h))`;
  if (/font-size\s*:/i.test(css || "")) return String(css).replace(/font-size\s*:\s*[^;}]+/i, decl);
  return (css ? css.replace(/\s*$/, "").replace(/;?\s*$/, "; ") : "") + decl + ";";
}

function main() {
  const project = path.resolve(process.argv[2] || "");
  if (!process.argv[2]) {
    console.error("usage: fit-fonts.cjs <project-dir>");
    process.exit(1);
  }
  const planPath = path.join(project, "plan.json");
  let plan;
  try {
    plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
  } catch {
    console.error("[fit-fonts] no plan.json (Cinematic only) — skipping");
    process.exit(0);
  }
  const W = plan.width || 1920,
    H = plan.height || 1080;
  const groups = (plan.groups || []).concat(plan.crown_group ? [plan.crown_group] : []);
  const MARGIN = 0.92; // leave 8% breathing room inside the box
  const HERO_MIN_FRAC = 0.18; // a hero below ~0.18·h isn't "big" — keep it punchy, widen its box instead

  let changed = 0;
  for (const g of groups) {
    const text = (g.words || []).map((w) => w.text).join(" ");
    const nChars = text.replace(/\s/g, "").length + (g.words || []).length * 0.5; // glyphs + ~half-space gaps
    if (nChars < 1) continue;
    const fam = familyOf(g.css);
    let adv = ADV[fam] ?? DEFAULT_ADV;
    if (/text-transform\s*:\s*uppercase/i.test(g.css || "") || text === text.toUpperCase())
      adv *= 1.05;
    const sizePx = sizePxOf(g.css, H);
    if (!sizePx) continue; // no explicit size → template default handles it
    const boxW = (g.plane ? planeWidthPx(plan, g.plane, W) : null) || W;
    const usable = boxW * MARGIN;
    // A WRAPPING group only overflows if a SINGLE word is wider than the box (the rest
    // wraps). A NOWRAP group must fit its whole line. So don't shrink wrapping narration
    // down to one line — only force the whole line for nowrap; else just the longest word.
    const nowrap = /white-space\s*:\s*nowrap/i.test(g.css || "");
    const longestWord = (g.words || []).reduce(
      (m, w) => Math.max(m, String(w.text || "").replace(/\s/g, "").length),
      0,
    );
    const constrainChars = nowrap ? nChars : longestWord;
    if (constrainChars < 1) continue;
    const estW = constrainChars * adv * sizePx;
    if (estW > usable) {
      const newPx = usable / (constrainChars * adv);
      let frac = Math.max(0.02, newPx / H);
      const isHero = g.hero === true || /^(hero|crown)$/i.test(g.plane || "");
      if (isHero && frac < HERO_MIN_FRAC) {
        // The hero must stay BIG. If it won't fit its box while staying punchy, the BOX is
        // too narrow (the hero should span the subject) — keep it at the floor + flag it,
        // rather than silently shrinking the peak into a small word.
        frac = HERO_MIN_FRAC;
        g.css = setFontSize(g.css, frac);
        changed++;
        console.log(
          `[fit-fonts] ⚠ ${g.id || "(group)"} HERO "${text.slice(0, 28)}" won't fit box ${Math.round(usable)}px while staying big → KEPT at floor ${frac}·h. WIDEN the hero plane (it should span the subject, centered), not shrink the peak.`,
        );
        continue;
      }
      g.css = setFontSize(g.css, frac);
      changed++;
      console.log(
        `[fit-fonts] ${g.id || "(group)"}: "${text.slice(0, 28)}" (${nowrap ? "nowrap line" : "longest word"}) est ${Math.round(estW)}px > box ${Math.round(usable)}px → shrink to ${frac.toFixed(3)}·h (${Math.round(newPx)}px)`,
      );
    }
  }
  if (changed) {
    fs.writeFileSync(planPath, JSON.stringify(plan, null, 2));
    console.log(`[fit-fonts] shrank ${changed} group(s) to fit; wrote plan.json`);
  } else console.log("[fit-fonts] all groups fit their box — no change");
}
main();
