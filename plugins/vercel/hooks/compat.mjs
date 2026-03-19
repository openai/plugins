// hooks/src/compat.mts
import { appendFileSync } from "fs";
var cursorSessionEnv = /* @__PURE__ */ new Map();
var currentHookEventName;
function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function readString(value) {
  return typeof value === "string" ? value : void 0;
}
function readRecord(value) {
  return isRecord(value) ? value : void 0;
}
function readWorkspaceRoot(raw) {
  if (!Array.isArray(raw.workspace_roots)) return void 0;
  const firstRoot = raw.workspace_roots[0];
  return typeof firstRoot === "string" ? firstRoot : void 0;
}
function normalizeToolOutputValue(value) {
  if (typeof value === "undefined") return void 0;
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}
function escapeShellEnvValue(value) {
  return value.replace(/(["\\$`])/g, "\\$1");
}
function drainCursorSessionEnv() {
  if (cursorSessionEnv.size === 0) return void 0;
  const env = Object.fromEntries(cursorSessionEnv);
  cursorSessionEnv.clear();
  return env;
}
function detectPlatform(raw) {
  if ("conversation_id" in raw || "workspace_roots" in raw || "cursor_version" in raw) {
    return "cursor";
  }
  return "claude-code";
}
function normalizeInput(raw) {
  const platform = detectPlatform(raw);
  const sessionId = readString(raw.session_id ?? raw.conversation_id) ?? "";
  const cwd = readString(raw.cwd) ?? readWorkspaceRoot(raw) ?? process.env.CURSOR_PROJECT_DIR ?? process.env.CLAUDE_PROJECT_DIR ?? process.cwd();
  const hookEvent = readString(raw.hook_event_name) ?? "";
  const toolOutput = normalizeToolOutputValue(raw.tool_output ?? raw.tool_response);
  currentHookEventName = hookEvent || void 0;
  return {
    platform,
    sessionId,
    cwd,
    hookEvent,
    toolName: readString(raw.tool_name),
    toolInput: readRecord(raw.tool_input),
    toolOutput,
    prompt: readString(raw.prompt),
    raw
  };
}
function formatOutput(platform, internal) {
  if (platform === "cursor") {
    const env = {
      ...drainCursorSessionEnv() ?? {},
      ...internal.env ?? {}
    };
    const output = {};
    if (typeof internal.additionalContext !== "undefined") {
      output.additional_context = internal.additionalContext;
    }
    if (typeof internal.permission !== "undefined") {
      output.permission = internal.permission;
    }
    if (Object.keys(env).length > 0) {
      output.env = env;
    }
    if (typeof internal.userMessage !== "undefined") {
      output.user_message = internal.userMessage;
    }
    return output;
  }
  const hookSpecificOutput = {};
  if (typeof internal.additionalContext !== "undefined") {
    if (currentHookEventName) {
      hookSpecificOutput.hookEventName = currentHookEventName;
    }
    hookSpecificOutput.additionalContext = internal.additionalContext;
  }
  if (typeof internal.permission !== "undefined") {
    if (currentHookEventName) {
      hookSpecificOutput.hookEventName = currentHookEventName;
    }
    hookSpecificOutput.permissionDecision = internal.permission;
  }
  if (Object.keys(hookSpecificOutput).length === 0) {
    return {};
  }
  return { hookSpecificOutput };
}
function getEnvFilePath() {
  return process.env.CLAUDE_ENV_FILE || null;
}
function setSessionEnv(platform, key, value) {
  if (platform === "cursor") {
    cursorSessionEnv.set(key, value);
    return;
  }
  const envFile = getEnvFilePath();
  if (!envFile) return;
  appendFileSync(envFile, `export ${key}="${escapeShellEnvValue(value)}"
`);
}
function getProjectRoot() {
  return process.env.CLAUDE_PROJECT_ROOT ?? process.env.CURSOR_PROJECT_DIR ?? process.cwd();
}
export {
  detectPlatform,
  formatOutput,
  getEnvFilePath,
  getProjectRoot,
  normalizeInput,
  setSessionEnv
};
