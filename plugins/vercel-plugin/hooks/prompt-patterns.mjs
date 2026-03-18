// hooks/src/prompt-patterns.mts
import { searchSkills } from "./lexical-index.mjs";
var MIN_LEXICAL_FALLBACK_SCORE = 20;
function lexicalFallbackMeetsFloor(score) {
  return score >= MIN_LEXICAL_FALLBACK_SCORE;
}
var CONTRACTIONS = {
  "it's": "it is",
  "what's": "what is",
  "where's": "where is",
  "that's": "that is",
  "there's": "there is",
  "who's": "who is",
  "how's": "how is",
  "isn't": "is not",
  "aren't": "are not",
  "wasn't": "was not",
  "weren't": "were not",
  "doesn't": "does not",
  "don't": "do not",
  "didn't": "did not",
  "won't": "will not",
  "can't": "cannot",
  "couldn't": "could not",
  "wouldn't": "would not",
  "shouldn't": "should not",
  "hasn't": "has not",
  "haven't": "have not"
};
var CONTRACTION_ENTRIES = Object.entries(CONTRACTIONS);
function expandContractions(text) {
  let t = text.replace(/[\u2018\u2019\u2032]/g, "'");
  for (const [contraction, expansion] of CONTRACTION_ENTRIES) {
    if (t.includes(contraction)) {
      t = t.replaceAll(contraction, expansion);
    }
  }
  return t;
}
function normalizePromptText(text) {
  if (typeof text !== "string") return "";
  let t = text.toLowerCase();
  t = expandContractions(t);
  return t.replace(/\s+/g, " ").trim();
}
function compilePromptSignals(signals) {
  const norm = (s) => expandContractions(s.toLowerCase());
  return {
    phrases: (signals.phrases || []).map(norm),
    allOf: (signals.allOf || []).map((group) => group.map(norm)),
    anyOf: (signals.anyOf || []).map(norm),
    noneOf: (signals.noneOf || []).map(norm),
    minScore: typeof signals.minScore === "number" && !Number.isNaN(signals.minScore) ? signals.minScore : 6
  };
}
function matchPromptWithReason(normalizedPrompt, compiled) {
  if (!normalizedPrompt) {
    return { matched: false, score: 0, reason: "empty prompt" };
  }
  for (const term of compiled.noneOf) {
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`(?:^|\\b|\\s)${escaped}(?:\\b|\\s|$)`);
    if (re.test(normalizedPrompt)) {
      return {
        matched: false,
        score: -Infinity,
        reason: `suppressed by noneOf "${term}"`
      };
    }
  }
  let score = 0;
  const reasons = [];
  for (const phrase of compiled.phrases) {
    if (normalizedPrompt.includes(phrase)) {
      score += 6;
      reasons.push(`phrase "${phrase}" +6`);
    }
  }
  for (const group of compiled.allOf) {
    const allMatch = group.every((term) => normalizedPrompt.includes(term));
    if (allMatch) {
      score += 4;
      reasons.push(`allOf [${group.join(", ")}] +4`);
    }
  }
  let anyOfScore = 0;
  for (const term of compiled.anyOf) {
    if (normalizedPrompt.includes(term)) {
      anyOfScore += 1;
      if (anyOfScore <= 2) {
        reasons.push(`anyOf "${term}" +1`);
      }
    }
  }
  const cappedAnyOf = Math.min(anyOfScore, 2);
  score += cappedAnyOf;
  const matched = score >= compiled.minScore;
  if (!matched) {
    const detail = reasons.length > 0 ? ` (${reasons.join("; ")})` : "";
    return {
      matched: false,
      score,
      reason: `below threshold: score ${score} < ${compiled.minScore}${detail}`
    };
  }
  return {
    matched: true,
    score,
    reason: reasons.join("; ")
  };
}
function findMatchedPhrases(normalizedPrompt, compiled) {
  if (!compiled) return [];
  return compiled.phrases.filter((phrase) => normalizedPrompt.includes(phrase));
}
function adaptiveBoostTier(exactScore, minScore) {
  if (exactScore <= 0) return { multiplier: 1.5, tier: "high" };
  if (exactScore < minScore / 2) return { multiplier: 1.35, tier: "mid" };
  return { multiplier: 1.1, tier: "low" };
}
function scorePromptWithLexical(prompt, skillSlug, compiled, lexicalHits) {
  const normalizedPrompt = normalizePromptText(prompt);
  const matchedPhrases = findMatchedPhrases(normalizedPrompt, compiled);
  const exactResult = compiled ? matchPromptWithReason(normalizedPrompt, compiled) : { score: 0, matched: false };
  const exactScore = exactResult.score;
  if (compiled && exactScore >= compiled.minScore) {
    return {
      score: exactScore,
      matchedPhrases,
      lexicalScore: 0,
      source: "exact",
      boostTier: null
    };
  }
  if (exactScore === -Infinity) {
    return {
      score: -Infinity,
      matchedPhrases: [],
      lexicalScore: 0,
      source: "exact",
      boostTier: null
    };
  }
  const lexicalHit = (lexicalHits ?? searchSkills(prompt)).find(
    (hit) => hit.skill === skillSlug
  );
  if (!lexicalHit) {
    return {
      score: exactScore,
      matchedPhrases,
      lexicalScore: 0,
      source: "exact",
      boostTier: null
    };
  }
  const minScore = compiled?.minScore ?? 6;
  const { multiplier, tier } = adaptiveBoostTier(exactScore, minScore);
  const lexicalBoost = lexicalHit.score * multiplier;
  return {
    score: Math.max(exactScore, lexicalBoost),
    matchedPhrases,
    lexicalScore: lexicalHit.score,
    source: lexicalBoost > exactScore ? "lexical" : matchedPhrases.length > 0 || exactScore > 0 ? "combined" : "lexical",
    boostTier: tier
  };
}
var FLOW_VERIFICATION_RE = /\b(?:loads?\s+but|submits?\s+but|redirects?\s+but|works?\s+(?:locally\s+)?but|saves?\s+but|sends?\s+but|returns?\s+but|fetches?\s+but|connects?\s+but|renders?\s+but|deploys?\s+but|builds?\s+but)\b/;
var STUCK_INVESTIGATION_RE = /\b(?:stuck|hung|frozen|tim(?:ed?|ing)\s*out|timeout|hanging|not\s+responding|no\s+response|spinning\s+forever|still\s+waiting|nothing\s+happened|nothing\s+is\s+happening|just\s+sits?\s+there)\b/;
var BROWSER_ONLY_RE = /\b(?:blank\s+page|white\s+screen|screen\s+is\s+(?:blank|white)|console\s+errors?|browser\s+errors?|nothing\s+(?:render(?:s|ed|ing)?|show(?:s|ing|n)?)|page\s+(?:is\s+)?(?:broken|empty)|ui\s+is\s+broken)\b/;
var TEST_FRAMEWORK_RE = /\b(?:jest|vitest|playwright\s+test|cypress\s+test|mocha|karma|testing\s+library)\b/;
function classifyTroubleshootingIntent(normalizedPrompt) {
  if (!normalizedPrompt) {
    return { intent: null, skills: [], reason: "empty prompt" };
  }
  if (TEST_FRAMEWORK_RE.test(normalizedPrompt)) {
    return {
      intent: null,
      skills: [],
      reason: "suppressed by test framework mention"
    };
  }
  if (BROWSER_ONLY_RE.test(normalizedPrompt)) {
    return {
      intent: "browser-only",
      skills: ["agent-browser-verify", "investigation-mode"],
      reason: "browser-only pattern matched"
    };
  }
  if (FLOW_VERIFICATION_RE.test(normalizedPrompt)) {
    return {
      intent: "flow-verification",
      skills: ["verification"],
      reason: "flow-verification pattern matched"
    };
  }
  if (STUCK_INVESTIGATION_RE.test(normalizedPrompt)) {
    return {
      intent: "stuck-investigation",
      skills: ["investigation-mode"],
      reason: "stuck-investigation pattern matched"
    };
  }
  return { intent: null, skills: [], reason: "no troubleshooting intent" };
}
export {
  adaptiveBoostTier,
  classifyTroubleshootingIntent,
  compilePromptSignals,
  lexicalFallbackMeetsFloor,
  matchPromptWithReason,
  normalizePromptText,
  scorePromptWithLexical
};
