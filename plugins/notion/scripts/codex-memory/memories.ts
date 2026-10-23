import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  CODEX_HOME,
  loadState,
  log,
  saveState,
  sleep,
  withLock,
} from "./config.ts";
import type { CallTool } from "./mcp.ts";

// Codex memories (`[features] memories = true`) are written by Codex itself, in the
// background: phase 1 extracts notes from idle sessions, phase 2 consolidates them into
// $CODEX_HOME/memories/memory_summary.md and MEMORY.md. This module turns those files into
// Notion memories and writes them with the same Notion MCP tools any agent uses, following
// the Notion memory guide (notion://docs/memory): one topic per memory, a topic title, a
// Type, details in the body, and no Source property.

export type MemoryType = "Profile" | "Preference" | "Work";

export interface CodexMemory {
  key: string;
  type: MemoryType;
  title: string;
  content: string;
  from: string;
}

export interface MemorySyncResult {
  total: number;
  created: number;
  updated: number;
  unchanged: number;
  changedInNotion: number;
  skippedExisting: number;
  noLongerInCodex: number;
}

const POLL_MS = 5000;
const PROFILE_TITLE = "Role and background";
const PREFERENCES_TITLE = "Coding workflow preferences";

export function memoriesDir(): string {
  return path.join(CODEX_HOME, "memories");
}

// Pure: reads the Codex memory files in `dir` and returns one memory per topic.
export function parseCodexMemories(
  dir: string,
  userName?: string,
): CodexMemory[] {
  const summary = readIfExists(path.join(dir, "memory_summary.md"));
  const memoryFile = readIfExists(path.join(dir, "MEMORY.md"));
  const out: CodexMemory[] = [];
  const seenPreferences: string[] = [];

  for (const section of sections(summary, 2)) {
    if (/^user profile/i.test(section.title) && isReal(section.body))
      out.push({
        key: "profile",
        type: "Profile",
        title: PROFILE_TITLE,
        content: unwrap(section.body),
        from: "`memory_summary.md` › User Profile",
      });
    if (/^user preferences/i.test(section.title)) {
      const prefs = bullets(section.body).filter(isReal);
      seenPreferences.push(...prefs.map(preferenceKey));
      if (prefs.length)
        out.push({
          key: "preferences",
          type: "Preference",
          title: PREFERENCES_TITLE,
          content: prefs.map((p) => `- ${p}`).join("\n"),
          from: "`memory_summary.md` › User preferences",
        });
    }
  }

  for (const group of sections(memoryFile, 1)) {
    const name = group.title.replace(/^Task Group:\s*/i, "").trim();
    const parts = sections(group.body, 2);
    const scope = group.body.match(/^scope:\s*(.+)$/m)?.[1];
    const appliesTo = group.body.match(/^applies_to:\s*(.+)$/m)?.[1];
    const tasks = parts
      .filter((s) => /^task \d+/i.test(s.title))
      .map((s) => s.title.replace(/^Task \d+:\s*/i, ""));
    const knowledge = parts.filter((s) =>
      /^(reusable knowledge|failures)/i.test(s.title),
    );
    // Preferences already in the global summary are not repeated per project.
    const prefs = parts
      .filter((s) => /^user preferences/i.test(s.title))
      .flatMap((s) => bullets(s.body))
      .filter(
        (p) =>
          isReal(p) &&
          !seenPreferences.some((k) => overlaps(k, preferenceKey(p))),
      );
    const blocks = [
      scope && `Scope: ${scope}`,
      appliesTo && `Applies to: ${appliesTo}`,
      tasks.length && `Recent tasks:\n${tasks.map((t) => `- ${t}`).join("\n")}`,
      prefs.length && `Preferences:\n${prefs.map((p) => `- ${p}`).join("\n")}`,
      ...knowledge.map(
        (k) =>
          `${k.title}:\n${bullets(k.body)
            .map((b) => `- ${b}`)
            .join("\n")}`,
      ),
    ].filter(Boolean);
    if (tasks.length || knowledge.length || prefs.length)
      out.push({
        key: `work:${normalizeKey(name)}`,
        type: "Work",
        title: name,
        content: blocks.join("\n\n"),
        from: `\`MEMORY.md\` › ${group.title}`,
      });
  }

  return out.map((m) => ({
    ...m,
    content: personalize(m.content.replace(/\s*\[Task \d+\]/g, ""), userName),
  }));
}

// Writes changed Codex memories to the user's Notion Memories through Notion MCP.
export async function syncMemories(
  callTool: CallTool,
): Promise<MemorySyncResult> {
  const state = loadState();
  if (parseCodexMemories(memoriesDir()).length)
    state.userName ??= await userName(callTool);
  const memories = parseCodexMemories(memoriesDir(), state.userName);
  const result: MemorySyncResult = {
    total: memories.length,
    created: 0,
    updated: 0,
    unchanged: 0,
    changedInNotion: 0,
    skippedExisting: 0,
    noLongerInCodex: 0,
  };
  if (!memories.length) {
    log("memories: none in", memoriesDir(), "(is [features] memories = true?)");
    saveState(state);
    return result;
  }

  let titles: string[] | undefined;
  for (const memory of memories) {
    const hash = sha1(`${memory.title}\n${memory.content}`);
    const prev = state.memories[memory.key];
    if (prev?.released) {
      result.changedInNotion++;
      continue;
    }
    if (prev?.hash === hash) {
      result.unchanged++;
      continue;
    }
    const body = `${memory.content}\n\nFrom Codex memories (${memory.from}).`;

    if (prev) {
      // Only overwrite the page if it is still exactly what the plugin wrote.
      const page = await fetchPage(callTool, prev.pageId);
      const released = page.deleted
        ? "deleted"
        : page.hash !== prev.pageHash
          ? "edited"
          : undefined;
      if (released) {
        log(`memories: ${prev.title} was ${released} in Notion, leaving it`);
        state.memories[memory.key] = { ...prev, released };
        result.changedInNotion++;
        saveState(state);
        continue;
      }
      await callTool("update-page", {
        page_id: prev.pageId,
        command: "replace_content",
        new_str: body,
        allow_deleting_content: true,
      });
      state.memories[memory.key] = { ...prev, hash };
      result.updated++;
    } else {
      // Search first: one memory per topic, so never add a second "Coding workflow
      // preferences" next to one the user or another agent already keeps.
      titles ??= await memoryTitles(callTool);
      if (titles.some((t) => sameTitle(t, memory.title))) {
        log("memories: a memory titled", memory.title, "already exists");
        result.skippedExisting++;
        continue;
      }
      const created = (await callTool("create-pages", {
        parent: "memory",
        pages: [
          {
            properties: { title: memory.title, Type: memory.type },
            content: body,
          },
        ],
      })) as { pages?: { id: string }[] };
      const pageId = created.pages?.[0]?.id;
      if (!pageId) throw new Error(`no page returned for ${memory.title}`);
      state.memories[memory.key] = {
        hash,
        title: memory.title,
        type: memory.type,
        pageId,
      };
      result.created++;
    }
    const entry = state.memories[memory.key];
    entry.pageHash = (await fetchPage(callTool, entry.pageId)).hash;
    saveState(state);
  }

  // Codex dropped these. Deleting a memory needs the user's confirmation, so the plugin
  // only stops managing them.
  const live = new Set(memories.map((m) => m.key));
  for (const key of Object.keys(state.memories)) {
    if (live.has(key)) continue;
    log("memories: Codex no longer has", state.memories[key].title);
    delete state.memories[key];
    result.noLongerInCodex++;
  }

  if (result.updated)
    await callTool("finish-revision", {
      title: "Update memories from Codex",
      description: `Codex updated ${result.updated} memor${result.updated === 1 ? "y" : "ies"}.`,
    }).catch((e: unknown) =>
      log("memories: could not name the revision:", String(e)),
    );
  saveState(state);
  log(`memories: ${JSON.stringify(result)}`);
  return result;
}

// Codex has no hook for "memories updated", so a hook worker watches Codex's own job table
// and the memory files, and imports as soon as a consolidation run finishes.
export async function watchMemories(
  callTool: CallTool,
  opts: { startWindowMs: number; maxMs: number },
): Promise<void> {
  const started = Date.now();
  let lastHash = memoryFilesHash();
  let sawRunning = false;
  while (Date.now() - started < opts.maxMs) {
    await sleep(POLL_MS);
    const running = await memoryJobRunning();
    sawRunning ||= running;
    const hash = memoryFilesHash();
    if (hash !== lastHash && !running) {
      log("memories: Codex updated its memory files, importing");
      await withLock(() => syncMemories(callTool));
      lastHash = hash;
    }
    if (!running && (sawRunning || Date.now() - started > opts.startWindowMs))
      return;
  }
}

async function userName(callTool: CallTool): Promise<string | undefined> {
  const self = (await callTool("get-self", {}).catch(() => undefined)) as
    | { user?: { name?: string } }
    | undefined;
  return self?.user?.name?.split(/\s+/)[0] || undefined;
}

// Titles of the user's existing memories. Uses the SQL view of the Memories data source,
// which can lag behind recent writes; the plugin's own pages are tracked by ID instead.
async function memoryTitles(callTool: CallTool): Promise<string[]> {
  const fetched = await callTool("fetch", { id: "memory" });
  const dataSource = JSON.stringify(fetched).match(
    /collection:\/\/[0-9a-f-]{36}/,
  )?.[0];
  if (!dataSource)
    throw new Error(
      "Notion Memories are not available for this connection (fetch id: memory)",
    );
  const res = (await callTool("query-data-sources", {
    data: {
      mode: "sql",
      data_source_urls: [dataSource],
      query: `SELECT "Title" FROM "${dataSource}" LIMIT 1000`,
    },
  })) as { results?: { Title?: string }[] };
  return (res.results ?? []).map((r) => r.Title ?? "");
}

// Reads a memory page and hashes what a person could change: title, type, and content.
async function fetchPage(
  callTool: CallTool,
  pageId: string,
): Promise<{ deleted: boolean; hash: string }> {
  const fetched = (await callTool("fetch", { id: pageId })) as {
    text?: string;
  };
  const text = fetched.text ?? "";
  const tag = text.match(/<page\b[^>]*>/)?.[0] ?? "";
  let properties: Record<string, unknown> = {};
  try {
    properties = JSON.parse(
      text.match(/<properties>\s*([\s\S]*?)\s*<\/properties>/)?.[1] ?? "{}",
    );
  } catch {}
  const content = text.match(/<content>([\s\S]*?)<\/content>/)?.[1] ?? "";
  return {
    deleted: /\sdeleted\b/.test(tag),
    hash: sha1(`${properties.Title}\n${properties.Type}\n${content.trim()}`),
  };
}

// The Notion memory guide asks for the user's name instead of "the user".
function personalize(text: string, name: string | undefined): string {
  if (!name) return text;
  return text
    .replace(/\b([Tt])he user's\b/g, `${name}'s`)
    .replace(/\b[Tt]he user\b/g, name);
}

async function memoryJobRunning(): Promise<boolean> {
  const db = path.join(CODEX_HOME, "memories_1.sqlite");
  if (!fs.existsSync(db)) return false;
  try {
    const { DatabaseSync } = await import("node:sqlite");
    const conn = new DatabaseSync(db, { readOnly: true });
    try {
      return (
        conn
          .prepare("SELECT 1 FROM jobs WHERE status = 'running' LIMIT 1")
          .all().length > 0
      );
    } finally {
      conn.close();
    }
  } catch (e) {
    log(
      "memories: job table unavailable:",
      e instanceof Error ? e.message : String(e),
    );
    return false;
  }
}

function memoryFilesHash(): string {
  return sha1(
    ["MEMORY.md", "memory_summary.md"]
      .map((f) => readIfExists(path.join(memoriesDir(), f)))
      .join("\0"),
  );
}

function sections(
  text: string,
  level: number,
): { title: string; body: string }[] {
  const heading = new RegExp(`^${"#".repeat(level)} (.+)$`, "gm");
  const out: { title: string; body: string }[] = [];
  let prev: { title: string; end: number } | undefined;
  for (const match of text.matchAll(heading)) {
    const index = match.index ?? 0;
    if (prev)
      out.push({ title: prev.title, body: text.slice(prev.end, index) });
    prev = { title: match[1].trim(), end: index + match[0].length };
  }
  if (prev) out.push({ title: prev.title, body: text.slice(prev.end) });
  return out;
}

// Codex hard-wraps prose. Notion would keep each line break, so join wrapped lines.
function unwrap(text: string): string {
  return text
    .trim()
    .split(/\n\s*\n/)
    .map((p) => p.replace(/\s*\n\s*/g, " "))
    .join("\n\n");
}

function bullets(section: string): string[] {
  return section
    .split("\n")
    .filter((l) => /^\s*- /.test(l))
    .map((l) => l.replace(/^\s*- /, "").trim())
    .filter(Boolean);
}

// Codex seeds memory files with placeholder text such as "No preferences recorded yet."
function isReal(content: string): boolean {
  const text = content.trim();
  return text.length >= 12 && !/^(no|not)\b[^.]*\b(yet|recorded)\b/i.test(text);
}

// The same preference often appears in both files with different wording around a quote.
function preferenceKey(bullet: string): string {
  return normalizeKey(bullet.match(/[“"]([^”"]{8,})[”"]/)?.[1] ?? bullet);
}

function overlaps(a: string, b: string): boolean {
  return a.includes(b) || b.includes(a);
}

function sameTitle(a: string | undefined, b: string): boolean {
  return normalizeKey(a ?? "") === normalizeKey(b);
}

function normalizeKey(text: string): string {
  return text
    .toLowerCase()
    .replace(/\[task \d+\]/g, "")
    .replace(/[^a-z0-9]/g, "");
}

function readIfExists(file: string): string {
  try {
    return fs.readFileSync(file, "utf8");
  } catch {
    return "";
  }
}

function sha1(text: string): string {
  return crypto.createHash("sha1").update(text).digest("hex");
}
