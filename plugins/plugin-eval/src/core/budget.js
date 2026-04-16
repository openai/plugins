import fs from "node:fs/promises";
import path from "node:path";

import { parseFrontmatter } from "../lib/frontmatter.js";
import { isDirectory, isProbablyTextFile, pathExists, readJson, readText, relativePath, walkFiles } from "../lib/files.js";
import { estimateTokenCount, sumTokenCounts } from "../lib/tokens.js";

function createComponent(label, componentPath, tokens, note) {
  return {
    label,
    path: componentPath,
    tokens,
    note,
  };
}

function buildBudgetBucket(value, thresholds, components) {
  const [goodMax, moderateMax, heavyMax] = thresholds;
  const band =
    value <= goodMax ? "good" : value <= moderateMax ? "moderate" : value <= heavyMax ? "heavy" : "excessive";
  return {
    value,
    band,
    thresholds: {
      goodMax,
      moderateMax,
      heavyMax,
    },
    components,
  };
}

async function gatherDeferredTextFiles(rootPath, excludeFiles = []) {
  const files = await walkFiles(rootPath);
  return files.filter(
    (filePath) => !excludeFiles.includes(filePath) && isProbablyTextFile(filePath),
  );
}

async function computeDeferredComponents(rootPath, excludeFiles = []) {
  const files = await gatherDeferredTextFiles(rootPath, excludeFiles);
  const components = [];
  for (const filePath of files) {
    const content = await readText(filePath);
    components.push(
      createComponent(
        relativePath(rootPath, filePath),
        filePath,
        estimateTokenCount(content),
        "Deferred supporting file",
      ),
    );
  }
  return components;
}

export async function computeSkillBudget(skillRoot) {
  const skillPath = path.join(skillRoot, "SKILL.md");
  const content = await readText(skillPath);
  const parsed = parseFrontmatter(content);
  const name = parsed.data?.name || path.basename(skillRoot);
  const description = parsed.data?.description || "";

  const triggerComponents = [
    createComponent("skill-name", skillPath, estimateTokenCount(name), "Always-loaded skill identifier"),
    createComponent(
      "skill-description",
      skillPath,
      estimateTokenCount(description),
      "Always-loaded trigger description",
    ),
  ];

  const invokeComponents = [
    createComponent("skill-file", skillPath, estimateTokenCount(content), "Loaded when the skill is invoked"),
  ];

  const deferredComponents = await computeDeferredComponents(skillRoot, [skillPath]);

  return {
    kind: "skill",
    trigger_cost_tokens: {
      value: sumTokenCounts(triggerComponents),
      components: triggerComponents,
    },
    invoke_cost_tokens: {
      value: sumTokenCounts(invokeComponents),
      components: invokeComponents,
    },
    deferred_cost_tokens: {
      value: sumTokenCounts(deferredComponents),
      components: deferredComponents,
    },
  };
}

export async function computePluginBudget(pluginRoot, manifest) {
  const manifestPath = path.join(pluginRoot, ".codex-plugin", "plugin.json");
  const manifestContent = await readText(manifestPath);
  const skillDirs = manifest?.skills
    ? await discoverSkillDirs(pluginRoot, manifest.skills)
    : await discoverSkillDirs(pluginRoot, "./skills/");

  const triggerComponents = [
    createComponent(
      "plugin-description",
      manifestPath,
      estimateTokenCount(manifest?.description || ""),
      "Plugin marketplace summary",
    ),
    createComponent(
      "default-prompts",
      manifestPath,
      estimateTokenCount((manifest?.interface?.defaultPrompt || []).join("\n")),
      "Starter prompts visible in the UI",
    ),
  ];

  const invokeComponents = [
    createComponent("plugin-manifest", manifestPath, estimateTokenCount(manifestContent), "Manifest load cost"),
  ];

  for (const skillDir of skillDirs) {
    const skillPath = path.join(skillDir, "SKILL.md");
    if (!(await pathExists(skillPath))) {
      continue;
    }
    const content = await readText(skillPath);
    const parsed = parseFrontmatter(content);
    triggerComponents.push(
      createComponent(
        `${path.basename(skillDir)}-description`,
        skillPath,
        estimateTokenCount(parsed.data?.description || ""),
        "Skill trigger description exposed through the plugin",
      ),
    );
    invokeComponents.push(
      createComponent(
        `${path.basename(skillDir)}-skill-file`,
        skillPath,
        estimateTokenCount(content),
        "Skill invocation cost ceiling",
      ),
    );
  }

  const deferredComponents = await computeDeferredComponents(pluginRoot, [
    manifestPath,
    ...skillDirs.map((skillDir) => path.join(skillDir, "SKILL.md")),
  ]);

  return {
    kind: "plugin",
    trigger_cost_tokens: {
      value: sumTokenCounts(triggerComponents),
      components: triggerComponents,
    },
    invoke_cost_tokens: {
      value: sumTokenCounts(invokeComponents),
      components: invokeComponents,
    },
    deferred_cost_tokens: {
      value: sumTokenCounts(deferredComponents),
      components: deferredComponents,
    },
  };
}

async function discoverSkillDirs(pluginRoot, skillsPath) {
  const directory = path.join(pluginRoot, skillsPath.replace(/^\.\//, ""));
  if (!(await isDirectory(directory))) {
    return [];
  }
  const entries = await fs.readdir(directory, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(directory, entry.name))
    .sort();
}

export async function computeBudgetProfile(target) {
  if (target.kind === "skill") {
    return computeSkillBudget(target.path);
  }
  if (target.kind === "plugin") {
    const manifest = await readJson(path.join(target.path, ".codex-plugin", "plugin.json"));
    return computePluginBudget(target.path, manifest);
  }

  const files = await gatherDeferredTextFiles(target.path);
  const components = [];
  for (const filePath of files) {
    const content = await readText(filePath);
    components.push(
      createComponent(
        relativePath(target.path, filePath),
        filePath,
        estimateTokenCount(content),
        "Generic text file budget",
      ),
    );
  }
  return {
    kind: target.kind,
    trigger_cost_tokens: { value: 0, components: [] },
    invoke_cost_tokens: { value: 0, components: [] },
    deferred_cost_tokens: { value: sumTokenCounts(components), components },
  };
}

export function applyBudgetBands(rawBudget, baseline) {
  const profile = baseline?.[rawBudget.kind] || baseline?.directory || baseline?.skill;
  const trigger = buildBudgetBucket(
    rawBudget.trigger_cost_tokens.value,
    profile.trigger_cost_tokens,
    rawBudget.trigger_cost_tokens.components,
  );
  const invoke = buildBudgetBucket(
    rawBudget.invoke_cost_tokens.value,
    profile.invoke_cost_tokens,
    rawBudget.invoke_cost_tokens.components,
  );
  const deferred = buildBudgetBucket(
    rawBudget.deferred_cost_tokens.value,
    profile.deferred_cost_tokens,
    rawBudget.deferred_cost_tokens.components,
  );
  const total = trigger.value + invoke.value + deferred.value;
  return {
    method: "estimated-static",
    trigger_cost_tokens: trigger,
    invoke_cost_tokens: invoke,
    deferred_cost_tokens: deferred,
    total_tokens: {
      value: total,
      band:
        [trigger.band, invoke.band, deferred.band].includes("excessive")
          ? "excessive"
          : [trigger.band, invoke.band, deferred.band].includes("heavy")
            ? "heavy"
            : [trigger.band, invoke.band, deferred.band].includes("moderate")
              ? "moderate"
              : "good",
    },
  };
}
