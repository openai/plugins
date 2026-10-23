import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

// The plugin resolves CODEX_HOME at import time, so point it at a temp dir first.
const home = fs.mkdtempSync(path.join(os.tmpdir(), "codex-notion-memory-"));
process.env.CODEX_HOME = home;
const FIXTURES = fileURLToPath(new URL("fixtures/memories", import.meta.url));
const { parseCodexMemories, syncMemories } = await import("../memories.ts");
const { loadState } = await import("../config.ts");
const { notionTools } = await import("../mcp.ts");

test("finds Notion tools on the MCP server and on the Notion app", () => {
  const mcp = notionTools({
    name: "notion",
    tools: {
      "notion-create-pages": {},
      "notion-fetch": {},
      "notion-update-page": {},
    },
  });
  assert.equal(mcp.get("createpages"), "notion-create-pages");
  assert.equal(mcp.get("updatepage"), "notion-update-page");
  const apps = notionTools({
    name: "codex_apps",
    tools: {
      notion_notion_create_pages: {},
      notion_notion_fetch: {},
      google_drive_fetch: {},
    },
  });
  assert.equal(apps.get("fetch"), "notion_notion_fetch");
  assert.equal(apps.size, 2);
  assert.equal(notionTools({ name: "other", tools: { fetch: {} } }).size, 0);
});

test("parses Codex memory files into one memory per topic", () => {
  const memories = parseCodexMemories(FIXTURES, "Casey");
  assert.deepEqual(
    memories.map((m) => [m.type, m.title]),
    [
      ["Profile", "Role and background"],
      ["Preference", "Coding workflow preferences"],
      ["Work", "Small Node.js CLI utilities"],
    ],
  );
  const [profile, preferences, work] = memories;
  assert.match(profile.content, /^Casey is a TypeScript developer/);
  assert.match(preferences.content, /keep answers short/);
  assert.match(work.content, /Scope: Node\.js command-line tools/);
  assert.match(work.content, /verify it with a one-line `node -e` check/);
  // Preferences from the global summary are not repeated in the project memory.
  assert.doesNotMatch(work.content, /zero dependencies/);
  assert.doesNotMatch(JSON.stringify(memories), /\[Task \d+\]/);
});

test("returns nothing for missing or placeholder memory files", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "codex-memories-"));
  fs.writeFileSync(
    path.join(dir, "memory_summary.md"),
    "## User preferences\n\n- No preferences recorded yet.\n",
  );
  assert.deepEqual(parseCodexMemories(dir), []);
  assert.deepEqual(parseCodexMemories(path.join(dir, "missing")), []);
});

interface FakePage {
  id: string;
  Title: string;
  Type?: string;
  content: string;
  deleted?: boolean;
}

// In-memory stand-in for the Notion MCP tools the sync calls.
function fakeNotionMcp(existing: Partial<FakePage>[] = []) {
  const DATA_SOURCE = "collection://00000000-0000-0000-0000-000000000001";
  const pages = new Map<string, FakePage>();
  const calls: string[] = [];
  const add = (page: Partial<FakePage>) => {
    const id = `page-${pages.size + 1}`;
    pages.set(id, {
      id,
      Title: "",
      content: "",
      ...page,
    });
    return id;
  };
  existing.forEach(add);

  async function callTool(tool: string, args: any): Promise<unknown> {
    calls.push(tool);
    switch (tool) {
      case "get-self":
        return { user: { name: "Casey Boyer" } };
      case "fetch": {
        if (args.id === "memory")
          return { text: `<data-source url="${DATA_SOURCE}">` };
        const page = pages.get(args.id);
        assert.ok(page, `unknown page ${args.id}`);
        const properties = JSON.stringify({
          Title: page.Title,
          Type: page.Type,
        });
        return {
          text: `<page url="https://notion.so/${page.id}"${page.deleted ? " deleted" : ""}>\n<properties>\n${properties}\n</properties>\n<content>\n${page.content}\n</content>\n</page>`,
        };
      }
      case "query-data-sources":
        assert.deepEqual(args.data.data_source_urls, [DATA_SOURCE]);
        return { results: [...pages.values()] };
      case "create-pages": {
        assert.equal(args.parent, "memory");
        const [page] = args.pages;
        assert.equal(page.properties.Source, undefined);
        return {
          pages: [
            {
              id: add({
                Title: page.properties.title,
                Type: page.properties.Type,
                content: page.content,
              }),
            },
          ],
        };
      }
      case "update-page": {
        const page = pages.get(args.page_id);
        assert.ok(page, `unknown page ${args.page_id}`);
        assert.equal(args.command, "replace_content");
        page.content = args.new_str;
        return {};
      }
      case "finish-revision":
        return {};
      default:
        throw new Error(`unexpected tool ${tool}`);
    }
  }
  return { pages, calls, callTool };
}

test("writes memories incrementally and never deletes", async () => {
  const dir = path.join(home, "memories");
  fs.cpSync(FIXTURES, dir, { recursive: true });
  const notion = fakeNotionMcp([
    { Title: "Coding workflow preferences", Type: "Preference" },
  ]);

  // An existing memory on the same topic wins over a second copy.
  assert.deepEqual(await syncMemories(notion.callTool), {
    total: 3,
    created: 2,
    updated: 0,
    unchanged: 0,
    changedInNotion: 0,
    skippedExisting: 1,
    noLongerInCodex: 0,
  });
  const profile = [...notion.pages.values()].find(
    (p) => p.Title === "Role and background",
  );
  assert.equal(profile?.Type, "Profile");
  assert.match(profile?.content ?? "", /^Casey is a TypeScript developer/);

  notion.calls.length = 0;
  const again = await syncMemories(notion.callTool);
  assert.equal(again.unchanged, 2);
  assert.ok(!notion.calls.includes("create-pages"));
  assert.ok(!notion.calls.includes("update-page"));

  // Codex rewrites its profile: the plugin updates the same page.
  const summary = path.join(dir, "memory_summary.md");
  const original = fs.readFileSync(summary, "utf8");
  fs.writeFileSync(summary, original.replace("TypeScript", "Rust"));
  const updated = await syncMemories(notion.callTool);
  assert.equal(updated.updated, 1);
  assert.match(profile?.content ?? "", /Rust developer/);
  assert.ok(notion.calls.includes("finish-revision"));

  // Casey edits the profile in Notion. Codex changes after that leave it alone.
  profile!.content += "\nAlso writes Python.";
  fs.writeFileSync(summary, original.replace("TypeScript", "Go"));
  const kept = await syncMemories(notion.callTool);
  assert.equal(kept.changedInNotion, 1);
  assert.match(profile?.content ?? "", /Rust developer/);
  fs.writeFileSync(summary, original.replace("TypeScript", "Zig"));
  await syncMemories(notion.callTool);
  assert.match(profile?.content ?? "", /Rust developer/);

  // Casey deletes the project memory in Notion. The plugin does not bring it back.
  const work = [...notion.pages.values()].find(
    (p) => p.Title === "Small Node.js CLI utilities",
  );
  work!.deleted = true;
  const memoryFile = path.join(dir, "MEMORY.md");
  fs.appendFileSync(memoryFile, "- Use `node --watch` while iterating\n");
  notion.calls.length = 0;
  assert.equal((await syncMemories(notion.callTool)).changedInNotion, 2);
  assert.ok(!notion.calls.includes("create-pages"));

  // Codex drops the project: the plugin forgets it and deletes nothing.
  fs.writeFileSync(memoryFile, "");
  const dropped = await syncMemories(notion.callTool);
  assert.equal(dropped.noLongerInCodex, 1);
  assert.deepEqual(Object.keys(loadState().memories), ["profile"]);
});
