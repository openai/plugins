#!/usr/bin/env node

// src/agent-skills/scripts/validate_theme.ts
import { access } from "fs/promises";
import { readFileSync } from "fs";
import { join, normalize } from "path";
import { parseArgs } from "util";
import {
  check,
  extractDocDefinition,
  FileType as NodeFileType,
  recommended,
  SourceCodeType,
  toSchema,
  toSourceCode
} from "@shopify/theme-check-common";
import { ThemeLiquidDocsManager } from "@shopify/theme-check-docs-updater";
import { themeCheckRun } from "@shopify/theme-check-node";

// src/validation/format.ts
import { randomUUID } from "crypto";

// src/validation/index.ts
function hasFailedValidation(responses) {
  return responses.some(
    (response) => response.result === "failed" /* FAILED */
  );
}

// src/validation/format.ts
function extractArtifactsFromItems(items) {
  return items.map((item) => ({
    artifactId: item.artifactId || `artifact-${randomUUID()}`,
    revision: item.revision ?? 1
  }));
}
function attachArtifactIds(responses, artifacts) {
  return responses.map((r, idx) => {
    const artifact = artifacts[idx];
    if (!artifact) {
      return r;
    }
    return {
      ...r,
      artifactId: artifact.artifactId,
      artifactRevision: artifact.revision
    };
  });
}
function formatValidationResult(result, itemName = "Items") {
  const hasFailed = hasFailedValidation(result);
  const hasInform = result.some((r) => r.result === "inform" /* INFORM */);
  let overallStatus;
  if (hasFailed) {
    overallStatus = "\u274C INVALID";
  } else if (hasInform) {
    overallStatus = "\u26A0\uFE0F VALID (with deprecated fields)";
  } else {
    overallStatus = "\u2705 VALID";
  }
  let responseText = `## Validation Summary

`;
  responseText += `**Overall Status:** ${overallStatus}
`;
  responseText += `**Total ${itemName}:** ${result.length}

`;
  responseText += `## Detailed Results

`;
  result.forEach((check2, index) => {
    let statusIcon;
    if (check2.result === "success" /* SUCCESS */) {
      statusIcon = "\u2705";
    } else if (check2.result === "inform" /* INFORM */) {
      statusIcon = "\u26A0\uFE0F";
    } else {
      statusIcon = "\u274C";
    }
    responseText += `### ${itemName.slice(0, -1)} ${index + 1}
`;
    if (check2.artifactId) {
      responseText += `**Artifact ID:** ${check2.artifactId}`;
      if (check2.artifactRevision) {
        responseText += `
**Revision:** ${check2.artifactRevision}`;
      }
      responseText += `
*Use same ID & increment revision when retrying on an improvement of this artifact*

`;
    }
    responseText += `**Status:** ${statusIcon} ${check2.result.toUpperCase()}
`;
    responseText += `**Details:** ${check2.resultDetail}

`;
  });
  return responseText;
}

// src/http/index.ts
var PROD_BASE_URL = "https://shopify.dev/";
var SHOP_DEV_BASE_URL = "https://shopify-dev.shop.dev/";
function stagingHost(serverNumber) {
  return `https://shopify-dev-staging${serverNumber}.shopifycloud.com/`;
}
function resolveShopifyDevBaseUrl(options) {
  const env = options?.env ?? process.env;
  const stagingRaw = env.SHOPIFY_DEV_STAGING_SERVER_NUMBER?.trim();
  if (stagingRaw) {
    if (!/^\d+$/.test(stagingRaw)) {
      throw new Error(
        `SHOPIFY_DEV_STAGING_SERVER_NUMBER must be a positive integer; got: "${stagingRaw}"`
      );
    }
    const serverNumber = Number(stagingRaw);
    if (!Number.isSafeInteger(serverNumber) || serverNumber <= 0) {
      throw new Error(
        `SHOPIFY_DEV_STAGING_SERVER_NUMBER must be a positive integer; got: "${stagingRaw}"`
      );
    }
    const token = env.MINERVA_TOKEN;
    if (!token) {
      const audience = stagingHost(serverNumber).replace(/\/$/, "");
      throw new Error(
        `SHOPIFY_DEV_STAGING_SERVER_NUMBER=${serverNumber} is set but no Minerva token is available. Staging servers are behind Minerva. Get a token via:
  export MINERVA_TOKEN=$(devx minerva-auth --client-id 0oa1bphetnkOusboI0x8 --audience ${audience})`
      );
    }
    return {
      url: stagingHost(serverNumber),
      headers: { Cookie: `MINERVA_TOKEN=${token}` }
    };
  }
  const instrumentationOverride = env.SHOPIFY_DEV_INSTRUMENTATION_URL?.trim();
  if (instrumentationOverride && options?.uri?.startsWith("/mcp/usage")) {
    return { url: instrumentationOverride, headers: {} };
  }
  if (env.DEV && env.DEV !== "false") {
    return { url: SHOP_DEV_BASE_URL, headers: {} };
  }
  return { url: PROD_BASE_URL, headers: {} };
}
async function shopifyDevFetch(uri, options) {
  let url;
  let resolvedHeaders = {};
  if (uri.startsWith("http://") || uri.startsWith("https://")) {
    url = new URL(uri);
  } else {
    const resolved = resolveShopifyDevBaseUrl({ uri });
    url = new URL(uri, resolved.url);
    resolvedHeaders = resolved.headers;
  }
  if (options?.parameters) {
    Object.entries(options.parameters).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }
  const response = await fetch(url.toString(), {
    method: options?.method || "GET",
    headers: {
      Accept: "application/json",
      "Cache-Control": "no-cache",
      "X-Shopify-Surface": "mcp",
      "X-Shopify-MCP-Version": options?.instrumentation?.packageVersion || "",
      "X-Shopify-Timestamp": options?.instrumentation?.timestamp || "",
      ...resolvedHeaders,
      ...options?.headers
    },
    ...options?.body && { body: options.body }
  });
  if (!response.ok) {
    let errorBody;
    try {
      errorBody = await response.text();
    } catch {
    }
    throw new Error(
      errorBody ? `HTTP ${response.status}: ${errorBody}` : `HTTP error! status: ${response.status}`
    );
  }
  return await response.text();
}

// src/agent-skills/scripts/instrumentation.ts
function isInstrumentationDisabled() {
  try {
    return process.env.OPT_OUT_INSTRUMENTATION === "true";
  } catch {
    return false;
  }
}
async function reportValidation(toolName, result, context) {
  if (isInstrumentationDisabled()) return;
  const { model, clientName, clientVersion, ...remainingContext } = context ?? {};
  try {
    const headers = {
      "Content-Type": "application/json",
      "X-Shopify-Surface": "skills"
    };
    if (clientName) headers["X-Shopify-Client-Name"] = String(clientName);
    if (clientVersion)
      headers["X-Shopify-Client-Version"] = String(clientVersion);
    if (model) headers["X-Shopify-Client-Model"] = String(model);
    await shopifyDevFetch("/mcp/usage", {
      method: "POST",
      headers,
      body: JSON.stringify({
        tool: toolName,
        parameters: {
          skill: "shopify-liquid",
          skillVersion: "1.9.1",
          ...remainingContext
        },
        result
      }),
      instrumentation: {
        packageVersion: "1.9.1",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
  } catch {
  }
}

// src/agent-skills/scripts/validate_theme.ts
var { values } = parseArgs({
  options: {
    "theme-path": { type: "string" },
    files: { type: "string" },
    filename: { type: "string" },
    filetype: { type: "string" },
    code: { type: "string", short: "c" },
    file: { type: "string", short: "f" },
    "artifact-id": { type: "string" },
    revision: { type: "string" },
    model: { type: "string" },
    "client-name": { type: "string" },
    "client-version": { type: "string" },
    json: { type: "boolean" }
  }
});
var capturedCode;
var VALID_FILE_TYPES = [
  "assets",
  "blocks",
  "config",
  "layout",
  "locales",
  "sections",
  "snippets",
  "templates"
];
async function validateFullApp(themePath, relativeFilePaths) {
  let configPath = join(themePath, ".theme-check.yml");
  try {
    await access(configPath);
  } catch {
    configPath = void 0;
  }
  const checkResult = await themeCheckRun(
    themePath,
    configPath,
    (msg) => console.error(msg)
  );
  const byUri = {};
  for (const offense of checkResult.offenses) {
    (byUri[offense.uri] ??= []).push(formatOffense(offense));
  }
  return relativeFilePaths.map((relPath) => {
    const matchedUri = Object.keys(byUri).find(
      (u) => normalize(u).endsWith(normalize(relPath))
    );
    if (matchedUri) {
      return {
        result: "failed" /* FAILED */,
        resultDetail: `${relPath}:
${byUri[matchedUri].join("\n")}`
      };
    }
    return {
      result: "success" /* SUCCESS */,
      resultDetail: `${relPath} passed all checks.`
    };
  });
}
var MockFileSystem = class {
  constructor(theme) {
    this.theme = theme;
  }
  async readFile(uri) {
    const file = this.theme[uri];
    if (!file) throw new Error(`File not found: ${uri}`);
    return file;
  }
  async readDirectory() {
    return [];
  }
  async stat(uri) {
    const file = this.theme[uri];
    if (!file) throw new Error(`File not found: ${uri}`);
    return { type: NodeFileType.File, size: file.length };
  }
};
async function validateCodeblock(fileName, fileType, content) {
  const uri = `file:///${fileType}/${fileName}`;
  const theme = { [uri]: content };
  const LOCALE_CHECKS_TO_SKIP = /* @__PURE__ */ new Set([
    "TranslationKeyExists",
    "ValidSchemaTranslations"
  ]);
  const config = {
    checks: recommended.filter(
      (c) => !LOCALE_CHECKS_TO_SKIP.has(
        c.meta?.code ?? ""
      )
    ),
    settings: {},
    rootUri: "file:///",
    context: "theme"
  };
  const docsManager = new ThemeLiquidDocsManager();
  const sourceCode = Object.entries(theme).filter(([u]) => u.endsWith(".liquid") || u.endsWith(".json")).map(([u, c]) => toSourceCode(u, c, void 0));
  const offenses = await check(sourceCode, config, {
    fs: new MockFileSystem(theme),
    themeDocset: docsManager,
    jsonValidationSet: docsManager,
    getBlockSchema: async (blockName) => {
      const blockUri = `file:///blocks/${blockName}.liquid`;
      const sc = sourceCode.find((s) => s.uri === blockUri);
      if (!sc) return void 0;
      return toSchema("theme", blockUri, sc, async () => true);
    },
    getSectionSchema: async (sectionName) => {
      const sectionUri = `file:///sections/${sectionName}.liquid`;
      const sc = sourceCode.find((s) => s.uri === sectionUri);
      if (!sc) return void 0;
      return toSchema("theme", sectionUri, sc, async () => true);
    },
    async getDocDefinition(relativePath) {
      const sc = sourceCode.find(
        (s) => normalize(s.uri).endsWith(normalize(relativePath))
      );
      if (!sc || sc.type !== SourceCodeType.LiquidHtml) return void 0;
      return extractDocDefinition(sc.uri, sc.ast);
    }
  });
  if (offenses.length === 0) {
    return {
      result: "success" /* SUCCESS */,
      resultDetail: `${fileName} passed all checks.`
    };
  }
  return {
    result: "failed" /* FAILED */,
    resultDetail: offenses.map((o) => formatOffense(o)).join("\n")
  };
}
function formatOffense(offense) {
  const line = offense.start.line + 1;
  const col = offense.start.character + 1;
  const base = `ERROR [line ${line}, col ${col}]: ${offense.message}`;
  if (offense.suggest && offense.suggest.length > 0) {
    return `${base}; SUGGESTED FIXES: ${offense.suggest.map((s) => s.message).join(" OR ")}.`;
  }
  return base;
}
function parseRevision(raw) {
  if (!raw) return void 0;
  const n = Number.parseInt(raw, 10);
  return Number.isFinite(n) && n > 0 ? n : void 0;
}
function formatErrorResponse(detail, count = 1) {
  const items = Array.from({ length: count }).map(() => ({
    artifactId: values["artifact-id"],
    revision: parseRevision(values["revision"])
  }));
  const artifacts = extractArtifactsFromItems(items);
  const responses = attachArtifactIds(
    items.map(() => ({
      result: "failed" /* FAILED */,
      resultDetail: detail
    })),
    artifacts
  );
  return {
    responses,
    text: formatValidationResult(responses, "Files")
  };
}
function emit(responses, success) {
  const text = formatValidationResult(responses, "Files");
  console.log(values.json ? JSON.stringify({ success, responses }) : text);
  return text;
}
async function main() {
  if (values["theme-path"]) {
    const themePath = values["theme-path"];
    const files = (values.files ?? "").split(",").map((f) => f.trim()).filter(Boolean);
    if (files.length === 0) {
      const { responses: responses3, text } = formatErrorResponse(
        "--files must list at least one relative file path"
      );
      console.log(
        values.json ? JSON.stringify({ success: false, responses: responses3 }) : text
      );
      process.exit(1);
    }
    const fileResults = await validateFullApp(themePath, files);
    const artifacts = extractArtifactsFromItems(
      files.map(() => ({
        artifactId: values["artifact-id"],
        revision: parseRevision(values["revision"])
      }))
    );
    const responses2 = attachArtifactIds(
      fileResults,
      artifacts
    );
    const success2 = fileResults.every(
      (r) => r.result !== "failed" /* FAILED */
    );
    const responseText2 = emit(responses2, success2);
    await reportValidation("validate_theme", responseText2, {
      model: values.model,
      clientName: values["client-name"],
      clientVersion: values["client-version"],
      themePath,
      files,
      artifactId: artifacts[0]?.artifactId,
      revision: artifacts[0]?.revision
    });
    process.exit(success2 ? 0 : 1);
    return;
  }
  const filename = values.filename;
  if (!filename) {
    const { responses: responses2, text } = formatErrorResponse(
      "Provide either --theme-path (full app mode) or --filename (stateless mode)"
    );
    console.log(
      values.json ? JSON.stringify({ success: false, responses: responses2 }) : text
    );
    process.exit(1);
  }
  let content = values.code;
  if (values.file) {
    content = readFileSync(values.file, "utf-8");
  }
  capturedCode = content;
  if (!content) {
    const { responses: responses2, text } = formatErrorResponse(
      "Provide --code or --file with the codeblock content"
    );
    console.log(
      values.json ? JSON.stringify({ success: false, responses: responses2 }) : text
    );
    process.exit(1);
  }
  const rawFileType = values.filetype ?? "sections";
  if (!VALID_FILE_TYPES.includes(rawFileType)) {
    const { responses: responses2, text } = formatErrorResponse(
      `Invalid --filetype "${rawFileType}". Valid values: ${VALID_FILE_TYPES.join(", ")}`
    );
    console.log(
      values.json ? JSON.stringify({ success: false, responses: responses2 }) : text
    );
    process.exit(1);
  }
  const [artifact] = extractArtifactsFromItems([
    {
      artifactId: values["artifact-id"],
      revision: parseRevision(values["revision"])
    }
  ]);
  const fileResult = await validateCodeblock(
    filename,
    rawFileType,
    content
  );
  const responses = attachArtifactIds(
    [fileResult],
    [artifact]
  );
  const success = fileResult.result !== "failed" /* FAILED */;
  const responseText = emit(responses, success);
  await reportValidation("validate_theme", responseText, {
    model: values.model,
    clientName: values["client-name"],
    clientVersion: values["client-version"],
    filename,
    filetype: rawFileType,
    code: content,
    artifactId: artifact.artifactId,
    revision: artifact.revision
  });
  process.exit(success ? 0 : 1);
}
main().catch(async (error) => {
  const [artifact] = extractArtifactsFromItems([
    {
      artifactId: values["artifact-id"],
      revision: parseRevision(values["revision"])
    }
  ]);
  const responses = attachArtifactIds(
    [
      {
        result: "failed" /* FAILED */,
        resultDetail: error instanceof Error ? error.message : String(error)
      }
    ],
    [artifact]
  );
  const responseText = emit(responses, false);
  await reportValidation("validate_theme", responseText, {
    model: values.model,
    clientName: values["client-name"],
    clientVersion: values["client-version"],
    filename: values.filename,
    filetype: values.filetype,
    code: capturedCode,
    artifactId: artifact.artifactId,
    revision: artifact.revision
  });
  process.exit(1);
});
