#!/usr/bin/env node

// hooks/src/session-start-seen-skills.mts
import { readFileSync } from "fs";
import { resolve } from "path";
import { fileURLToPath } from "url";
import {
  formatOutput
} from "./compat.mjs";
import {
  removeAllSessionDedupArtifacts
} from "./hook-env.mjs";
import { createLogger } from "./logger.mjs";
var CONTEXT_CLEARING_EVENTS = /* @__PURE__ */ new Set(["clear", "compact"]);
function parseSessionStartSeenSkillsInput(raw) {
  try {
    if (!raw.trim()) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
function detectSessionStartSeenSkillsPlatform(input, _env = process.env) {
  if (input && ("conversation_id" in input || "cursor_version" in input)) {
    return "cursor";
  }
  return "claude-code";
}
function formatSessionStartSeenSkillsCursorOutput() {
  return JSON.stringify(formatOutput("cursor", {
    env: {
      VERCEL_PLUGIN_SEEN_SKILLS: ""
    }
  }));
}
function resetDedupStateForSession(sessionId) {
  return removeAllSessionDedupArtifacts(sessionId);
}
function main() {
  const log = createLogger();
  const input = parseSessionStartSeenSkillsInput(readFileSync(0, "utf8"));
  const platform = detectSessionStartSeenSkillsPlatform(input);
  if (platform === "cursor") {
    process.stdout.write(formatSessionStartSeenSkillsCursorOutput());
    return;
  }
  const hookEvent = input?.hook_event_name ?? "";
  const sessionId = input?.session_id ?? "";
  const resetTriggered = CONTEXT_CLEARING_EVENTS.has(hookEvent) && !!sessionId;
  let removedFiles = 0;
  let removedDirs = 0;
  if (resetTriggered) {
    const result = resetDedupStateForSession(sessionId);
    removedFiles = result.removedFiles;
    removedDirs = result.removedDirs;
  }
  log.debug("session-start-seen-skills:decision", {
    event: hookEvent || "unknown",
    sessionId: sessionId || "none",
    resetTriggered,
    removedFiles,
    removedDirs
  });
}
var SESSION_START_SEEN_SKILLS_ENTRYPOINT = fileURLToPath(import.meta.url);
var isSessionStartSeenSkillsEntrypoint = process.argv[1] ? resolve(process.argv[1]) === SESSION_START_SEEN_SKILLS_ENTRYPOINT : false;
if (isSessionStartSeenSkillsEntrypoint) {
  main();
}
export {
  detectSessionStartSeenSkillsPlatform,
  formatSessionStartSeenSkillsCursorOutput,
  parseSessionStartSeenSkillsInput,
  resetDedupStateForSession
};
