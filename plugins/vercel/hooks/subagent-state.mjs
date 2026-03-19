// hooks/src/subagent-state.mts
import { createHash } from "crypto";
import {
  appendFileSync,
  closeSync,
  mkdirSync,
  openSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync
} from "fs";
import { tmpdir } from "os";
import { dirname, join, resolve } from "path";
import * as hookEnvNs from "./hook-env.mjs";
import { createLogger, logCaughtError } from "./logger.mjs";
var PENDING_LAUNCH_TTL_MS = 6e4;
var LOCK_WAIT_TIMEOUT_MS = 2e3;
var LOCK_WAIT_INTERVAL_MS = 10;
var LOCK_STALE_MS = 5e3;
var hookEnv = hookEnvNs;
var log = createLogger();
function isNodeErrorCode(error, code) {
  return typeof error === "object" && error !== null && "code" in error && error.code === code;
}
function sleepMs(ms) {
  const deadline = Date.now() + ms;
  while (Date.now() < deadline) {
  }
}
function resolveTmpRoot() {
  try {
    const tempRoot = hookEnv.getTmpDir?.();
    if (typeof tempRoot === "string" && tempRoot.trim() !== "") {
      return resolve(tempRoot);
    }
  } catch (error) {
    logCaughtError(log, "subagent-state:get-tmp-dir-failed", error, {});
  }
  return resolve(tmpdir());
}
function pendingLaunchPath(sessionId) {
  return join(resolveTmpRoot(), `vercel-${sessionId}-pending-launches.jsonl`);
}
function pendingLaunchLockPath(sessionId) {
  return `${pendingLaunchPath(sessionId)}.lock`;
}
function agentStatePath(sessionId, agentId) {
  const agentHash = createHash("sha256").update(agentId).digest("hex");
  return join(resolveTmpRoot(), `vercel-${sessionId}-agent-${agentHash}.json`);
}
function maybeClearStaleLock(lockPath, context) {
  try {
    const stats = statSync(lockPath);
    if (Date.now() - stats.mtimeMs > LOCK_STALE_MS) {
      rmSync(lockPath, { force: true });
      log.debug("subagent-state:stale-lock-cleared", { lockPath, ...context });
    }
  } catch (error) {
    if (!isNodeErrorCode(error, "ENOENT")) {
      logCaughtError(log, "subagent-state:stale-lock-check-failed", error, { lockPath, ...context });
    }
  }
}
function acquireLock(lockPath, context) {
  mkdirSync(dirname(lockPath), { recursive: true });
  const deadline = Date.now() + LOCK_WAIT_TIMEOUT_MS;
  while (Date.now() <= deadline) {
    try {
      const fd = openSync(lockPath, "wx");
      closeSync(fd);
      return true;
    } catch (error) {
      if (isNodeErrorCode(error, "EEXIST")) {
        maybeClearStaleLock(lockPath, context);
        sleepMs(LOCK_WAIT_INTERVAL_MS);
        continue;
      }
      logCaughtError(log, "subagent-state:acquire-lock-failed", error, { lockPath, ...context });
      return false;
    }
  }
  log.debug("subagent-state:lock-timeout", { lockPath, ...context });
  return false;
}
function releaseLock(lockPath, context) {
  try {
    rmSync(lockPath, { force: true });
  } catch (error) {
    logCaughtError(log, "subagent-state:release-lock-failed", error, { lockPath, ...context });
  }
}
function withLock(lockPath, context, fallback, action) {
  if (!acquireLock(lockPath, context)) {
    return fallback;
  }
  try {
    return action();
  } finally {
    releaseLock(lockPath, context);
  }
}
function isPendingLaunch(value) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return false;
  }
  const record = value;
  if (typeof record.description !== "string" || typeof record.prompt !== "string" || typeof record.subagent_type !== "string" || typeof record.createdAt !== "number" || !Number.isFinite(record.createdAt)) {
    return false;
  }
  if ("resume" in record && typeof record.resume !== "string" && typeof record.resume !== "undefined") {
    return false;
  }
  if ("name" in record && typeof record.name !== "string" && typeof record.name !== "undefined") {
    return false;
  }
  return true;
}
function parsePendingLaunchLine(line, filePath) {
  if (line.trim() === "") return null;
  try {
    const parsed = JSON.parse(line);
    if (isPendingLaunch(parsed)) {
      return parsed;
    }
    log.debug("subagent-state:invalid-pending-launch-record", { filePath, line });
    return null;
  } catch (error) {
    logCaughtError(log, "subagent-state:parse-pending-launch-line-failed", error, { filePath, line });
    return null;
  }
}
function readPendingLaunchFile(filePath) {
  try {
    const content = readFileSync(filePath, "utf-8");
    return content.split("\n").map((line) => parsePendingLaunchLine(line, filePath)).filter((launch) => launch !== null);
  } catch (error) {
    if (isNodeErrorCode(error, "ENOENT")) {
      return [];
    }
    logCaughtError(log, "subagent-state:read-pending-launch-file-failed", error, { filePath });
    return [];
  }
}
function isPendingLaunchExpired(launch, now) {
  return now - launch.createdAt > PENDING_LAUNCH_TTL_MS;
}
function serializePendingLaunches(launches) {
  if (launches.length === 0) {
    return "";
  }
  return `${launches.map((launch) => JSON.stringify(launch)).join("\n")}
`;
}
function writeFileAtomically(path, content, context) {
  const tempPath = `${path}.${process.pid}.${Date.now()}.tmp`;
  try {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(tempPath, content, "utf-8");
    renameSync(tempPath, path);
  } catch (error) {
    logCaughtError(log, "subagent-state:atomic-write-failed", error, { path, tempPath, ...context });
    try {
      rmSync(tempPath, { force: true });
    } catch {
    }
  }
}
function listPendingLaunches(sessionId) {
  const now = Date.now();
  return readPendingLaunchFile(pendingLaunchPath(sessionId)).filter((launch) => !isPendingLaunchExpired(launch, now)).sort((left, right) => left.createdAt - right.createdAt);
}
function claimPendingLaunch(sessionId, agentType) {
  const filePath = pendingLaunchPath(sessionId);
  const lockPath = pendingLaunchLockPath(sessionId);
  return withLock(lockPath, { sessionId, agentType, filePath, operation: "claim" }, null, () => {
    const now = Date.now();
    const launches = readPendingLaunchFile(filePath);
    const activeLaunches = launches.filter((launch) => !isPendingLaunchExpired(launch, now));
    const hadExpiredLaunches = activeLaunches.length !== launches.length;
    let claimedLaunch = null;
    let claimedIndex = -1;
    for (const [index, launch] of activeLaunches.entries()) {
      if (launch.subagent_type !== agentType) {
        continue;
      }
      if (claimedLaunch === null || launch.createdAt < claimedLaunch.createdAt) {
        claimedLaunch = launch;
        claimedIndex = index;
      }
    }
    if (claimedIndex >= 0) {
      activeLaunches.splice(claimedIndex, 1);
    }
    if (claimedLaunch !== null || hadExpiredLaunches) {
      writeFileAtomically(filePath, serializePendingLaunches(activeLaunches), {
        sessionId,
        agentType,
        filePath,
        claimed: claimedLaunch !== null
      });
    }
    return claimedLaunch;
  });
}
function appendPendingLaunch(sessionId, launch) {
  const filePath = pendingLaunchPath(sessionId);
  const lockPath = pendingLaunchLockPath(sessionId);
  withLock(lockPath, { sessionId, filePath, operation: "append" }, void 0, () => {
    try {
      mkdirSync(dirname(filePath), { recursive: true });
      appendFileSync(filePath, `${JSON.stringify(launch)}
`, "utf-8");
    } catch (error) {
      logCaughtError(log, "subagent-state:append-pending-launch-failed", error, { sessionId, filePath });
    }
  });
}
function readAgentState(sessionId, agentId) {
  const filePath = agentStatePath(sessionId, agentId);
  try {
    const content = readFileSync(filePath, "utf-8").trim();
    if (content === "") {
      return {};
    }
    const parsed = JSON.parse(content);
    if (typeof parsed === "object" && parsed !== null && !Array.isArray(parsed)) {
      return parsed;
    }
    log.debug("subagent-state:agent-state-not-object", { filePath, agentId, sessionId });
    return {};
  } catch (error) {
    if (!isNodeErrorCode(error, "ENOENT")) {
      logCaughtError(log, "subagent-state:read-agent-state-failed", error, { filePath, agentId, sessionId });
    }
    return {};
  }
}
function writeAgentState(sessionId, agentId, state) {
  const filePath = agentStatePath(sessionId, agentId);
  writeFileAtomically(filePath, `${JSON.stringify(state)}
`, { sessionId, agentId, filePath });
}
export {
  appendPendingLaunch,
  claimPendingLaunch,
  listPendingLaunches,
  readAgentState,
  writeAgentState
};
