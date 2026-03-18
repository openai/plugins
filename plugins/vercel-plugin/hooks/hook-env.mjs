// hooks/src/hook-env.mts
import { createHash, randomUUID } from "crypto";
import {
  appendFileSync,
  closeSync,
  mkdirSync,
  openSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync
} from "fs";
import { homedir, tmpdir } from "os";
import { dirname, join, resolve, sep } from "path";
import { fileURLToPath } from "url";
import { createLogger, logCaughtError } from "./logger.mjs";
var log = createLogger();
function pluginRoot(metaUrl) {
  const base = metaUrl ?? import.meta.url;
  return resolve(dirname(fileURLToPath(base)), "..");
}
function resolveAuditLogPath(hookInputCwd) {
  const cwdFromHookInput = typeof hookInputCwd === "string" && hookInputCwd.trim() !== "" ? hookInputCwd : null;
  const projectRoot = process.env.CLAUDE_PROJECT_ROOT || cwdFromHookInput || process.cwd();
  const configuredPath = process.env.VERCEL_PLUGIN_AUDIT_LOG_FILE;
  if (configuredPath === "off") {
    return null;
  }
  if (typeof configuredPath === "string" && configuredPath.trim() !== "") {
    return resolve(projectRoot, configuredPath);
  }
  const projectSlug = projectRoot.replaceAll("/", "-");
  return join(homedir(), ".claude", "projects", projectSlug, "vercel-plugin", "skill-injections.jsonl");
}
function appendAuditLog(record, hookInputCwd) {
  const auditLogPath = resolveAuditLogPath(hookInputCwd);
  if (auditLogPath === null) return;
  try {
    mkdirSync(dirname(auditLogPath), { recursive: true });
    const payload = { timestamp: (/* @__PURE__ */ new Date()).toISOString(), ...record };
    appendFileSync(auditLogPath, `${JSON.stringify(payload)}
`, "utf-8");
  } catch (error) {
    logCaughtError(log, "hook-env:append-audit-log-failed", error, { auditLogPath });
  }
}
function getDedupScopeId(payload) {
  if (payload && typeof payload === "object" && "agent_id" in payload && typeof payload.agent_id === "string" && payload.agent_id.length > 0) {
    return payload.agent_id;
  }
  return "main";
}
var SAFE_SESSION_ID_RE = /^[a-zA-Z0-9_-]+$/;
function dedupSessionIdSegment(sessionId) {
  if (SAFE_SESSION_ID_RE.test(sessionId)) {
    return sessionId;
  }
  return createHash("sha256").update(sessionId).digest("hex");
}
function dedupScopeIdSegment(scopeId) {
  if (SAFE_SESSION_ID_RE.test(scopeId)) {
    return scopeId;
  }
  return createHash("sha256").update(scopeId).digest("hex");
}
function resolveDedupTempPath(sessionId, basename, scopeId) {
  const tempRoot = resolve(tmpdir());
  const scopeSegment = scopeId ? `-${dedupScopeIdSegment(scopeId)}` : "";
  const candidate = resolve(join(tempRoot, `vercel-plugin-${dedupSessionIdSegment(sessionId)}${scopeSegment}-${basename}`));
  const tempPrefix = tempRoot.endsWith(sep) ? tempRoot : `${tempRoot}${sep}`;
  if (!candidate.startsWith(tempPrefix)) {
    throw new Error(`dedup temp path escaped tmpdir: tempRoot=${tempRoot} candidate=${candidate}`);
  }
  return candidate;
}
function dedupFilePath(sessionId, kind, scopeId) {
  return resolveDedupTempPath(sessionId, `${kind}.txt`, scopeId);
}
function dedupClaimDirPath(sessionId, kind, scopeId) {
  return resolveDedupTempPath(sessionId, `${kind}.d`, scopeId);
}
function readSessionFile(sessionId, kind, scopeId) {
  try {
    return readFileSync(dedupFilePath(sessionId, kind, scopeId), "utf-8");
  } catch (error) {
    logCaughtError(log, "hook-env:read-session-file-failed", error, { sessionId, kind, scopeId });
    return "";
  }
}
function writeSessionFile(sessionId, kind, value, scopeId) {
  try {
    writeFileSync(dedupFilePath(sessionId, kind, scopeId), value, "utf-8");
  } catch (error) {
    logCaughtError(log, "hook-env:write-session-file-failed", error, { sessionId, kind, scopeId });
  }
}
function tryClaimSessionKey(sessionId, kind, key, scopeId) {
  try {
    const claimDir = dedupClaimDirPath(sessionId, kind, scopeId);
    mkdirSync(claimDir, { recursive: true });
    const file = join(claimDir, encodeURIComponent(key));
    const fd = openSync(file, "wx");
    closeSync(fd);
    return true;
  } catch (error) {
    if (typeof error === "object" && error !== null && "code" in error && error.code === "EEXIST") {
      return false;
    }
    return false;
  }
}
function listSessionKeys(sessionId, kind, scopeId) {
  try {
    return readdirSync(dedupClaimDirPath(sessionId, kind, scopeId)).map((entry) => decodeURIComponent(entry)).filter((entry) => entry !== "").sort();
  } catch (error) {
    logCaughtError(log, "hook-env:list-session-keys-failed", error, { sessionId, kind, scopeId });
    return [];
  }
}
function syncSessionFileFromClaims(sessionId, kind, scopeId) {
  const value = listSessionKeys(sessionId, kind, scopeId).join(",");
  writeSessionFile(sessionId, kind, value, scopeId);
  return value;
}
function removeSessionClaimDir(sessionId, kind, scopeId) {
  try {
    rmSync(dedupClaimDirPath(sessionId, kind, scopeId), { recursive: true, force: true });
  } catch (error) {
    logCaughtError(log, "hook-env:remove-session-claim-dir-failed", error, { sessionId, kind, scopeId });
  }
}
function removeAllSessionDedupArtifacts(sessionId) {
  const result = { removedFiles: 0, removedDirs: 0 };
  const tempRoot = resolve(tmpdir());
  const prefix = `vercel-plugin-${dedupSessionIdSegment(sessionId)}-`;
  let entries;
  try {
    entries = readdirSync(tempRoot).filter(
      (name) => name.startsWith(prefix) && (name.endsWith("-seen-skills.d") || name.endsWith("-seen-skills.txt"))
    );
  } catch {
    return result;
  }
  for (const entry of entries) {
    const fullPath = join(tempRoot, entry);
    if (entry.endsWith(".d")) {
      try {
        rmSync(fullPath, { recursive: true, force: true });
        result.removedDirs++;
      } catch (error) {
        logCaughtError(log, "hook-env:remove-all-session-dedup-artifacts-dir", error, { fullPath });
      }
    } else {
      try {
        rmSync(fullPath);
        result.removedFiles++;
      } catch (error) {
        logCaughtError(log, "hook-env:remove-all-session-dedup-artifacts-file", error, { fullPath });
      }
    }
  }
  return result;
}
function profileCachePath(sessionId) {
  return resolveDedupTempPath(sessionId, "profile.json");
}
function generateVerificationId() {
  return randomUUID();
}
function safeReadFile(path) {
  try {
    return readFileSync(path, "utf-8");
  } catch (error) {
    logCaughtError(log, "hook-env:safe-read-file-failed", error, { path });
    return null;
  }
}
function safeReadJson(path) {
  const content = safeReadFile(path);
  if (content === null) return null;
  try {
    return JSON.parse(content);
  } catch (error) {
    logCaughtError(log, "hook-env:safe-read-json-failed", error, { path });
    return null;
  }
}
export {
  appendAuditLog,
  dedupClaimDirPath,
  dedupFilePath,
  generateVerificationId,
  getDedupScopeId,
  listSessionKeys,
  pluginRoot,
  profileCachePath,
  readSessionFile,
  removeAllSessionDedupArtifacts,
  removeSessionClaimDir,
  safeReadFile,
  safeReadJson,
  syncSessionFileFromClaims,
  tryClaimSessionKey,
  writeSessionFile
};
