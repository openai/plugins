import path from "node:path";

import { createArtifact, createCheck, createMetric } from "../core/schema.js";
import { parseFrontmatter } from "../lib/frontmatter.js";
import { pathExists, readText, relativePath, walkFiles } from "../lib/files.js";

const ALLOWED_FRONTMATTER_KEYS = new Set([
  "name",
  "description",
  "license",
  "allowed-tools",
  "metadata",
  "disable-model-invocation",
  "user-invocable",
  "context",
  "agent",
]);

function countCodeFences(markdown) {
  return (markdown.match(/```/g) || []).length / 2;
}

function findRelativeLinks(markdown) {
  return [...markdown.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)]
    .map((match) => match[1])
    .filter(
      (target) =>
        !target.startsWith("http://") &&
        !target.startsWith("https://") &&
        !target.startsWith("app://") &&
        !target.startsWith("plugin://") &&
        !target.startsWith("rules://") &&
        !target.startsWith("mailto:") &&
        !target.startsWith("#"),
    );
}

function isHyphenCase(value) {
  return /^[a-z0-9-]+$/.test(value) && !value.startsWith("-") && !value.endsWith("-") && !value.includes("--");
}

export async function evaluateSkill(skillRoot, options = {}) {
  const prefix = options.prefix ? `${options.prefix}:` : "";
  const skillPath = path.join(skillRoot, "SKILL.md");
  const targetPath = relativePath(process.cwd(), skillRoot);
  const checks = [];
  const metrics = [];
  const artifacts = [];

  if (!(await pathExists(skillPath))) {
    checks.push(
      createCheck({
        id: `${prefix}skill-file-missing`,
        category: "skill-structure",
        severity: "error",
        status: "fail",
        message: "The target skill directory is missing SKILL.md.",
        evidence: [targetPath],
        remediation: ["Add SKILL.md to the skill root."],
        targetPath,
      }),
    );
    return { checks, metrics, artifacts };
  }

  const content = await readText(skillPath);
  const lines = content.replace(/\r\n/g, "\n").split("\n");
  const parsed = parseFrontmatter(content);
  const relativeLinks = findRelativeLinks(content);
  const supportFiles = (await walkFiles(skillRoot)).filter((filePath) => filePath !== skillPath);

  if (parsed.errors.length > 0) {
    checks.push(
      createCheck({
        id: `${prefix}frontmatter-invalid`,
        category: "skill-structure",
        severity: "error",
        status: "fail",
        message: "The skill frontmatter could not be parsed.",
        evidence: parsed.errors,
        remediation: ["Fix the YAML frontmatter at the top of SKILL.md."],
        targetPath,
      }),
    );
  }

  const frontmatter = parsed.data || {};
  const unexpectedKeys = Object.keys(frontmatter).filter((key) => !ALLOWED_FRONTMATTER_KEYS.has(key));
  if (unexpectedKeys.length > 0) {
    checks.push(
      createCheck({
        id: `${prefix}frontmatter-extra-keys`,
        category: "best-practice",
        severity: "warning",
        status: "warn",
        message: "The skill frontmatter contains keys outside the common Codex skill conventions.",
        evidence: unexpectedKeys.map((key) => `Unexpected key: ${key}`),
        remediation: ["Remove non-standard frontmatter keys or move the metadata into references."],
        targetPath,
      }),
    );
  }

  if (!frontmatter.name) {
    checks.push(
      createCheck({
        id: `${prefix}name-missing`,
        category: "skill-structure",
        severity: "error",
        status: "fail",
        message: "The skill frontmatter is missing `name`.",
        evidence: [targetPath],
        remediation: ["Add a hyphen-case `name` field to the frontmatter."],
        targetPath,
      }),
    );
  } else if (!isHyphenCase(frontmatter.name)) {
    checks.push(
      createCheck({
        id: `${prefix}name-not-hyphen-case`,
        category: "skill-structure",
        severity: "error",
        status: "fail",
        message: "The skill name should be lowercase hyphen-case.",
        evidence: [`Current name: ${frontmatter.name}`],
        remediation: ["Rename the skill using lowercase letters, digits, and single hyphens only."],
        targetPath,
      }),
    );
  }

  if (!frontmatter.description) {
    checks.push(
      createCheck({
        id: `${prefix}description-missing`,
        category: "skill-structure",
        severity: "error",
        status: "fail",
        message: "The skill frontmatter is missing `description`.",
        evidence: [targetPath],
        remediation: ["Add a description that explains what the skill does and when to use it."],
        targetPath,
      }),
    );
  } else {
    if (frontmatter.description.length > 1024) {
      checks.push(
        createCheck({
          id: `${prefix}description-too-long`,
          category: "budget",
          severity: "warning",
          status: "warn",
          message: "The skill description is long enough to create unnecessary always-loaded context cost.",
          evidence: [`Description length: ${frontmatter.description.length} characters`],
          remediation: ["Shorten the description and push details into SKILL.md or references."],
          targetPath,
        }),
      );
    }
    if (!/use when/i.test(frontmatter.description)) {
      checks.push(
        createCheck({
          id: `${prefix}description-trigger-weak`,
          category: "best-practice",
          severity: "warning",
          status: "warn",
          message: "The description does not clearly advertise when the skill should trigger.",
          evidence: ["Descriptions are the primary auto-load surface in Codex."],
          remediation: ["Rewrite the description to include a clear 'Use when ...' trigger sentence."],
          targetPath,
        }),
      );
    }
  }

  if (lines.length > 800) {
    checks.push(
      createCheck({
        id: `${prefix}skill-too-large`,
        category: "budget",
        severity: "error",
        status: "fail",
        message: "SKILL.md is extremely large for an always-loaded invocation surface.",
        evidence: [`Line count: ${lines.length}`],
        remediation: ["Move large details into references/ and keep SKILL.md focused on the core workflow."],
        targetPath,
      }),
    );
  } else if (lines.length > 500) {
    checks.push(
      createCheck({
        id: `${prefix}skill-large`,
        category: "budget",
        severity: "warning",
        status: "warn",
        message: "SKILL.md exceeds the recommended compact size for progressive disclosure.",
        evidence: [`Line count: ${lines.length}`],
        remediation: ["Trim repetitive detail and move long variants into references/."],
        targetPath,
      }),
    );
  }

  if (lines.length > 350 && supportFiles.filter((filePath) => filePath.includes("/references/")).length === 0) {
    checks.push(
      createCheck({
        id: `${prefix}progressive-disclosure-missing`,
        category: "best-practice",
        severity: "warning",
        status: "warn",
        message: "The skill is getting large without using references for progressive disclosure.",
        evidence: ["Large skills are easier to maintain when variants live under references/."],
        remediation: ["Move deep detail or edge-case variants into references/ and link them from SKILL.md."],
        targetPath,
      }),
    );
  }

  const brokenLinks = [];
  for (const target of relativeLinks) {
    const candidatePath = path.resolve(skillRoot, target);
    if (!(await pathExists(candidatePath))) {
      brokenLinks.push(target);
    }
  }
  if (brokenLinks.length > 0) {
    checks.push(
      createCheck({
        id: `${prefix}broken-relative-links`,
        category: "skill-structure",
        severity: "error",
        status: "fail",
        message: "The skill contains relative links that do not resolve inside the skill directory.",
        evidence: brokenLinks,
        remediation: ["Fix or remove broken links in SKILL.md."],
        targetPath,
      }),
    );
  }

  const extraDocs = supportFiles
    .map((filePath) => path.basename(filePath))
    .filter((name) => ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"].includes(name));
  if (extraDocs.length > 0) {
    checks.push(
      createCheck({
        id: `${prefix}extra-doc-files`,
        category: "best-practice",
        severity: "warning",
        status: "warn",
        message: "The skill includes extra documentation files that usually belong in references/ or outside the skill bundle.",
        evidence: extraDocs,
        remediation: ["Move reusable guidance into references/ and avoid extra top-level docs inside the skill bundle."],
        targetPath,
      }),
    );
  }

  metrics.push(
    createMetric({
      id: `${prefix}skill_line_count`,
      category: "budget",
      value: lines.length,
      unit: "lines",
      band: lines.length > 500 ? "heavy" : lines.length > 350 ? "moderate" : "good",
      targetPath,
    }),
    createMetric({
      id: `${prefix}description_length_chars`,
      category: "budget",
      value: String(frontmatter.description || "").length,
      unit: "chars",
      band:
        String(frontmatter.description || "").length > 1024
          ? "heavy"
          : String(frontmatter.description || "").length > 512
            ? "moderate"
            : "good",
      targetPath,
    }),
    createMetric({
      id: `${prefix}relative_link_count`,
      category: "documentation",
      value: relativeLinks.length,
      unit: "links",
      band: relativeLinks.length > 10 ? "moderate" : "good",
      targetPath,
    }),
    createMetric({
      id: `${prefix}code_fence_count`,
      category: "readability",
      value: countCodeFences(content),
      unit: "blocks",
      band: countCodeFences(content) > 8 ? "moderate" : "good",
      targetPath,
    }),
    createMetric({
      id: `${prefix}support_file_count`,
      category: "documentation",
      value: supportFiles.length,
      unit: "files",
      band: supportFiles.length > 0 ? "good" : "info",
      targetPath,
    }),
  );

  artifacts.push(
    createArtifact({
      id: `${prefix}skill-link-inventory`,
      type: "inventory",
      label: "Skill relative links",
      description: "Relative links found in SKILL.md.",
      data: {
        links: relativeLinks,
      },
    }),
  );

  return { checks, metrics, artifacts };
}
