import path from "node:path";
import { spawnSync } from "node:child_process";

import { pathExists, readJson } from "../lib/files.js";

function normalizeCommand(manifest) {
  if (Array.isArray(manifest.command)) {
    return manifest.command.map((part, index) => (index === 0 && part === "node" ? process.execPath : part));
  }
  if (typeof manifest.command === "string") {
    return manifest.command
      .split(/\s+/)
      .filter(Boolean)
      .map((part, index) => (index === 0 && part === "node" ? process.execPath : part));
  }
  return [];
}

export async function runMetricPacks(target, manifestPaths = []) {
  const extensions = [];

  for (const manifestPath of manifestPaths) {
    const resolvedManifestPath = path.resolve(manifestPath);
    if (!(await pathExists(resolvedManifestPath))) {
      throw new Error(`Metric pack manifest not found: ${resolvedManifestPath}`);
    }

    const manifest = await readJson(resolvedManifestPath);
    if (
      Array.isArray(manifest.supportedTargetKinds) &&
      !manifest.supportedTargetKinds.includes(target.kind)
    ) {
      continue;
    }

    const command = normalizeCommand(manifest);
    if (command.length === 0) {
      throw new Error(`Metric pack command is missing: ${resolvedManifestPath}`);
    }

    const [bin, ...args] = command;
    const execution = spawnSync(
      bin,
      [...args, target.path, target.kind],
      {
        cwd: path.dirname(resolvedManifestPath),
        encoding: "utf8",
        env: {
          ...process.env,
          PLUGIN_EVAL_TARGET: target.path,
          PLUGIN_EVAL_TARGET_KIND: target.kind,
          PLUGIN_EVAL_METRIC_PACK_MANIFEST: resolvedManifestPath,
        },
      },
    );

    if (execution.status !== 0) {
      throw new Error(
        `Metric pack failed (${manifest.name || resolvedManifestPath}): ${execution.stderr || execution.stdout}`,
      );
    }

    const payload = JSON.parse(execution.stdout || "{}");
    extensions.push({
      name: manifest.name || path.basename(resolvedManifestPath),
      version: manifest.version || "0.0.0",
      manifestPath: resolvedManifestPath,
      checks: Array.isArray(payload.checks) ? payload.checks : [],
      metrics: Array.isArray(payload.metrics) ? payload.metrics : [],
      artifacts: Array.isArray(payload.artifacts) ? payload.artifacts : [],
    });
  }

  return extensions;
}
