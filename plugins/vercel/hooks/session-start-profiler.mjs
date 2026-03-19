// hooks/src/session-start-profiler.mts
import {
  accessSync,
  constants as fsConstants,
  existsSync,
  readFileSync,
  readdirSync,
  writeFileSync
} from "fs";
import { homedir } from "os";
import { delimiter, join, resolve } from "path";
import { execFileSync } from "child_process";
import { fileURLToPath } from "url";
import {
  formatOutput,
  normalizeInput,
  setSessionEnv
} from "./compat.mjs";
import { pluginRoot, profileCachePath, safeReadJson, writeSessionFile } from "./hook-env.mjs";
import { createLogger, logCaughtError } from "./logger.mjs";
import { buildSkillMap } from "./skill-map-frontmatter.mjs";
import { isTelemetryEnabled, trackEvents } from "./telemetry.mjs";
var FILE_MARKERS = [
  { file: "next.config.js", skills: ["nextjs", "turbopack"] },
  { file: "next.config.mjs", skills: ["nextjs", "turbopack"] },
  { file: "next.config.ts", skills: ["nextjs", "turbopack"] },
  { file: "next.config.mts", skills: ["nextjs", "turbopack"] },
  { file: "turbo.json", skills: ["turborepo"] },
  { file: "vercel.json", skills: ["vercel-cli", "deployments-cicd", "vercel-functions"] },
  { file: ".mcp.json", skills: ["vercel-api"] },
  { file: "middleware.ts", skills: ["routing-middleware"] },
  { file: "middleware.js", skills: ["routing-middleware"] },
  { file: "components.json", skills: ["shadcn"] },
  { file: ".env.local", skills: ["env-vars"] },
  { file: "pnpm-workspace.yaml", skills: ["turborepo"] },
  { file: "backend/pyproject.toml", skills: ["vercel-services"] },
  { file: "backend/main.py", skills: ["vercel-services"] },
  { file: "backend/go.mod", skills: ["vercel-services"] },
  { file: "backend/main.go", skills: ["vercel-services"] }
];
var PACKAGE_MARKERS = {
  "next": ["nextjs"],
  "ai": ["ai-sdk", "ai-elements"],
  "ai-elements": ["ai-elements"],
  "@ai-sdk/openai": ["ai-sdk"],
  "@ai-sdk/anthropic": ["ai-sdk"],
  "@ai-sdk/react": ["ai-sdk", "ai-elements"],
  "@ai-sdk/gateway": ["ai-sdk", "ai-gateway"],
  "@vercel/blob": ["vercel-storage"],
  "@vercel/kv": ["vercel-storage"],
  "@vercel/postgres": ["vercel-storage"],
  "@vercel/edge-config": ["vercel-storage"],
  "@vercel/analytics": ["observability"],
  "@vercel/speed-insights": ["observability"],
  "@vercel/flags": ["vercel-flags"],
  "@vercel/workflow": ["workflow"],
  "@vercel/queue": ["vercel-queues"],
  "@vercel/sandbox": ["vercel-sandbox"],
  "@vercel/sdk": ["vercel-api"],
  "turbo": ["turborepo"],
  "@repo/auth": ["next-forge"],
  "@repo/database": ["next-forge"],
  "@repo/design-system": ["next-forge"],
  "@repo/payments": ["next-forge"],
  "@t3-oss/env-nextjs": ["next-forge"]
};
var SETUP_ENV_TEMPLATE_FILES = [
  ".env.example",
  ".env.sample",
  ".env.template"
];
var SETUP_DB_SCRIPT_MARKERS = [
  "db:push",
  "db:seed",
  "db:migrate",
  "db:generate"
];
var SETUP_AUTH_DEPENDENCIES = /* @__PURE__ */ new Set([
  "next-auth",
  "@auth/core",
  "better-auth"
]);
var SETUP_RESOURCE_DEPENDENCIES = {
  "@neondatabase/serverless": "postgres",
  "drizzle-orm": "postgres",
  "@upstash/redis": "redis",
  "@vercel/blob": "blob",
  "@vercel/edge-config": "edge-config"
};
var SETUP_MODE_THRESHOLD = 3;
var GREENFIELD_DEFAULT_SKILLS = [
  "nextjs",
  "ai-sdk",
  "vercel-cli",
  "env-vars"
];
var GREENFIELD_SETUP_SIGNALS = {
  bootstrapHints: ["greenfield"],
  resourceHints: [],
  setupMode: true
};
var SESSION_GREENFIELD_KIND = "greenfield";
var SESSION_LIKELY_SKILLS_KIND = "likely-skills";
var log = createLogger();
function readPackageJson(projectRoot) {
  return safeReadJson(join(projectRoot, "package.json"));
}
function profileProject(projectRoot) {
  const skills = /* @__PURE__ */ new Set();
  for (const marker of FILE_MARKERS) {
    if (existsSync(join(projectRoot, marker.file))) {
      for (const s of marker.skills) skills.add(s);
    }
  }
  const pkg = readPackageJson(projectRoot);
  if (pkg) {
    const allDeps = {
      ...pkg.dependencies || {},
      ...pkg.devDependencies || {}
    };
    for (const [dep, skillSlugs] of Object.entries(PACKAGE_MARKERS)) {
      if (dep in allDeps) {
        for (const s of skillSlugs) skills.add(s);
      }
    }
  }
  const vercelConfig = safeReadJson(join(projectRoot, "vercel.json"));
  if (vercelConfig) {
    if (vercelConfig.crons) skills.add("cron-jobs");
    if (vercelConfig.rewrites || vercelConfig.redirects || vercelConfig.headers) {
      skills.add("routing-middleware");
    }
    if (vercelConfig.functions) skills.add("vercel-functions");
    if (vercelConfig.experimentalServices) skills.add("vercel-services");
  }
  return [...skills].sort();
}
function profileBootstrapSignals(projectRoot) {
  const bootstrapHints = /* @__PURE__ */ new Set();
  const resourceHints = /* @__PURE__ */ new Set();
  if (SETUP_ENV_TEMPLATE_FILES.some((file) => existsSync(join(projectRoot, file)))) {
    bootstrapHints.add("env-example");
  }
  try {
    const dirents = readdirSync(projectRoot, { withFileTypes: true });
    if (dirents.some((d) => d.isFile() && d.name.toLowerCase().startsWith("readme"))) {
      bootstrapHints.add("readme");
    }
    if (dirents.some((d) => d.isFile() && /^drizzle\.config\./i.test(d.name))) {
      bootstrapHints.add("drizzle-config");
      bootstrapHints.add("postgres");
      resourceHints.add("postgres");
    }
  } catch (error) {
    logCaughtError(log, "session-start-profiler:profile-bootstrap-signals-readdir-failed", error, { projectRoot });
  }
  if (existsSync(join(projectRoot, "prisma", "schema.prisma"))) {
    bootstrapHints.add("prisma-schema");
    bootstrapHints.add("postgres");
    resourceHints.add("postgres");
  }
  const pkg = readPackageJson(projectRoot);
  if (pkg) {
    const scripts = pkg.scripts && typeof pkg.scripts === "object" ? pkg.scripts : {};
    const scriptEntries = Object.entries(scripts).map(([name, cmd]) => `${name} ${typeof cmd === "string" ? cmd : ""}`).join("\n");
    for (const marker of SETUP_DB_SCRIPT_MARKERS) {
      if (scriptEntries.includes(marker)) {
        bootstrapHints.add(marker.replace(":", "-"));
      }
    }
    const allDeps = {
      ...pkg.dependencies || {},
      ...pkg.devDependencies || {}
    };
    for (const dep of Object.keys(allDeps)) {
      const resource = SETUP_RESOURCE_DEPENDENCIES[dep];
      if (resource) {
        bootstrapHints.add(resource);
        resourceHints.add(resource);
      }
      if (SETUP_AUTH_DEPENDENCIES.has(dep)) {
        bootstrapHints.add("auth-secret");
      }
    }
  }
  const hints = [...bootstrapHints].sort();
  const resources = [...resourceHints].sort();
  return {
    bootstrapHints: hints,
    resourceHints: resources,
    setupMode: hints.length >= SETUP_MODE_THRESHOLD
  };
}
function checkGreenfield(projectRoot) {
  let dirents;
  try {
    dirents = readdirSync(projectRoot, { withFileTypes: true });
  } catch (error) {
    logCaughtError(log, "session-start-profiler:check-greenfield-readdir-failed", error, { projectRoot });
    return null;
  }
  const hasNonDotDir = dirents.some((d) => !d.name.startsWith("."));
  const hasDotFile = dirents.some((d) => d.name.startsWith(".") && d.isFile());
  if (!hasNonDotDir && !hasDotFile) {
    return { entries: dirents.map((d) => d.name).sort() };
  }
  return null;
}
var VERCEL_VERSION_ARGS = "--version".split(" ");
var NPM_VIEW_ARGS = "view vercel version".split(" ");
var SPAWN_STDIO = "ignore pipe ignore".split(" ");
var EXEC_SYNC_TIMEOUT_MS = 3e3;
var NUMERIC_VERSION_RE = /\d+(?:\.\d+)*/;
var WINDOWS_EXECUTABLE_EXTENSIONS = (process.env.PATHEXT || ".EXE;.CMD;.BAT;.COM").split(";").filter(Boolean);
function getBinaryPathCandidates(binaryName) {
  if (process.platform !== "win32") {
    return [binaryName];
  }
  const hasExecutableExtension = /\.[^./\\]+$/.test(binaryName);
  const suffixes = hasExecutableExtension ? [""] : ["", ...WINDOWS_EXECUTABLE_EXTENSIONS];
  return suffixes.map((suffix) => `${binaryName}${suffix}`);
}
function resolveBinaryFromPath(binaryName) {
  try {
    const pathEntries = (process.env.PATH || "").split(delimiter).filter(Boolean);
    for (const pathEntry of pathEntries) {
      for (const candidateName of getBinaryPathCandidates(binaryName)) {
        const candidatePath = join(pathEntry, candidateName);
        try {
          accessSync(candidatePath, fsConstants.X_OK);
          return candidatePath;
        } catch {
          continue;
        }
      }
    }
  } catch (error) {
    logCaughtError(log, "session-start-profiler:binary-resolution-failed", error, {
      binaryName
    });
    return null;
  }
  log.debug("session-start-profiler:binary-resolution-skipped", {
    binaryName,
    reason: "not-found"
  });
  return null;
}
function parseVersionSegments(version) {
  const matchedVersion = version.match(NUMERIC_VERSION_RE)?.[0];
  if (!matchedVersion) {
    return null;
  }
  return matchedVersion.split(".").map((segment) => Number.parseInt(segment, 10));
}
function compareVersionSegments(leftVersion, rightVersion) {
  const leftSegments = parseVersionSegments(leftVersion);
  const rightSegments = parseVersionSegments(rightVersion);
  if (!leftSegments || !rightSegments) {
    return null;
  }
  const maxLength = Math.max(leftSegments.length, rightSegments.length);
  for (let index = 0; index < maxLength; index += 1) {
    const leftSegment = leftSegments[index] ?? 0;
    const rightSegment = rightSegments[index] ?? 0;
    if (leftSegment !== rightSegment) {
      return leftSegment - rightSegment;
    }
  }
  return 0;
}
function checkVercelCli() {
  const vercelBinary = resolveBinaryFromPath("vercel");
  if (!vercelBinary) {
    return { installed: false, needsUpdate: false };
  }
  let currentVersion;
  try {
    const raw = execFileSync(vercelBinary, VERCEL_VERSION_ARGS, {
      timeout: EXEC_SYNC_TIMEOUT_MS,
      encoding: "utf-8",
      stdio: SPAWN_STDIO
    }).trim();
    const lines = raw.split("\n").map((l) => l.trim()).filter(Boolean);
    currentVersion = lines[lines.length - 1];
  } catch (error) {
    logCaughtError(log, "session-start-profiler:vercel-version-check-failed", error, {
      command: vercelBinary,
      args: VERCEL_VERSION_ARGS.join(" ")
    });
    return { installed: false, needsUpdate: false };
  }
  const npmBinary = resolveBinaryFromPath("npm");
  if (!npmBinary) {
    return { installed: true, currentVersion, needsUpdate: false };
  }
  let latestVersion;
  try {
    const raw = execFileSync(npmBinary, NPM_VIEW_ARGS, {
      timeout: EXEC_SYNC_TIMEOUT_MS,
      encoding: "utf-8",
      stdio: SPAWN_STDIO
    }).trim();
    latestVersion = raw;
  } catch (error) {
    logCaughtError(log, "session-start-profiler:npm-latest-version-check-failed", error, {
      command: npmBinary,
      args: NPM_VIEW_ARGS.join(" "),
      currentVersion
    });
    return { installed: true, currentVersion, needsUpdate: false };
  }
  const versionComparison = currentVersion && latestVersion ? compareVersionSegments(currentVersion, latestVersion) : null;
  const needsUpdate = versionComparison === null ? !!(currentVersion && latestVersion && currentVersion !== latestVersion) : versionComparison < 0;
  return { installed: true, currentVersion, latestVersion, needsUpdate };
}
var AGENT_BROWSER_BINARY = "agent-browser";
function checkAgentBrowser() {
  return resolveBinaryFromPath(AGENT_BROWSER_BINARY) !== null;
}
function parseSessionStartInput(raw) {
  try {
    if (!raw.trim()) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
function detectSessionStartPlatform(input, env = process.env) {
  if (typeof env.CLAUDE_ENV_FILE === "string" && env.CLAUDE_ENV_FILE.trim() !== "") {
    return "claude-code";
  }
  if (input && ("conversation_id" in input || "cursor_version" in input)) {
    return "cursor";
  }
  return "claude-code";
}
function normalizeSessionStartSessionId(input) {
  if (!input) return null;
  const sessionId = normalizeInput(input).sessionId;
  return sessionId || null;
}
function resolveSessionStartProjectRoot(env = process.env) {
  return env.CLAUDE_PROJECT_ROOT ?? env.CURSOR_PROJECT_DIR ?? process.cwd();
}
function collectBrokenSkillFrontmatterNames(files) {
  return [...new Set(
    files.map((file) => file.replaceAll("\\", "/").split("/").at(-2) || "").filter((skill) => skill !== "")
  )].sort();
}
function logBrokenSkillFrontmatterSummary(rootDir = pluginRoot(), logger = log) {
  if (!logger.isEnabled("summary")) {
    return null;
  }
  try {
    const built = buildSkillMap(join(rootDir, "skills"));
    const brokenSkills = collectBrokenSkillFrontmatterNames(
      built.diagnostics.map((diagnostic) => diagnostic.file)
    );
    if (brokenSkills.length === 0) {
      return null;
    }
    const message = `WARNING: ${brokenSkills.length} skills have broken frontmatter: ${brokenSkills.join(", ")}`;
    logger.summary("session-start-profiler:broken-skill-frontmatter", {
      message,
      brokenSkillCount: brokenSkills.length,
      brokenSkills
    });
    return message;
  } catch (error) {
    logCaughtError(logger, "session-start-profiler:broken-skill-frontmatter-check-failed", error, {
      rootDir
    });
    return null;
  }
}
function buildSessionStartProfilerEnvVars(args) {
  const envVars = {
    VERCEL_PLUGIN_AGENT_BROWSER_AVAILABLE: args.agentBrowserAvailable ? "1" : "0"
  };
  if (args.greenfield) {
    envVars.VERCEL_PLUGIN_GREENFIELD = "true";
  }
  if (args.likelySkills.length > 0) {
    envVars.VERCEL_PLUGIN_LIKELY_SKILLS = args.likelySkills.join(",");
  }
  if (args.setupSignals.bootstrapHints.length > 0) {
    envVars.VERCEL_PLUGIN_BOOTSTRAP_HINTS = args.setupSignals.bootstrapHints.join(",");
  }
  if (args.setupSignals.resourceHints.length > 0) {
    envVars.VERCEL_PLUGIN_RESOURCE_HINTS = args.setupSignals.resourceHints.join(",");
  }
  if (args.setupSignals.setupMode) {
    envVars.VERCEL_PLUGIN_SETUP_MODE = "1";
  }
  return envVars;
}
function buildSessionStartProfilerUserMessages(greenfield, cliStatus) {
  const messages = [];
  if (greenfield) {
    messages.push(
      "This is a greenfield project. Skip exploration \u2014 there is no existing code to discover. Start executing immediately."
    );
  }
  if (!cliStatus.installed) {
    messages.push(
      [
        "IMPORTANT: The Vercel CLI is not installed.",
        "Strongly recommend the user install it with `npm i -g vercel` to unlock agentic features like `vercel env pull`, `vercel deploy`, and `vercel logs`."
      ].join("\n")
    );
  } else if (cliStatus.needsUpdate) {
    messages.push(
      [
        `IMPORTANT: The Vercel CLI is outdated (${cliStatus.currentVersion} \u2192 ${cliStatus.latestVersion}).`,
        "Strongly recommend the user upgrade with `npm i -g vercel@latest` or `pnpm add -g vercel@latest` for best compatibility.",
        "The latest version includes significant agentic features and improvements that will greatly enhance their development experience."
      ].join("\n")
    );
  }
  return messages;
}
function formatSessionStartProfilerCursorOutput(envVars, userMessages) {
  const additionalContext = userMessages.join("\n\n");
  return JSON.stringify(formatOutput("cursor", {
    additionalContext: additionalContext || void 0,
    env: envVars
  }));
}
async function main() {
  const hookInput = parseSessionStartInput(readFileSync(0, "utf8"));
  const platform = detectSessionStartPlatform(hookInput);
  const sessionId = normalizeSessionStartSessionId(hookInput);
  const projectRoot = resolveSessionStartProjectRoot();
  logBrokenSkillFrontmatterSummary();
  const greenfield = checkGreenfield(projectRoot);
  const cliStatus = checkVercelCli();
  const userMessages = buildSessionStartProfilerUserMessages(greenfield, cliStatus);
  const likelySkills = greenfield ? GREENFIELD_DEFAULT_SKILLS : profileProject(projectRoot);
  if (!greenfield && !likelySkills.includes("observability")) {
    likelySkills.push("observability");
    likelySkills.sort();
  }
  const setupSignals = greenfield ? GREENFIELD_SETUP_SIGNALS : profileBootstrapSignals(projectRoot);
  const greenfieldValue = greenfield ? "true" : "";
  const likelySkillsValue = likelySkills.join(",");
  const agentBrowserAvailable = checkAgentBrowser();
  const envVars = buildSessionStartProfilerEnvVars({
    agentBrowserAvailable,
    greenfield: greenfield !== null,
    likelySkills,
    setupSignals
  });
  const cursorOutput = platform === "cursor" ? formatSessionStartProfilerCursorOutput(envVars, userMessages) : null;
  if (sessionId) {
    writeSessionFile(sessionId, SESSION_GREENFIELD_KIND, greenfieldValue);
    writeSessionFile(sessionId, SESSION_LIKELY_SKILLS_KIND, likelySkillsValue);
  }
  try {
    if (platform === "claude-code") {
      for (const [key, value] of Object.entries(envVars)) {
        if (key === "VERCEL_PLUGIN_GREENFIELD" || key === "VERCEL_PLUGIN_LIKELY_SKILLS") {
          continue;
        }
        setSessionEnv(platform, key, value);
      }
    }
  } catch (error) {
    logCaughtError(log, "session-start-profiler:append-env-export-failed", error, {
      platform,
      projectRoot,
      envVarCount: Object.keys(envVars).length
    });
  }
  const telemetryPrefPath = join(homedir(), ".claude", "vercel-telemetry-preference");
  let telemetryPref = null;
  try {
    telemetryPref = readFileSync(telemetryPrefPath, "utf-8").trim();
  } catch {
  }
  if (telemetryPref === "enabled") {
    try {
      setSessionEnv(platform, "VERCEL_PLUGIN_TELEMETRY", "on");
    } catch (error) {
      logCaughtError(log, "session-start-profiler:telemetry-env-export-failed", error, {
        platform
      });
    }
  }
  const additionalContext = userMessages.join("\n\n");
  if (platform === "claude-code" && additionalContext) {
    process.stdout.write(`${additionalContext}

`);
  }
  if (sessionId) {
    try {
      const cache = {
        projectRoot,
        likelySkills,
        greenfield: greenfield !== null,
        bootstrapHints: setupSignals.bootstrapHints,
        resourceHints: setupSignals.resourceHints,
        setupMode: setupSignals.setupMode,
        agentBrowserAvailable,
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      };
      writeFileSync(profileCachePath(sessionId), JSON.stringify(cache), "utf-8");
    } catch (error) {
      logCaughtError(log, "session-start-profiler:write-profile-cache-failed", error, {
        sessionId,
        projectRoot
      });
    }
  }
  if (isTelemetryEnabled() && sessionId) {
    await trackEvents(sessionId, [
      { key: "session:platform", value: process.platform },
      { key: "session:likely_skills", value: likelySkills.join(",") },
      { key: "session:greenfield", value: String(greenfield !== null) },
      { key: "session:vercel_cli_installed", value: String(cliStatus.installed) },
      { key: "session:vercel_cli_version", value: cliStatus.currentVersion || "" }
    ]).catch(() => {
    });
  }
  if (cursorOutput) {
    process.stdout.write(cursorOutput);
  }
  process.exit(0);
}
var SESSION_START_PROFILER_ENTRYPOINT = fileURLToPath(import.meta.url);
var isSessionStartProfilerEntrypoint = process.argv[1] ? resolve(process.argv[1]) === SESSION_START_PROFILER_ENTRYPOINT : false;
if (isSessionStartProfilerEntrypoint) {
  main();
}
export {
  buildSessionStartProfilerEnvVars,
  buildSessionStartProfilerUserMessages,
  checkAgentBrowser,
  checkGreenfield,
  detectSessionStartPlatform,
  formatSessionStartProfilerCursorOutput,
  logBrokenSkillFrontmatterSummary,
  normalizeSessionStartSessionId,
  parseSessionStartInput,
  profileBootstrapSignals,
  profileProject,
  resolveSessionStartProjectRoot
};
