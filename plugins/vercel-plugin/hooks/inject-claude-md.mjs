#!/usr/bin/env node

// hooks/src/inject-claude-md.mts
import { readFileSync } from "fs";
import { join, resolve } from "path";
import { fileURLToPath } from "url";
import { formatOutput } from "./compat.mjs";
import { pluginRoot, safeReadFile } from "./hook-env.mjs";
var GREENFIELD_CONTEXT = `<!-- vercel-plugin:greenfield-execution -->
## Greenfield execution mode

This directory is empty.
Do not stop in planning mode or spin up a read-only planning subagent.
Choose sensible defaults immediately.
Start executing with real tool calls.
Use non-interactive scaffolding commands (--yes) where available.
Only ask follow-up questions when blocked by missing credentials or irreversible decisions.`;
function parseInjectClaudeMdInput(raw) {
  try {
    if (!raw.trim()) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
function detectInjectClaudeMdPlatform(input, _env = process.env) {
  if (input && ("conversation_id" in input || "cursor_version" in input)) {
    return "cursor";
  }
  return "claude-code";
}
function buildInjectClaudeMdParts(content, env = process.env) {
  const parts = [];
  if (content !== null) {
    parts.push(content);
  }
  if (env.VERCEL_PLUGIN_GREENFIELD === "true") {
    parts.push(GREENFIELD_CONTEXT);
  }
  return parts;
}
function formatInjectClaudeMdOutput(platform, content) {
  if (platform === "cursor") {
    return JSON.stringify(formatOutput(platform, { additionalContext: content }));
  }
  return content;
}
function main() {
  const input = parseInjectClaudeMdInput(readFileSync(0, "utf8"));
  const platform = detectInjectClaudeMdPlatform(input);
  const parts = buildInjectClaudeMdParts(safeReadFile(join(pluginRoot(), "vercel.md")));
  if (parts.length === 0) {
    return;
  }
  process.stdout.write(formatInjectClaudeMdOutput(platform, parts.join("\n\n")));
}
var INJECT_CLAUDE_MD_ENTRYPOINT = fileURLToPath(import.meta.url);
var isInjectClaudeMdEntrypoint = process.argv[1] ? resolve(process.argv[1]) === INJECT_CLAUDE_MD_ENTRYPOINT : false;
if (isInjectClaudeMdEntrypoint) {
  main();
}
export {
  buildInjectClaudeMdParts,
  detectInjectClaudeMdPlatform,
  formatInjectClaudeMdOutput,
  parseInjectClaudeMdInput
};
