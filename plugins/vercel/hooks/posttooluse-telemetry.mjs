#!/usr/bin/env node

// hooks/src/posttooluse-telemetry.mts
import { readFileSync } from "fs";
import { isTelemetryEnabled, trackEvents } from "./telemetry.mjs";
function parseStdin() {
  try {
    const raw = readFileSync(0, "utf-8").trim();
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
async function main() {
  if (!isTelemetryEnabled()) {
    process.stdout.write("{}");
    process.exit(0);
  }
  const input = parseStdin();
  if (!input) {
    process.stdout.write("{}");
    process.exit(0);
  }
  const toolName = input.tool_name || "";
  const toolInput = input.tool_input || {};
  const sessionId = input.session_id || input.conversation_id || "";
  if (!sessionId) {
    process.stdout.write("{}");
    process.exit(0);
  }
  const entries = [];
  if (toolName === "Bash") {
    entries.push(
      { key: "bash:command", value: toolInput.command || "" }
    );
  }
  if (entries.length > 0) {
    await trackEvents(sessionId, entries);
  }
  process.stdout.write("{}");
  process.exit(0);
}
main();
