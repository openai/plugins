// Calls Notion MCP tools through Codex's own MCP client, so these scripts never handle a
// Notion token: Codex owns the connection. The worker starts `codex app-server`, opens an
// ephemeral thread (no model call, and ephemeral threads never feed Codex's memory
// pipeline), and uses `mcpServer/tool/call`.
//
// Codex routes this plugin's Notion tools two ways: through the Notion app (`.app.json`,
// served by the `codex_apps` server) for ChatGPT sign-in, and through the `notion` server in
// `.mcp.json` for API key sign-in. Tool names differ in prefix and separators, so callers use
// logical names such as "create-pages" and this module resolves them per server.
import { type ChildProcess, spawn } from "node:child_process";
import readline from "node:readline";

// `tool` is a logical Notion MCP tool name such as "create-pages" or "fetch".
export type CallTool = (tool: string, args: unknown) => Promise<unknown>;

interface RpcResponse {
  id?: number;
  method?: string;
  result?: unknown;
  error?: { message?: string };
}

interface McpServerStatus {
  name: string;
  runtimeStatus?: string;
  tools?: Record<string, unknown>;
}

interface ToolResult {
  content?: { type: string; text?: string }[];
  isError?: boolean;
}

const REQUEST_TIMEOUT_MS = 60_000;
const PROBE_TOOL = "create-pages";

export class CodexNotionMcp {
  private child: ChildProcess;
  private pending = new Map<number, (message: RpcResponse) => void>();
  private nextId = 0;
  private threadId = "";
  private tools = new Map<string, string>();
  server = "";

  private constructor(codexPath: string) {
    this.child = spawn(codexPath, ["app-server"], {
      stdio: ["pipe", "pipe", "ignore"],
      env: { ...process.env, NOTION_MEMORY_WORKER: "1" },
    });
    readline
      .createInterface({ input: this.child.stdout! })
      .on("line", (line) => {
        let message: RpcResponse;
        try {
          message = JSON.parse(line);
        } catch {
          return;
        }
        if (message.id === undefined) return;
        this.pending.get(message.id)?.(message);
        this.pending.delete(message.id);
      });
  }

  static async connect(opts: {
    codexPath: string;
    cwd: string;
    server?: string;
  }): Promise<CodexNotionMcp> {
    const mcp = new CodexNotionMcp(opts.codexPath);
    try {
      await mcp.rpc("initialize", {
        clientInfo: { name: "notion-memory", version: "0.1.0" },
      });
      mcp.notify("initialized");
      const thread = (await mcp.rpc("thread/start", {
        ephemeral: true,
        cwd: opts.cwd,
      })) as { thread?: { id?: string } };
      mcp.threadId = thread.thread?.id ?? "";
      if (!mcp.threadId) throw new Error("codex app-server returned no thread");
      await mcp.findNotionServer(opts.server);
      return mcp;
    } catch (e) {
      mcp.close();
      throw e;
    }
  }

  readonly callTool: CallTool = async (tool, args) => {
    const name = this.tools.get(squash(tool));
    if (!name) throw new Error(`${this.server} has no Notion ${tool} tool`);
    const result = (await this.rpc("mcpServer/tool/call", {
      threadId: this.threadId,
      server: this.server,
      tool: name,
      arguments: args,
    })) as ToolResult;
    const text = (result.content ?? []).map((part) => part.text ?? "").join("");
    if (result.isError) throw new Error(`${tool}: ${text.slice(0, 500)}`);
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  };

  close(): void {
    this.child.kill();
  }

  private async findNotionServer(preferred?: string): Promise<void> {
    const status = (await this.rpc("mcpServerStatus/list", {
      threadId: this.threadId,
    })) as { data?: McpServerStatus[] };
    const candidates = (status.data ?? []).flatMap((server) => {
      const tools = notionTools(server);
      return tools.has(squash(PROBE_TOOL)) ? [{ server, tools }] : [];
    });
    const match =
      candidates.find((c) => c.server.name === preferred) ??
      candidates.find((c) => c.server.name === "notion") ??
      candidates[0];
    if (!match) {
      const names = (status.data ?? [])
        .map((s) => `${s.name} (${s.runtimeStatus})`)
        .join(", ");
      throw new Error(
        `no connected Notion server exposes ${PROBE_TOOL}; found: ${names || "none"}. Connect Notion in Codex first.`,
      );
    }
    this.server = match.server.name;
    this.tools = match.tools;
  }

  private rpc(method: string, params: unknown): Promise<unknown> {
    const id = ++this.nextId;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`${method} timed out`));
      }, REQUEST_TIMEOUT_MS);
      this.pending.set(id, (message) => {
        clearTimeout(timer);
        if (message.error)
          reject(new Error(`${method}: ${message.error.message}`));
        else resolve(message.result);
      });
      this.child.stdin!.write(
        `${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`,
      );
    });
  }

  private notify(method: string): void {
    this.child.stdin!.write(`${JSON.stringify({ jsonrpc: "2.0", method })}\n`);
  }
}

// Maps logical tool names to the server's tool names. Hosted Notion MCP names its tools
// `notion-create-pages`; the Notion app on `codex_apps` uses a connector prefix and
// underscores. On servers that also host other apps, only tools with the same prefix as the
// Notion create-pages tool count.
export function notionTools(server: {
  name: string;
  tools?: Record<string, unknown>;
}): Map<string, string> {
  const names = Object.keys(server.tools ?? {});
  const probe = names.find((n) => /notion.*create.?pages$/i.test(n));
  const out = new Map<string, string>();
  if (!probe) return out;
  const prefix = squash(probe).slice(0, -squash(PROBE_TOOL).length);
  for (const name of names) {
    const key = squash(name);
    if (key.startsWith(prefix)) out.set(key.slice(prefix.length), name);
  }
  return out;
}

function squash(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]/g, "");
}
