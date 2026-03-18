// hooks/src/patterns.mts
import { createHash } from "crypto";
import { appendFileSync, readdirSync, readFileSync, rmSync, writeFileSync } from "fs";
import { tmpdir } from "os";
import { basename } from "path";
import { join, resolve } from "path";
var REGEX_META_CHARS = ".()+[]{}|^$\\";
function parseBraceExpansion(pattern, startIndex) {
  let depth = 0;
  let current = "";
  let sawTopLevelComma = false;
  const alternatives = [];
  for (let i = startIndex; i < pattern.length; i++) {
    const c = pattern[i];
    if (i === startIndex) {
      depth = 1;
      continue;
    }
    if (c === "{") {
      depth++;
      current += c;
      continue;
    }
    if (c === "}") {
      depth--;
      if (depth === 0) {
        if (!sawTopLevelComma) {
          return null;
        }
        alternatives.push(current);
        return { alternatives, endIndex: i };
      }
      current += c;
      continue;
    }
    if (c === "," && depth === 1) {
      sawTopLevelComma = true;
      alternatives.push(current);
      current = "";
      continue;
    }
    current += c;
  }
  return null;
}
function globPatternToRegexSource(pattern) {
  let re = "";
  let i = 0;
  while (i < pattern.length) {
    const c = pattern[i];
    if (c === "*") {
      if (pattern[i + 1] === "*") {
        i += 2;
        if (pattern[i] === "/") {
          re += "(?:[^/]+/)*";
          i++;
        } else {
          re += ".*";
        }
        continue;
      }
      re += "[^/]*";
      i++;
      continue;
    }
    if (c === "?") {
      re += "[^/]";
      i++;
      continue;
    }
    if (c === "{") {
      const expansion = parseBraceExpansion(pattern, i);
      if (expansion) {
        re += `(?:${expansion.alternatives.map(globPatternToRegexSource).join("|")})`;
        i = expansion.endIndex + 1;
        continue;
      }
    }
    if (REGEX_META_CHARS.includes(c)) {
      re += "\\" + c;
    } else {
      re += c;
    }
    i++;
  }
  return re;
}
function globToRegex(pattern) {
  if (typeof pattern !== "string") {
    throw new TypeError(`globToRegex: expected string, got ${typeof pattern}`);
  }
  if (pattern === "") {
    throw new Error("globToRegex: pattern must not be empty");
  }
  return new RegExp(`^${globPatternToRegexSource(pattern)}$`);
}
function parseSeenSkills(envValue) {
  if (typeof envValue !== "string" || envValue.trim() === "") {
    return /* @__PURE__ */ new Set();
  }
  const seen = /* @__PURE__ */ new Set();
  for (const part of envValue.split(",")) {
    const skill = part.trim();
    if (skill !== "") {
      seen.add(skill);
    }
  }
  return seen;
}
function serializeSeenSkills(seen) {
  return [...seen].sort().join(",");
}
function mergeSeenSkillStates(...values) {
  const merged = /* @__PURE__ */ new Set();
  for (const value of values) {
    for (const skill of parseSeenSkills(value)) {
      merged.add(skill);
    }
  }
  return serializeSeenSkills(merged);
}
var COMPACTION_REINJECT_MIN_PRIORITY = 7;
var SAFE_SESSION_ID_RE = /^[a-zA-Z0-9_-]+$/;
function dedupSessionIdSegment(sessionId) {
  if (SAFE_SESSION_ID_RE.test(sessionId)) {
    return sessionId;
  }
  return createHash("sha256").update(sessionId).digest("hex");
}
function listSessionSeenSkillArtifactPaths(sessionId) {
  const tempRoot = resolve(tmpdir());
  const prefix = `vercel-plugin-${dedupSessionIdSegment(sessionId)}-`;
  const files = [];
  const claimDirs = [];
  try {
    for (const entry of readdirSync(tempRoot)) {
      if (!entry.startsWith(prefix)) continue;
      const fullPath = join(tempRoot, entry);
      if (entry.endsWith("-seen-skills.txt")) {
        files.push(fullPath);
        continue;
      }
      if (entry.endsWith("-seen-skills.d")) {
        claimDirs.push(fullPath);
      }
    }
  } catch {
    return { files: [], claimDirs: [] };
  }
  return { files, claimDirs };
}
function collectSessionSeenSkillValues(sessionId) {
  const { files, claimDirs } = listSessionSeenSkillArtifactPaths(sessionId);
  const values = [];
  for (const filePath of files) {
    try {
      values.push(readFileSync(filePath, "utf-8"));
    } catch {
    }
  }
  for (const claimDirPath of claimDirs) {
    try {
      const claimedSkills = readdirSync(claimDirPath).map((entry) => decodeURIComponent(entry)).filter((entry) => entry !== "").join(",");
      values.push(claimedSkills);
    } catch {
    }
  }
  return values;
}
function filterSeenSkillState(value, blockedSkills) {
  if (blockedSkills.size === 0) return value;
  const filtered = /* @__PURE__ */ new Set();
  for (const skill of parseSeenSkills(value)) {
    if (!blockedSkills.has(skill)) {
      filtered.add(skill);
    }
  }
  return serializeSeenSkills(filtered);
}
function isHighPrioritySkill(skill, skillMap, minPriority = COMPACTION_REINJECT_MIN_PRIORITY) {
  const priority = skillMap?.[skill]?.priority;
  return typeof priority === "number" && priority >= minPriority;
}
function escapeShellEnvValue(value) {
  return value.replace(/(["\\$`])/g, "\\$1");
}
function persistCompactionResetEnv(nextSeenEnv) {
  process.env.VERCEL_PLUGIN_SEEN_SKILLS = nextSeenEnv;
  process.env.VERCEL_PLUGIN_CONTEXT_COMPACTED = "";
  const envFile = process.env.CLAUDE_ENV_FILE;
  if (!envFile) return;
  try {
    appendFileSync(
      envFile,
      [
        `export VERCEL_PLUGIN_SEEN_SKILLS="${escapeShellEnvValue(nextSeenEnv)}"`,
        'export VERCEL_PLUGIN_CONTEXT_COMPACTED=""'
      ].join("\n") + "\n",
      "utf-8"
    );
  } catch {
  }
}
function pruneSessionSeenSkillArtifacts(sessionId, clearedSkills) {
  if (clearedSkills.size === 0) return;
  const { files, claimDirs } = listSessionSeenSkillArtifactPaths(sessionId);
  for (const filePath of files) {
    try {
      const rawValue = readFileSync(filePath, "utf-8");
      writeFileSync(filePath, filterSeenSkillState(rawValue, clearedSkills), "utf-8");
    } catch {
    }
  }
  for (const claimDirPath of claimDirs) {
    for (const skill of clearedSkills) {
      try {
        rmSync(join(claimDirPath, encodeURIComponent(skill)), { force: true });
      } catch {
      }
    }
  }
}
function mergeSeenSkillStatesWithCompactionReset(envValue, fileValue, claimValue, options) {
  const includeEnv = options?.includeEnv ?? true;
  const compactionTriggered = process.env.VERCEL_PLUGIN_CONTEXT_COMPACTED === "true";
  let seenEnv = envValue;
  let seenFile = fileValue;
  let seenClaims = claimValue;
  let clearedSkills = [];
  if (compactionTriggered) {
    const compactionState = options?.sessionId ? mergeSeenSkillStates(envValue, ...collectSessionSeenSkillValues(options.sessionId)) : mergeSeenSkillStates(envValue, fileValue, claimValue);
    const skillsToClear = /* @__PURE__ */ new Set();
    for (const skill of parseSeenSkills(compactionState)) {
      if (isHighPrioritySkill(skill, options?.skillMap)) {
        skillsToClear.add(skill);
      }
    }
    if (skillsToClear.size > 0) {
      seenEnv = filterSeenSkillState(envValue, skillsToClear);
      seenFile = filterSeenSkillState(fileValue, skillsToClear);
      seenClaims = filterSeenSkillState(claimValue, skillsToClear);
      if (options?.sessionId) {
        pruneSessionSeenSkillArtifacts(options.sessionId, skillsToClear);
      }
      clearedSkills = [...skillsToClear].sort();
    }
    persistCompactionResetEnv(seenEnv);
  }
  const seenState = includeEnv ? mergeSeenSkillStates(seenEnv, seenFile, seenClaims) : mergeSeenSkillStates(seenFile, seenClaims);
  return {
    seenEnv,
    seenFile,
    seenClaims,
    seenState,
    compactionResetApplied: compactionTriggered,
    clearedSkills
  };
}
function mergeScopedSeenSkillStates(scopeId, envValue, fileValue, claimValue) {
  if (scopeId === "main") {
    return mergeSeenSkillStates(envValue, fileValue, claimValue);
  }
  return mergeSeenSkillStates(fileValue, claimValue);
}
function appendSeenSkill(envValue, skill) {
  if (typeof skill !== "string" || skill.trim() === "") return envValue || "";
  const current = typeof envValue === "string" ? envValue.trim() : "";
  return current === "" ? skill : `${current},${skill}`;
}
function compileSkillPatterns(skillMap, callbacks) {
  const cb = callbacks || {};
  return Object.entries(skillMap).map(([skill, config]) => {
    const compiledPaths = [];
    for (const p of config.pathPatterns || []) {
      try {
        compiledPaths.push({ pattern: p, regex: globToRegex(p) });
      } catch (err) {
        if (cb.onPathGlobError) cb.onPathGlobError(skill, p, err);
      }
    }
    const compiledBash = [];
    for (const p of config.bashPatterns || []) {
      try {
        compiledBash.push({ pattern: p, regex: new RegExp(p) });
      } catch (err) {
        if (cb.onBashRegexError) cb.onBashRegexError(skill, p, err);
      }
    }
    const compiledImports = [];
    for (const p of config.importPatterns || []) {
      try {
        compiledImports.push({ pattern: p, regex: importPatternToRegex(p) });
      } catch (err) {
        if (cb.onImportPatternError) cb.onImportPatternError(skill, p, err);
      }
    }
    return {
      skill,
      priority: typeof config.priority === "number" ? config.priority : 0,
      compiledPaths,
      compiledBash,
      compiledImports
    };
  });
}
function importPatternToRegex(pattern) {
  if (typeof pattern !== "string") {
    throw new TypeError(`importPatternToRegex: expected string, got ${typeof pattern}`);
  }
  if (pattern === "") {
    throw new Error("importPatternToRegex: pattern must not be empty");
  }
  const escaped = pattern.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, `[^'"]*`);
  return new RegExp(`(?:from\\s+|require\\s*\\(\\s*|import\\s*\\(\\s*)['"]${escaped}(?:/[^'"]*)?['"]`, "m");
}
function matchImportWithReason(content, compiled) {
  if (!content || compiled.length === 0) return null;
  for (const { pattern, regex } of compiled) {
    if (regex.test(content)) {
      return { pattern, matchType: "import" };
    }
  }
  return null;
}
function matchPathWithReason(filePath, compiled) {
  if (!filePath || compiled.length === 0) return null;
  const normalized = filePath.replace(/\\/g, "/");
  for (const { pattern, regex } of compiled) {
    if (regex.test(normalized)) return { pattern, matchType: "full" };
    const base = basename(normalized);
    if (regex.test(base)) return { pattern, matchType: "basename" };
    const segments = normalized.split("/");
    for (let i = 1; i < segments.length; i++) {
      const suffix = segments.slice(-i).join("/");
      if (regex.test(suffix)) return { pattern, matchType: "suffix" };
    }
  }
  return null;
}
function matchBashWithReason(command, compiled) {
  if (!command || compiled.length === 0) return null;
  for (const { pattern, regex } of compiled) {
    if (regex.test(command)) return { pattern, matchType: "full" };
  }
  return null;
}
function parseLikelySkills(envValue) {
  return parseSeenSkills(envValue);
}
function rankEntries(entries) {
  return entries.slice().sort((a, b) => {
    const aPri = typeof a.effectivePriority === "number" ? a.effectivePriority : a.priority;
    const bPri = typeof b.effectivePriority === "number" ? b.effectivePriority : b.priority;
    return bPri - aPri || a.skill.localeCompare(b.skill);
  });
}
var DOCS_WARNING = "**MANDATORY: Your training data for these libraries is OUTDATED and UNRELIABLE.** APIs, method signatures, and config options change frequently and WITHOUT WARNING. You MUST open and read the official docs linked below BEFORE writing ANY code. DO NOT guess, assume, or rely on memorized APIs \u2014 they are likely WRONG.";
function buildDocsBlock(injectedSkills, skillMap) {
  if (!skillMap) return "";
  const entries = [];
  for (const skill of injectedSkills) {
    const cfg = skillMap[skill];
    const docs = cfg?.docs;
    if (docs && docs.length > 0) {
      let line = `  - **${skill}**: ${docs.join(" , ")}`;
      if (cfg?.sitemap) {
        line += ` (sitemap: ${cfg.sitemap})`;
      }
      entries.push(line);
    }
  }
  if (entries.length === 0) return "";
  return [
    "---",
    DOCS_WARNING,
    "",
    "Official documentation:",
    ...entries,
    "---"
  ].join("\n");
}
export {
  COMPACTION_REINJECT_MIN_PRIORITY,
  appendSeenSkill,
  buildDocsBlock,
  compileSkillPatterns,
  globToRegex,
  importPatternToRegex,
  matchBashWithReason,
  matchImportWithReason,
  matchPathWithReason,
  mergeScopedSeenSkillStates,
  mergeSeenSkillStates,
  mergeSeenSkillStatesWithCompactionReset,
  parseLikelySkills,
  parseSeenSkills,
  rankEntries,
  serializeSeenSkills
};
