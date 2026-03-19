#!/usr/bin/env node

// hooks/src/posttooluse-bash-chain.mts
import { readFileSync, realpathSync } from "fs";
import { join, resolve } from "path";
import { fileURLToPath } from "url";
import { detectPlatform } from "./compat.mjs";
import {
  pluginRoot as resolvePluginRoot,
  readSessionFile,
  safeReadFile,
  tryClaimSessionKey,
  syncSessionFileFromClaims
} from "./hook-env.mjs";
import { extractFrontmatter } from "./skill-map-frontmatter.mjs";
import { createLogger } from "./logger.mjs";
var PLUGIN_ROOT = resolvePluginRoot();
var CHAIN_BUDGET_BYTES = 18e3;
var DEFAULT_CHAIN_CAP = 2;
var PACKAGE_SKILL_MAP = {
  // Express / traditional Node servers → Vercel Functions
  express: {
    skill: "vercel-functions",
    message: "Express.js detected \u2014 Vercel uses Web API route handlers, not Express. Loading Vercel Functions guidance."
  },
  fastify: {
    skill: "vercel-functions",
    message: "Fastify detected \u2014 consider Vercel Functions with Web Request/Response API for serverless deployment."
  },
  koa: {
    skill: "vercel-functions",
    message: "Koa detected \u2014 consider Vercel Functions with Web Request/Response API for serverless deployment."
  },
  // Queue / background job libraries → Vercel Queues
  bullmq: {
    skill: "vercel-queues",
    message: "BullMQ detected \u2014 Vercel Queues provides durable event streaming without self-managed Redis. Loading Queues guidance."
  },
  bull: {
    skill: "vercel-queues",
    message: "Bull detected \u2014 Vercel Queues provides durable event streaming without self-managed Redis. Loading Queues guidance."
  },
  // Database / ORM libraries → Vercel Storage
  mongoose: {
    skill: "vercel-storage",
    message: "Mongoose detected \u2014 loading Vercel Storage guidance for database options on the platform."
  },
  prisma: {
    skill: "vercel-storage",
    message: "Prisma detected \u2014 loading Vercel Storage guidance for Neon Postgres (recommended) and other Marketplace databases."
  },
  "@libsql/client": {
    skill: "vercel-storage",
    message: "@libsql/client detected \u2014 loading Vercel Storage guidance for Marketplace database alternatives."
  },
  "@vercel/postgres": {
    skill: "vercel-storage",
    message: "@vercel/postgres is sunset \u2014 use @neondatabase/serverless instead. Loading Storage migration guidance."
  },
  "@vercel/kv": {
    skill: "vercel-storage",
    message: "@vercel/kv is sunset \u2014 use @upstash/redis instead. Loading Storage migration guidance."
  },
  // Payments → Stripe integration
  stripe: {
    skill: "payments",
    message: "Stripe detected \u2014 loading Vercel Marketplace Stripe integration guidance for checkout, webhooks, and subscriptions."
  },
  // Direct AI provider SDKs → AI Gateway
  openai: {
    skill: "ai-gateway",
    message: "Direct OpenAI SDK detected \u2014 AI Gateway provides OIDC auth, failover, and cost tracking with no manual API keys. Loading AI Gateway guidance."
  },
  "@anthropic-ai/sdk": {
    skill: "ai-gateway",
    message: "Direct Anthropic SDK detected \u2014 AI Gateway provides unified access to all providers. Loading AI Gateway guidance."
  },
  "@google/generative-ai": {
    skill: "ai-gateway",
    message: "Direct Google AI SDK detected \u2014 AI Gateway provides unified access to all providers. Loading AI Gateway guidance."
  },
  langchain: {
    skill: "ai-sdk",
    message: "LangChain detected \u2014 AI SDK v6 provides native tool calling, agents, and streaming without the LangChain abstraction layer. Loading AI SDK guidance."
  },
  "@langchain/core": {
    skill: "ai-sdk",
    message: "LangChain Core detected \u2014 AI SDK v6 provides native tool calling, agents, and streaming without the LangChain abstraction layer. Loading AI SDK guidance."
  },
  // Auth
  "next-auth": {
    skill: "auth",
    message: "next-auth detected \u2014 consider Clerk via Vercel Marketplace for managed auth with auto-provisioned env vars. Loading auth guidance."
  },
  "@clerk/nextjs": {
    skill: "auth",
    message: "@clerk/nextjs detected \u2014 loading Vercel Marketplace Clerk integration guidance for middleware auth and sign-in flows."
  },
  // CMS
  "@sanity/client": {
    skill: "cms",
    message: "@sanity/client detected \u2014 loading Vercel Marketplace Sanity integration guidance for studio, preview mode, and revalidation."
  },
  contentful: {
    skill: "cms",
    message: "Contentful detected \u2014 loading CMS integration guidance for content modeling, preview mode, and revalidation webhooks."
  },
  // Chat platforms → Chat SDK
  "@slack/bolt": {
    skill: "chat-sdk",
    message: "@slack/bolt detected \u2014 Chat SDK provides a unified multi-platform API (Slack, Teams, Discord, Telegram) with a single codebase. Loading Chat SDK guidance."
  },
  "@slack/web-api": {
    skill: "chat-sdk",
    message: "@slack/web-api detected \u2014 Chat SDK provides a unified multi-platform API with cards, streaming, and state management. Loading Chat SDK guidance."
  },
  "discord.js": {
    skill: "chat-sdk",
    message: "discord.js detected \u2014 Chat SDK provides a unified multi-platform API (Slack, Teams, Discord, Telegram) with a single codebase. Loading Chat SDK guidance."
  },
  telegraf: {
    skill: "chat-sdk",
    message: "Telegraf detected \u2014 Chat SDK provides a unified multi-platform API (Slack, Teams, Discord, Telegram) with a single codebase. Loading Chat SDK guidance."
  },
  grammy: {
    skill: "chat-sdk",
    message: "Grammy detected \u2014 Chat SDK provides a unified multi-platform API (Slack, Teams, Discord, Telegram) with a single codebase. Loading Chat SDK guidance."
  },
  // Email
  resend: {
    skill: "email",
    message: "Resend detected \u2014 loading Vercel Marketplace Resend integration guidance for transactional emails and React Email templates."
  },
  // Workflow-related
  workflow: {
    skill: "workflow",
    message: "Workflow DevKit installed \u2014 loading WDK guidance for durable workflows."
  },
  // AI SDK
  ai: {
    skill: "ai-sdk",
    message: "AI SDK installed \u2014 loading AI SDK v6 guidance."
  },
  "@ai-sdk/react": {
    skill: "ai-sdk",
    message: "@ai-sdk/react installed \u2014 loading AI SDK v6 guidance for React hooks."
  },
  // Feature flags
  "@vercel/flags": {
    skill: "vercel-flags",
    message: "Vercel Flags installed \u2014 loading feature flags guidance."
  },
  // SWR
  swr: {
    skill: "swr",
    message: "SWR installed \u2014 loading data-fetching guidance."
  },
  // Security / middleware
  helmet: {
    skill: "vercel-firewall",
    message: "Helmet detected \u2014 Vercel Firewall provides DDoS protection, WAF rules, and security headers at the edge. Loading Firewall guidance."
  },
  cors: {
    skill: "routing-middleware",
    message: "cors detected \u2014 Vercel Routing Middleware handles CORS at the platform level with rewrites and headers. Loading Routing Middleware guidance."
  },
  // Env management
  dotenv: {
    skill: "env-vars",
    message: "dotenv detected \u2014 Vercel manages environment variables natively via `vercel env`. Loading env-vars guidance."
  },
  // Cron / scheduling → Vercel cron jobs
  "node-cron": {
    skill: "cron-jobs",
    message: "node-cron detected \u2014 Vercel Cron Jobs provides managed scheduling via vercel.json. Loading cron guidance."
  },
  cron: {
    skill: "cron-jobs",
    message: "cron package detected \u2014 Vercel Cron Jobs provides managed scheduling via vercel.json. Loading cron guidance."
  }
};
var log = createLogger();
var INSTALL_CMD_RE = /(?:npm\s+(?:install|i|add)|yarn\s+add|pnpm\s+(?:add|install)|bun\s+(?:add|install))\s+(.+)/;
function parseInstallCommand(command) {
  if (!command || typeof command !== "string") return [];
  const match = INSTALL_CMD_RE.exec(command);
  if (!match) return [];
  const pkgString = match[1];
  const packages = [];
  for (const token of pkgString.split(/\s+/)) {
    if (!token) continue;
    if (token.startsWith("-")) continue;
    if (token.startsWith(".") || token.startsWith("/")) continue;
    let pkgName = token;
    if (pkgName.startsWith("@")) {
      const slashIndex = pkgName.indexOf("/");
      if (slashIndex > 0) {
        const afterSlash = pkgName.slice(slashIndex + 1);
        const versionAt = afterSlash.indexOf("@");
        if (versionAt > 0) {
          pkgName = pkgName.slice(0, slashIndex + 1 + versionAt);
        }
      }
    } else {
      const atIndex = pkgName.indexOf("@");
      if (atIndex > 0) {
        pkgName = pkgName.slice(0, atIndex);
      }
    }
    if (pkgName) packages.push(pkgName);
  }
  return packages;
}
function resolveSessionId(input) {
  const sessionId = input.session_id ?? input.conversation_id;
  return typeof sessionId === "string" && sessionId.trim() !== "" ? sessionId : null;
}
function parseBashInput(raw, logger) {
  const l = logger || log;
  const trimmed = (raw || "").trim();
  if (!trimmed) return null;
  let input;
  try {
    input = JSON.parse(trimmed);
  } catch {
    return null;
  }
  const toolName = input.tool_name || "";
  if (toolName !== "Bash") {
    l.debug("posttooluse-bash-chain-skip", { reason: "not_bash_tool", toolName });
    return null;
  }
  const toolInput = input.tool_input || {};
  const command = toolInput.command || "";
  if (!command) {
    l.debug("posttooluse-bash-chain-skip", { reason: "no_command" });
    return null;
  }
  const sessionId = resolveSessionId(input);
  const platform = detectPlatform(input);
  return { command, sessionId, platform };
}
function runBashChainInjection(packages, sessionId, pluginRoot, logger, env = process.env) {
  const l = logger || log;
  const result = { injected: [], totalBytes: 0 };
  if (packages.length === 0) return result;
  const chainCap = Math.max(
    1,
    parseInt(env.VERCEL_PLUGIN_CHAIN_CAP || "", 10) || DEFAULT_CHAIN_CAP
  );
  const fileSeen = sessionId ? readSessionFile(sessionId, "seen-skills") : "";
  const seenSet = new Set(fileSeen.split(",").filter(Boolean));
  const targetsSeen = /* @__PURE__ */ new Set();
  for (const pkg of packages) {
    const mapping = PACKAGE_SKILL_MAP[pkg];
    if (!mapping) continue;
    const { skill, message } = mapping;
    if (targetsSeen.has(skill)) continue;
    targetsSeen.add(skill);
    if (result.injected.length >= chainCap) {
      l.debug("posttooluse-bash-chain-cap-reached", {
        cap: chainCap,
        remaining: packages.length - result.injected.length
      });
      break;
    }
    if (seenSet.has(skill)) {
      l.debug("posttooluse-bash-chain-skip-dedup", { pkg, skill });
      continue;
    }
    const skillPath = join(pluginRoot, "skills", skill, "SKILL.md");
    const skillContent = safeReadFile(skillPath);
    if (!skillContent) {
      l.debug("posttooluse-bash-chain-skip-missing", { pkg, skill, path: skillPath });
      continue;
    }
    const { body } = extractFrontmatter(skillContent);
    const trimmedBody = body.trim();
    if (!trimmedBody) continue;
    const bytes = Buffer.byteLength(trimmedBody, "utf-8");
    if (result.totalBytes + bytes > CHAIN_BUDGET_BYTES) {
      l.debug("posttooluse-bash-chain-budget-exceeded", {
        pkg,
        skill,
        bytes,
        totalBytes: result.totalBytes,
        budget: CHAIN_BUDGET_BYTES
      });
      break;
    }
    if (sessionId) {
      const claimed = tryClaimSessionKey(sessionId, "seen-skills", skill);
      if (!claimed) {
        l.debug("posttooluse-bash-chain-skip-concurrent-claim", { pkg, skill });
        seenSet.add(skill);
        continue;
      }
      syncSessionFileFromClaims(sessionId, "seen-skills");
    }
    seenSet.add(skill);
    result.injected.push({ packageName: pkg, skill, message, content: trimmedBody });
    result.totalBytes += bytes;
    l.debug("posttooluse-bash-chain-injected", { pkg, skill, bytes, totalBytes: result.totalBytes });
  }
  if (result.injected.length > 0) {
    l.summary("posttooluse-bash-chain-result", {
      injectedCount: result.injected.length,
      totalBytes: result.totalBytes,
      targets: result.injected.map((i) => i.skill)
    });
  }
  return result;
}
function formatPlatformOutput(platform, additionalContext) {
  if (platform === "cursor") {
    return JSON.stringify({ additional_context: additionalContext });
  }
  const output = {
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext
    }
  };
  return JSON.stringify(output);
}
function formatBashChainOutput(chainResult, platform = "claude-code") {
  if (chainResult.injected.length === 0) return "{}";
  const parts = [];
  for (const chain of chainResult.injected) {
    parts.push(
      `<!-- posttooluse-bash-chain: ${chain.packageName} \u2192 ${chain.skill} -->`,
      `**Skill context auto-loaded** (${chain.skill}): ${chain.message}`,
      "",
      chain.content,
      `<!-- /posttooluse-bash-chain: ${chain.skill} -->`
    );
  }
  const metadata = {
    version: 1,
    hook: "posttooluse-bash-chain",
    packages: chainResult.injected.map((i) => i.packageName),
    chainedSkills: chainResult.injected.map((i) => i.skill)
  };
  parts.push(`<!-- postBashChain: ${JSON.stringify(metadata)} -->`);
  return formatPlatformOutput(platform, parts.join("\n"));
}
function run() {
  const tStart = log.active ? log.now() : 0;
  let raw;
  try {
    raw = readFileSync(0, "utf-8");
  } catch {
    return "{}";
  }
  const parsed = parseBashInput(raw, log);
  if (!parsed) return "{}";
  const { command, sessionId, platform } = parsed;
  const packages = parseInstallCommand(command);
  if (packages.length === 0) {
    log.debug("posttooluse-bash-chain-skip", { reason: "no_packages_detected", command });
    return "{}";
  }
  log.debug("posttooluse-bash-chain-packages", { packages, command });
  const chainResult = runBashChainInjection(packages, sessionId, PLUGIN_ROOT, log);
  const output = formatBashChainOutput(chainResult, platform);
  log.complete("posttooluse-bash-chain-done", {
    matchedCount: packages.length,
    injectedCount: chainResult.injected.length,
    dedupedCount: 0,
    cappedCount: 0
  }, log.active ? { total: Math.round(log.now() - tStart) } : {});
  return output;
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
      `[${(/* @__PURE__ */ new Date()).toISOString()}] CRASH in posttooluse-bash-chain.mts`,
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
  PACKAGE_SKILL_MAP,
  formatBashChainOutput,
  parseBashInput,
  parseInstallCommand,
  run,
  runBashChainInjection
};
