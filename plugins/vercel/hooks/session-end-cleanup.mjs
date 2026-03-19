#!/usr/bin/env node

// hooks/src/session-end-cleanup.mts
import { createHash } from "crypto";
import { readdirSync, readFileSync, rmSync, unlinkSync, writeFileSync } from "fs";
import { homedir, tmpdir } from "os";
import { join, resolve } from "path";
import { fileURLToPath } from "url";
var SAFE_SESSION_ID_RE = /^[a-zA-Z0-9_-]+$/;
function tempSessionIdSegment(sessionId) {
  if (SAFE_SESSION_ID_RE.test(sessionId)) {
    return sessionId;
  }
  return createHash("sha256").update(sessionId).digest("hex");
}
function removeFileIfPresent(path) {
  try {
    unlinkSync(path);
  } catch {
  }
}
function removeDirIfPresent(path) {
  try {
    rmSync(path, { recursive: true, force: true });
  } catch {
  }
}
function parseSessionEndHookInput(raw) {
  try {
    if (!raw.trim()) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
function normalizeSessionEndSessionId(input) {
  if (!input) return null;
  const sessionId = input.session_id ?? input.conversation_id ?? "";
  return typeof sessionId === "string" && sessionId.length > 0 ? sessionId : null;
}
function parseSessionIdFromStdin() {
  return normalizeSessionEndSessionId(parseSessionEndHookInput(readFileSync(0, "utf8")));
}
function main() {
  try {
    const prefPath = join(homedir(), ".claude", "vercel-telemetry-preference");
    const pref = readFileSync(prefPath, "utf-8").trim();
    if (pref === "asked") {
      writeFileSync(prefPath, "disabled");
    }
  } catch {
  }
  const sessionId = parseSessionIdFromStdin();
  if (sessionId === null) {
    process.exit(0);
  }
  const tempRoot = tmpdir();
  const prefix = `vercel-${tempSessionIdSegment(sessionId)}-`;
  let entries = [];
  try {
    entries = readdirSync(tempRoot).filter((name) => name.startsWith(prefix));
  } catch {
  }
  for (const entry of entries) {
    const fullPath = join(tempRoot, entry);
    if (entry.endsWith(".d") || entry.endsWith("-pending-launches")) {
      removeDirIfPresent(fullPath);
    } else {
      removeFileIfPresent(fullPath);
    }
  }
  process.exit(0);
}
var SESSION_END_CLEANUP_ENTRYPOINT = fileURLToPath(import.meta.url);
var isSessionEndCleanupEntrypoint = process.argv[1] ? resolve(process.argv[1]) === SESSION_END_CLEANUP_ENTRYPOINT : false;
if (isSessionEndCleanupEntrypoint) {
  main();
}
export {
  normalizeSessionEndSessionId,
  parseSessionEndHookInput
};
