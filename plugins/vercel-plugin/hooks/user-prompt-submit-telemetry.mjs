#!/usr/bin/env node

// hooks/src/user-prompt-submit-telemetry.mts
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "fs";
import { homedir, tmpdir } from "os";
import { join, dirname } from "path";
var PREF_PATH = join(homedir(), ".claude", "vercel-plugin-telemetry-preference");
function parseStdin() {
  try {
    const raw = readFileSync(0, "utf-8").trim();
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
function resolveSessionId(input) {
  return input.session_id || input.conversation_id || "";
}
function resolvePrompt(input) {
  return input.prompt || input.message || "";
}
async function main() {
  const input = parseStdin();
  const sessionId = input ? resolveSessionId(input) : "";
  const prompt = input ? resolvePrompt(input) : "";
  try {
    const pref = readFileSync(PREF_PATH, "utf-8").trim();
    if (pref === "enabled" || pref === "disabled" || pref === "asked") {
      process.stdout.write("{}");
      process.exit(0);
    }
  } catch {
  }
  if (sessionId) {
    const flagPath = join(tmpdir(), `vercel-plugin-telemetry-asked-${sessionId}`);
    if (existsSync(flagPath)) {
      process.stdout.write("{}");
      process.exit(0);
    }
    try {
      mkdirSync(dirname(flagPath), { recursive: true });
      writeFileSync(flagPath, "1", { flag: "wx" });
    } catch {
      process.stdout.write("{}");
      process.exit(0);
    }
  }
  try {
    mkdirSync(dirname(PREF_PATH), { recursive: true });
    writeFileSync(PREF_PATH, "asked");
  } catch {
  }
  const message = [
    "After responding to the user's message, use the AskUserQuestion tool to ask about telemetry.",
    "Use this exact question configuration:",
    '- question: "The Vercel plugin can collect anonymous telemetry data (skill usage, code changes, and commands) to help improve the plugin. Would you like to opt in?"',
    '- header: "Telemetry"',
    '- options: [{"label": "Enable telemetry", "description": "Share anonymous usage data to help improve the plugin"}, {"label": "No thanks", "description": "Disable telemetry \u2014 no data will be collected"}]',
    "- multiSelect: false",
    "",
    "After the user responds:",
    "- If they chose \"Enable telemetry\", run: `echo 'enabled' > ~/.claude/vercel-plugin-telemetry-preference`",
    "- If they chose \"No thanks\" or anything else, run: `echo 'disabled' > ~/.claude/vercel-plugin-telemetry-preference`"
  ].join("\n");
  const output = {
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: message
    }
  };
  process.stdout.write(JSON.stringify(output));
  process.exit(0);
}
main();
