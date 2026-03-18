// hooks/src/telemetry.mts
import { randomUUID } from "crypto";
import { readFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";
var MAX_VALUE_BYTES = 1e5;
var TRUNCATION_SUFFIX = "[TRUNCATED]";
var BRIDGE_ENDPOINT = "https://telemetry.vercel.com/api/vercel-plugin/v1/events";
var FLUSH_TIMEOUT_MS = 3e3;
function truncateValue(value) {
  if (Buffer.byteLength(value, "utf-8") <= MAX_VALUE_BYTES) {
    return value;
  }
  const truncated = Buffer.from(value, "utf-8").subarray(0, MAX_VALUE_BYTES).toString("utf-8");
  return truncated + TRUNCATION_SUFFIX;
}
async function send(sessionId, events) {
  if (events.length === 0) return;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FLUSH_TIMEOUT_MS);
  try {
    await fetch(BRIDGE_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-vercel-plugin-session-id": sessionId,
        "x-vercel-plugin-topic-id": "generic"
      },
      body: JSON.stringify(events),
      signal: controller.signal
    });
  } catch {
  } finally {
    clearTimeout(timeout);
  }
}
function isTelemetryEnabled() {
  if (process.env.VERCEL_PLUGIN_TELEMETRY === "on") return true;
  try {
    const prefPath = join(homedir(), ".claude", "vercel-plugin-telemetry-preference");
    const pref = readFileSync(prefPath, "utf-8").trim();
    return pref === "enabled";
  } catch {
    return false;
  }
}
async function trackEvent(sessionId, key, value) {
  if (!isTelemetryEnabled()) return;
  const event = {
    id: randomUUID(),
    event_time: Date.now(),
    key,
    value: truncateValue(value)
  };
  await send(sessionId, [event]);
}
async function trackEvents(sessionId, entries) {
  if (!isTelemetryEnabled() || entries.length === 0) return;
  const now = Date.now();
  const events = entries.map((entry) => ({
    id: randomUUID(),
    event_time: now,
    key: entry.key,
    value: truncateValue(entry.value)
  }));
  await send(sessionId, events);
}
export {
  isTelemetryEnabled,
  trackEvent,
  trackEvents
};
