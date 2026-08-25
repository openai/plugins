import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";

export function assert(condition, message, path = null) {
  if (!condition) throw new Error(path ? `${path}: ${message}` : message);
}

export function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function requireRecord(value, path) {
  assert(isRecord(value), "must be an object", path);
  return value;
}

export function requireArray(value, path) {
  assert(Array.isArray(value), "must be an array", path);
  return value;
}

export function requireString(value, path, { allowEmpty = false } = {}) {
  assert(typeof value === "string" && (allowEmpty || value.length > 0), "must be a non-empty string", path);
  return value;
}

export function requireInteger(value, path, { minimum = null } = {}) {
  assert(Number.isInteger(value), "must be an integer", path);
  if (minimum !== null) assert(value >= minimum, `must be >= ${minimum}`, path);
  return value;
}

export function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  if (isRecord(value)) {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sha256Text(value) {
  return createHash("sha256").update(String(value)).digest("hex");
}

export function sha256Json(value) {
  return sha256Text(stableStringify(value));
}

export async function sha256File(path) {
  return createHash("sha256").update(await readFile(path)).digest("hex");
}

export async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

export async function writeJson(path, value) {
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
}

export function rangesOverlap(left, right) {
  if ((left.tabId ?? null) !== (right.tabId ?? null) || (left.segmentId ?? null) !== (right.segmentId ?? null)) return false;
  return left.startIndex < right.endIndex && right.startIndex < left.endIndex;
}

export function rangeContains(outer, inner) {
  return (outer.tabId ?? null) === (inner.tabId ?? null) &&
    (outer.segmentId ?? null) === (inner.segmentId ?? null) &&
    outer.startIndex <= inner.startIndex && outer.endIndex >= inner.endIndex;
}

export function findFirstRecord(value, predicate) {
  const seen = new Set();
  const visit = (candidate) => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return null;
    seen.add(candidate);
    if (isRecord(candidate) && predicate(candidate)) return candidate;
    for (const child of Array.isArray(candidate) ? candidate : Object.values(candidate)) {
      const found = visit(child);
      if (found) return found;
    }
    return null;
  };
  return visit(value);
}

export function collectRecords(value, predicate) {
  const output = [];
  const seen = new Set();
  const visit = (candidate) => {
    if (!candidate || typeof candidate !== "object" || seen.has(candidate)) return;
    seen.add(candidate);
    if (isRecord(candidate) && predicate(candidate)) output.push(candidate);
    for (const child of Array.isArray(candidate) ? candidate : Object.values(candidate)) visit(child);
  };
  visit(value);
  return output;
}
