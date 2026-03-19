#!/usr/bin/env node

// hooks/src/posttooluse-validate.mts
import { createHash } from "crypto";
import { readFileSync, realpathSync } from "fs";
import { join, resolve } from "path";
import { fileURLToPath } from "url";
import { detectPlatform } from "./compat.mjs";
import {
  pluginRoot as resolvePluginRoot,
  readSessionFile,
  safeReadFile,
  writeSessionFile,
  tryClaimSessionKey,
  syncSessionFileFromClaims
} from "./hook-env.mjs";
import { buildSkillMap, extractFrontmatter } from "./skill-map-frontmatter.mjs";
import {
  compileSkillPatterns,
  matchPathWithReason,
  matchImportWithReason
} from "./patterns.mjs";
import { createLogger } from "./logger.mjs";
var PLUGIN_ROOT = resolvePluginRoot();
var SUPPORTED_TOOLS = ["Write", "Edit"];
var VALIDATED_FILES_ENV_KEY = "VERCEL_PLUGIN_VALIDATED_FILES";
var CHAIN_BUDGET_BYTES = 18e3;
var DEFAULT_CHAIN_CAP = 2;
function resolveToolFilePaths(toolInput) {
  const collected = [];
  const pushPath = (value) => {
    if (typeof value !== "string") return;
    const trimmed = value.trim();
    if (trimmed !== "") {
      collected.push(trimmed);
    }
  };
  pushPath(toolInput.file_path);
  if (Array.isArray(toolInput.file_paths)) {
    for (const value of toolInput.file_paths) {
      pushPath(value);
    }
  }
  if (Array.isArray(toolInput.files)) {
    for (const value of toolInput.files) {
      if (typeof value === "string") {
        pushPath(value);
        continue;
      }
      if (value && typeof value === "object" && "file_path" in value) {
        pushPath(value.file_path);
      }
    }
  }
  return [...new Set(collected)];
}
function resolveSessionId(input) {
  const sessionId = input.session_id ?? input.conversation_id;
  return typeof sessionId === "string" && sessionId.trim() !== "" ? sessionId : null;
}
function resolveHookCwd(input, env) {
  const workspaceRoot = Array.isArray(input.workspace_roots) ? input.workspace_roots[0] : void 0;
  const candidate = input.cwd ?? workspaceRoot ?? env.CURSOR_PROJECT_DIR ?? env.CLAUDE_PROJECT_ROOT ?? process.cwd();
  return typeof candidate === "string" && candidate.trim() !== "" ? candidate : process.cwd();
}
function formatPlatformOutput(platform, additionalContext, env) {
  if (!additionalContext) {
    return "{}";
  }
  if (platform === "cursor") {
    const output2 = {
      additional_context: additionalContext
    };
    if (env && Object.keys(env).length > 0) {
      output2.env = env;
    }
    return JSON.stringify(output2);
  }
  const output = {
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext
    }
  };
  return JSON.stringify(output);
}
function validationRuleId(skill, rule) {
  return `${skill}::${rule.pattern}`;
}
var log = createLogger();
function parseInput(raw, logger, env = process.env) {
  const l = logger || log;
  const trimmed = (raw || "").trim();
  if (!trimmed) {
    l.debug("posttooluse-validate-skip", { reason: "stdin_empty" });
    return null;
  }
  let input;
  try {
    input = JSON.parse(trimmed);
  } catch {
    l.debug("posttooluse-validate-skip", { reason: "stdin_parse_fail" });
    return null;
  }
  const toolName = input.tool_name || "";
  if (!SUPPORTED_TOOLS.includes(toolName)) {
    l.debug("posttooluse-validate-skip", { reason: "unsupported_tool", toolName });
    return null;
  }
  const toolInput = input.tool_input || {};
  const filePaths = resolveToolFilePaths(toolInput);
  const filePath = filePaths[0] || "";
  if (!filePath) {
    l.debug("posttooluse-validate-skip", { reason: "no_file_path", toolName });
    return null;
  }
  const sessionId = resolveSessionId(input);
  const cwd = resolveHookCwd(input, env);
  const platform = detectPlatform(input);
  l.debug("posttooluse-validate-input", {
    toolName,
    filePath,
    filePathsCount: filePaths.length,
    sessionId,
    cwd,
    platform
  });
  return { toolName, filePath, filePaths, sessionId, cwd, platform };
}
function loadValidateRules(pluginRoot, logger) {
  const l = logger || log;
  const skillsDir = join(pluginRoot, "skills");
  const { skills: skillMap } = buildSkillMap(skillsDir);
  const rulesMap = /* @__PURE__ */ new Map();
  const chainMap = /* @__PURE__ */ new Map();
  for (const [slug, config] of Object.entries(skillMap)) {
    if (config.validate && config.validate.length > 0) {
      rulesMap.set(slug, config.validate);
    }
    if (config.chainTo && config.chainTo.length > 0) {
      chainMap.set(slug, config.chainTo);
    }
  }
  if (rulesMap.size === 0 && chainMap.size === 0) {
    l.debug("posttooluse-validate-skip", { reason: "no_validate_rules" });
    return null;
  }
  const compiledSkills = compileSkillPatterns(skillMap);
  l.debug("posttooluse-validate-loaded", {
    totalSkills: Object.keys(skillMap).length,
    skillsWithRules: rulesMap.size,
    skillsWithChainTo: chainMap.size
  });
  return { skillMap, compiledSkills, rulesMap, chainMap };
}
function matchFileToSkills(filePath, fileContent, compiledSkills, rulesMap, logger, chainMap) {
  const l = logger || log;
  const matched = [];
  for (const entry of compiledSkills) {
    if (!rulesMap.has(entry.skill) && !chainMap?.has(entry.skill)) continue;
    const pathMatch = matchPathWithReason(filePath, entry.compiledPaths);
    if (pathMatch) {
      matched.push(entry.skill);
      l.trace("posttooluse-validate-match", {
        skill: entry.skill,
        matchType: "path",
        pattern: pathMatch.pattern
      });
      continue;
    }
    const importMatch = matchImportWithReason(fileContent, entry.compiledImports);
    if (importMatch) {
      matched.push(entry.skill);
      l.trace("posttooluse-validate-match", {
        skill: entry.skill,
        matchType: "import",
        pattern: importMatch.pattern
      });
    }
  }
  l.debug("posttooluse-validate-matched", { matchedSkills: matched });
  return matched;
}
function runValidation(fileContent, matchedSkills, rulesMap, logger, filePath) {
  const l = logger || log;
  const violations = [];
  const lines = fileContent.split("\n");
  for (const skill of matchedSkills) {
    const rules = rulesMap.get(skill);
    if (!rules) continue;
    for (const rule of rules) {
      const ruleId = validationRuleId(skill, rule);
      if (rule.skipIfFileContains) {
        try {
          if (new RegExp(rule.skipIfFileContains, "m").test(fileContent)) {
            l.trace("posttooluse-validate-rule-skip", {
              skill,
              pattern: rule.pattern,
              reason: "skipIfFileContains matched"
            });
            continue;
          }
        } catch {
        }
      }
      let regex;
      try {
        regex = new RegExp(rule.pattern, "g");
      } catch {
        l.debug("posttooluse-validate-regex-fail", {
          skill,
          pattern: rule.pattern
        });
        continue;
      }
      for (let i = 0; i < lines.length; i++) {
        regex.lastIndex = 0;
        const match = regex.exec(lines[i]);
        if (match) {
          violations.push({
            skill,
            line: i + 1,
            message: rule.message,
            severity: rule.severity,
            matchedText: match[0].slice(0, 80),
            filePath,
            ruleId,
            upgradeToSkill: rule.upgradeToSkill,
            upgradeWhy: rule.upgradeWhy,
            upgradeMode: rule.upgradeMode ?? (rule.upgradeToSkill ? "soft" : void 0)
          });
        }
      }
    }
  }
  l.debug("posttooluse-validate-violations", {
    total: violations.length,
    errors: violations.filter((v) => v.severity === "error").length,
    recommended: violations.filter((v) => v.severity === "recommended").length,
    warns: violations.filter((v) => v.severity === "warn").length
  });
  return violations;
}
function runChainInjection(fileContent, matchedSkills, chainMap, sessionId, pluginRoot, logger, env = process.env) {
  const l = logger || log;
  const result = { injected: [], totalBytes: 0 };
  const chainCap = Math.max(1, parseInt(env.VERCEL_PLUGIN_CHAIN_CAP || "", 10) || DEFAULT_CHAIN_CAP);
  const candidates = [];
  for (const skill of matchedSkills) {
    const rules = chainMap.get(skill);
    if (!rules) continue;
    for (const rule of rules) {
      if (rule.skipIfFileContains) {
        try {
          if (new RegExp(rule.skipIfFileContains, "m").test(fileContent)) {
            l.debug("posttooluse-chain-skip-contains", {
              skill,
              targetSkill: rule.targetSkill,
              reason: "skipIfFileContains matched"
            });
            continue;
          }
        } catch {
        }
      }
      try {
        const regex = new RegExp(rule.pattern, "m");
        if (regex.test(fileContent)) {
          candidates.push({ sourceSkill: skill, rule });
        }
      } catch {
        l.debug("posttooluse-chain-regex-fail", {
          skill,
          pattern: rule.pattern
        });
      }
    }
  }
  if (candidates.length === 0) return result;
  const seenTargets = /* @__PURE__ */ new Set();
  const uniqueCandidates = candidates.filter(({ rule }) => {
    if (seenTargets.has(rule.targetSkill)) return false;
    seenTargets.add(rule.targetSkill);
    return true;
  });
  const fileSeen = sessionId ? readSessionFile(sessionId, "seen-skills") : "";
  const seenSet = new Set(fileSeen.split(",").filter(Boolean));
  for (const { sourceSkill, rule } of uniqueCandidates) {
    if (result.injected.length >= chainCap) {
      l.debug("posttooluse-chain-cap-reached", {
        cap: chainCap,
        remaining: uniqueCandidates.length - result.injected.length
      });
      break;
    }
    if (seenSet.has(rule.targetSkill)) {
      l.debug("posttooluse-chain-skip-dedup", {
        sourceSkill,
        targetSkill: rule.targetSkill
      });
      continue;
    }
    const skillPath = join(pluginRoot, "skills", rule.targetSkill, "SKILL.md");
    const skillContent = safeReadFile(skillPath);
    if (!skillContent) {
      l.debug("posttooluse-chain-skip-missing", {
        sourceSkill,
        targetSkill: rule.targetSkill,
        path: skillPath
      });
      continue;
    }
    const { body } = extractFrontmatter(skillContent);
    const trimmedBody = body.trim();
    if (!trimmedBody) continue;
    const bytes = Buffer.byteLength(trimmedBody, "utf-8");
    if (result.totalBytes + bytes > CHAIN_BUDGET_BYTES) {
      l.debug("posttooluse-chain-budget-exceeded", {
        sourceSkill,
        targetSkill: rule.targetSkill,
        bytes,
        totalBytes: result.totalBytes,
        budget: CHAIN_BUDGET_BYTES
      });
      break;
    }
    if (sessionId) {
      const claimed = tryClaimSessionKey(sessionId, "seen-skills", rule.targetSkill);
      if (!claimed) {
        l.debug("posttooluse-chain-skip-concurrent-claim", {
          sourceSkill,
          targetSkill: rule.targetSkill
        });
        seenSet.add(rule.targetSkill);
        continue;
      }
      syncSessionFileFromClaims(sessionId, "seen-skills");
    }
    seenSet.add(rule.targetSkill);
    result.injected.push({
      sourceSkill,
      targetSkill: rule.targetSkill,
      message: rule.message,
      content: trimmedBody
    });
    result.totalBytes += bytes;
    l.debug("posttooluse-chain-injected", {
      sourceSkill,
      targetSkill: rule.targetSkill,
      bytes,
      totalBytes: result.totalBytes
    });
  }
  if (result.injected.length > 0) {
    l.summary("posttooluse-chain-result", {
      injectedCount: result.injected.length,
      totalBytes: result.totalBytes,
      targets: result.injected.map((i) => i.targetSkill)
    });
  }
  return result;
}
function contentHash(content) {
  return createHash("md5").update(content).digest("hex").slice(0, 12);
}
function parseValidatedFiles(envValue) {
  if (typeof envValue !== "string" || envValue.trim() === "") {
    return /* @__PURE__ */ new Set();
  }
  const set = /* @__PURE__ */ new Set();
  for (const part of envValue.split(",")) {
    const trimmed = part.trim();
    if (trimmed !== "") set.add(trimmed);
  }
  return set;
}
function appendValidatedFile(envValue, entry) {
  const current = typeof envValue === "string" ? envValue.trim() : "";
  return current === "" ? entry : `${current},${entry}`;
}
function isAlreadyValidated(filePath, hash, sessionId) {
  const entry = `${filePath}:${hash}`;
  const validated = parseValidatedFiles(process.env.VERCEL_PLUGIN_VALIDATED_FILES);
  if (validated.has(entry)) {
    return true;
  }
  if (!sessionId) {
    return false;
  }
  const persisted = parseValidatedFiles(readSessionFile(sessionId, "validated-files"));
  return persisted.has(entry);
}
function markValidated(filePath, hash, sessionId) {
  const entry = `${filePath}:${hash}`;
  const persistedState = sessionId ? readSessionFile(sessionId, "validated-files") : "";
  const current = process.env[VALIDATED_FILES_ENV_KEY] || persistedState;
  const next = appendValidatedFile(current, entry);
  process.env[VALIDATED_FILES_ENV_KEY] = next;
  if (sessionId) {
    writeSessionFile(sessionId, "validated-files", next);
  }
  return next;
}
function formatOutput(violations, matchedSkills, filePath, logger, platform = "claude-code", env, chainResult) {
  const l = logger || log;
  const hasChains = chainResult && chainResult.injected.length > 0;
  if (violations.length === 0 && !hasChains) {
    l.debug("posttooluse-validate-no-output", { reason: "no_actionable_violations" });
    return "{}";
  }
  const errors = violations.filter((v) => v.severity === "error");
  const recommended = violations.filter((v) => v.severity === "recommended");
  const warns = violations.filter((v) => v.severity === "warn");
  const hasErrors = errors.length > 0;
  const hasRecommended = recommended.length > 0;
  const hasWarns = warns.length > 0;
  const bySkill = /* @__PURE__ */ new Map();
  for (const v of violations) {
    if (!bySkill.has(v.skill)) bySkill.set(v.skill, []);
    bySkill.get(v.skill).push(v);
  }
  const emittedUpgradeSkills = /* @__PURE__ */ new Set();
  const formatViolationLine = (violation, label) => {
    const lines = [`- Line ${violation.line} [${label}]: ${violation.message}`];
    if (violation.upgradeToSkill && !emittedUpgradeSkills.has(violation.upgradeToSkill)) {
      emittedUpgradeSkills.add(violation.upgradeToSkill);
      const reason = violation.upgradeWhy ? ` Reason: ${violation.upgradeWhy}` : "";
      const prefix = violation.upgradeMode === "hard" ? "REQUIRED: " : "";
      lines.push("");
      lines.push(`${prefix}Use the Skill tool now to load ${violation.upgradeToSkill}.${reason}`);
      lines.push(
        `<!-- skillUpgrade: ${JSON.stringify({
          from: violation.skill,
          to: violation.upgradeToSkill,
          line: violation.line
        })} -->`
      );
    }
    return lines.join("\n");
  };
  const parts = [];
  for (const [skill, skillViolations] of bySkill) {
    const errorLines = skillViolations.filter((v) => v.severity === "error").map((v) => formatViolationLine(v, "ERROR"));
    const recommendedLines = skillViolations.filter((v) => v.severity === "recommended").map((v) => formatViolationLine(v, "RECOMMENDED"));
    const warnLines = skillViolations.filter((v) => v.severity === "warn").map((v) => formatViolationLine(v, "SUGGESTION"));
    parts.push([...errorLines, ...recommendedLines, ...warnLines].join("\n"));
  }
  const skillList = [...bySkill.keys()].join(", ");
  const counts = [
    hasErrors ? `${errors.length} error${errors.length > 1 ? "s" : ""}` : "",
    hasRecommended ? `${recommended.length} recommendation${recommended.length > 1 ? "s" : ""}` : "",
    hasWarns ? `${warns.length} suggestion${warns.length > 1 ? "s" : ""}` : ""
  ].filter(Boolean).join(", ");
  const callToAction = hasErrors ? `Please fix these issues before proceeding.` : hasRecommended ? `Apply these recommendations before continuing \u2014 they reflect current best practices.` : `Consider applying these suggestions to follow best practices.`;
  const contextParts = [];
  if (violations.length > 0) {
    contextParts.push(
      `<!-- posttooluse-validate: ${skillList} -->`,
      `VALIDATION (${counts}) for \`${filePath}\`:`,
      ...parts,
      callToAction,
      `<!-- /posttooluse-validate -->`
    );
  }
  if (hasChains) {
    for (const chain of chainResult.injected) {
      const reason = chain.message ? ` ${chain.message}` : "";
      contextParts.push(
        `<!-- posttooluse-chain: ${chain.sourceSkill} \u2192 ${chain.targetSkill} -->`,
        `**Skill context auto-loaded** (${chain.targetSkill}):${reason}`,
        "",
        chain.content,
        `<!-- /posttooluse-chain: ${chain.targetSkill} -->`
      );
    }
  }
  const context = contextParts.join("\n");
  const chainedSkills = hasChains ? chainResult.injected.map((c) => c.targetSkill) : [];
  const metadata = {
    version: 1,
    hook: "posttooluse-validate",
    filePath,
    matchedSkills,
    errorCount: errors.length,
    recommendedCount: recommended.length,
    warnCount: warns.length,
    chainedSkills
  };
  const metaComment = `<!-- postValidation: ${JSON.stringify(metadata)} -->`;
  l.summary("posttooluse-validate-output", {
    filePath,
    matchedSkills,
    errorCount: errors.length,
    recommendedCount: recommended.length,
    warnCount: warns.length,
    chainedSkills
  });
  return formatPlatformOutput(platform, context + "\n" + metaComment, env);
}
function run() {
  const timing = {};
  const tStart = log.active ? log.now() : 0;
  let raw;
  try {
    raw = readFileSync(0, "utf-8");
  } catch {
    return "{}";
  }
  const parsed = parseInput(raw, log);
  if (!parsed) return "{}";
  if (log.active) timing.parse = Math.round(log.now() - tStart);
  const { toolName, filePath, sessionId, cwd, platform } = parsed;
  const resolvedPath = cwd ? resolve(cwd, filePath) : filePath;
  const fileContent = safeReadFile(resolvedPath);
  if (!fileContent) {
    log.debug("posttooluse-validate-skip", { reason: "file_unreadable", filePath: resolvedPath });
    return "{}";
  }
  const hash = contentHash(fileContent);
  if (isAlreadyValidated(filePath, hash, sessionId)) {
    log.debug("posttooluse-validate-skip", { reason: "already_validated", filePath, hash });
    return "{}";
  }
  const tLoad = log.active ? log.now() : 0;
  const data = loadValidateRules(PLUGIN_ROOT, log);
  if (!data) return "{}";
  if (log.active) timing.load = Math.round(log.now() - tLoad);
  const { compiledSkills, rulesMap, chainMap } = data;
  const tMatch = log.active ? log.now() : 0;
  const matchedSkills = matchFileToSkills(filePath, fileContent, compiledSkills, rulesMap, log, chainMap);
  if (log.active) timing.match = Math.round(log.now() - tMatch);
  if (matchedSkills.length === 0) {
    log.debug("posttooluse-validate-skip", { reason: "no_skill_match", filePath });
    markValidated(filePath, hash, sessionId);
    return "{}";
  }
  const tValidate = log.active ? log.now() : 0;
  const violations = runValidation(fileContent, matchedSkills, rulesMap, log);
  if (log.active) timing.validate = Math.round(log.now() - tValidate);
  const tChain = log.active ? log.now() : 0;
  const chainResult = runChainInjection(
    fileContent,
    matchedSkills,
    chainMap,
    sessionId,
    PLUGIN_ROOT,
    log
  );
  if (log.active) timing.chain = Math.round(log.now() - tChain);
  const validatedFiles = markValidated(filePath, hash, sessionId);
  const hasOutput = violations.length > 0 || chainResult.injected.length > 0;
  const cursorEnv = platform === "cursor" && hasOutput ? { [VALIDATED_FILES_ENV_KEY]: validatedFiles } : void 0;
  const result = formatOutput(violations, matchedSkills, filePath, log, platform, cursorEnv, chainResult);
  log.complete("posttooluse-validate-done", {
    matchedCount: matchedSkills.length,
    injectedCount: violations.filter((v) => v.severity === "error").length
  }, timing);
  return result;
}
function isMainModule() {
  try {
    const scriptPath = realpathSync(resolve(process.argv[1] || ""));
    const modulePath = realpathSync(fileURLToPath(import.meta.url));
    return scriptPath === modulePath;
  } catch {
    return false;
  }
}
if (isMainModule()) {
  try {
    const output = run();
    process.stdout.write(output);
  } catch (err) {
    const entry = [
      `[${(/* @__PURE__ */ new Date()).toISOString()}] CRASH in posttooluse-validate.mts`,
      `  error: ${err?.message || String(err)}`,
      `  stack: ${err?.stack || "(no stack)"}`,
      `  PLUGIN_ROOT: ${PLUGIN_ROOT}`,
      ""
    ].join("\n");
    process.stderr.write(entry);
    process.stdout.write("{}");
  }
}
export {
  appendValidatedFile,
  contentHash,
  formatOutput,
  isAlreadyValidated,
  loadValidateRules,
  markValidated,
  matchFileToSkills,
  parseInput,
  parseValidatedFiles,
  run,
  runChainInjection,
  runValidation
};
