import fs from "node:fs/promises";
import path from "node:path";

import { parseFrontmatter, parseYamlDocument } from "../lib/frontmatter.js";
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

const INSTRUCTION_EXTENSIONS = new Set([".md", ".txt", ".rst", ".adoc"]);
const NON_INSTRUCTION_DIRS = new Set(["src", "source", "lib", "scripts", "test", "tests", "__tests__", "fixtures", "__fixtures__", "config", "configs", "assets"]);
const SECRET_FILE_NAMES = /^(?:credentials|secrets|auth|cookies|tokens|session)\.(?:json|jsonc|txt|yaml|yml)$/i;

function isInstructionFile(filePath) {
  return INSTRUCTION_EXTENSIONS.has(path.extname(filePath).toLowerCase()) && !SECRET_FILE_NAMES.test(path.basename(filePath));
}

async function gatherPackageTextFiles(rootPath) {
  const files = await walkFiles(rootPath);
  return files.filter((filePath) => (isProbablyTextFile(filePath) || isInstructionFile(filePath)) && !SECRET_FILE_NAMES.test(path.basename(filePath)));
}

async function computeDeferredComponents(rootPath, excludeFiles = []) {
  const excluded = new Set(excludeFiles.map((filePath) => path.resolve(filePath)));
  const files = (await gatherPackageTextFiles(rootPath)).filter((filePath) =>
    !excluded.has(path.resolve(filePath)) && isInstructionFile(filePath) &&
    !path.relative(rootPath, filePath).split(path.sep).slice(0, -1).some((part) => NON_INSTRUCTION_DIRS.has(part.toLowerCase())),
  );
  const components = [];
  for (const filePath of files) {
    const content = await readText(filePath);
    components.push(
      createComponent(
        relativePath(rootPath, filePath),
        filePath,
        estimateTokenCount(content),
        "Potential supporting instructions; not evidence this file was loaded",
      ),
    );
  }
  return components;
}

function estimateBucket(components, basis, note) {
  return { value: sumTokenCounts(components), components, measurement: "static-token-estimate", observed: false, basis, note };
}

// All explicit context is opt-in. Do not guess dependencies from instruction prose
// or follow arbitrary references outside the selected package.
async function finishBudget(rawBudget, rootPath, options = {}) {
  const selected = options.additionalContextPaths ?? [];
  if (!Array.isArray(selected)) {
    throw new TypeError("additionalContextPaths must be an array of instruction file paths.");
  }
  const canonicalRoot = await fs.realpath(rootPath);
  const canonicalKey = (filePath) => process.platform === "win32" ? filePath.toLowerCase() : filePath;
  const included = new Set();
  for (const component of rawBudget.invoke_cost_tokens.components) {
    component.real_path = await fs.realpath(component.path);
    included.add(canonicalKey(component.real_path));
  }
  const additions = [];
  for (const selectedPath of selected) {
    if (typeof selectedPath !== "string" || !isInstructionFile(selectedPath)) {
      throw new TypeError(`additionalContextPaths requires a supported instruction file extension (.md, .txt, .rst, .adoc): ${selectedPath}`);
    }
    const resolvedPath = path.resolve(selectedPath);
    let realPath;
    try {
      realPath = await fs.realpath(resolvedPath);
      if (!(await fs.stat(realPath)).isFile()) throw new Error("not a regular file");
    } catch (error) {
      throw new Error(`additionalContextPaths cannot read ${resolvedPath}: ${error.message}`, { cause: error });
    }
    if (!isInstructionFile(realPath)) {
      throw new TypeError(`additionalContextPaths resolved to an unsupported instruction file: ${realPath}`);
    }
    const key = canonicalKey(realPath);
    if (included.has(key)) continue;
    const relative = path.relative(canonicalRoot, realPath);
    const scope = relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative)) ? "local" : "external";
    const component = {
      ...createComponent(relativePath(rootPath, resolvedPath), resolvedPath, estimateTokenCount(await readText(realPath)), "Explicitly selected context; static estimate, not observed runtime usage"),
      real_path: realPath,
      source: "additionalContextPaths",
      scope,
    };
    included.add(key);
    additions.push(component);
  }
  const deferred = [];
  const deferredSeen = new Set(included);
  for (const component of rawBudget.deferred_cost_tokens.components) {
    component.real_path = await fs.realpath(component.path);
    const key = canonicalKey(component.real_path);
    if (!deferredSeen.has(key)) deferred.push(component);
    deferredSeen.add(key);
  }
  const packageComponents = [];
  const packageSeen = new Set();
  for (const filePath of await gatherPackageTextFiles(rootPath)) {
    const realPath = await fs.realpath(filePath);
    const key = canonicalKey(realPath);
    if (packageSeen.has(key)) continue;
    packageSeen.add(key);
    packageComponents.push({ ...createComponent(relativePath(rootPath, filePath), filePath, estimateTokenCount(await readText(filePath)), "Package text inventory; not loaded context"), real_path: realPath });
  }
  return {
    ...rawBudget,
    method: rawBudget.method || "estimated-static",
    measurement: { version: 2, observed: false, tokenizer: "character-based-heuristic", scope: "selected local package and explicitly supplied instruction paths", runtime_usage: "unknown" },
    trigger_cost_tokens: estimateBucket(rawBudget.trigger_cost_tokens.components, "static-discovery-metadata-estimate", "Estimated discovery metadata; actual host serialization and load behavior are unmeasured."),
    invoke_cost_tokens: estimateBucket([...rawBudget.invoke_cost_tokens.components, ...additions], "static-invocation-scenario-estimate", "Estimated invocation scenario; plugin scenarios aggregate eligible skills rather than a measured single invocation."),
    deferred_cost_tokens: estimateBucket(deferred, "potential-supporting-instruction-inventory", "Optional human-readable supporting instructions, not actual loaded context; excludes source, scripts, tests, configuration and assets."),
    package_text_tokens: estimateBucket(packageComponents, "package-text-inventory", "Recognized text files from the package walker, including code; excluded directories, binaries, symlinks and known secret-file names are not inventoried. This is not a context or runtime usage measurement."),
    additional_context: { components: additions, value: sumTokenCounts(additions), source: "additionalContextPaths" },
    external_context: {
      coverage: "unknown",
      complete: false,
      discovery: "explicit-paths-only",
      components: additions.filter((component) => component.scope === "external"),
      note: "External dependencies are not inferred or resolved from freeform text. Explicit additions are counted once; other external context and runtime/tool output remain unknown.",
    },
  };
}

async function readInvocationPolicy(rootPath) {
  const policyPath = path.join(rootPath, "agents", "openai.yaml");
  if (!(await pathExists(policyPath))) {
    return {
      allowImplicitInvocation: true,
      path: null,
    };
  }

  try {
    const parsed = parseYamlDocument(await readText(policyPath));
    return {
      allowImplicitInvocation: parsed?.policy?.allow_implicit_invocation !== false,
      path: policyPath,
    };
  } catch {
    return {
      allowImplicitInvocation: true,
      path: policyPath,
    };
  }
}

export async function computeSkillBudget(skillRoot, options = {}) {
  const skillPath = path.join(skillRoot, "SKILL.md");
  const content = await readText(skillPath);
  const parsed = parseFrontmatter(content);
  const name = parsed.data?.name || path.basename(skillRoot);
  const description = parsed.data?.description || "";
  const invocationPolicy = await readInvocationPolicy(skillRoot);

  const triggerComponents = invocationPolicy.allowImplicitInvocation ? [
    createComponent("skill-name", skillPath, estimateTokenCount(name), "Candidate discovery identifier; actual host exposure is unmeasured"),
    createComponent(
      "skill-description",
      skillPath,
      estimateTokenCount(description),
      "Candidate discovery description; actual host exposure is unmeasured",
    ),
  ] : [];

  const invokeComponents = [
    createComponent("skill-file", skillPath, estimateTokenCount(content), "Full skill text in the static invocation scenario; not an observed load"),
  ];

  const deferredComponents = await computeDeferredComponents(skillRoot, [skillPath]);

  return finishBudget({
    kind: "skill",
    method: invocationPolicy.allowImplicitInvocation ? "estimated-static" : "estimated-static-policy-aware",
    invocation_policy: {
      allow_implicit_invocation: invocationPolicy.allowImplicitInvocation,
      ...(invocationPolicy.path ? { path: invocationPolicy.path } : {}),
    },
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
  }, skillRoot, options);
}

export async function computePluginBudget(pluginRoot, manifest, options = {}) {
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
      estimateTokenCount(Array.isArray(manifest?.interface?.defaultPrompt) ? manifest.interface.defaultPrompt.join("\n") : (manifest?.interface?.defaultPrompt || "")),
      "Starter prompts visible in the UI; model-context inclusion is unmeasured",
    ),
  ];

  const invokeComponents = [
    createComponent("plugin-manifest", manifestPath, estimateTokenCount(manifestContent), "Manifest text included in the static scenario; actual model-context inclusion is unmeasured"),
  ];
  const explicitOnlyComponents = [];
  const implicitSkills = [];
  const explicitOnlySkills = [];

  for (const skillDir of skillDirs) {
    const skillPath = path.join(skillDir, "SKILL.md");
    if (!(await pathExists(skillPath))) {
      continue;
    }
    const content = await readText(skillPath);
    const parsed = parseFrontmatter(content);
    const skillName = path.basename(skillDir);
    const invocationPolicy = await readInvocationPolicy(skillDir);

    if (invocationPolicy.allowImplicitInvocation) {
      implicitSkills.push(skillName);
      triggerComponents.push(
        createComponent(
          `${skillName}-description`,
          skillPath,
          estimateTokenCount(parsed.data?.description || ""),
          "Skill trigger description exposed through the plugin",
        ),
      );
      invokeComponents.push(
        createComponent(
          `${skillName}-skill-file`,
          skillPath,
          estimateTokenCount(content),
          "Eligible skill text in an aggregate static scenario; not a measured invocation or proven ceiling",
        ),
      );
    } else {
      explicitOnlySkills.push(skillName);
      explicitOnlyComponents.push(
        createComponent(
          `${skillName}-skill-file`,
          skillPath,
          estimateTokenCount(content),
          "Explicit-only skill file; excluded from implicit trigger/invoke budget",
        ),
      );
    }
  }

  const deferredComponents = await computeDeferredComponents(pluginRoot, [
    manifestPath,
    ...skillDirs.map((skillDir) => path.join(skillDir, "SKILL.md")),
  ]);

  return finishBudget({
    kind: "plugin",
    method: explicitOnlySkills.length > 0 ? "estimated-static-policy-aware" : "estimated-static",
    invocation_policy: {
      implicit_skill_count: implicitSkills.length,
      explicit_only_skill_count: explicitOnlySkills.length,
      implicit_skills: implicitSkills,
      explicit_only_skills: explicitOnlySkills,
    },
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
    explicit_only_invoke_cost_tokens: estimateBucket(explicitOnlyComponents, "explicit-only-skill-text-inventory", "Alternative explicit-only skill text; excluded from the implicit invocation scenario unless selected in additionalContextPaths."),
  }, pluginRoot, options);
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

export async function computeBudgetProfile(target, options = {}) {
  if (target.kind === "skill") {
    return computeSkillBudget(target.path, options);
  }
  if (target.kind === "plugin") {
    const manifest = await readJson(path.join(target.path, ".codex-plugin", "plugin.json"));
    return computePluginBudget(target.path, manifest, options);
  }

  const components = await computeDeferredComponents(target.path);
  return finishBudget({
    kind: target.kind,
    trigger_cost_tokens: { value: 0, components: [] },
    invoke_cost_tokens: { value: 0, components: [] },
    deferred_cost_tokens: { value: sumTokenCounts(components), components },
  }, target.path, options);
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
  const deferred = {
    ...rawBudget.deferred_cost_tokens,
    band: "unrated",
    calibration_note: "Supporting instruction inventory is not measured runtime context. Historical all-package-text thresholds are inapplicable.",
  };
  const explicitOnly = rawBudget.explicit_only_invoke_cost_tokens
    ? buildBudgetBucket(
        rawBudget.explicit_only_invoke_cost_tokens.value,
        profile.invoke_cost_tokens,
        rawBudget.explicit_only_invoke_cost_tokens.components,
      )
    : null;
  const calibrationNote = "Descriptive static size comparison only; thresholds are not calibrated runtime-context, quality, cost or efficiency measurements.";
  const total = trigger.value + invoke.value;
  return {
    ...rawBudget,
    method: rawBudget.method || "estimated-static",
    ...(rawBudget.invocation_policy ? { invocation_policy: rawBudget.invocation_policy } : {}),
    trigger_cost_tokens: { ...rawBudget.trigger_cost_tokens, ...trigger, calibration_note: calibrationNote },
    invoke_cost_tokens: { ...rawBudget.invoke_cost_tokens, ...invoke, calibration_note: calibrationNote },
    deferred_cost_tokens: deferred,
    ...(explicitOnly ? { explicit_only_invoke_cost_tokens: { ...rawBudget.explicit_only_invoke_cost_tokens, ...explicitOnly, calibration_note: calibrationNote } } : {}),
    total_tokens: {
      value: total,
      band: "unrated",
      observed: false,
      measurement: "static-token-estimate",
      basis: "trigger-plus-invocation-scenario-estimate",
      note: "Static aggregate of discovery metadata and the invocation scenario, not observed context or billing usage. Optional supporting inventory and package inventory are excluded; external dependencies may be missing.",
    },
  };
}
