#!/usr/bin/env node

// hooks/src/pretooluse-subagent-spawn-observe.mts
import { readFileSync } from "fs";
import { resolve } from "path";
import { fileURLToPath } from "url";
import { appendPendingLaunch } from "./subagent-state.mjs";
import { createLogger, logCaughtError } from "./logger.mjs";
var log = createLogger();
var EMPTY_OUTPUT = "{}";
function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function resolveSessionId(input, env) {
  if (typeof input.session_id === "string" && input.session_id.trim() !== "") {
    return input.session_id;
  }
  if (typeof env.SESSION_ID === "string" && env.SESSION_ID.trim() !== "") {
    return env.SESSION_ID;
  }
  return null;
}
function parseInput(raw, env = process.env) {
  const trimmed = (raw || "").trim();
  if (!trimmed) {
    log.debug("pretooluse-subagent-spawn-observe-skip", { reason: "stdin_empty" });
    return null;
  }
  let input;
  try {
    const parsed = JSON.parse(trimmed);
    if (!isRecord(parsed)) {
      log.debug("pretooluse-subagent-spawn-observe-skip", { reason: "stdin_not_object" });
      return null;
    }
    input = parsed;
  } catch {
    log.debug("pretooluse-subagent-spawn-observe-skip", { reason: "stdin_parse_fail" });
    return null;
  }
  const toolName = typeof input.tool_name === "string" ? input.tool_name : "";
  if (toolName !== "Agent") {
    log.debug("pretooluse-subagent-spawn-observe-skip", { reason: "unsupported_tool", toolName });
    return null;
  }
  const sessionId = resolveSessionId(input, env);
  if (!sessionId) {
    log.debug("pretooluse-subagent-spawn-observe-skip", { reason: "missing_session_id" });
    return null;
  }
  const toolInput = isRecord(input.tool_input) ? input.tool_input : {};
  return { sessionId, toolInput };
}
function buildPendingLaunchRecord(toolInput, createdAt) {
  const resume = typeof toolInput.resume === "string" ? toolInput.resume : void 0;
  const name = typeof toolInput.name === "string" ? toolInput.name : void 0;
  const pendingLaunch = {
    description: typeof toolInput.description === "string" ? toolInput.description : "",
    prompt: typeof toolInput.prompt === "string" ? toolInput.prompt : "",
    subagent_type: typeof toolInput.subagent_type === "string" ? toolInput.subagent_type : "",
    createdAt,
    ...resume !== void 0 ? { resume } : {},
    ...name !== void 0 ? { name } : {}
  };
  return pendingLaunch;
}
function writePendingLaunchRecord(sessionId, toolInput) {
  const createdAt = Date.now();
  const payload = buildPendingLaunchRecord(toolInput, createdAt);
  appendPendingLaunch(sessionId, payload);
  log.debug("pretooluse-subagent-spawn-observe-recorded", {
    sessionId,
    subagentType: typeof payload.subagent_type === "string" ? payload.subagent_type : null,
    name: typeof payload.name === "string" ? payload.name : null
  });
  return sessionId;
}
function run(rawInput) {
  let raw = rawInput;
  if (raw === void 0) {
    try {
      raw = readFileSync(0, "utf-8");
    } catch {
      return EMPTY_OUTPUT;
    }
  }
  const parsed = parseInput(raw);
  if (!parsed) {
    return EMPTY_OUTPUT;
  }
  try {
    writePendingLaunchRecord(parsed.sessionId, parsed.toolInput);
  } catch (error) {
    logCaughtError(log, "pretooluse-subagent-spawn-observe-write-failed", error, {
      attempted: "write_pending_launch_record",
      sessionId: parsed.sessionId,
      state: "launch_observation_failed"
    });
  }
  return EMPTY_OUTPUT;
}
function isMainModule() {
  const entrypoint = fileURLToPath(import.meta.url);
  return process.argv[1] ? resolve(process.argv[1]) === entrypoint : false;
}
if (isMainModule()) {
  process.stdout.write(run());
}
export {
  buildPendingLaunchRecord,
  parseInput,
  run,
  writePendingLaunchRecord
};
