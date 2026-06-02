import os from "node:os";
import path from "node:path";

import { computePluginBudget, computeSkillBudget } from "./budget.js";
import { listImmediateDirectories, pathExists, readJson, relativePath } from "../lib/files.js";

const DEFAULT_BASELINE = {
  skill: {
    trigger_cost_tokens: [48, 92, 150],
    invoke_cost_tokens: [220, 480, 900],
    deferred_cost_tokens: [180, 520, 1200],
  },
  plugin: {
    trigger_cost_tokens: [120, 260, 420],
    invoke_cost_tokens: [500, 1200, 2400],
    deferred_cost_tokens: [320, 900, 2200],
  },
  directory: {
    trigger_cost_tokens: [1, 1, 1],
    invoke_cost_tokens: [1, 1, 1],
    deferred_cost_tokens: [240, 640, 1600],
  },
};

let cachedBaseline = null;

function quantile(values, percentile) {
  if (values.length === 0) {
    return 0;
  }
  const sorted = [...values].sort((left, right) => left - right);
  const index = Math.min(sorted.length - 1, Math.max(0, Math.floor((sorted.length - 1) * percentile)));
  return sorted[index];
}

function summarizeSamples(samples) {
  if (samples.length < 4) {
    return null;
  }
  return {
    trigger_cost_tokens: [
      quantile(samples.map((sample) => sample.trigger_cost_tokens.value), 0.5),
      quantile(samples.map((sample) => sample.trigger_cost_tokens.value), 0.75),
      quantile(samples.map((sample) => sample.trigger_cost_tokens.value), 0.9),
    ],
    invoke_cost_tokens: [
      quantile(samples.map((sample) => sample.invoke_cost_tokens.value), 0.5),
      quantile(samples.map((sample) => sample.invoke_cost_tokens.value), 0.75),
      quantile(samples.map((sample) => sample.invoke_cost_tokens.value), 0.9),
    ],
    deferred_cost_tokens: [
      quantile(samples.map((sample) => sample.deferred_cost_tokens.value), 0.5),
      quantile(samples.map((sample) => sample.deferred_cost_tokens.value), 0.75),
      quantile(samples.map((sample) => sample.deferred_cost_tokens.value), 0.9),
    ],
  };
}

async function collectSkillSamples(skillRoot) {
  if (!(await pathExists(skillRoot))) {
    return [];
  }
  const directories = await listImmediateDirectories(skillRoot);
  const samples = [];
  for (const directory of directories) {
    const skillPath = path.join(directory, "SKILL.md");
    if (!(await pathExists(skillPath))) {
      continue;
    }
    try {
      samples.push(await computeSkillBudget(directory));
    } catch {
      // Ignore malformed shipped samples and keep the baseline usable.
    }
  }
  return samples;
}

async function collectPluginSamples(pluginRoot) {
  if (!(await pathExists(pluginRoot))) {
    return [];
  }
  const directories = await listImmediateDirectories(pluginRoot);
  const samples = [];
  for (const directory of directories) {
    const manifestPath = path.join(directory, ".codex-plugin", "plugin.json");
    if (!(await pathExists(manifestPath))) {
      continue;
    }
    try {
      const manifest = await readJson(manifestPath);
      samples.push(await computePluginBudget(directory, manifest));
    } catch {
      // Ignore malformed shipped samples and keep the baseline usable.
    }
  }
  return samples;
}

export async function loadBudgetBaseline() {
  if (cachedBaseline) {
    return cachedBaseline;
  }

  const home = os.homedir();
  const skillRoot = path.join(home, ".codex", "skills");
  const curatedPluginRoot = path.join(home, ".codex", "plugins", "cache", "openai-curated");
  const tempPluginRoot = path.join(home, ".codex", ".tmp", "plugins", "plugins");

  const skillSamples = await collectSkillSamples(skillRoot);
  const pluginSamples = [
    ...(await collectPluginSamples(curatedPluginRoot)),
    ...(await collectPluginSamples(tempPluginRoot)),
  ];

  cachedBaseline = {
    skill: summarizeSamples(skillSamples) || DEFAULT_BASELINE.skill,
    plugin: summarizeSamples(pluginSamples) || DEFAULT_BASELINE.plugin,
    directory: DEFAULT_BASELINE.directory,
    evidence: {
      skillSamples: skillSamples.length,
      pluginSamples: pluginSamples.length,
      sourceRoots: [
        relativePath(process.cwd(), skillRoot),
        relativePath(process.cwd(), curatedPluginRoot),
        relativePath(process.cwd(), tempPluginRoot),
      ],
    },
  };

  return cachedBaseline;
}
