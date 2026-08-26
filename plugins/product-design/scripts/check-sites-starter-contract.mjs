#!/usr/bin/env node
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const templatesRoot = path.join(pluginRoot, "templates");
const templateNames = ["prototype", "mobile-app"];
const sharedFiles = [
  ".openai/hosting.json",
  "scripts/prepare-sites-build.mjs",
  "tests/sites-worker.test.mjs",
  "worker/index.js",
];

function readTemplateFile(templateName, relativePath) {
  return readFileSync(path.join(templatesRoot, templateName, relativePath), "utf8");
}

for (const templateName of templateNames) {
  const packageJson = JSON.parse(readTemplateFile(templateName, "package.json"));
  const viteConfigPath = templateName === "prototype" ? "vite.config.mjs" : "vite.config.ts";
  const viteConfig = readTemplateFile(templateName, viteConfigPath);

  assert.equal(packageJson.scripts.dev, "vite", templateName + " must use Vite for local preview");
  assert.match(
    packageJson.scripts.build,
    /node scripts\/prepare-sites-build\.mjs/u,
    templateName + " build must prepare the Sites artifact",
  );
  assert.equal(
    packageJson.scripts["test:sites"],
    "node --test tests/sites-worker.test.mjs",
    templateName + " must expose the Sites contract test",
  );
  assert.match(viteConfig, /outDir: "dist\/client"/u);
  assert.match(viteConfig, /host: "0\.0\.0\.0"/u);
  assert.match(viteConfig, /allowedHosts: \["terminal\.local"\]/u);
}

for (const relativePath of sharedFiles) {
  assert.equal(
    readTemplateFile("prototype", relativePath),
    readTemplateFile("mobile-app", relativePath),
    relativePath + " must stay identical across Product Design starters",
  );
}

console.log("Product Design web and mobile starters share the Sites preview and artifact contract.");
