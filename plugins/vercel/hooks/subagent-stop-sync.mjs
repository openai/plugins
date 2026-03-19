#!/usr/bin/env node

// hooks/src/subagent-stop-sync.mts
import { appendFileSync } from "fs";
import { readFileSync } from "fs";
import { resolve } from "path";
import { tmpdir } from "os";
import { fileURLToPath } from "url";
import { listSessionKeys } from "./hook-env.mjs";
import { createLogger, logCaughtError } from "./logger.mjs";
var log = createLogger();
function parseInput() {
  try {
    const raw = readFileSync(0, "utf8");
    if (!raw.trim()) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
function ledgerPath(sessionId) {
  return resolve(tmpdir(), `vercel-${sessionId}-subagent-ledger.jsonl`);
}
function appendLedger(entry) {
  const path = ledgerPath(entry.session_id);
  try {
    appendFileSync(path, JSON.stringify(entry) + "\n", "utf-8");
  } catch (error) {
    logCaughtError(log, "subagent-stop-sync:append-ledger-failed", error, { path });
  }
}
function main() {
  const input = parseInput();
  if (!input) {
    process.exit(0);
  }
  const sessionId = input.session_id;
  if (!sessionId) {
    process.exit(0);
  }
  const agentId = input.agent_id ?? "unknown";
  const agentType = input.agent_type ?? "unknown";
  log.debug("subagent-stop-sync", { sessionId, agentId, agentType });
  let ledgerEntryWritten = false;
  try {
    appendLedger({
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      session_id: sessionId,
      agent_id: agentId,
      agent_type: agentType,
      agent_transcript_path: input.agent_transcript_path
    });
    ledgerEntryWritten = true;
  } catch (error) {
    logCaughtError(log, "subagent-stop-sync:ledger-write-failed", error, {
      sessionId,
      agentId
    });
  }
  let skillsInjected = 0;
  try {
    const claimed = listSessionKeys(sessionId, "seen-skills", agentId !== "unknown" ? agentId : void 0);
    skillsInjected = claimed.length;
  } catch {
  }
  log.summary("subagent-stop-sync:complete", {
    agent_id: agentId,
    agent_type: agentType,
    skills_injected: skillsInjected,
    ledger_entry_written: ledgerEntryWritten
  });
  process.exit(0);
}
var ENTRYPOINT = fileURLToPath(import.meta.url);
var isEntrypoint = process.argv[1] ? resolve(process.argv[1]) === ENTRYPOINT : false;
if (isEntrypoint) {
  main();
}
export {
  appendLedger,
  ledgerPath,
  main,
  parseInput
};
