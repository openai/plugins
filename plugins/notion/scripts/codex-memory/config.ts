import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import type { MemoryType } from "./memories.ts";

export interface Config {
  // Codex executable used to start `codex app-server`.
  codexPath: string;
  // Name of the Notion MCP server in Codex. Detected automatically when unset.
  mcpServer?: string;
}

export interface MemoryState {
  hash: string;
  title: string;
  type: MemoryType;
  pageId: string;
  // Hash of the page as Notion returned it right after the plugin wrote it. A different
  // page later means someone edited it in Notion.
  pageHash?: string;
  // Set once the page was edited or deleted in Notion. The plugin never touches it again.
  released?: "edited" | "deleted";
}

export interface State {
  memories: Record<string, MemoryState>;
  userName?: string;
}

export const CODEX_HOME =
  process.env.CODEX_HOME || path.join(os.homedir(), ".codex");
export const CONFIG_FILE =
  process.env.NOTION_MEMORY_CONFIG ||
  path.join(CODEX_HOME, "notion-memory.json");
// Not $PLUGIN_DATA: hooks and manual commands from the skill must share one state file.
export const DATA_DIR = path.join(CODEX_HOME, "notion-memory");
export const LOG_FILE = path.join(DATA_DIR, "notion-memory.log");
const STATE_FILE = path.join(DATA_DIR, "state.json");
const LOCK_DIR = path.join(DATA_DIR, "lock");
const STALE_LOCK_MS = 120_000;

export function loadConfig(): Config {
  let file: Partial<Config> = {};
  if (fs.existsSync(CONFIG_FILE))
    file = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8"));
  return {
    codexPath: process.env.CODEX_PATH || file.codexPath || "codex",
    mcpServer: process.env.NOTION_MCP_SERVER || file.mcpServer,
  };
}

export function loadState(): State {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
  } catch {
    return { memories: {} };
  }
}

export function saveState(state: State): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(`${STATE_FILE}.tmp`, JSON.stringify(state, null, 2));
  fs.renameSync(`${STATE_FILE}.tmp`, STATE_FILE);
}

export function log(...parts: unknown[]): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const text = parts
    .map((p) => (typeof p === "string" ? p : JSON.stringify(p)))
    .join(" ");
  const line = `[${new Date().toISOString()}] ${text}\n`;
  fs.appendFileSync(LOG_FILE, line);
  if (process.env.NOTION_SYNC_VERBOSE) process.stderr.write(line);
}

// Cross-process lock. Workers from back-to-back hooks can overlap, and two imports
// running at once would create the same memory twice.
export async function withLock<T>(fn: () => Promise<T>): Promise<T> {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  for (let attempt = 0; ; attempt++) {
    try {
      fs.mkdirSync(LOCK_DIR);
      break;
    } catch {
      if (lockIsStale()) fs.rmSync(LOCK_DIR, { recursive: true, force: true });
      if (attempt > 600) throw new Error(`could not acquire ${LOCK_DIR}`);
      await sleep(200);
    }
  }
  try {
    return await fn();
  } finally {
    fs.rmSync(LOCK_DIR, { recursive: true, force: true });
  }
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function lockIsStale(): boolean {
  try {
    return Date.now() - fs.statSync(LOCK_DIR).mtimeMs > STALE_LOCK_MS;
  } catch {
    return false;
  }
}
