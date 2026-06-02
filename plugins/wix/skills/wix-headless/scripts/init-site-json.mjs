#!/usr/bin/env node
// Write the initial .wix/site.json — slim metadata snapshot for resume
// detection + run.json composition. Subagents do NOT read this file during
// the run; the orchestrator is the sole reader/writer and inlines anything
// downstream phases need into their prompts.
//
// Final shape:
//   {
//     "brand":     { "name": "...", "description": "..." },
//     "frontend":  "astro" | "custom",
//     "verticals": ["stores", "cms", ...],
//     "siteId":    "..." (optional — Setup Step 1 may patch later),
//     "appId":     "..." (optional — Setup Step 1 may patch later)
//   }
//
// Usage:
//   node init-site-json.mjs <project-dir> <brand-name> <brand-description> \
//     <verticals-csv> --frontend <astro|custom> \
//     [--site-id <id>] [--app-id <id>]
//   (In practice only "astro" reaches this step — custom frontends route to the
//    not-available stub before Discovery's approval/site.json write.)
//
// Behavior:
//   - Refuses to overwrite an existing .wix/site.json (exit 2). The orchestrator
//     should call this exactly once during Discovery's "After Approval" step.
//     To re-init for testing, the caller can rm the file first.
//   - Creates .wix/ if it doesn't exist.
//   - Outputs a JSON summary to stdout.

import { writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const ALLOWED_FRONTENDS = new Set(["astro", "custom"]);

let frontend = "astro";
let siteId;
let appId;
const positional = [];
const rawArgs = process.argv.slice(2);
for (let i = 0; i < rawArgs.length; i++) {
  const arg = rawArgs[i];
  if (arg === "--frontend") {
    frontend = rawArgs[++i];
  } else if (arg.startsWith("--frontend=")) {
    frontend = arg.slice("--frontend=".length);
  } else if (arg === "--site-id") {
    siteId = rawArgs[++i];
  } else if (arg.startsWith("--site-id=")) {
    siteId = arg.slice("--site-id=".length);
  } else if (arg === "--app-id") {
    appId = rawArgs[++i];
  } else if (arg.startsWith("--app-id=")) {
    appId = arg.slice("--app-id=".length);
  } else {
    positional.push(arg);
  }
}

if (!ALLOWED_FRONTENDS.has(frontend)) {
  console.error(`init-site-json: --frontend must be one of ${[...ALLOWED_FRONTENDS].join(", ")}; got ${JSON.stringify(frontend)}`);
  process.exit(2);
}

const [projectDir, brandName, brandDescription, verticalsCsv] = positional;

if (!projectDir || !brandName || brandDescription === undefined || !verticalsCsv) {
  console.error("usage: init-site-json.mjs <project-dir> <brand-name> <brand-description> <verticals-csv> --frontend <astro|custom> [--site-id <id>] [--app-id <id>]");
  process.exit(2);
}

const verticals = verticalsCsv
  .split(",")
  .map((v) => v.trim())
  .filter(Boolean);

if (verticals.length === 0) {
  console.error("init-site-json: <verticals-csv> resolved to zero verticals — cms is always loaded, so this is a bug");
  process.exit(2);
}

const wixDir = join(projectDir, ".wix");
const sitePath = join(wixDir, "site.json");

if (existsSync(sitePath)) {
  console.error(`init-site-json: ${sitePath} already exists — refusing to overwrite. Discovery should call this exactly once.`);
  process.exit(2);
}

mkdirSync(wixDir, { recursive: true });

const site = {
  brand: { name: brandName, description: brandDescription },
  frontend,
  verticals,
};
if (siteId) site.siteId = siteId;
if (appId) site.appId = appId;

writeFileSync(sitePath, JSON.stringify(site, null, 2) + "\n");

console.log(JSON.stringify({ status: "ok", path: sitePath, frontend, verticals, ...(siteId ? { siteId } : {}), ...(appId ? { appId } : {}) }, null, 2));
