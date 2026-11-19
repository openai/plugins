import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import test from "node:test";

import { evaluatePlugin } from "../src/evaluators/plugin.js";
import { analyzePath } from "../src/core/analyze.js";
import { computeSummary } from "../src/core/scoring.js";
import { createEvaluationResult } from "../src/core/schema.js";

const execFileAsync = promisify(execFile);
const cli = fileURLToPath(new URL("../scripts/plugin-eval.js", import.meta.url));
const listingIds = ["websiteURL", "privacyPolicyURL", "termsOfServiceURL"]
  .map((field) => `interface-missing-${field}`);

async function fixture(t) {
  const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "plugin-eval-distribution-"));
  const relative = path.relative(path.resolve(os.tmpdir()), path.resolve(tempRoot));
  assert.ok(relative && !relative.startsWith("..") && !path.isAbsolute(relative));
  t.after(() => fs.rm(tempRoot, { recursive: true, force: true }));
  const root = path.join(tempRoot, "scope-plugin");
  const manifest = {
    name: "scope-plugin", version: "1.0.0", description: "Distribution fixture", author: { name: "Fixture" },
    skills: "./skills/", interface: {
      displayName: "Scope Plugin", shortDescription: "Distribution fixture", longDescription: "Distribution fixture",
      developerName: "Fixture", category: "Developer Tools", capabilities: [], defaultPrompt: ["Evaluate this plugin."],
    },
  };
  await fs.mkdir(path.join(root, ".codex-plugin"), { recursive: true });
  await fs.mkdir(path.join(root, "skills", "scope"), { recursive: true });
  await fs.writeFile(path.join(root, "skills", "scope", "SKILL.md"),
    "---\nname: scope\ndescription: Use for distribution fixture checks.\n---\n\nFollow the fixture request.\n");
  const write = () => fs.writeFile(path.join(root, ".codex-plugin", "plugin.json"), JSON.stringify(manifest));
  await write();
  return { root, manifest, write };
}

function listingChecks(result) {
  return result.checks.filter((check) => listingIds.includes(check.id));
}

test("private-local plugins have no public listing deductions", async (t) => {
  const { root } = await fixture(t);
  const result = await evaluatePlugin(root, { distribution: "private-local" });
  assert.deepEqual(listingChecks(result), []);
  assert.deepEqual(result.artifacts.find((item) => item.id === "plugin-distribution").data,
    { distribution: "private-local", publicListingMetadataGraded: false });
});

test("unspecified distribution does not assume public listing requirements", async (t) => {
  const { root } = await fixture(t);
  assert.deepEqual(listingChecks(await evaluatePlugin(root)), []);
});

test("public distribution retains all three listing requirements", async (t) => {
  const { root } = await fixture(t);
  const result = await evaluatePlugin(root, { distribution: "public" });
  assert.deepEqual(listingChecks(result).map((check) => check.id), listingIds);
  assert.ok(listingChecks(result).every((check) => check.status === "fail" && check.severity === "error"));
});

test("private-local scope preserves functional manifest checks", async (t) => {
  const { root, manifest, write } = await fixture(t);
  delete manifest.interface.displayName;
  await write();
  const result = await evaluatePlugin(root, { distribution: "private-local" });
  assert.ok(result.checks.some((check) => check.id === "interface-missing-displayName" && check.status === "fail"));
});

test("public plugins with listing metadata pass those requirements", async (t) => {
  const { root, manifest, write } = await fixture(t);
  for (const field of ["websiteURL", "privacyPolicyURL", "termsOfServiceURL"]) {
    manifest.interface[field] = `https://example.com/${field}`;
  }
  await write();
  assert.deepEqual(listingChecks(await evaluatePlugin(root, { distribution: "public" })), []);
});

test("distribution changes only the 42 public-metadata points", async (t) => {
  const { root } = await fixture(t);
  const local = await evaluatePlugin(root, { distribution: "private-local" });
  const published = await evaluatePlugin(root, { distribution: "public" });
  const score = (result) => computeSummary({ ...createEvaluationResult({ kind: "plugin", path: root }), ...result }).score;
  assert.equal(score(local) - score(published), 42);
});

test("invalid distribution is rejected rather than silently weakening checks", async (t) => {
  const { root } = await fixture(t);
  await assert.rejects(evaluatePlugin(root, { distribution: "publci" }), /distribution/i);
});

test("analyze API passes distribution to plugin checks", async (t) => {
  const { root } = await fixture(t);
  assert.deepEqual(listingChecks(await analyzePath(root, { distribution: "private-local" })), []);
  const result = await analyzePath(root, { distribution: "public" });
  assert.equal(listingChecks(result).length, 3);
  assert.match(result.nextAction.command, /--distribution public/);
  assert.match(result.measurementPlan.nextAction.command, /--distribution public/);
});

test("CLI honors private-local and public scope and rejects invalid values", async (t) => {
  const { root } = await fixture(t);
  for (const distribution of ["private-local", "public"]) {
    const { stdout } = await execFileAsync(process.execPath,
      [cli, "analyze", root, "--distribution", distribution, "--format", "json"], { timeout: 30000 });
    assert.equal(listingChecks(JSON.parse(stdout)).length, distribution === "public" ? 3 : 0);
  }
  await assert.rejects(execFileAsync(process.execPath,
    [cli, "analyze", root, "--distribution", "publci"], { timeout: 30000 }), /distribution/i);
});

test("chat-first routing preserves explicit public scope in suggested commands", async (t) => {
  const { root } = await fixture(t);
  const { stdout } = await execFileAsync(process.execPath,
    [cli, "start", root, "--distribution", "public", "--format", "json"], { timeout: 30000 });
  const result = JSON.parse(stdout);
  assert.equal(result.distribution, "public");
  assert.match(result.startHere.firstCommand, /--distribution public/);
  assert.match(result.startHere.startCommand, /--distribution public/);
});

test("measurement plans preserve the evaluation distribution", async (t) => {
  const { root } = await fixture(t);
  const { stdout } = await execFileAsync(process.execPath,
    [cli, "measurement-plan", root, "--distribution", "private-local", "--format", "json"], { timeout: 30000 });
  const result = JSON.parse(stdout);
  assert.equal(result.workflowGuide.distribution, "private-local");
  assert.match(result.nextAction.command, /--distribution private-local/);
});

test("CLI requires a value for distribution", async (t) => {
  const { root } = await fixture(t);
  await assert.rejects(execFileAsync(process.execPath,
    [cli, "analyze", root, "--distribution"], { timeout: 30000 }), /Missing distribution value/);
});
