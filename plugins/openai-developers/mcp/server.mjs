import path from "node:path";
import readline from "node:readline";

const SERVER_NAME = "OpenAI Developers MCP";
const TOOL_NAME = "confirm_openai_api_key_local_destination";
const DEFAULT_ENV_NAME = "OPENAI_API_KEY";
const ENV_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;
const JsonRpcError = {
  METHOD_NOT_FOUND: -32601,
  INVALID_PARAMS: -32602,
};

let nextRequestId = 1;
const pendingRequests = new Map();

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function sendResult(id, result) {
  send({ jsonrpc: "2.0", id, result });
}

function sendError(id, code, message) {
  send({ jsonrpc: "2.0", id, error: { code, message } });
}

function request(method, params) {
  const id = `server-${nextRequestId++}`;
  send({ jsonrpc: "2.0", id, method, params });
  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject });
  });
}

function requireNonEmptyString(value, name) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${name} must be a non-empty string.`);
  }
  return value.trim();
}

function resolveTarget(workspacePath, targetPath) {
  const workspace = path.resolve(requireNonEmptyString(workspacePath, "workspacePath"));
  const target = path.resolve(
    workspace,
    requireNonEmptyString(targetPath, "targetPath"),
  );
  const relative = path.relative(workspace, target);
  if (
    relative === ".." ||
    relative.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relative)
  ) {
    throw new Error("The env file must be inside the selected workspace.");
  }
  return { workspace, target };
}

async function handleToolCall(id, params) {
  if (params?.name !== TOOL_NAME) {
    sendError(id, JsonRpcError.INVALID_PARAMS, `Unknown tool: ${params?.name ?? ""}`);
    return;
  }

  const args = params.arguments ?? {};
  const envName = args.envName ?? DEFAULT_ENV_NAME;
  if (typeof envName !== "string" || !ENV_NAME_PATTERN.test(envName)) {
    throw new Error("envName must be a valid environment variable name.");
  }

  const { workspace, target: recommendedTarget } = resolveTarget(
    args.workspacePath,
    args.targetPath,
  );
  const elicitation = await request("elicitation/create", {
    mode: "form",
    message: `Choose where OpenAI Developers should save the new API key as ${envName}.`,
    requestedSchema: {
      type: "object",
      properties: {
        targetPath: {
          type: "string",
          title: "Save location",
          default: recommendedTarget,
          minLength: 1,
        },
      },
      required: ["targetPath"],
    },
  });

  if (elicitation?.action !== "accept") {
    sendResult(id, {
      content: [
        {
          type: "text",
          text: "The local API key destination was not approved. Do not create or write a key.",
        },
      ],
      structuredContent: {
        status: "not_approved",
        action: elicitation?.action ?? "cancel",
      },
    });
    return;
  }

  const { target } = resolveTarget(workspace, elicitation.content?.targetPath);
  sendResult(id, {
    content: [
      {
        type: "text",
        text: `The developer approved ${target} for ${envName}. Continue with secure key creation and write only to that env file.`,
      },
    ],
    structuredContent: {
      status: "approved",
      workspacePath: workspace,
      targetPath: target,
      envName,
    },
  });
}

async function handleRequest(message) {
  const { id, method, params } = message;

  if (method === "initialize") {
    sendResult(id, {
      protocolVersion: params?.protocolVersion ?? "2025-11-25",
      capabilities: { tools: {} },
      serverInfo: {
        name: SERVER_NAME,
        version: "0.1.0",
      },
      instructions:
        "Use confirm_openai_api_key_local_destination after the OpenAI Platform picker returns a key name and target ids. It asks the developer to confirm or edit the local env-file destination before a secret is created or written.",
    });
    return;
  }

  if (method === "ping") {
    sendResult(id, {});
    return;
  }

  if (method === "tools/list") {
    sendResult(id, {
      tools: [
        {
          name: TOOL_NAME,
          title: "Confirm OpenAI API Key Local Destination",
          description:
            "Ask the developer to confirm or edit the local env-file destination for a new OpenAI API key. Call this after the Platform picker returns the confirmed key name and target ids, and proceed only when it returns approved.",
          inputSchema: {
            type: "object",
            properties: {
              workspacePath: {
                type: "string",
                description:
                  "Absolute workspace root used to confine the local env-file write.",
              },
              targetPath: {
                type: "string",
                description:
                  "Recommended env-file path inside the workspace, such as .env.local.",
              },
              envName: {
                type: "string",
                description:
                  "Environment variable name to create or update. Defaults to OPENAI_API_KEY.",
                default: DEFAULT_ENV_NAME,
              },
            },
            required: ["workspacePath", "targetPath"],
          },
          annotations: {
            readOnlyHint: true,
            destructiveHint: false,
            idempotentHint: true,
            openWorldHint: false,
          },
        },
      ],
    });
    return;
  }

  if (method === "tools/call") {
    try {
      await handleToolCall(id, params);
    } catch (error) {
      sendError(
        id,
        JsonRpcError.INVALID_PARAMS,
        error instanceof Error ? error.message : String(error),
      );
    }
    return;
  }

  if (id !== undefined) {
    sendError(id, JsonRpcError.METHOD_NOT_FOUND, `Method not found: ${method}`);
  }
}

const lines = readline.createInterface({
  input: process.stdin,
  crlfDelay: Infinity,
});

lines.on("line", (line) => {
  if (line.trim().length === 0) {
    return;
  }

  let message;
  try {
    message = JSON.parse(line);
  } catch {
    return;
  }

  if (message.method === undefined && message.id !== undefined) {
    const pending = pendingRequests.get(message.id);
    if (pending !== undefined) {
      pendingRequests.delete(message.id);
      if (message.error !== undefined) {
        pending.reject(new Error(message.error.message ?? "MCP request failed."));
      } else {
        pending.resolve(message.result);
      }
    }
    return;
  }

  void handleRequest(message);
});
