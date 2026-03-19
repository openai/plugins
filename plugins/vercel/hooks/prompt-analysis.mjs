// hooks/src/prompt-analysis.mts
import { normalizePromptText, compilePromptSignals, matchPromptWithReason, scorePromptWithLexical } from "./prompt-patterns.mjs";
import { searchSkills } from "./lexical-index.mjs";
import { parseSeenSkills } from "./patterns.mjs";
function analyzePrompt(prompt, skillMap, seenSkills, budgetBytes, maxSkills, options) {
  const t0 = performance.now();
  const lexicalEnabled = options?.lexicalEnabled ?? false;
  const normalizedPrompt = normalizePromptText(prompt);
  const dedupOff = process.env.VERCEL_PLUGIN_HOOK_DEDUP === "off";
  const hasEnvVar = typeof seenSkills === "string";
  const strategy = dedupOff ? "disabled" : hasEnvVar ? "env-var" : "memory-only";
  const seenSet = dedupOff ? /* @__PURE__ */ new Set() : parseSeenSkills(seenSkills);
  const lexicalHits = lexicalEnabled ? searchSkills(prompt) : [];
  const lexicalScoreMap = new Map(lexicalHits.map((h) => [h.skill, h.score]));
  const LEXICAL_BOOST_CAP = 4;
  const RETRIEVAL_LEXICAL_BOOST_CAP = 8;
  const RETRIEVAL_TOP_K = 5;
  const topKLexicalSkills = new Set(
    lexicalHits.slice(0, RETRIEVAL_TOP_K).map((h) => h.skill)
  );
  const perSkillResults = {};
  const matched = [];
  for (const [skill, config] of Object.entries(skillMap)) {
    const hasPromptSignals = !!config.promptSignals;
    if (!hasPromptSignals && !lexicalEnabled) continue;
    if (!hasPromptSignals && !config.retrieval) continue;
    const compiled = hasPromptSignals ? compilePromptSignals(config.promptSignals) : void 0;
    if (lexicalEnabled) {
      const exactResult = compiled ? matchPromptWithReason(normalizedPrompt, compiled) : { matched: false, score: 0, reason: "no promptSignals" };
      if (exactResult.score === -Infinity) {
        perSkillResults[skill] = {
          score: -Infinity,
          reason: exactResult.reason,
          matched: false,
          suppressed: true
        };
        continue;
      }
      const minScore = compiled?.minScore ?? 6;
      const rawLexical = lexicalScoreMap.get(skill) ?? 0;
      if (exactResult.matched) {
        perSkillResults[skill] = {
          score: exactResult.score,
          reason: exactResult.reason,
          matched: true,
          suppressed: false
        };
        matched.push({ skill, score: exactResult.score, priority: config.priority });
      } else if (rawLexical > 0 && (exactResult.score > 0 || !hasPromptSignals || !!config.retrieval && topKLexicalSkills.has(skill))) {
        const lexResult = scorePromptWithLexical(prompt, skill, compiled, lexicalHits);
        const isRetrievalRecall = !!config.retrieval && topKLexicalSkills.has(skill) && exactResult.score <= 0;
        const boostCap = isRetrievalRecall ? RETRIEVAL_LEXICAL_BOOST_CAP : LEXICAL_BOOST_CAP;
        const lexicalBoost = Math.min(
          Math.max(lexResult.score - exactResult.score, 0),
          boostCap
        );
        const effectiveScore = exactResult.score + lexicalBoost;
        const isMatched = effectiveScore >= minScore;
        const parts = [];
        if (exactResult.score > 0) parts.push(exactResult.reason);
        parts.push(
          `lexical ${isMatched ? "recall" : "boost"} (raw ${rawLexical.toFixed(1)}, capped +${lexicalBoost.toFixed(1)}, source: ${lexResult.source})`
        );
        const reason = parts.join("; ");
        perSkillResults[skill] = {
          score: effectiveScore,
          reason,
          matched: isMatched,
          suppressed: false
        };
        if (isMatched) {
          matched.push({ skill, score: effectiveScore, priority: config.priority });
        }
      } else {
        perSkillResults[skill] = {
          score: exactResult.score,
          reason: exactResult.reason,
          matched: false,
          suppressed: false
        };
      }
    } else {
      const result = matchPromptWithReason(normalizedPrompt, compiled);
      perSkillResults[skill] = {
        score: result.score,
        reason: result.reason,
        matched: result.matched,
        suppressed: result.score === -Infinity
      };
      if (result.matched) {
        matched.push({ skill, score: result.score, priority: config.priority });
      }
    }
  }
  matched.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    if (b.priority !== a.priority) return b.priority - a.priority;
    return a.skill.localeCompare(b.skill);
  });
  const filteredByDedup = [];
  const afterDedup = matched.filter((m) => {
    if (!dedupOff && seenSet.has(m.skill)) {
      filteredByDedup.push(m.skill);
      return false;
    }
    return true;
  });
  const selected = afterDedup.slice(0, maxSkills);
  const droppedByCap = afterDedup.slice(maxSkills).map((m) => m.skill);
  const selectedSkills = selected.map((m) => m.skill);
  const droppedByBudget = [];
  let usedBytes = 0;
  const finalSelected = [];
  for (const skill of selectedSkills) {
    const config = skillMap[skill];
    const estimatedSize = config?.summary ? Math.max(config.summary.length * 10, 500) : 500;
    if (usedBytes + estimatedSize > budgetBytes && finalSelected.length > 0) {
      droppedByBudget.push(skill);
    } else {
      usedBytes += estimatedSize;
      finalSelected.push(skill);
    }
  }
  const timingMs = Math.round(performance.now() - t0);
  return {
    normalizedPrompt,
    perSkillResults,
    selectedSkills: finalSelected,
    droppedByCap,
    droppedByBudget,
    dedupState: {
      strategy,
      seenSkills: [...seenSet],
      filteredByDedup
    },
    budgetBytes,
    timingMs
  };
}
export {
  analyzePrompt
};
