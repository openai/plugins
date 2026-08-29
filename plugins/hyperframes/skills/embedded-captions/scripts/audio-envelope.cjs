#!/usr/bin/env node
/*
 * audio-envelope.cjs — extract a per-50ms RMS loudness envelope from the source audio.
 *
 *   node audio-envelope.cjs <project-dir>     → <project>/envelope.json
 *
 * { hop: 0.05, rms: [linear 0..1 per hop] }
 *
 * Used by lib-dna.cjs to couple the hero's entrance amplitude to how hard the word was
 * actually SPOKEN (percentile of the hero window's loudness within the clip). ffmpeg
 * astats over fixed windows — deterministic, no network, no Python.
 */
const path = require("path");
const fs = require("fs");
const cp = require("child_process");

const HOP = 0.05;

function findSource(project) {
  for (const c of ["source.mp4"].concat(
    fs
      .readdirSync(project)
      .filter(
        (f) =>
          /\.(mp4|mov|webm|mkv|m4v|wav|m4a|mp3)$/i.test(f) &&
          !/^(final|bg_plus_caps|fg_caps|rail|index)/.test(f),
      ),
  )) {
    const p = path.join(project, c);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function main() {
  const project = path.resolve(process.argv[2] || "");
  if (!process.argv[2]) {
    console.error("usage: audio-envelope.cjs <project-dir>");
    process.exit(1);
  }
  const src = findSource(project);
  if (!src) {
    console.error("[envelope] no source media found");
    process.exit(2);
  }

  // asetnsamples groups audio into fixed windows; astats prints RMS per window
  const sr = 16000,
    n = Math.round(sr * HOP);
  let out;
  try {
    // resample INSIDE the filter chain — an output-option -ar applies after the
    // filtergraph, which would make each window n/<input-rate> seconds instead of HOP
    out = cp.execFileSync(
      "ffmpeg",
      [
        "-v",
        "info",
        "-i",
        src,
        "-map",
        "a:0",
        "-af",
        `aresample=${sr},aformat=channel_layouts=mono,asetnsamples=n=${n}:p=0,astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-`,
        "-f",
        "null",
        "-",
      ],
      { encoding: "utf8", maxBuffer: 64 * 1024 * 1024, stdio: ["ignore", "pipe", "pipe"] },
    );
  } catch (e) {
    // ffmpeg writes the metadata to stdout before exiting; some containers still exit 0 — re-throw only if nothing parsed
    out = (e.stdout || "") + "";
    if (!out.includes("RMS_level")) {
      console.error(`[envelope] ffmpeg failed: ${e.message}`);
      process.exit(2);
    }
  }
  const rmsDb = [];
  for (const line of String(out).split("\n")) {
    const m = line.match(/lavfi\.astats\.Overall\.RMS_level=(-?[\d.]+|-inf)/);
    if (m) rmsDb.push(m[1] === "-inf" ? -90 : Math.max(-90, parseFloat(m[1])));
  }
  if (!rmsDb.length) {
    console.error("[envelope] no RMS windows parsed");
    process.exit(2);
  }
  const rms = rmsDb.map((db) => +Math.pow(10, db / 20).toFixed(5)); // linear 0..1
  fs.writeFileSync(path.join(project, "envelope.json"), JSON.stringify({ hop: HOP, rms }));
  const peakAt = rms.indexOf(Math.max(...rms)) * HOP;
  console.log(
    `[envelope] ${rms.length} windows @ ${HOP}s → envelope.json (loudest beat ~${peakAt.toFixed(2)}s)`,
  );
}
main();
