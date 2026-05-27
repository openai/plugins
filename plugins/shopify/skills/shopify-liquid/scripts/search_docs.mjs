#!/usr/bin/env node

// src/agent-skills/scripts/search_docs.ts
import { parseArgs } from "util";

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
          skillVersion: "1.9.0",
          ...remainingContext
        },
        result
      }),
      instrumentation: {
        packageVersion: "1.9.0",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
  } catch {
  }
}

// src/agent-skills/scripts/search_docs.ts
var { values, positionals } = parseArgs({
  options: {
    model: { type: "string" },
    "client-name": { type: "string" },
    "client-version": { type: "string" }
  },
  allowPositionals: true
});
var query = positionals[0];
if (!query) {
  console.error(
    "Usage: search_docs.js <query> [--model <id>] [--client-name <name>]"
  );
  process.exit(1);
}
async function performSearch(query2, apiName) {
  const body = { query: query2 };
  if (apiName) body.api_name = apiName;
  const responseText = await shopifyDevFetch("/assistant/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Surface": "skills"
    },
    body: JSON.stringify(body),
    instrumentation: {
      packageVersion: "1.9.0",
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    }
  });
  try {
    const jsonData = JSON.parse(responseText);
    return JSON.stringify(jsonData, null, 2);
  } catch {
    return responseText;
  }
}
try {
  const result = await performSearch(query, "liquid");
  process.stdout.write(result);
  process.stdout.write("\n");
  await reportValidation("search_docs", result, {
    model: values.model,
    clientName: values["client-name"],
    clientVersion: values["client-version"],
    query
  });
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Search failed: ${message}`);
  await reportValidation("search_docs", message, {
    model: values.model,
    clientName: values["client-name"],
    clientVersion: values["client-version"],
    query
  });
  process.exit(1);
}
