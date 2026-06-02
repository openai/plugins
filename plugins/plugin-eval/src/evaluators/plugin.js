import path from "node:path";

import { createArtifact, createCheck, createMetric } from "../core/schema.js";
import { evaluateSkill } from "./skill.js";
import { discoverPluginSkillDirectories } from "../core/target.js";
import { pathExists, readJson, relativePath } from "../lib/files.js";

function isHyphenCase(value) {
  return /^[a-z0-9-]+$/.test(value) && !value.startsWith("-") && !value.endsWith("-") && !value.includes("--");
}

export async function evaluatePlugin(pluginRoot) {
  const manifestPath = path.join(pluginRoot, ".codex-plugin", "plugin.json");
  const targetPath = relativePath(process.cwd(), pluginRoot);
  const checks = [];
  const metrics = [];
  const artifacts = [];

  if (!(await pathExists(manifestPath))) {
    checks.push(
      createCheck({
        id: "plugin-manifest-missing",
        category: "manifest",
        severity: "error",
        status: "fail",
        message: "The plugin root is missing .codex-plugin/plugin.json.",
        evidence: [targetPath],
        remediation: ["Add .codex-plugin/plugin.json to the plugin root."],
        targetPath,
      }),
    );
    return { checks, metrics, artifacts };
  }

  let manifest;
  try {
    manifest = await readJson(manifestPath);
  } catch (error) {
    checks.push(
      createCheck({
        id: "plugin-manifest-invalid-json",
        category: "manifest",
        severity: "error",
        status: "fail",
        message: "plugin.json could not be parsed as JSON.",
        evidence: [error instanceof Error ? error.message : String(error)],
        remediation: ["Fix the JSON syntax in .codex-plugin/plugin.json."],
        targetPath,
      }),
    );
    return { checks, metrics, artifacts };
  }

  const requiredFields = ["name", "version", "description", "author", "interface"];
  for (const field of requiredFields) {
    if (!(field in manifest)) {
      checks.push(
        createCheck({
          id: `manifest-missing-${field}`,
          category: "manifest",
          severity: "error",
          status: "fail",
          message: `plugin.json is missing the required \`${field}\` field.`,
          evidence: [manifestPath],
          remediation: [`Add \`${field}\` to plugin.json.`],
          targetPath,
        }),
      );
    }
  }

  if (manifest.name && !isHyphenCase(manifest.name)) {
    checks.push(
      createCheck({
        id: "manifest-name-not-hyphen-case",
        category: "manifest",
        severity: "error",
        status: "fail",
        message: "The plugin name should be lowercase hyphen-case.",
        evidence: [`Current name: ${manifest.name}`],
        remediation: ["Rename the plugin using lowercase letters, digits, and single hyphens only."],
        targetPath,
      }),
    );
  }

  if (manifest.name && manifest.name !== path.basename(pluginRoot)) {
    checks.push(
      createCheck({
        id: "manifest-name-directory-mismatch",
        category: "manifest",
        severity: "warning",
        status: "warn",
        message: "The plugin manifest name does not match the plugin directory name.",
        evidence: [`Directory: ${path.basename(pluginRoot)}`, `Manifest: ${manifest.name}`],
        remediation: ["Keep the plugin directory name and plugin.json name aligned."],
        targetPath,
      }),
    );
  }

  const interfaceFields = [
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "defaultPrompt",
  ];
  const iface = manifest.interface || {};
  for (const field of interfaceFields) {
    if (!(field in iface)) {
      checks.push(
        createCheck({
          id: `interface-missing-${field}`,
          category: "manifest",
          severity: "error",
          status: "fail",
          message: `plugin.json interface is missing \`${field}\`.`,
          evidence: [manifestPath],
          remediation: [`Add interface.${field} to plugin.json.`],
          targetPath,
        }),
      );
    }
  }

  const pathFields = [
    ["skills", manifest.skills],
    ["hooks", manifest.hooks],
    ["mcpServers", manifest.mcpServers],
    ["apps", manifest.apps],
    ["interface.composerIcon", iface.composerIcon],
    ["interface.logo", iface.logo],
  ];
  for (const [label, fieldValue] of pathFields) {
    if (!fieldValue) {
      continue;
    }
    if (typeof fieldValue !== "string" || !fieldValue.startsWith("./")) {
      checks.push(
        createCheck({
          id: `${label}-path-invalid`,
          category: "manifest",
          severity: "error",
          status: "fail",
          message: `${label} should use a plugin-relative path that starts with ./`,
          evidence: [`Current value: ${String(fieldValue)}`],
          remediation: [`Rewrite ${label} as a plugin-relative path like ./skills/.`],
          targetPath,
        }),
      );
      continue;
    }

    const resolvedPath = path.resolve(pluginRoot, fieldValue);
    if (!(await pathExists(resolvedPath))) {
      checks.push(
        createCheck({
          id: `${label}-path-missing`,
          category: "manifest",
          severity: "error",
          status: "fail",
          message: `${label} points to a missing file or directory.`,
          evidence: [fieldValue],
          remediation: [`Create the target for ${label} or remove the field.`],
          targetPath,
        }),
      );
    }
  }

  if (Array.isArray(iface.defaultPrompt)) {
    if (iface.defaultPrompt.length > 3) {
      checks.push(
        createCheck({
          id: "default-prompt-too-many",
          category: "manifest",
          severity: "warning",
          status: "warn",
          message: "Only the first three default prompts are used by Codex.",
          evidence: [`Prompt count: ${iface.defaultPrompt.length}`],
          remediation: ["Trim interface.defaultPrompt to three strong starters."],
          targetPath,
        }),
      );
    }
    const oversizedPrompts = iface.defaultPrompt.filter((prompt) => prompt.length > 128);
    if (oversizedPrompts.length > 0) {
      checks.push(
        createCheck({
          id: "default-prompt-too-long",
          category: "manifest",
          severity: "warning",
          status: "warn",
          message: "One or more default prompts exceed the UI-friendly length budget.",
          evidence: oversizedPrompts.map((prompt) => `${prompt.slice(0, 140)} (${prompt.length} chars)`),
          remediation: ["Keep default prompts under 128 characters and ideally closer to 50."],
          targetPath,
        }),
      );
    }
  }

  if (iface.brandColor && !/^#[0-9A-Fa-f]{6}$/.test(iface.brandColor)) {
    checks.push(
      createCheck({
        id: "brand-color-invalid",
        category: "manifest",
        severity: "warning",
        status: "warn",
        message: "brandColor should be a six-character hex color.",
        evidence: [`Current value: ${iface.brandColor}`],
        remediation: ["Use a color like #0F766E."],
        targetPath,
      }),
    );
  }

  const skillDirs = await discoverPluginSkillDirectories(pluginRoot, manifest);
  if (skillDirs.length === 0) {
    checks.push(
      createCheck({
        id: "plugin-skills-missing",
        category: "manifest",
        severity: "warning",
        status: "warn",
        message: "The plugin did not expose any discoverable skills.",
        evidence: [manifest.skills || "./skills/"],
        remediation: ["Add at least one skill under the configured skills path."],
        targetPath,
      }),
    );
  }

  for (const skillDir of skillDirs) {
    const prefix = `skill:${path.basename(skillDir)}`;
    const fragment = await evaluateSkill(skillDir, { prefix });
    checks.push(...fragment.checks);
    metrics.push(...fragment.metrics);
    artifacts.push(...fragment.artifacts);
  }

  metrics.push(
    createMetric({
      id: "plugin_skill_count",
      category: "manifest",
      value: skillDirs.length,
      unit: "skills",
      band: skillDirs.length > 0 ? "good" : "moderate",
      targetPath,
    }),
    createMetric({
      id: "plugin_keyword_count",
      category: "manifest",
      value: Array.isArray(manifest.keywords) ? manifest.keywords.length : 0,
      unit: "keywords",
      band: Array.isArray(manifest.keywords) && manifest.keywords.length > 0 ? "good" : "info",
      targetPath,
    }),
    createMetric({
      id: "plugin_default_prompt_count",
      category: "manifest",
      value: Array.isArray(iface.defaultPrompt) ? iface.defaultPrompt.length : 0,
      unit: "prompts",
      band:
        Array.isArray(iface.defaultPrompt) && iface.defaultPrompt.length <= 3
          ? "good"
          : "moderate",
      targetPath,
    }),
  );

  artifacts.push(
    createArtifact({
      id: "plugin-skill-inventory",
      type: "inventory",
      label: "Plugin skills",
      description: "Discoverable skills under the plugin.",
      data: {
        skills: skillDirs.map((skillDir) => relativePath(pluginRoot, skillDir)),
      },
    }),
  );

  return { checks, metrics, artifacts, manifest };
}
