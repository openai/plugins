#!/usr/bin/env node

import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { inspectOutputIssues } from "../runtime/output-issues.mjs";
import { normalizePresentation } from "../runtime/normalize.mjs";

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) throw new Error(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    if (key === "help") {
      options.help = true;
      continue;
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for --${key}`);
    options[key] = value;
    index += 1;
  }
  return options;
}

function requireOption(options, key) {
  if (!options[key]) throw new Error(`Missing required --${key}`);
  return resolve(options[key]);
}

async function writeAtomic(path, contents) {
  await mkdir(dirname(path), { recursive: true });
  const temporary = `${path}.tmp-${process.pid}`;
  await writeFile(temporary, contents, "utf8");
  await rename(temporary, path);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stdout.write("Usage: check_output_issues.mjs --input <raw-output.json> --output <output-issues.json> [--presentation-id <id>] [--max-issues <1-1000>]\n");
    return;
  }

  const inputPath = requireOption(options, "input");
  const outputPath = requireOption(options, "output");
  const raw = JSON.parse(await readFile(inputPath, "utf8"));
  const snapshot = normalizePresentation(raw, {
    presentationId: options["presentation-id"] ?? null,
  });
  const report = inspectOutputIssues(snapshot, {
    maxIssues: options["max-issues"] === undefined ? undefined : Number(options["max-issues"]),
  });
  await writeAtomic(outputPath, `${JSON.stringify(report, null, 2)}\n`);

  process.stdout.write(`${JSON.stringify({
    output: outputPath,
    presentation: report.presentation,
    summary: report.summary,
  }, null, 2)}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error?.name ?? "Error"}: ${error?.message ?? String(error)}\n`);
  process.exitCode = 1;
});
