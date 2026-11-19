import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { applyBudgetBands, computeBudgetProfile, computePluginBudget } from "../src/core/budget.js";
import { estimateTokenCount } from "../src/lib/tokens.js";

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "budget-measurements-"));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const skill = path.join(root, "skill");
  await fs.mkdir(skill);
  await fs.writeFile(path.join(skill, "SKILL.md"), "---\nname: example\ndescription: Run an example.\n---\n# Example\nRead references when needed.\n");
  return { root, skill, target: { kind: "skill", path: skill } };
}

test("source, test and configuration growth changes package inventory, not deferred context", async (t) => {
  const { skill, target } = await fixture(t);
  const before = await computeBudgetProfile(target);
  for (const [name, content] of [["source.js", "export const x = 1;"], ["tests/example.test.js", "assert.ok(true);"], ["config.json", '{"flag":true}'], ["tests/README.md", "Test harness instructions"]]) {
    await fs.mkdir(path.dirname(path.join(skill, name)), { recursive: true });
    await fs.writeFile(path.join(skill, name), content.repeat(40));
  }
  const after = await computeBudgetProfile(target);
  assert.equal(after.deferred_cost_tokens.value, before.deferred_cost_tokens.value);
  assert.equal(after.invoke_cost_tokens.value, before.invoke_cost_tokens.value);
  assert.ok(after.package_text_tokens.value > before.package_text_tokens.value);
  assert.equal(after.package_text_tokens.observed, false);
});

test("supporting instructions remain a potential inventory excluded from total context estimate", async (t) => {
  const { skill, target } = await fixture(t);
  await fs.mkdir(path.join(skill, "references"));
  const reference = "Only consult this optional reference when needed.\n".repeat(25);
  await fs.writeFile(path.join(skill, "references", "guide.md"), reference);
  const raw = await computeBudgetProfile(target);
  assert.equal(raw.deferred_cost_tokens.value, estimateTokenCount(reference));
  assert.equal(raw.deferred_cost_tokens.basis, "potential-supporting-instruction-inventory");
  const bands = applyBudgetBands(raw, { skill: { trigger_cost_tokens: [1, 2, 3], invoke_cost_tokens: [1, 2, 3], deferred_cost_tokens: [1, 2, 3] } });
  assert.equal(bands.total_tokens.value, raw.trigger_cost_tokens.value + raw.invoke_cost_tokens.value);
  assert.equal(bands.total_tokens.observed, false);
  assert.equal(bands.deferred_cost_tokens.band, "unrated");
  assert.equal(bands.total_tokens.band, "unrated");
  assert.match(bands.deferred_cost_tokens.calibration_note, /not.*runtime|not.*context/i);
});

test("supported plain-text documentation formats contribute to instruction inventory", async (t) => {
  const { skill, target } = await fixture(t);
  for (const filename of ["guide.txt", "guide.rst", "guide.adoc"]) {
    await fs.writeFile(path.join(skill, filename), "Read these instructions.\n");
  }
  const result = await computeBudgetProfile(target);
  assert.equal(result.deferred_cost_tokens.value, 21);
  assert.equal(result.deferred_cost_tokens.components.length, 3);
});

test("external context coverage stays unknown and prose references are not followed", async (t) => {
  const { root, skill, target } = await fixture(t);
  const external = path.join(root, "outside.md");
  await fs.writeFile(external, "External instructions that must not be inferred.\n".repeat(100));
  await fs.appendFile(path.join(skill, "SKILL.md"), `Read ${external} when running this skill.\n`);
  const result = await computeBudgetProfile(target);
  assert.equal(result.external_context.coverage, "unknown");
  assert.equal(result.external_context.complete, false);
  assert.equal(result.external_context.discovery, "explicit-paths-only");
  assert.deepEqual(result.external_context.components, []);
});

test("a junction alias to external instructions is canonicalized and counted once", async (t) => {
  const { root, target } = await fixture(t);
  const externalDir = path.join(root, "external");
  await fs.mkdir(externalDir);
  const external = path.join(externalDir, "SKILL.md");
  await fs.writeFile(external, "# External instructions\n");
  const aliasDir = path.join(root, "alias");
  await fs.symlink(externalDir, aliasDir, process.platform === "win32" ? "junction" : "dir");
  const before = await computeBudgetProfile(target);
  const result = await computeBudgetProfile(target, { additionalContextPaths: [external, path.join(aliasDir, "SKILL.md")] });
  assert.equal(result.invoke_cost_tokens.value, before.invoke_cost_tokens.value + 6);
  assert.equal(result.additional_context.components.length, 1);
  assert.equal(result.external_context.components.length, 1);
});

test("explicit external instructions add invoke tokens once with canonical path provenance", async (t) => {
  const { root, skill, target } = await fixture(t);
  const external = path.join(root, "external", "SKILL.md");
  await fs.mkdir(path.dirname(external));
  const text = "# External skill\nFollow these external instructions.\n".repeat(30);
  await fs.writeFile(external, text);
  const before = await computeBudgetProfile(target);
  const result = await computeBudgetProfile(target, { additionalContextPaths: [external, path.join(root, "external", "..", "external", "SKILL.md"), path.join(skill, "SKILL.md")] });
  assert.equal(result.invoke_cost_tokens.value, before.invoke_cost_tokens.value + estimateTokenCount(text));
  assert.equal(result.external_context.components.length, 1);
  assert.equal(result.external_context.components[0].path, external);
  assert.equal(result.external_context.components[0].real_path, await fs.realpath(external));
  assert.equal(result.external_context.components[0].tokens, estimateTokenCount(text));
  assert.equal(result.external_context.components[0].source, "additionalContextPaths");
  assert.equal(result.external_context.complete, false);
  assert.equal(result.package_text_tokens.value, before.package_text_tokens.value);
});

test("selected local instructions move from potential inventory to invoke without double counting", async (t) => {
  const { skill, target } = await fixture(t);
  const selected = path.join(skill, "guide.md");
  await fs.writeFile(selected, "Instructions to load explicitly.\n".repeat(30));
  const before = await computeBudgetProfile(target);
  const result = await computeBudgetProfile(target, { additionalContextPaths: [selected, selected] });
  assert.equal(result.invoke_cost_tokens.value, before.invoke_cost_tokens.value + before.deferred_cost_tokens.value);
  assert.equal(result.deferred_cost_tokens.value, 0);
  assert.equal(result.external_context.components.length, 0);
  assert.equal(result.additional_context.components.length, 1);
  assert.equal(result.additional_context.components[0].scope, "local");
});

test("missing explicit context is an actionable error rather than a silent incomplete estimate", async (t) => {
  const { root, target } = await fixture(t);
  const missing = path.join(root, "missing", "SKILL.md");
  await assert.rejects(computeBudgetProfile(target, { additionalContextPaths: [missing] }), /additionalContextPaths.*missing/i);
});

test("explicit paths cannot cause source or secret-like files to be read as skill context", async (t) => {
  const { root, target } = await fixture(t);
  const envFile = path.join(root, ".env");
  await fs.writeFile(envFile, "fixture-only");
  await assert.rejects(computeBudgetProfile(target, { additionalContextPaths: [envFile] }), /instruction.*file|supported.*extension/i);
});

test("plugin string defaultPrompt is estimated without an array join error", async (t) => {
  const { root } = await fixture(t);
  await fs.mkdir(path.join(root, ".codex-plugin"));
  const manifest = { name: "example", description: "Example plugin", interface: { defaultPrompt: "Run this example" } };
  await fs.writeFile(path.join(root, ".codex-plugin", "plugin.json"), JSON.stringify(manifest));
  const result = await computePluginBudget(root, manifest);
  assert.equal(result.trigger_cost_tokens.components.find((item) => item.label === "default-prompts").tokens, estimateTokenCount(manifest.interface.defaultPrompt));
});

test("explicit-only plugin skill stays outside implicit estimate unless selected as context", async (t) => {
  const { root } = await fixture(t);
  await fs.mkdir(path.join(root, ".codex-plugin"));
  const manifest = { name: "policy", skills: "./skills/" };
  await fs.writeFile(path.join(root, ".codex-plugin", "plugin.json"), JSON.stringify(manifest));
  const specialist = path.join(root, "skills", "specialist");
  await fs.mkdir(path.join(specialist, "agents"), { recursive: true });
  const skillPath = path.join(specialist, "SKILL.md");
  await fs.writeFile(skillPath, "---\nname: specialist\ndescription: Specialized work\n---\n# Specialist\n");
  await fs.writeFile(path.join(specialist, "agents", "openai.yaml"), "policy:\n  allow_implicit_invocation: false\n");
  const before = await computePluginBudget(root, manifest);
  const selected = await computePluginBudget(root, manifest, { additionalContextPaths: [skillPath] });
  assert.equal(before.invocation_policy.explicit_only_skill_count, 1);
  assert.equal(before.trigger_cost_tokens.components.some((item) => item.path === skillPath), false);
  assert.equal(before.invoke_cost_tokens.components.some((item) => item.path === skillPath), false);
  assert.equal(selected.invoke_cost_tokens.value, before.invoke_cost_tokens.value + before.explicit_only_invoke_cost_tokens.value);
  assert.equal(selected.trigger_cost_tokens.value, before.trigger_cost_tokens.value);
});
