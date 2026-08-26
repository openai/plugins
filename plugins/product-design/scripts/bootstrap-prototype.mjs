#!/usr/bin/env node
import {
  cpSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptPath = fileURLToPath(import.meta.url);
const pluginRoot = path.resolve(path.dirname(scriptPath), "..");
const templatesRoot = path.join(pluginRoot, "templates");

const availableTemplates = new Set(["prototype", "mobile-app"]);

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith("--")) continue;
    const raw = arg.slice(2);
    const [key, inlineValue] = raw.split("=", 2);
    if (inlineValue !== undefined) {
      args[key] = inlineValue;
      continue;
    }
    const next = argv[index + 1];
    if (next && !next.startsWith("--")) {
      args[key] = next;
      index += 1;
    } else {
      args[key] = true;
    }
  }
  return args;
}

function slugify(value) {
  return (
    String(value || "prototype")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "") || "prototype"
  );
}

function readText(filePath) {
  return existsSync(filePath) ? readFileSync(filePath, "utf8") : "";
}

function writeText(filePath, value) {
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, value, "utf8");
}

function copyDir(source, target) {
  cpSync(source, target, {
    recursive: true,
    force: true,
    filter(current) {
      const name = path.basename(current);
      return !["node_modules", "dist", ".vite", ".turbo", ".DS_Store"].includes(name);
    },
  });
}

function hasFiles(dir) {
  return existsSync(dir) && readdirSync(dir).length > 0;
}

function ensureEmptyDest(dest) {
  if (existsSync(dest) && statSync(dest).isFile()) {
    throw new Error(`Destination exists and is not a directory: ${dest}`);
  }
  if (hasFiles(dest)) {
    throw new Error(`Destination exists and is not empty: ${dest}`);
  }
  mkdirSync(dest, { recursive: true });
}

function nearestPrototypeRoot(args) {
  const root = args.root || args.dest || process.cwd();
  return path.resolve(root);
}

function selectedTemplate(args) {
  const template = String(args.template || "prototype").trim();
  if (!availableTemplates.has(template)) {
    throw new Error(
      `Unknown template: ${template}. Available templates: ${Array.from(availableTemplates).join(", ")}`,
    );
  }
  return template;
}

function packageJsonPath(root) {
  return path.join(root, "package.json");
}

function readPackage(root) {
  const filePath = packageJsonPath(root);
  if (!existsSync(filePath)) return null;
  return JSON.parse(readText(filePath));
}

function writePackage(root, pkg) {
  writeText(packageJsonPath(root), `${JSON.stringify(pkg, null, 2)}\n`);
}

function setPackageName(root) {
  const pkg = readPackage(root);
  if (!pkg) return;
  pkg.name = slugify(path.basename(root));
  writePackage(root, pkg);
}

function setNpmDefaults(root) {
  writeText(path.join(root, ".npmrc"), [
    "fund=false",
    "audit=false",
    "",
  ].join("\n"));
}

function createNew(root, template) {
  const templateRoot = path.join(templatesRoot, template);
  if (!existsSync(templateRoot)) {
    throw new Error(`Bundled Product Design template is missing: ${templateRoot}`);
  }
  ensureEmptyDest(root);
  copyDir(templateRoot, root);
  setPackageName(root);
  setNpmDefaults(root);
  return { status: "created", root, template };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = nearestPrototypeRoot(args);

  if (args.mode && args.mode !== "new") {
    const mode = String(args.mode);
    throw new Error(`Unknown mode: ${mode}`);
  }
  const result = createNew(root, selectedTemplate(args));
  console.log(JSON.stringify(result, null, 2));
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
