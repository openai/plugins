import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import readline from "node:readline";
import path from "node:path";

export const MCP_SERVER_NAME = "creative_production_mcp";

export const REQUIRED_MCP_TOOLS = [
  "creative_production_board",
  ];

export const CURRENT_MCP_TOOLS = [
  ...REQUIRED_MCP_TOOLS,
];

export const MODEL_AND_APP_MCP_TOOLS = [
  "creative_production_board",
];

export function pluginRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
}

export function mcpServerPath(root = pluginRoot()) {
  const sourceServerPath = path.join(root, "mcp", "server.mjs");
  if (existsSync(sourceServerPath)) return sourceServerPath;
  return path.join(root, "mcp", "server.bundle.mjs");
}

export async function probeMcpTools({
  expectedTools = CURRENT_MCP_TOOLS,
  root = pluginRoot(),
} = {}) {
  const client = createJsonRpcStdioClient({
    command: process.execPath,
    args: [mcpServerPath(root)],
    cwd: root,
  });

  try {
    await client.start();
    await client.request("initialize", {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: {
        name: "creative-production-mcp-probe",
        version: "0.0.0",
      },
    });
    client.notify("notifications/initialized");
    const response = await client.request("tools/list", {});
    const tools = response.tools || [];
    const toolNames = tools.map((tool) => tool.name).sort();
    const missing = expectedTools.filter((toolName) => !toolNames.includes(toolName));
    if (missing.length) {
      throw new Error(`Missing ${MCP_SERVER_NAME} tool(s): ${missing.join(", ")}`);
    }
    const unexpected = toolNames.filter((toolName) => !expectedTools.includes(toolName));
    if (unexpected.length) {
      throw new Error(`Unexpected ${MCP_SERVER_NAME} tool(s): ${unexpected.join(", ")}`);
    }
    const wrongVisibility = MODEL_AND_APP_MCP_TOOLS.filter((toolName) => {
      const tool = tools.find((candidate) => candidate.name === toolName);
      const visibility = tool?._meta?.ui?.visibility;
      return !Array.isArray(visibility)
        || !visibility.includes("model")
        || !visibility.includes("app");
    });
    if (wrongVisibility.length) {
      throw new Error(
        `MCP tool(s) must be visible to both model and app: ${wrongVisibility.join(", ")}`,
      );
    }
    return toolNames;
  } finally {
    await client.close();
  }
}

function createJsonRpcStdioClient({ command, args, cwd }) {
  let child = null;
  let nextId = 1;
  const pending = new Map();

  function settle(id, outcome, payload) {
    const entry = pending.get(id);
    if (!entry) return;
    pending.delete(id);
    clearTimeout(entry.timeout);
    entry[outcome](payload);
  }

  return {
    async start() {
      child = spawn(command, args, {
        cwd,
        stdio: ["pipe", "pipe", "inherit"],
      });
      child.once("error", (error) => {
        for (const id of pending.keys()) settle(id, "reject", error);
      });
      child.once("exit", (code, signal) => {
        const error = new Error(
          `MCP server exited before probe completed: code=${code} signal=${signal}`,
        );
        for (const id of pending.keys()) settle(id, "reject", error);
      });
      readline.createInterface({ input: child.stdout }).on("line", (line) => {
        if (!line.trim()) return;
        let message;
        try {
          message = JSON.parse(line);
        } catch (error) {
          for (const id of pending.keys()) settle(id, "reject", error);
          return;
        }
        if (message.id === undefined) return;
        if (message.error) {
          settle(message.id, "reject", new Error(message.error.message || "MCP request failed"));
        } else {
          settle(message.id, "resolve", message.result);
        }
      });
    },
    request(method, params = {}) {
      if (!child?.stdin) throw new Error("MCP server is not started.");
      const id = nextId;
      nextId += 1;
      const payload = { jsonrpc: "2.0", id, method, params };
      const result = new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          settle(id, "reject", new Error(`Timed out waiting for MCP response: ${method}`));
        }, 10_000);
        pending.set(id, { resolve, reject, timeout });
      });
      child.stdin.write(`${JSON.stringify(payload)}\n`);
      return result;
    },
    notify(method, params = {}) {
      if (!child?.stdin) throw new Error("MCP server is not started.");
      child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", method, params })}\n`);
    },
    async close() {
      if (!child) return;
      const closing = child;
      child = null;
      closing.stdin?.end();
      await new Promise((resolve) => {
        const timeout = setTimeout(resolve, 2_000);
        closing.once("close", () => {
          clearTimeout(timeout);
          resolve();
        });
      });
      if (closing.exitCode === null) closing.kill("SIGTERM");
    },
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const toolNames = await probeMcpTools({ expectedTools: CURRENT_MCP_TOOLS });
  console.log(toolNames.join("\n"));
}
