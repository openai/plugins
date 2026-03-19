#!/usr/bin/env node

// hooks/src/user-prompt-submit-skill-inject.mts
import { readFileSync, realpathSync } from "fs";
import { resolve } from "path";
import { fileURLToPath } from "url";
import {
  appendAuditLog,
  listSessionKeys,
  pluginRoot as resolvePluginRoot,
  readSessionFile,
  syncSessionFileFromClaims,
  tryClaimSessionKey,
  writeSessionFile
} from "./hook-env.mjs";
import { loadSkills, injectSkills } from "./pretooluse-skill-inject.mjs";
import {
  COMPACTION_REINJECT_MIN_PRIORITY,
  parseSeenSkills,
  mergeSeenSkillStates,
  mergeSeenSkillStatesWithCompactionReset,
  buildDocsBlock
} from "./patterns.mjs";
import { normalizePromptText, compilePromptSignals, matchPromptWithReason, scorePromptWithLexical, classifyTroubleshootingIntent, lexicalFallbackMeetsFloor } from "./prompt-patterns.mjs";
import { searchSkills, initializeLexicalIndex } from "./lexical-index.mjs";
import { analyzePrompt } from "./prompt-analysis.mjs";
import { createLogger, logDecision } from "./logger.mjs";
import { isTelemetryEnabled, trackEvents } from "./telemetry.mjs";
var MAX_SKILLS = 2;
var DEFAULT_INJECTION_BUDGET_BYTES = 8e3;
var MIN_PROMPT_LENGTH = 10;
var PLUGIN_ROOT = resolvePluginRoot();
var SKILL_INJECTION_VERSION = 1;
var ENV_SEEN_SKILLS_KEY = "VERCEL_PLUGIN_SEEN_SKILLS";
var ENV_CONTEXT_COMPACTED_KEY = "VERCEL_PLUGIN_CONTEXT_COMPACTED";
var DEFAULT_PROMPT_MIN_SCORE = 6;
var PROJECT_CONTEXT_PROMPT_SCORE_BOOST = 3;
var DOMINANT_TOPIC_SCORE_THRESHOLD = 600;
var DOMINANT_TOPIC_MIN_SCORE = 50;
var INVESTIGATION_COMPANION_SKILLS = [
  "workflow",
  "agent-browser-verify",
  "vercel-cli"
];
var log = createLogger();
function getSeenSkillsEnv() {
  return typeof process.env[ENV_SEEN_SKILLS_KEY] === "string" ? process.env[ENV_SEEN_SKILLS_KEY] : "";
}
function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function nonEmptyString(value) {
  return typeof value === "string" && value.trim() !== "" ? value : null;
}
function detectPromptHookPlatform(input) {
  if ("conversation_id" in input || "cursor_version" in input) {
    return "cursor";
  }
  return "claude-code";
}
function detectPromptHookPlatformFromRaw(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (isRecord(parsed)) {
      return detectPromptHookPlatform(parsed);
    }
  } catch {
  }
  return "claude-code";
}
function resolvePromptSessionId(input, env) {
  return nonEmptyString(input.session_id) ?? nonEmptyString(input.conversation_id) ?? nonEmptyString(env.SESSION_ID);
}
function resolvePromptCwd(input, env) {
  const workspaceRoot = Array.isArray(input.workspace_roots) ? input.workspace_roots.find((entry) => typeof entry === "string" && entry.trim() !== "") : null;
  return nonEmptyString(input.cwd) ?? (typeof workspaceRoot === "string" ? workspaceRoot : null) ?? nonEmptyString(env.CURSOR_PROJECT_DIR) ?? nonEmptyString(env.CLAUDE_PROJECT_ROOT) ?? process.cwd();
}
function resolvePromptText(input) {
  return nonEmptyString(input.prompt) ?? nonEmptyString(input.message) ?? "";
}
function formatEmptyOutput(platform, env) {
  if (platform === "cursor") {
    const output = { continue: true };
    if (env && Object.keys(env).length > 0) {
      output.env = env;
    }
    return JSON.stringify(output);
  }
  return "{}";
}
function getInjectionBudget() {
  const envVal = process.env.VERCEL_PLUGIN_PROMPT_INJECTION_BUDGET;
  if (envVal != null && envVal !== "") {
    const parsed = parseInt(envVal, 10);
    if (Number.isFinite(parsed) && parsed > 0) return parsed;
  }
  return DEFAULT_INJECTION_BUDGET_BYTES;
}
function capturePromptEnvSnapshot(env = process.env) {
  return {
    [ENV_SEEN_SKILLS_KEY]: env[ENV_SEEN_SKILLS_KEY],
    [ENV_CONTEXT_COMPACTED_KEY]: env[ENV_CONTEXT_COMPACTED_KEY]
  };
}
function finalizePromptEnvUpdates(platform, before, env = process.env) {
  if (platform !== "cursor") return void 0;
  const updates = {};
  for (const key of [ENV_SEEN_SKILLS_KEY, ENV_CONTEXT_COMPACTED_KEY]) {
    const nextValue = env[key];
    if (typeof nextValue === "string" && nextValue !== before[key]) {
      updates[key] = nextValue;
    }
  }
  return Object.keys(updates).length > 0 ? updates : void 0;
}
function resolvePromptSeenSkillState(sessionId, skillMap) {
  const dedupOff = process.env.VERCEL_PLUGIN_HOOK_DEDUP === "off";
  const hasFileDedup = !dedupOff && !!sessionId;
  const seenEnv = getSeenSkillsEnv();
  const seenClaims = hasFileDedup ? listSessionKeys(sessionId, "seen-skills").join(",") : "";
  const seenFile = hasFileDedup ? readSessionFile(sessionId, "seen-skills") : "";
  const seenStateResult = dedupOff ? {
    seenEnv,
    seenState: hasFileDedup ? mergeSeenSkillStates(seenFile, seenClaims) : seenEnv,
    compactionResetApplied: false,
    clearedSkills: []
  } : mergeSeenSkillStatesWithCompactionReset(seenEnv, seenFile, seenClaims, {
    sessionId: hasFileDedup ? sessionId : void 0,
    includeEnv: !hasFileDedup,
    skillMap
  });
  const seenState = seenStateResult.seenState;
  if (hasFileDedup) {
    writeSessionFile(sessionId, "seen-skills", seenState);
  }
  return {
    dedupOff,
    hasFileDedup,
    seenClaims,
    seenFile,
    seenEnv: seenStateResult.seenEnv,
    seenState,
    compactionResetApplied: seenStateResult.compactionResetApplied,
    clearedSkills: seenStateResult.clearedSkills
  };
}
function syncPromptSeenSkillClaims(sessionId, loadedSkills) {
  for (const skill of loadedSkills) {
    tryClaimSessionKey(sessionId, "seen-skills", skill);
  }
  return syncSessionFileFromClaims(sessionId, "seen-skills");
}
function parsePromptInput(raw, logger, env = process.env) {
  const l = logger || log;
  const trimmed = (raw || "").trim();
  if (!trimmed) {
    l.debug("stdin-empty", {});
    return null;
  }
  let input;
  try {
    const parsed = JSON.parse(trimmed);
    if (!isRecord(parsed)) {
      l.debug("stdin-not-object", {});
      return null;
    }
    input = parsed;
  } catch (err) {
    l.issue("STDIN_PARSE_FAIL", "Failed to parse stdin as JSON", "Verify stdin contains valid JSON", { error: String(err) });
    return null;
  }
  const platform = detectPromptHookPlatform(input);
  const prompt = resolvePromptText(input);
  const sessionId = resolvePromptSessionId(input, env);
  const cwd = resolvePromptCwd(input, env);
  if (prompt.length < MIN_PROMPT_LENGTH) {
    l.debug("prompt-too-short", { length: prompt.length, min: MIN_PROMPT_LENGTH });
    return null;
  }
  l.debug("input-parsed", {
    promptLength: prompt.length,
    sessionId,
    cwd,
    platform
  });
  return { prompt, platform, sessionId, cwd };
}
function parseLikelySkillsEnv(envValue = process.env.VERCEL_PLUGIN_LIKELY_SKILLS) {
  if (typeof envValue !== "string" || envValue.trim() === "") {
    return /* @__PURE__ */ new Set();
  }
  return new Set(
    envValue.split(",").map((skill) => skill.trim()).filter((skill) => skill.length > 0)
  );
}
function getPromptSignalMinScore(skillConfig) {
  const minScore = skillConfig?.promptSignals?.minScore;
  return typeof minScore === "number" && !Number.isNaN(minScore) ? minScore : DEFAULT_PROMPT_MIN_SCORE;
}
function formatPromptScore(score) {
  return Number.isInteger(score) ? String(score) : score.toFixed(1);
}
function extractLexicalScore(reason) {
  const match = reason.match(/lexical [^(]*\((?:raw |score )([0-9]+(?:\.[0-9]+)?)/);
  return match ? Number(match[1]) : null;
}
function extractBelowThresholdScore(reason) {
  const match = reason.match(/below threshold: score (-?[0-9]+(?:\.[0-9]+)?)/);
  return match ? Number(match[1]) : null;
}
function applyLexicalFallbackFloor(entry) {
  const lexicalScore = extractLexicalScore(entry.reason);
  if (lexicalScore == null || lexicalFallbackMeetsFloor(lexicalScore) || entry.score === -Infinity) {
    return entry;
  }
  const exactScore = extractBelowThresholdScore(entry.reason);
  const score = exactScore ?? entry.score;
  return {
    ...entry,
    score,
    matched: score >= entry.minScore,
    reason: `${entry.reason}; lexical floor rejected (raw ${formatPromptScore(lexicalScore)} < 20)`
  };
}
function applyProjectContextBoost(entry, likelySkills) {
  if (!likelySkills.has(entry.skill) || entry.score === -Infinity) {
    return entry;
  }
  const boostedScore = entry.score + PROJECT_CONTEXT_PROMPT_SCORE_BOOST;
  const boostReason = `project-context +${PROJECT_CONTEXT_PROMPT_SCORE_BOOST} (${formatPromptScore(entry.score)} -> ${formatPromptScore(boostedScore)})`;
  const reason = entry.reason.startsWith("below threshold:") && boostedScore >= entry.minScore ? boostReason : entry.reason ? `${entry.reason}; ${boostReason}` : boostReason;
  return {
    ...entry,
    score: boostedScore,
    reason,
    matched: boostedScore >= entry.minScore
  };
}
function applyDominantTopicSuppression(entry, topScore) {
  if (!entry.matched || !Number.isFinite(entry.score) || entry.score >= DOMINANT_TOPIC_MIN_SCORE || topScore < DOMINANT_TOPIC_SCORE_THRESHOLD) {
    return entry;
  }
  return {
    ...entry,
    matched: false,
    suppressed: true,
    reason: `${entry.reason}; suppressed by dominant topic (${formatPromptScore(topScore)} >= ${DOMINANT_TOPIC_SCORE_THRESHOLD}, score < ${DOMINANT_TOPIC_MIN_SCORE})`
  };
}
function applyPromptScoreAdjustments(entries, logger) {
  const l = logger || log;
  const likelySkills = parseLikelySkillsEnv();
  const lexicalFloorRejected = [];
  const flooredEntries = entries.map((entry) => {
    const adjusted = applyLexicalFallbackFloor(entry);
    if (adjusted !== entry) {
      lexicalFloorRejected.push(entry.skill);
    }
    return adjusted;
  });
  const boostedSkills = [];
  if (lexicalFloorRejected.length > 0) {
    l.debug("prompt-lexical-floor-rejected", {
      minRawScore: 20,
      rejectedSkills: lexicalFloorRejected
    });
  }
  const boostedEntries = flooredEntries.map((entry) => {
    const boosted = applyProjectContextBoost(entry, likelySkills);
    if (boosted !== entry) {
      boostedSkills.push(entry.skill);
    }
    return boosted;
  });
  if (boostedSkills.length > 0) {
    l.debug("prompt-project-context-boost", {
      boost: PROJECT_CONTEXT_PROMPT_SCORE_BOOST,
      boostedSkills
    });
  }
  const topScore = boostedEntries.reduce((max, entry) => {
    if (Number.isFinite(entry.score) && entry.score > max) {
      return entry.score;
    }
    return max;
  }, -Infinity);
  if (topScore < DOMINANT_TOPIC_SCORE_THRESHOLD) {
    return boostedEntries;
  }
  const suppressedSkills = [];
  const adjustedEntries = boostedEntries.map((entry) => {
    const adjusted = applyDominantTopicSuppression(entry, topScore);
    if (adjusted !== entry) {
      suppressedSkills.push(entry.skill);
    }
    return adjusted;
  });
  if (suppressedSkills.length > 0) {
    l.debug("prompt-dominant-topic-suppression", {
      topScore,
      minScore: DOMINANT_TOPIC_MIN_SCORE,
      suppressedSkills
    });
  }
  return adjustedEntries;
}
function sortPromptScoreStates(entries) {
  entries.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    if (b.priority !== a.priority) return b.priority - a.priority;
    return a.skill.localeCompare(b.skill);
  });
}
function estimatePromptSkillSize(skillConfig) {
  return skillConfig?.summary ? Math.max(skillConfig.summary.length * 10, 500) : 500;
}
function rerankPromptAnalysisReport(report, skillMap, maxSkills, budgetBytes) {
  const ranked = Object.entries(report.perSkillResults).filter(([, result]) => result.matched).map(([skill, result]) => ({
    skill,
    score: result.score,
    reason: result.reason,
    priority: skillMap[skill]?.priority ?? 0,
    matched: true,
    minScore: getPromptSignalMinScore(skillMap[skill]),
    suppressed: result.suppressed
  }));
  sortPromptScoreStates(ranked);
  const dedupDisabled = report.dedupState.strategy === "disabled";
  const seenSkills = new Set(report.dedupState.seenSkills);
  const filteredByDedup = [];
  const afterDedup = ranked.filter((entry) => {
    if (!dedupDisabled && seenSkills.has(entry.skill)) {
      filteredByDedup.push(entry.skill);
      return false;
    }
    return true;
  });
  report.dedupState.filteredByDedup = filteredByDedup;
  report.droppedByCap = afterDedup.slice(maxSkills).map((entry) => entry.skill);
  const droppedByBudget = [];
  const selectedSkills = [];
  let usedBytes = 0;
  for (const entry of afterDedup.slice(0, maxSkills)) {
    const estimatedSize = estimatePromptSkillSize(skillMap[entry.skill]);
    if (usedBytes + estimatedSize > budgetBytes && selectedSkills.length > 0) {
      droppedByBudget.push(entry.skill);
      continue;
    }
    usedBytes += estimatedSize;
    selectedSkills.push(entry.skill);
  }
  report.selectedSkills = selectedSkills;
  report.droppedByBudget = droppedByBudget;
}
function applyPromptScoreAdjustmentsToReport(report, skillMap, logger, options) {
  const scoredEntries = Object.entries(report.perSkillResults).map(
    ([skill, result]) => ({
      skill,
      score: result.score,
      reason: result.reason,
      priority: skillMap[skill]?.priority ?? 0,
      matched: result.matched,
      minScore: getPromptSignalMinScore(skillMap[skill]),
      suppressed: result.suppressed
    })
  );
  const adjustedEntries = applyPromptScoreAdjustments(scoredEntries, logger);
  for (const entry of adjustedEntries) {
    report.perSkillResults[entry.skill] = {
      score: entry.score,
      reason: entry.reason,
      matched: entry.matched,
      suppressed: entry.suppressed
    };
  }
  rerankPromptAnalysisReport(
    report,
    skillMap,
    options?.maxSkills ?? MAX_SKILLS,
    options?.budgetBytes ?? report.budgetBytes
  );
  return report;
}
function matchPromptSignals(normalizedPrompt, skills, logger, options) {
  const l = logger || log;
  const lexical = options?.lexical ?? false;
  const { skillMap } = skills;
  const scoredEntries = [];
  const lexicalHits = lexical ? searchSkills(normalizedPrompt) : void 0;
  for (const [skill, config] of Object.entries(skillMap)) {
    if (!config.promptSignals) continue;
    const compiled = compilePromptSignals(config.promptSignals);
    if (lexical) {
      const lexResult = scorePromptWithLexical(normalizedPrompt, skill, compiled, lexicalHits);
      const lexicalFloorRejected = lexResult.source !== "exact" && !lexicalFallbackMeetsFloor(lexResult.lexicalScore);
      const isMatched = lexResult.score >= compiled.minScore && !lexicalFloorRejected;
      const reason = lexResult.source === "exact" ? matchPromptWithReason(normalizedPrompt, compiled).reason : `${matchPromptWithReason(normalizedPrompt, compiled).reason}; lexical ${lexResult.source} (score ${lexResult.lexicalScore.toFixed(1)}, tier ${lexResult.boostTier ?? "none"})${lexicalFloorRejected ? "; lexical floor rejected" : ""}`;
      scoredEntries.push({
        skill,
        score: lexResult.score,
        reason,
        priority: config.priority,
        matched: isMatched,
        minScore: compiled.minScore,
        suppressed: lexResult.score === -Infinity
      });
    } else {
      const result = matchPromptWithReason(normalizedPrompt, compiled);
      scoredEntries.push({
        skill,
        matched: result.matched,
        score: result.score,
        reason: result.reason,
        priority: config.priority,
        minScore: compiled.minScore,
        suppressed: result.score === -Infinity
      });
    }
  }
  const adjustedEntries = applyPromptScoreAdjustments(scoredEntries, l);
  for (const entry of adjustedEntries) {
    l.trace("prompt-signal-eval", {
      skill: entry.skill,
      matched: entry.matched,
      score: entry.score,
      reason: entry.reason,
      suppressed: entry.suppressed
    });
  }
  const matches = adjustedEntries.filter((entry) => entry.matched).map(({ skill, score, reason, priority }) => ({
    skill,
    score,
    reason,
    priority
  }));
  sortPromptScoreStates(matches);
  l.debug("prompt-matches", {
    totalWithSignals: Object.values(skillMap).filter((c) => c.promptSignals).length,
    matched: matches.map((m) => ({ skill: m.skill, score: m.score })),
    lexical
  });
  return matches;
}
function selectInvestigationCompanion(selectedSkills, perSkillResults) {
  if (!selectedSkills.includes("investigation-mode")) {
    return { companion: null, reason: "investigation-mode not selected" };
  }
  let bestCompanion = null;
  let bestScore = -Infinity;
  for (const candidate of INVESTIGATION_COMPANION_SKILLS) {
    const result = perSkillResults[candidate];
    if (result && result.matched && result.score > bestScore) {
      bestScore = result.score;
      bestCompanion = candidate;
    }
  }
  if (!bestCompanion) {
    return { companion: null, reason: "no companion scored high enough" };
  }
  return {
    companion: bestCompanion,
    reason: `companion "${bestCompanion}" scored ${bestScore}`
  };
}
function deduplicateAndInject(matches, skills, logger, platform) {
  const l = logger || log;
  const dedupOff = process.env.VERCEL_PLUGIN_HOOK_DEDUP === "off";
  const seenState = getSeenSkillsEnv();
  const injectedSkills = dedupOff ? /* @__PURE__ */ new Set() : parseSeenSkills(seenState);
  const budget = getInjectionBudget();
  const allMatched = matches.map((m) => m.skill);
  const newMatches = dedupOff ? matches : matches.filter((m) => !injectedSkills.has(m.skill));
  if (newMatches.length === 0) {
    l.debug("all-prompt-matches-deduped", { matched: allMatched, seen: [...injectedSkills] });
    return { parts: [], loaded: [], summaryOnly: [], droppedByCap: [], droppedByBudget: [], matchedSkills: allMatched };
  }
  const rankedSkills = newMatches.slice(0, MAX_SKILLS).map((m) => m.skill);
  const droppedByCap = newMatches.slice(MAX_SKILLS).map((m) => m.skill);
  l.debug("prompt-dedup", {
    rankedSkills,
    droppedByCap,
    previouslyInjected: [...injectedSkills]
  });
  const result = injectSkills(rankedSkills, {
    pluginRoot: PLUGIN_ROOT,
    hasEnvDedup: !dedupOff,
    injectedSkills,
    budgetBytes: budget,
    maxSkills: MAX_SKILLS,
    skillMap: skills.skillMap,
    logger: l,
    platform: platform ?? "claude-code"
  });
  return {
    ...result,
    droppedByCap: [...result.droppedByCap, ...droppedByCap],
    matchedSkills: allMatched
  };
}
function formatOutput(parts, matchedSkills, injectedSkills, summaryOnly, droppedByCap, droppedByBudget, promptMatchReasons, skillMap, platform = "claude-code", env) {
  if (parts.length === 0) {
    return formatEmptyOutput(platform, env);
  }
  const skillInjection = {
    version: SKILL_INJECTION_VERSION,
    hookEvent: "UserPromptSubmit",
    matchedSkills,
    injectedSkills,
    summaryOnly,
    droppedByBudget
  };
  const metaComment = `<!-- skillInjection: ${JSON.stringify(skillInjection)} -->`;
  const bannerLines = ["[vercel] Best practices auto-suggested based on prompt analysis:"];
  for (const skill of injectedSkills) {
    const reason = promptMatchReasons?.[skill];
    if (reason) {
      bannerLines.push(`  - "${skill}" matched: ${reason}`);
    } else {
      bannerLines.push(`  - "${skill}"`);
    }
  }
  const banner = bannerLines.join("\n");
  const docsBlock = buildDocsBlock(injectedSkills, skillMap);
  const sections = [banner];
  if (docsBlock) sections.push(docsBlock);
  sections.push(parts.join("\n\n"));
  const additionalContext = sections.join("\n\n") + "\n" + metaComment;
  if (platform === "cursor") {
    const output2 = {
      additional_context: additionalContext,
      continue: true
    };
    if (env && Object.keys(env).length > 0) {
      output2.env = env;
    }
    return JSON.stringify(output2);
  }
  const output = {
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext
    }
  };
  return JSON.stringify(output);
}
function run() {
  const timing = {};
  const tPhase = log.active ? log.now() : 0;
  let raw;
  try {
    raw = readFileSync(0, "utf-8");
  } catch {
    return "{}";
  }
  const platform = detectPromptHookPlatformFromRaw(raw);
  const parsed = parsePromptInput(raw, log);
  if (!parsed) return formatEmptyOutput(platform);
  if (log.active) timing.stdin_parse = Math.round(log.now() - tPhase);
  const { prompt, sessionId, cwd } = parsed;
  const promptEnvBefore = capturePromptEnvSnapshot();
  const normalizedPrompt = normalizePromptText(prompt);
  if (!normalizedPrompt) {
    log.debug("normalized-prompt-empty", {});
    return formatEmptyOutput(platform);
  }
  const tSkillmap = log.active ? log.now() : 0;
  const skills = loadSkills(PLUGIN_ROOT, log);
  if (!skills) return formatEmptyOutput(platform);
  if (log.active) timing.skillmap_load = Math.round(log.now() - tSkillmap);
  const tAnalyze = log.active ? log.now() : 0;
  const seenSkillState = resolvePromptSeenSkillState(sessionId, skills.skillMap);
  const { dedupOff, hasFileDedup, seenState } = seenSkillState;
  if (seenSkillState.compactionResetApplied) {
    log.debug("dedup-compaction-reset", {
      sessionId,
      threshold: COMPACTION_REINJECT_MIN_PRIORITY,
      clearedSkills: seenSkillState.clearedSkills
    });
  }
  const budget = getInjectionBudget();
  const lexicalEnabled = process.env.VERCEL_PLUGIN_LEXICAL_PROMPT !== "0";
  if (lexicalEnabled) {
    initializeLexicalIndex(new Map(Object.entries(skills.skillMap)));
  }
  const report = analyzePrompt(prompt, skills.skillMap, seenState, budget, MAX_SKILLS, { lexicalEnabled });
  applyPromptScoreAdjustmentsToReport(report, skills.skillMap, log, {
    maxSkills: MAX_SKILLS,
    budgetBytes: budget
  });
  if (log.active) timing.analyze = Math.round(log.now() - tAnalyze);
  log.trace("prompt-analysis-full", report);
  for (const [skill, r] of Object.entries(report.perSkillResults)) {
    log.debug("prompt-signal-eval", {
      skill,
      score: r.score,
      reason: r.reason,
      matched: r.matched,
      suppressed: r.suppressed
    });
  }
  log.debug("prompt-selection", {
    selectedSkills: report.selectedSkills,
    droppedByCap: report.droppedByCap,
    droppedByBudget: report.droppedByBudget,
    dedupStrategy: report.dedupState.strategy,
    filteredByDedup: report.dedupState.filteredByDedup,
    budgetBytes: report.budgetBytes,
    timingMs: report.timingMs
  });
  const intentResult = classifyTroubleshootingIntent(normalizedPrompt);
  if (intentResult.intent) {
    for (const skill of intentResult.skills) {
      if (!report.selectedSkills.includes(skill) && report.selectedSkills.length < MAX_SKILLS) {
        report.selectedSkills.push(skill);
      }
    }
    logDecision(log, {
      hook: "UserPromptSubmit",
      event: "troubleshooting_intent_routed",
      intent: intentResult.intent,
      skills: intentResult.skills,
      reason: intentResult.reason,
      durationMs: log.active ? log.elapsed() : void 0
    });
  } else if (intentResult.reason === "suppressed by test framework mention") {
    const suppressSet = /* @__PURE__ */ new Set(["verification", "investigation-mode", "agent-browser-verify"]);
    const before = report.selectedSkills.length;
    report.selectedSkills = report.selectedSkills.filter((s) => !suppressSet.has(s));
    if (report.selectedSkills.length < before) {
      logDecision(log, {
        hook: "UserPromptSubmit",
        event: "verification_family_suppressed",
        reason: intentResult.reason,
        durationMs: log.active ? log.elapsed() : void 0
      });
    }
  }
  const investigationSkills = ["investigation-mode", "observability", "workflow"];
  const matchedInvestigation = Object.entries(report.perSkillResults).filter(([skill, r]) => r.matched && investigationSkills.includes(skill));
  if (matchedInvestigation.length > 0) {
    logDecision(log, {
      hook: "UserPromptSubmit",
      event: "investigation_intent_detected",
      reason: "frustration_or_debug_signals",
      skills: matchedInvestigation.map(([skill, r]) => ({ skill, score: r.score })),
      durationMs: log.active ? log.elapsed() : void 0
    });
  }
  const companionResult = selectInvestigationCompanion(
    report.selectedSkills,
    report.perSkillResults
  );
  if (companionResult.companion) {
    const companion = companionResult.companion;
    const newSelected = ["investigation-mode"];
    if (!report.selectedSkills.includes(companion)) {
      newSelected.push(companion);
    } else {
      newSelected.push(companion);
    }
    report.selectedSkills.length = 0;
    report.selectedSkills.push(...newSelected);
    logDecision(log, {
      hook: "UserPromptSubmit",
      event: "companion_selected",
      skill: "investigation-mode",
      companion,
      reason: companionResult.reason,
      durationMs: log.active ? log.elapsed() : void 0
    });
  } else if (report.selectedSkills.length > 1) {
    logDecision(log, {
      hook: "UserPromptSubmit",
      event: "companion_selected",
      skill: report.selectedSkills[0],
      companion: report.selectedSkills[1],
      reason: "multi_skill_prompt_match",
      durationMs: log.active ? log.elapsed() : void 0
    });
  }
  const allMatched = Object.entries(report.perSkillResults).filter(([, r]) => r.matched).map(([skill]) => skill);
  if (allMatched.length === 0) {
    log.debug("prompt-analysis-issue", {
      issue: "no_prompt_matches",
      evaluatedSkills: Object.keys(report.perSkillResults),
      suppressedSkills: Object.entries(report.perSkillResults).filter(([, r]) => r.suppressed).map(([skill]) => skill)
    });
    log.complete("no_prompt_matches", { matchedCount: 0 }, log.active ? timing : null);
    return formatEmptyOutput(platform, finalizePromptEnvUpdates(platform, promptEnvBefore));
  }
  if (report.selectedSkills.length === 0) {
    log.debug("prompt-analysis-issue", {
      issue: "all_deduped",
      matchedSkills: allMatched,
      seenSkills: report.dedupState.seenSkills,
      dedupStrategy: report.dedupState.strategy
    });
    log.complete("all_deduped", {
      matchedCount: allMatched.length,
      dedupedCount: allMatched.length
    }, log.active ? timing : null);
    return formatEmptyOutput(platform, finalizePromptEnvUpdates(platform, promptEnvBefore));
  }
  const tInject = log.active ? log.now() : 0;
  const injectedSkills = dedupOff ? /* @__PURE__ */ new Set() : parseSeenSkills(seenState);
  const injectResult = injectSkills(report.selectedSkills, {
    pluginRoot: PLUGIN_ROOT,
    hasEnvDedup: !dedupOff,
    sessionId,
    injectedSkills,
    budgetBytes: budget,
    maxSkills: MAX_SKILLS,
    skillMap: skills.skillMap,
    logger: log,
    platform
  });
  if (log.active) timing.inject = Math.round(log.now() - tInject);
  const { parts, loaded, summaryOnly } = injectResult;
  let syncedSeenSkills = seenState;
  if (hasFileDedup) {
    syncedSeenSkills = syncPromptSeenSkillClaims(sessionId, loaded);
  }
  const droppedByCap = [...injectResult.droppedByCap, ...report.droppedByCap];
  const droppedByBudget = [...injectResult.droppedByBudget, ...report.droppedByBudget];
  const matchedSkills = allMatched;
  if (parts.length === 0) {
    log.complete("all_deduped", {
      matchedCount: matchedSkills.length,
      dedupedCount: matchedSkills.length
    }, log.active ? timing : null);
    return formatEmptyOutput(platform);
  }
  if (log.active) timing.total = log.elapsed();
  log.complete("injected", {
    matchedCount: matchedSkills.length,
    injectedCount: loaded.length,
    dedupedCount: matchedSkills.length - loaded.length - droppedByCap.length - droppedByBudget.length,
    cappedCount: droppedByCap.length + droppedByBudget.length
  }, log.active ? timing : null);
  if (loaded.length > 0) {
    appendAuditLog({
      event: "prompt-skill-injection",
      hookEvent: "UserPromptSubmit",
      matchedSkills,
      injectedSkills: loaded,
      summaryOnly,
      droppedByCap,
      droppedByBudget
    }, cwd);
  }
  if (isTelemetryEnabled() && sessionId && loaded.length > 0) {
    const telemetryEntries = [];
    for (const skill of loaded) {
      const r = report.perSkillResults[skill];
      telemetryEntries.push(
        { key: "prompt:skill", value: skill },
        { key: "prompt:score", value: String(r?.score ?? 0) },
        { key: "prompt:hook", value: "UserPromptSubmit" }
      );
    }
    trackEvents(sessionId, telemetryEntries).catch(() => {
    });
  }
  let outputEnv;
  const envFile = nonEmptyString(process.env.CLAUDE_ENV_FILE);
  const seenSkills = hasFileDedup ? syncedSeenSkills : seenState;
  if (platform === "cursor") {
    if (!envFile) {
      process.env[ENV_SEEN_SKILLS_KEY] = seenSkills;
    }
    outputEnv = finalizePromptEnvUpdates(platform, promptEnvBefore);
  }
  const promptMatchReasons = {};
  for (const skill of loaded) {
    const r = report.perSkillResults[skill];
    if (r?.reason) {
      promptMatchReasons[skill] = r.reason;
    }
  }
  return formatOutput(
    parts,
    matchedSkills,
    loaded,
    summaryOnly,
    droppedByCap,
    droppedByBudget,
    promptMatchReasons,
    skills.skillMap,
    platform,
    outputEnv
  );
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
      `[${(/* @__PURE__ */ new Date()).toISOString()}] CRASH in user-prompt-submit-skill-inject.mts`,
      `  error: ${err?.message || String(err)}`,
      `  stack: ${err?.stack || "(no stack)"}`,
      `  PLUGIN_ROOT: ${PLUGIN_ROOT}`,
      `  argv: ${JSON.stringify(process.argv)}`,
      `  cwd: ${process.cwd()}`,
      ""
    ].join("\n");
    process.stderr.write(entry);
    process.stdout.write("{}");
  }
}
export {
  INVESTIGATION_COMPANION_SKILLS,
  deduplicateAndInject,
  formatOutput,
  matchPromptSignals,
  parsePromptInput,
  resolvePromptSeenSkillState,
  run,
  selectInvestigationCompanion,
  syncPromptSeenSkillClaims
};
