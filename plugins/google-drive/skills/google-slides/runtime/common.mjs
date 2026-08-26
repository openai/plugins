import { createHash } from "node:crypto";

export const SHA256_RE = /^[a-f0-9]{64}$/;
export const OBJECT_ID_RE = /^[A-Za-z0-9_][A-Za-z0-9_:-]{4,49}$/;

export class SlidesValidationError extends Error {
  constructor(message, { path = null, details = null } = {}) {
    super(path ? `${path}: ${message}` : message);
    this.name = "SlidesValidationError";
    this.path = path;
    this.details = details;
  }
}

export function fail(message, path = null, details = null) {
  throw new SlidesValidationError(message, { path, details });
}

export function assert(condition, message, path = null, details = null) {
  if (!condition) fail(message, path, details);
}

export function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function requireRecord(value, path) {
  assert(isRecord(value), "must be an object", path);
  return value;
}

export function requireString(value, path, { nonempty = true } = {}) {
  assert(typeof value === "string", "must be a string", path);
  if (nonempty) assert(value.trim().length > 0, "must not be empty", path);
  return value;
}

export function requireStringArray(value, path, { unique = true } = {}) {
  assert(Array.isArray(value), "must be an array", path);
  for (let index = 0; index < value.length; index += 1) {
    requireString(value[index], `${path}[${index}]`);
  }
  if (unique) {
    assert(new Set(value).size === value.length, "must not contain duplicates", path);
  }
  return value;
}

export function uniqueSorted(values) {
  return [...new Set(values)].sort((left, right) => left.localeCompare(right));
}

export function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (!isRecord(value)) return value;

  const output = {};
  for (const key of Object.keys(value).sort()) {
    if (value[key] !== undefined) output[key] = canonicalize(value[key]);
  }
  return output;
}

export function stableStringify(value, space = 0) {
  return JSON.stringify(canonicalize(value), null, space);
}

export function sha256Text(value) {
  return createHash("sha256").update(value).digest("hex");
}

export function sha256Json(value) {
  return sha256Text(stableStringify(value));
}

export function snapshotPayload(snapshot) {
  const { sha256: _ignored, ...payload } = requireRecord(snapshot, "snapshot");
  return payload;
}

export function verifySnapshotHash(snapshot) {
  requireString(snapshot.sha256, "snapshot.sha256");
  assert(SHA256_RE.test(snapshot.sha256), "must be a lowercase SHA-256 hex digest", "snapshot.sha256");
  const actual = sha256Json(snapshotPayload(snapshot));
  assert(actual === snapshot.sha256, `does not match snapshot payload (actual ${actual})`, "snapshot.sha256");
  return actual;
}

export function deepEqual(left, right) {
  return stableStringify(left) === stableStringify(right);
}

export function redactSensitive(value) {
  if (Array.isArray(value)) return value.map(redactSensitive);
  if (typeof value === "string") {
    return value.replace(/https?:\/\/[^\s"'<>]+/gi, (url) =>
      /(?:x-goog-|x-amz-|access_token=|refresh_token=|[?&]token=|[?&]signature=|googleaccessid=)/i.test(url)
        ? "[EPHEMERAL_URL_REDACTED]"
        : url,
    )
      .replace(/\b(authorization\s*:\s*bearer|bearer)\s+[A-Za-z0-9._~+\/=:-]+/gi, "$1 [REDACTED]")
      .replace(/\b(x-api-key|api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[:=]\s*["']?[^\s"',;}]*/gi, "$1=[REDACTED]")
      .replace(/\b(set-cookie|cookie)\s*:\s*[^\r\n]+/gi, "$1: [REDACTED]");
  }
  if (!isRecord(value)) return value;

  const redacted = {};
  for (const [key, child] of Object.entries(value)) {
    if (/authorization|access.?token|refresh.?token|oauth|signed.?url/i.test(key)) {
      redacted[key] = "[REDACTED]";
    } else if (/content.?url|thumbnail.?url|download.?url|image.?pointer|staged.?url/i.test(key)) {
      redacted[key] = "[EPHEMERAL_URL_REDACTED]";
    } else {
      redacted[key] = redactSensitive(child);
    }
  }
  return redacted;
}

export function findFirstRecord(root, predicate, { maxNodes = 10000 } = {}) {
  const queue = [root];
  const seen = new Set();
  let visited = 0;

  while (queue.length > 0 && visited < maxNodes) {
    const value = queue.shift();
    if (!isRecord(value) && !Array.isArray(value)) continue;
    if (seen.has(value)) continue;
    seen.add(value);
    visited += 1;

    if (isRecord(value) && predicate(value)) return value;
    const children = Array.isArray(value) ? value : Object.values(value);
    for (const child of children) {
      if (isRecord(child) || Array.isArray(child)) queue.push(child);
    }
  }
  return null;
}

export function getAtPath(value, path) {
  let current = value;
  for (const key of path) {
    if (current === null || current === undefined) return undefined;
    current = current[key];
  }
  return current;
}

export function firstDefined(value, paths) {
  for (const path of paths) {
    const candidate = getAtPath(value, path);
    if (candidate !== undefined && candidate !== null && candidate !== "") return candidate;
  }
  return undefined;
}

export function validateObjectId(value, path) {
  requireString(value, path);
  assert(
    OBJECT_ID_RE.test(value),
    "must be 5-50 characters, start with an alphanumeric or underscore, and contain only alphanumerics, underscores, hyphens, or colons",
    path,
  );
  return value;
}

export function assertNoPlaceholders(value, path) {
  requireString(value, path);
  assert(!/^(?:TODO|TBD|UNKNOWN|PLACEHOLDER)$/i.test(value), "contains an unresolved placeholder", path);
  assert(!/^<[^>]+>$/.test(value), "contains an unresolved angle-bracket placeholder", path);
  assert(!/^\{\{[^}]+\}\}$/.test(value), "contains an unresolved template placeholder", path);
  return value;
}
