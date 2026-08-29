/*
 * lib-dna.cjs — DNA registry loader + scene-token resolver.
 *
 * A DNA is a complete visual language (type, palette logic, motion grammar, hero
 * orchestration) that PARAMETERIZES per scene instead of shipping fixed look files.
 * The resolver folds in safe-zones.json's v2 scene measurements (palette / optics /
 * lighting) and envelope.json's loudness so the compiled tokens fit THIS clip:
 *
 *   accent      — scene-sampled when the DNA says "scene" (clamped readable)
 *   text shadow — contact shadow cast along the measured light direction
 *   depth match — embed text blur follows the scene's depth-of-field
 *   hero amp    — entrance amplitude coupled to the spoken word's loudness (RMS)
 *
 * Everything is read from files written by deterministic scripts — no randomness.
 */
const path = require("path");
const fs = require("fs");

const SKILL_ROOT = path.resolve(__dirname, "..");
const DNA_DIR = path.join(SKILL_ROOT, "dna");

// legacy template names → DNA (back-compat for existing plan.json files)
const LEGACY = { "cinematic-cream": "cream" };

function list() {
  try {
    return fs
      .readdirSync(DNA_DIR)
      .filter((f) => f.endsWith(".json"))
      .map((f) => f.replace(/\.json$/, ""))
      .sort();
  } catch {
    return [];
  }
}

function load(name) {
  const p = path.join(DNA_DIR, `${name}.json`);
  if (!fs.existsSync(p)) {
    throw new Error(`unknown DNA "${name}". Available: ${list().join(", ")}`);
  }
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

// ── audio impact: where does this window's loudness rank within the clip? ──────
// envelope.json = { hop, rms: [linear 0..1 per hop] } (audio-envelope.cjs)
function heroImpact(project, t0, t1) {
  const env = readJson(path.join(project, "envelope.json"));
  if (!env || !Array.isArray(env.rms) || !env.rms.length) return 0.6; // neutral default
  const hop = env.hop || 0.05;
  const i0 = Math.max(0, Math.floor(t0 / hop)),
    i1 = Math.min(env.rms.length, Math.ceil(t1 / hop));
  if (i1 <= i0) return 0.6;
  const span = i1 - i0;
  const mean = (arr, a, b) => {
    let s = 0;
    for (let i = a; i < b; i++) s += arr[i];
    return s / (b - a);
  };
  const target = mean(env.rms, i0, i1);
  // percentile of this window vs all same-length windows across the clip
  let below = 0,
    total = 0;
  for (let s = 0; s + span <= env.rms.length; s += Math.max(1, Math.floor(span / 2))) {
    total++;
    if (mean(env.rms, s, s + span) <= target) below++;
  }
  return total ? below / total : 0.6;
}

// ── scene-aware token resolution ───────────────────────────────────────────────
function resolveTokens(dna, project, opts) {
  const sz = readJson(path.join(project, "safe-zones.json")) || {};
  const palette = sz.palette || {};
  const optics = sz.optics || {};
  const lighting = sz.lighting || {};

  // accent: "scene" → sampled suggestion, else literal.
  // accentMode "counter" (loud registers): the accent must FIGHT the scene's
  // temperature, not harmonize with it — a sampled warm sienna inside a tungsten room
  // camouflages (the warm-on-warm failure a blind review caught across three DNAs).
  // Counter-pole = rotate the sampled hue 180° and push saturation/lightness hot.
  let accent =
    dna.palette.accent === "scene"
      ? palette.accentSuggestion || dna.palette.accent_fallback || "#e3c06a"
      : dna.palette.accent;
  if (
    dna.palette.accentMode === "counter" &&
    dna.palette.accent === "scene" &&
    /^#([0-9a-f]{6})$/i.test(accent || "")
  ) {
    const n = parseInt(accent.slice(1), 16);
    let r = (n >> 16) / 255,
      g2 = ((n >> 8) & 255) / 255,
      b = (n & 255) / 255;
    const mx = Math.max(r, g2, b),
      mn = Math.min(r, g2, b),
      d = mx - mn;
    let h = 0;
    if (d > 0) {
      h = mx === r ? ((g2 - b) / d) % 6 : mx === g2 ? (b - r) / d + 2 : (r - g2) / d + 4;
      h *= 60;
      if (h < 0) h += 360;
    }
    h = (h + 180) % 360;
    const s = 0.85,
      v = 0.92; // hot, acid, readable
    const c = v * s,
      x = c * (1 - Math.abs(((h / 60) % 2) - 1)),
      m = v - c;
    const [r2, g3, b2] =
      h < 60
        ? [c, x, 0]
        : h < 120
          ? [x, c, 0]
          : h < 180
            ? [0, c, x]
            : h < 240
              ? [0, x, c]
              : h < 300
                ? [x, 0, c]
                : [c, 0, x];
    const f = (q) =>
      Math.round((q + m) * 255)
        .toString(16)
        .padStart(2, "0");
    accent = `#${f(r2)}${f(g3)}${f(b2)}`;
  }

  const dark = dna.palette.scheme === "dark-on-light";

  // contact shadow along the measured light direction + a soft ambient.
  // light-on-dark also gets the warm bloom layer when the DNA asks for it.
  let shadowParts = [];
  if (dna.optics && dna.optics.contactShadow) {
    const sd = lighting.shadow || { dx: 0, dy: 3 };
    shadowParts.push(`${sd.dx}px ${sd.dy + 1}px 10px rgba(0,0,0,${dark ? 0.22 : 0.32})`);
  }
  shadowParts.push(dark ? "0 1px 14px rgba(0,0,0,0.10)" : "0 2px 22px rgba(0,0,0,0.28)");
  if (dna.optics && dna.optics.warmBloom) shadowParts.push("0 0 26px rgba(255,214,160,0.18)");
  const textShadow = shadowParts.join(", ");

  // depth match: embed (bg) text picks up the scene's bokeh; fg/rail stay sharp
  const blurPx = (dna.optics && dna.optics.depthMatch && optics.suggestedTextBlurPx) || 0;
  const baseFilter = dna.filter && dna.filter !== "none" ? dna.filter : "";
  const filterBg = `${baseFilter}${blurPx ? ` blur(${blurPx}px)` : ""}`.trim() || "none";
  const filterFg = baseFilter || "none";

  // hero orchestration + loudness coupling — one config PER hero (scarcity is per
  // beat/block, not per clip; each hero's amplitude follows ITS spoken loudness)
  const heroGroups = (opts && (opts.heroGroups || (opts.heroGroup ? [opts.heroGroup] : []))) || [];
  const heroes = heroGroups.map((hg) => {
    const impact = heroImpact(project, hg.in, Math.min(hg.in + 0.7, hg.out));
    const amp = +((0.75 + impact * 0.5) * (hg.minor ? 0.7 : 1)).toFixed(3); // 0.75…1.25, minors damped
    return {
      // spread the DNA's full hero block (entrance/perLetter/glow/breathe/ripple/loom/
      // letterBlur/sheen/echoes/… — new fx fields flow through with no plumbing),
      // then the per-hero computed values
      ...dna.hero,
      entrance: dna.hero.entrance || "emergence",
      dimOthers: dna.hero.dimOthers != null ? dna.hero.dimOthers : 0.45,
      id: hg.id,
      minor: hg.minor === true,
      in: hg.in,
      out: hg.out,
      amp,
      heroColor: dna.palette.heroColor === "accent" ? accent : null,
    };
  });
  const hero = heroes[0] || null; // back-compat single accessor

  return {
    fontFamily: dna.font.family,
    capColor: dna.palette.cap_color,
    blend: dna.palette.blend,
    accent,
    textShadow,
    filterBg,
    filterFg,
    blurPx,
    motion: dna.motion,
    hero,
    heroes,
    heroCss: (dna.hero && dna.hero.css) || "",
    heroCase: (dna.hero && dna.hero.case) || "none",
    heroTracking: (dna.hero && dna.hero.tracking) || "0",
    dnaCss: dna.css || "",
    register: dna.register,
    name: dna.name,
  };
}

module.exports = { LEGACY, list, load, resolveTokens, heroImpact };
