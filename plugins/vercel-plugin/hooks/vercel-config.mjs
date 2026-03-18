// hooks/src/vercel-config.mts
import { safeReadFile } from "./hook-env.mjs";
var KEY_SKILL_MAP = {
  // Routing
  redirects: ["routing-middleware"],
  rewrites: ["routing-middleware"],
  headers: ["routing-middleware"],
  cleanUrls: ["routing-middleware"],
  trailingSlash: ["routing-middleware"],
  // Cron
  crons: ["cron-jobs"],
  // Functions / compute
  functions: ["vercel-functions"],
  regions: ["vercel-functions"],
  // Build / CI-CD
  builds: ["deployments-cicd"],
  buildCommand: ["deployments-cicd"],
  installCommand: ["deployments-cicd"],
  outputDirectory: ["deployments-cicd"],
  framework: ["deployments-cicd"],
  devCommand: ["deployments-cicd"],
  ignoreCommand: ["deployments-cicd"],
  // Services
  experimentalServices: ["vercel-services"]
};
var VERCEL_JSON_SKILLS = /* @__PURE__ */ new Set([
  "cron-jobs",
  "deployments-cicd",
  "routing-middleware",
  "vercel-functions",
  "vercel-services"
]);
function resolveVercelJsonSkills(filePath) {
  const content = safeReadFile(filePath);
  if (content === null) return null;
  let parsed;
  try {
    parsed = JSON.parse(content);
  } catch {
    return null;
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    return null;
  }
  const keys = Object.keys(parsed);
  const relevantSkills = /* @__PURE__ */ new Set();
  for (const key of keys) {
    const skills = KEY_SKILL_MAP[key];
    if (skills) {
      for (const s of skills) {
        relevantSkills.add(s);
      }
    }
  }
  return { relevantSkills, keys };
}
function isVercelJsonPath(filePath) {
  if (typeof filePath !== "string") return false;
  const normalized = filePath.replace(/\\/g, "/");
  const base = normalized.split("/").pop();
  return base === "vercel.json";
}
export {
  VERCEL_JSON_SKILLS,
  isVercelJsonPath,
  resolveVercelJsonSkills
};
