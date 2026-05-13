const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const APP_RESOURCE_URI = "ui://widget/plugin-builder-summary-v3.html";
const WIDGET_MIME_TYPE = "text/html;profile=mcp-app";
const pluginRoot = path.resolve(__dirname, "..");

const tools = [
  {
    name: "open_created_plugin_summary",
    title: "Open created plugin summary",
    description:
      "Render a right-side Codex app for a newly created local plugin, with View and Share handoff actions.",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        pluginPath: {
          type: "string",
          description: "Absolute filesystem path to the created plugin root.",
        },
        targetMarketplacePath: {
          type: "string",
          description:
            "Absolute filesystem path to the marketplace.json Codex should use for View and Share.",
        },
        relatedMarketplacePaths: {
          type: "array",
          items: { type: "string" },
          description:
            "Optional additional absolute marketplace.json paths that also contain this plugin.",
        },
      },
      required: ["pluginPath", "targetMarketplacePath"],
    },
    _meta: {
      ui: {
        resourceUri: APP_RESOURCE_URI,
      },
      "ui/resourceUri": APP_RESOURCE_URI,
      "openai/outputTemplate": APP_RESOURCE_URI,
    },
  },
];

function sendResult(id, result) {
  process.stdout.write(`${JSON.stringify({ jsonrpc: "2.0", id, result })}\n`);
}

function sendError(id, code, message) {
  process.stdout.write(
    `${JSON.stringify({
      jsonrpc: "2.0",
      id,
      error: { code, message },
    })}\n`,
  );
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function readTextIfPresent(filePath) {
  return fs.existsSync(filePath) ? fs.readFileSync(filePath, "utf8") : null;
}

function assertAbsolutePath(value, label) {
  if (typeof value !== "string" || !path.isAbsolute(value)) {
    throw new Error(`${label} must be an absolute filesystem path.`);
  }
  return path.resolve(value);
}

function listDirectories(root) {
  if (!fs.existsSync(root)) {
    return [];
  }
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(root, entry.name))
    .sort((left, right) => left.localeCompare(right));
}

function parseFrontmatter(markdown) {
  if (!markdown.startsWith("---\n")) {
    return { body: markdown.trim(), fields: {} };
  }

  const end = markdown.indexOf("\n---\n", 4);
  if (end === -1) {
    return { body: markdown.trim(), fields: {} };
  }

  const frontmatterBody = markdown.slice(4, end);
  const body = markdown.slice(end + 5).trim();
  const fields = {};

  for (const line of frontmatterBody.split("\n")) {
    const separator = line.indexOf(":");
    if (separator === -1) {
      continue;
    }
    const key = line.slice(0, separator).trim();
    const rawValue = line.slice(separator + 1).trim();
    fields[key] = rawValue.replace(/^["']|["']$/g, "");
  }

  return { body, fields };
}

function summarizeText(text, maxLength = 180) {
  const normalized = String(text ?? "").replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, maxLength - 1).trim()}...`;
}

function previewMarkdown(markdown) {
  const withoutFences = markdown.replace(/```[\s\S]*?```/g, " ");
  const withoutHeadings = withoutFences.replace(/^#{1,6}\s+/gm, "");
  return summarizeText(withoutHeadings, 280) || "This skill does not have a Markdown body.";
}

function relativeLabel(pluginPath, filePath) {
  return path.relative(pluginPath, filePath) || ".";
}

function extractMarkdownHeadings(markdown) {
  const headings = [];
  let inFence = false;

  for (const line of markdown.split("\n")) {
    const trimmed = line.trim();
    if (trimmed.startsWith("```") || trimmed.startsWith("~~~")) {
      inFence = !inFence;
      continue;
    }
    if (inFence || !/^#{1,3}\s+/.test(line)) {
      continue;
    }

    const heading = line.replace(/^#{1,3}\s+/, "").trim();
    if (heading) {
      headings.push(heading);
    }
  }

  return headings.slice(0, 6);
}

function readSkills(pluginPath, manifest) {
  const skillsRoot = path.resolve(
    pluginPath,
    typeof manifest.skills === "string" ? manifest.skills : "./skills",
  );

  return listDirectories(skillsRoot)
    .map((skillDir) => path.join(skillDir, "SKILL.md"))
    .filter((skillPath) => fs.existsSync(skillPath))
    .map((skillPath) => {
      const markdown = fs.readFileSync(skillPath, "utf8");
      const parsed = parseFrontmatter(markdown);
      const fallbackName = path.basename(path.dirname(skillPath));
      const title = parsed.fields.name || fallbackName;
      const summary = summarizeText(
        parsed.fields.description ||
          summarizeText(parsed.body) ||
          "No skill description provided.",
        150,
      );
      const headings = extractMarkdownHeadings(parsed.body);

      return {
        id: fallbackName,
        title,
        summary,
        pathLabel: relativeLabel(pluginPath, skillPath),
        frontmatterSummary: parsed.fields.description || "No summary provided.",
        headings,
        preview: previewMarkdown(parsed.body),
      };
    });
}

function readApps(pluginPath, manifest) {
  const appPath = path.resolve(
    pluginPath,
    typeof manifest.apps === "string" ? manifest.apps : "./.app.json",
  );
  const appText = readTextIfPresent(appPath);
  if (appText == null) {
    return [];
  }

  const appManifest = JSON.parse(appText);
  const apps = appManifest.apps && typeof appManifest.apps === "object"
    ? appManifest.apps
    : {};

  return Object.entries(apps).map(([key, value]) => ({
    id: key,
    title: key,
    summary: value?.description || value?.title || "Plugin app definition.",
    pathLabel: relativeLabel(pluginPath, appPath),
    appId: value?.id || "No app id provided.",
  }));
}

function readMcpServers(pluginPath, manifest) {
  const mcpPath = path.resolve(
    pluginPath,
    typeof manifest.mcpServers === "string" ? manifest.mcpServers : "./.mcp.json",
  );
  const mcpText = readTextIfPresent(mcpPath);
  if (mcpText == null) {
    return [];
  }

  const mcpManifest = JSON.parse(mcpText);
  const servers =
    mcpManifest.mcpServers && typeof mcpManifest.mcpServers === "object"
      ? mcpManifest.mcpServers
      : {};

  return Object.entries(servers).map(([key, value]) => {
    const args = Array.isArray(value?.args) ? value.args.join(" ") : "";
    const commandLabel = [value?.command || "No command provided.", args]
      .filter(Boolean)
      .join(" ");
    return {
      id: key,
      title: key,
      summary: value?.cwd
        ? `Runs from ${value.cwd === "." ? "the plugin root" : value.cwd}.`
        : "Local MCP server definition.",
      pathLabel: relativeLabel(pluginPath, mcpPath),
      commandLabel,
    };
  });
}

function describeMarketplace(marketplacePath, targetMarketplacePath) {
  const personalMarketplacePath = path.join(
    os.homedir(),
    ".agents",
    "plugins",
    "marketplace.json",
  );
  const marketplaceRoot = path.dirname(path.dirname(path.dirname(marketplacePath)));
  const label =
    marketplacePath === personalMarketplacePath
      ? "Personal marketplace"
      : `${path.basename(marketplaceRoot) || "Workspace"} marketplace`;
  const suffix =
    marketplacePath === targetMarketplacePath ? " (View and Share target)" : "";
  return {
    label: `${label}${suffix}`,
    value: marketplacePath,
  };
}

function buildPluginDeepLink(pluginName, marketplacePath, mode) {
  const params = new URLSearchParams({ marketplacePath });
  if (mode === "share") {
    params.set("mode", "share");
  }
  return `codex://plugins/${encodeURIComponent(pluginName)}?${params.toString()}`;
}

function uniquePaths(paths) {
  return [...new Set(paths)];
}

function readPluginSummary(args = {}) {
  const pluginPath = assertAbsolutePath(args.pluginPath, "pluginPath");
  const targetMarketplacePath = assertAbsolutePath(
    args.targetMarketplacePath,
    "targetMarketplacePath",
  );
  const manifestPath = path.join(pluginPath, ".codex-plugin", "plugin.json");
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`pluginPath does not contain ${manifestPath}.`);
  }

  const manifest = readJson(manifestPath);
  const pluginName = manifest.name || path.basename(pluginPath);
  const displayName = manifest.interface?.displayName || pluginName;
  const relatedMarketplacePaths = Array.isArray(args.relatedMarketplacePaths)
    ? args.relatedMarketplacePaths.map((value) =>
        assertAbsolutePath(value, "relatedMarketplacePaths entry"),
      )
    : [];
  const marketplaces = uniquePaths([
    targetMarketplacePath,
    ...relatedMarketplacePaths,
  ]).map((marketplacePath) =>
    describeMarketplace(marketplacePath, targetMarketplacePath),
  );

  return {
    plugin: {
      name: pluginName,
      displayName,
      description:
        manifest.interface?.shortDescription ||
        manifest.description ||
        "No plugin description provided.",
      viewUrl: buildPluginDeepLink(pluginName, targetMarketplacePath, "view"),
      shareUrl: buildPluginDeepLink(pluginName, targetMarketplacePath, "share"),
    },
    skills: readSkills(pluginPath, manifest),
    apps: readApps(pluginPath, manifest),
    mcpServers: readMcpServers(pluginPath, manifest),
    marketplaces,
    localDetails: [
      { label: "Plugin path", value: pluginPath },
      { label: "Manifest", value: manifestPath },
    ],
  };
}

function widgetResourceMeta() {
  return {
    "openai/widgetDescription":
      "A right-side Codex app that presents a newly created local plugin and offers View or Share handoff actions.",
    "openai/widgetPrefersBorder": false,
    "openai/widgetCSP": {
      connect_domains: [],
      resource_domains: [],
      frame_domains: [],
    },
    ui: {
      prefersBorder: false,
      csp: {
        connectDomains: [],
        resourceDomains: [],
        frameDomains: [],
      },
    },
  };
}

function widgetHtml() {
  return fs.readFileSync(
    path.join(pluginRoot, "app", "dist", "plugin-builder-widget.html"),
    "utf8",
  );
}

function toolResult(summary) {
  return {
    content: [
      {
        type: "text",
        text: `Opened the Plugin Builder summary for ${summary.plugin.displayName}.`,
      },
    ],
    structuredContent: summary,
  };
}

function handleToolCall(params = {}) {
  if (params.name !== "open_created_plugin_summary") {
    throw new Error(`Unknown tool: ${params.name}`);
  }
  return toolResult(readPluginSummary(params.arguments || params.args || {}));
}

function handleRequest(request) {
  if (!request?.id && request?.method?.startsWith("notifications/")) {
    return;
  }

  switch (request.method) {
    case "initialize":
      sendResult(request.id, {
        protocolVersion: request.params?.protocolVersion || "2024-11-05",
        capabilities: {
          tools: {},
          resources: {
            subscribe: false,
            listChanged: false,
          },
        },
        serverInfo: {
          name: "plugin-builder",
          version: "0.1.0",
        },
      });
      return;
    case "tools/list":
      sendResult(request.id, { tools });
      return;
    case "tools/call":
      sendResult(request.id, handleToolCall(request.params));
      return;
    case "resources/list":
      sendResult(request.id, {
        resources: [
          {
            uri: APP_RESOURCE_URI,
            name: "plugin_creation_summary",
            title: "Plugin Builder summary",
            description: "Read-only local plugin summary and sharing handoff.",
            mimeType: WIDGET_MIME_TYPE,
            _meta: widgetResourceMeta(),
          },
        ],
      });
      return;
    case "resources/templates/list":
      sendResult(request.id, { resourceTemplates: [] });
      return;
    case "resources/read":
      if (request.params?.uri !== APP_RESOURCE_URI) {
        sendError(request.id, -32602, `Unknown resource: ${request.params?.uri}`);
        return;
      }
      sendResult(request.id, {
        contents: [
          {
            uri: APP_RESOURCE_URI,
            mimeType: WIDGET_MIME_TYPE,
            text: widgetHtml(),
            _meta: widgetResourceMeta(),
          },
        ],
      });
      return;
    default:
      sendError(request.id, -32601, `Unsupported method: ${request.method}`);
  }
}

process.stdin.setEncoding("utf8");
let buffer = "";

process.stdin.on("data", (chunk) => {
  buffer += chunk;
  let newlineIndex = buffer.indexOf("\n");

  while (newlineIndex >= 0) {
    const line = buffer.slice(0, newlineIndex).trim();
    buffer = buffer.slice(newlineIndex + 1);
    newlineIndex = buffer.indexOf("\n");

    if (!line) {
      continue;
    }

    let request;
    try {
      request = JSON.parse(line);
      handleRequest(request);
    } catch (error) {
      sendError(
        request?.id ?? null,
        -32000,
        error instanceof Error ? error.message : String(error),
      );
    }
  }
});
