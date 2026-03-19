// hooks/src/unified-ranker.mts
import { createLogger } from "./logger.mjs";
var log = createLogger();
var MATCH_POINTS = 10;
var LEXICAL_MULTIPLIER = 1.35;
function rankSkills(candidates) {
  const ranked = candidates.map(({ skill, pathMatch = false, commandMatch = false, importMatch = false, profilerBoost = 0, promptScore = 0, lexicalScore = 0, basePriority = 5 }) => {
    const breakdown = {
      pathPoints: pathMatch ? MATCH_POINTS : 0,
      commandPoints: commandMatch ? MATCH_POINTS : 0,
      importPoints: importMatch ? MATCH_POINTS : 0,
      profilerPoints: profilerBoost,
      promptPoints: promptScore,
      lexicalPoints: lexicalScore * LEXICAL_MULTIPLIER,
      priorityPoints: basePriority
    };
    return {
      skill,
      finalScore: Object.values(breakdown).reduce((sum, points) => sum + points, 0),
      breakdown
    };
  }).sort((a, b) => b.finalScore - a.finalScore || a.skill.localeCompare(b.skill));
  log.debug("unified-ranker-ranked", {
    candidateCount: candidates.length,
    rankedSkills: ranked.map(({ skill, finalScore }) => ({ skill, finalScore }))
  });
  return ranked;
}
export {
  rankSkills
};
