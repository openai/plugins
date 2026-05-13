import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptDir, "..");
const rawDir = path.join(appRoot, "dist", "raw");
const outputPath = path.join(appRoot, "dist", "plugin-builder-widget.html");
const indexPath = path.join(rawDir, "index.html");

function readAsset(reference) {
  const normalized = reference.replace(/^\.\//, "");
  return fs.readFileSync(path.join(rawDir, normalized), "utf8");
}

let html = fs.readFileSync(indexPath, "utf8");
const stylesheetMatch = html.match(
  /<link rel="stylesheet" crossorigin href="([^"]+)"[^>]*>/,
);
const scriptMatch = html.match(
  /<script type="module" crossorigin src="([^"]+)"><\/script>/,
);

if (!stylesheetMatch || !scriptMatch) {
  throw new Error("Unable to inline the Plugin Builder widget assets.");
}

const css = readAsset(stylesheetMatch[1]);
const javascript = readAsset(scriptMatch[1]);

html = html
  .replace(stylesheetMatch[0], () => `<style>\n${css}\n</style>`)
  .replace(scriptMatch[0], () => `<script type="module">\n${javascript}\n</script>`);

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html);
