// src/record.ts
function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function asRecord(value) {
  return isRecord(value) ? value : void 0;
}

// src/deep-scan/permission-profile-preflight.ts
import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { createReadStream } from "node:fs";
import { isDeepStrictEqual } from "node:util";

// package.json
var version = "0.1.161";

// src/deep-scan/errors.ts
var DeepScanNonRetryableError = class extends Error {
  constructor(message, options) {
    super(message, options);
    this.name = "DeepScanNonRetryableError";
  }
};

// src/executable-path.ts
import { win32 } from "node:path";
function executablePathForSpawn(command) {
  if (process.platform !== "win32" || !win32.isAbsolute(command))
    return command;
  const root = win32.parse(command).root;
  return root === "\\" || root === "/" ? command : win32.toNamespacedPath(command);
}

// ../scripts/codex_profile.mjs
function isPermissionProfileFallbackWarning(message, profileId) {
  if (typeof message !== "string") return false;
  const prefix = `Configured value for \`permission_profile\` is disallowed by requirements; falling back from \`${profileId}\` to required value \``;
  const warning = message.trim();
  return warning.startsWith(prefix) && warning.endsWith("`.");
}

// src/deep-scan/permission-profile-preflight.ts
var DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID = "codex_security_deep_scan_worker";
async function readDeepScanRuntimeConfig(options, inspect) {
  return withPreflightClient(options, async (client) => {
    const response = await client.request("config/read", {
      cwd: options.configCwd ?? options.cwd,
      includeLayers: false
    });
    let config = asRecord(response.config);
    if (!config) throw malformedPreflightError(options.context);
    if (options.plugin) {
      const detail = await client.request("plugin/read", options.plugin).catch(() => void 0);
      options.signal.throwIfAborted();
      const plugin = asRecord(detail?.plugin);
      const summary = asRecord(plugin?.summary);
      const servers = plugin?.mcpServers;
      if (summary?.installed !== true || summary.enabled !== true || !Array.isArray(servers) || !servers.every((name) => typeof name === "string"))
        return void 0;
      config = {
        ...config,
        mcp_servers: {
          ...Object.fromEntries(servers.map((name) => [name, {}])),
          ...asRecord(config.mcp_servers)
        }
      };
    }
    if (!inspect) return config;
    return inspect(config, async (serverName) => {
      const result = await client.request("mcpServerStatus/list", {
        serverName,
        detail: "toolsAndAuthOnly"
      }).catch(() => void 0);
      options.signal.throwIfAborted();
      const match = Array.isArray(result?.data) ? result.data.map(asRecord).find((entry) => entry?.name === serverName) : void 0;
      const tools = asRecord(match?.tools);
      return match?.toolsError === null && tools !== void 0 && Object.keys(tools).length === 0;
    });
  });
}
async function readDeepScanRuntimeConfigWithOrigins(options) {
  return withPreflightClient(
    options,
    (client) => client.request("config/read", { cwd: options.cwd, includeLayers: true })
  );
}
async function readDeepScanParentCyberAccessProgram(options) {
  return withPreflightClient(options, async (client) => {
    let response;
    try {
      response = await client.request("thread/read", {
        threadId: options.parentTurn.threadId,
        includeTurns: false
      });
    } catch (error) {
      const nativeError = asRecord(
        error instanceof Error ? error.cause : void 0
      );
      if (nativeError?.code === -32600 && nativeError.message === `thread not loaded: ${options.parentTurn.threadId}`)
        return void 0;
      throw error;
    }
    const thread = asRecord(response.thread);
    if (thread?.id !== options.parentTurn.threadId || typeof thread.path !== "string")
      return void 0;
    const input = createReadStream(thread.path, { encoding: "utf8" });
    const lines = createInterface({ input, crlfDelay: Infinity });
    try {
      for await (const line of lines) {
        if (!line.trim()) continue;
        const entry = asRecord(JSON.parse(line));
        if (entry?.type !== "turn_context") continue;
        const context = asRecord(entry.payload);
        if (context?.turn_id !== options.parentTurn.turnId) continue;
        const program = context.cyber_access_program;
        return typeof program === "string" ? program : void 0;
      }
      return void 0;
    } finally {
      lines.close();
      input.destroy();
    }
  });
}
async function prepareCliDeepScanSession(options) {
  return withPreflightClient(options, async (client) => {
    const response = await client.request("thread/start", {
      cwd: options.cwd,
      threadSource: "security_scan",
      ephemeral: false
    });
    const thread = asRecord(response.thread);
    if (typeof thread?.id !== "string" || typeof thread.path !== "string" || typeof response.model !== "string") {
      throw new Error("Codex did not return the owning Deep Scan session.");
    }
    await client.request("thread/inject_items", {
      threadId: thread.id,
      items: [
        {
          type: "message",
          role: "user",
          content: [{ type: "input_text", text: options.prompt }]
        }
      ]
    });
    let permissionProfile;
    const input = createReadStream(thread.path, { encoding: "utf8" });
    const lines = createInterface({ input, crlfDelay: Infinity });
    try {
      for await (const line of lines) {
        if (!line.trim()) continue;
        const entry = asRecord(JSON.parse(line));
        if (entry?.type === "turn_context") {
          permissionProfile = asRecord(entry.payload)?.permission_profile;
        }
      }
    } finally {
      lines.close();
      input.destroy();
    }
    if (permissionProfile === void 0) {
      throw new Error(
        "Codex did not persist the Deep Scan session's effective permissions."
      );
    }
    return {
      threadId: thread.id,
      model: response.model,
      ...typeof response.reasoningEffort === "string" ? { reasoningEffort: response.reasoningEffort } : {},
      permissionProfile
    };
  });
}
async function preflightDeepScanWorkerPermissionProfile(options) {
  return withPreflightClient(options, async (client) => {
    const configResponse = await client.request("config/read", {
      cwd: options.cwd,
      includeLayers: false
    });
    const catalog = await client.readPermissionProfileCatalog(options.cwd);
    const matchingEntries = catalog.filter(
      (entry) => entry.id === DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID
    );
    if (matchingEntries.length !== 1)
      throw malformedPreflightError(options.context);
    const catalogEntry = matchingEntries[0];
    const requirementsResponse = catalogEntry.allowed === true ? void 0 : await client.readConfigRequirementsForClassification();
    verifyPreflightResult(
      options,
      configResponse,
      catalogEntry,
      requirementsResponse
    );
    const config = asRecord(configResponse.config);
    const mcpServerNames = Object.keys(asRecord(config?.mcp_servers) ?? {});
    if (!options.allowOpenAiApiKeyFallback || config?.forced_login_method === "chatgpt") {
      return { useOpenAiApiKey: false, mcpServerNames };
    }
    const account = await client.request("account/read", {
      refreshToken: false
    });
    return {
      mcpServerNames,
      useOpenAiApiKey: account.requiresOpenaiAuth === true && account.account === null
    };
  });
}
async function withPreflightClient(options, operation) {
  if (options.signal.aborted)
    throw abortError(options.signal.reason, options.context);
  const client = new AppServerPreflightClient(options);
  try {
    await client.initialize();
    return await operation(client);
  } catch (error) {
    await client.close();
    const stderr = client.stderrText;
    if (error instanceof Error && stderr)
      Object.defineProperty(error, "message", {
        value: error.message + "\n" + stderr,
        writable: true,
        configurable: true,
        enumerable: false
      });
    throw error;
  } finally {
    await client.close();
  }
}
var AppServerPreflightClient = class {
  constructor(options) {
    this.options = options;
    const args = [
      ...options.appServerArgs ?? options.commandArgs ?? []
    ];
    if (options.appServerArgs === void 0) {
      for (const override of options.configOverrides) {
        args.push("--config", override);
      }
      for (const override of options.providerConfigOverrides ?? []) {
        args.push("--config", override);
      }
      args.push("app-server", "--stdio");
      if (options.configCwd !== void 0) args.push("--cd", options.configCwd);
    }
    this.child = spawn(executablePathForSpawn(options.codexPath), args, {
      cwd: options.cwd,
      ...options.env === void 0 ? {} : { env: options.env },
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true
    });
    this.childClose = new Promise((resolve) => {
      this.child.once("close", () => {
        this.childClosed = true;
        resolve();
      });
    });
    this.child.stderr.on("data", (chunk) => this.stderr.push(chunk));
    this.stdoutLines = createInterface({
      input: this.child.stdout,
      crlfDelay: Infinity
    });
    this.stdoutLines.on("line", (line) => this.consumeStdoutLine(line));
    this.stdoutLines.on("error", this.onStdioError);
    this.child.stdin.on("error", this.onStdioError);
    this.child.on("error", (error) => {
      this.fail(
        codexExecutableStartError(options.codexPath, error, options.context)
      );
    });
    this.child.on("close", (code, signal) => {
      if (!this.closed) {
        this.fail(
          codexExecutableExitError(
            options.codexPath,
            code,
            signal,
            options.context
          )
        );
      }
    });
    const onAbort = () => {
      this.fail(abortError(options.signal.reason, options.context));
      this.stopChild();
    };
    options.signal.addEventListener("abort", onAbort, { once: true });
    this.removeAbortListener = () => options.signal.removeEventListener("abort", onAbort);
  }
  options;
  child;
  childClose;
  stdoutLines;
  pending;
  nextId = 1;
  stderr = [];
  terminalError;
  closed = false;
  childClosed = false;
  removeAbortListener;
  onStdioError = (error) => {
    const failure = codexExecutableStdioError(
      this.options.codexPath,
      this.options.context
    );
    failure.message += "\n" + error.message;
    this.fail(failure);
  };
  get stderrText() {
    return Buffer.concat(this.stderr).toString("utf8");
  }
  async initialize() {
    await this.request("initialize", {
      clientInfo: {
        name: "codex_security_deep_scan",
        title: "Codex Security Deep Scan",
        version
      },
      capabilities: { experimentalApi: true }
    });
    if (this.terminalError) throw this.terminalError;
    this.write({ jsonrpc: "2.0", method: "initialized", params: {} });
  }
  async readPermissionProfileCatalog(cwd) {
    const entries = [];
    const seenCursors = /* @__PURE__ */ new Set();
    let cursor;
    while (true) {
      const result = await this.request("permissionProfile/list", {
        cwd,
        ...cursor === void 0 ? {} : { cursor }
      });
      const data = result.data;
      if (!Array.isArray(data))
        throw malformedPreflightError(this.options.context);
      for (const value of data) {
        const entry = asRecord(value);
        if (!entry || typeof entry.id !== "string") {
          throw malformedPreflightError(this.options.context);
        }
        if (typeof entry.allowed !== "boolean")
          throw malformedPreflightError(this.options.context);
        entries.push(entry);
      }
      const nextCursor = result.nextCursor;
      if (nextCursor === null) return entries;
      if (typeof nextCursor !== "string" || nextCursor.length === 0 || seenCursors.has(nextCursor)) {
        throw malformedPreflightError(this.options.context);
      }
      seenCursors.add(nextCursor);
      cursor = nextCursor;
    }
  }
  /**
   * Classification is best effort after the catalog already rejected the
   * profile. An older runtime may not expose this API; that is still a safe
   * generic managed-policy rejection, not a reason to guess at remediation.
   */
  async readConfigRequirementsForClassification() {
    try {
      return await this.request("configRequirements/read");
    } catch (error) {
      if (this.options.signal.aborted || isAbortError(error)) throw error;
      return void 0;
    }
  }
  request(method, params) {
    if (this.terminalError) return Promise.reject(this.terminalError);
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending = { id, method, resolve, reject };
      this.write({
        jsonrpc: "2.0",
        id,
        method,
        ...params === void 0 ? {} : { params }
      });
    });
  }
  async close() {
    this.closed = true;
    this.removeAbortListener();
    this.stopChild();
    if (this.childClosed) return;
    const forcedTermination = setTimeout(() => {
      if (this.child.exitCode === null && this.child.signalCode === null) {
        this.child.kill("SIGKILL");
      }
      this.child.stdin.destroy();
      this.child.stdout.destroy();
      this.child.stderr.destroy();
    }, 1e3);
    try {
      await this.childClose;
    } finally {
      clearTimeout(forcedTermination);
    }
  }
  write(message) {
    if (!this.child.stdin.writable) {
      this.fail(
        codexExecutableStdioError(this.options.codexPath, this.options.context)
      );
      return;
    }
    this.child.stdin.write(`${JSON.stringify(message)}
`, (error) => {
      if (error) this.onStdioError(error);
    });
  }
  consumeStdoutLine(line) {
    if (this.terminalError || line.trim().length === 0) return;
    let value;
    try {
      value = JSON.parse(line);
    } catch {
      this.fail(malformedPreflightError(this.options.context));
      return;
    }
    const message = asRecord(value);
    if (!message) {
      this.fail(malformedPreflightError(this.options.context));
      return;
    }
    const id = message.id;
    if (typeof id !== "number") {
      return;
    }
    const pending = this.pending;
    if (!pending || pending.id !== id) {
      this.fail(malformedPreflightError(this.options.context));
      return;
    }
    this.pending = void 0;
    if (message.error !== void 0) {
      pending.reject(
        jsonRpcPreflightError(
          this.options.codexPath,
          pending.method,
          message.error,
          this.options.context
        )
      );
      return;
    }
    const result = asRecord(message.result);
    if (!result) {
      pending.reject(malformedPreflightError(this.options.context));
      return;
    }
    pending.resolve(result);
  }
  fail(error) {
    if (this.terminalError) return;
    this.terminalError = error;
    this.pending?.reject(error);
    this.pending = void 0;
  }
  stopChild() {
    this.stdoutLines.close();
    if (!this.child.stdin.destroyed) this.child.stdin.end();
    if (this.child.exitCode === null && this.child.signalCode === null) {
      this.child.kill("SIGTERM");
    }
  }
};
function verifyPreflightResult(options, configResponse, catalogEntry, requirementsResponse) {
  if (catalogEntry.allowed !== true) {
    throw existingAllowlistExcludesProfile(requirementsResponse) ? disallowedProfileAllowlistError(options.context) : managedPolicyRejectedError(options.context);
  }
  const config = asRecord(configResponse.config);
  const permissions = asRecord(config?.permissions);
  const actualProfile = permissions ? asRecord(permissions[DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID]) : void 0;
  if (!config || !permissions || !actualProfile || typeof config.default_permissions !== "string")
    throw malformedPreflightError(options.context);
  if (config.default_permissions !== DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID) {
    throw profileNotSelectedError(options.context);
  }
  const expectedProfile = comparableProfile(options.expectedProfile);
  const actualWithoutDescription = comparableProfile(actualProfile);
  if (!isDeepStrictEqual(actualWithoutDescription, expectedProfile)) {
    throw profileCollisionError(options.context);
  }
}
function existingAllowlistExcludesProfile(response) {
  if (!response || !Object.hasOwn(response, "requirements")) return false;
  if (response.requirements === null) return false;
  const requirements = asRecord(response.requirements);
  if (!requirements || !Object.hasOwn(requirements, "allowedPermissionProfiles"))
    return false;
  if (requirements.allowedPermissionProfiles === null) return false;
  const allowlist = asRecord(requirements.allowedPermissionProfiles);
  if (!allowlist) return false;
  if (Object.values(allowlist).some((value) => typeof value !== "boolean"))
    return false;
  return allowlist[DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID] !== true;
}
function comparableProfile(value) {
  const { description: _description, ...rest } = stripNullObjectFields(
    value
  );
  return rest;
}
function stripNullObjectFields(value) {
  if (Array.isArray(value))
    return value.map((entry) => stripNullObjectFields(entry));
  const object = asRecord(value);
  if (!object) return value;
  return Object.fromEntries(
    Object.entries(object).filter(([, entry]) => entry !== null).map(([key, entry]) => [key, stripNullObjectFields(entry)])
  );
}
function disallowedProfileAllowlistError(context) {
  return new DeepScanNonRetryableError(
    `${subject(context)} cannot safely start a read-only worker because organization policy does not allow the required \`${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}\` permission profile. Ask your Codex administrator to define this read-only stub in a normal config layer:

[permissions.${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}]
extends = ":read-only"

and add this entry to your existing allowlist in requirements.toml:

[allowed_permission_profiles]
${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID} = true

${subject(context)} did not run.`
  );
}
function managedPolicyRejectedError(context) {
  return new DeepScanNonRetryableError(
    `${subject(context)} cannot safely start a read-only worker because managed Codex policy rejected the required \`${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}\` permission profile. Ask your Codex administrator to review the managed permission, sandbox, and filesystem requirements. ${subject(context)} did not run.`
  );
}
function profileNotSelectedError(context) {
  return new DeepScanNonRetryableError(
    `${subject(context)} cannot safely start a read-only worker because Codex did not select the required \`${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}\` permission profile. Ask your Codex administrator to allow that profile for ${subject(context)}. ${subject(context)} did not run.`
  );
}
function profileCollisionError(context) {
  return new DeepScanNonRetryableError(
    `${subject(context)} cannot safely start a read-only worker because existing Codex configuration changes the reserved \`${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}\` permission profile. Ask your Codex administrator to keep the normal-config \`[permissions.${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}]\` stub limited to \`extends = ":read-only"\`; ${subject(context)} supplies its deny rules at runtime. ${subject(context)} did not run.`
  );
}
function failedOperation(context) {
  return context === "parent-config" ? "Could not read the Deep Scan parent configuration" : `${subject(context)} cannot safely verify its read-only worker permission profile`;
}
function malformedPreflightError(context) {
  return new Error(
    context === "parent-config" ? `${failedOperation(context)}. Codex returned an invalid app-server response.` : `${failedOperation(context)} with this Codex configuration. ${subject(context)} did not run.`
  );
}
function unsupportedCodexApiError(codexPath, api, context) {
  return new DeepScanNonRetryableError(
    failedOperation(context) + " because the selected Codex executable " + JSON.stringify(codexPath) + " does not support the required " + JSON.stringify(api) + " API. Update the Codex installation at that path (the desktop app if it is bundled, otherwise the selected CLI) and retry. " + subject(context) + " did not run."
  );
}
function jsonRpcPreflightError(codexPath, method, value, context) {
  const error = asRecord(value);
  const code = typeof error?.code === "number" && Number.isFinite(error.code) ? error.code : void 0;
  if (code === -32601) {
    const failure = unsupportedCodexApiError(codexPath, method, context);
    if (typeof error?.message === "string")
      failure.message += "\n" + error.message;
    return failure;
  }
  return new Error(
    failedOperation(context) + " because the selected Codex executable " + JSON.stringify(codexPath) + " returned an error for " + JSON.stringify(method) + (code === void 0 ? "" : " (JSON-RPC code " + code + ")") + ". Check the Codex configuration and retry. " + subject(context) + " did not run." + (typeof error?.message === "string" ? "\n" + error.message : ""),
    { cause: value }
  );
}
function codexExecutableStartError(codexPath, error, context) {
  const value = "code" in error ? error.code : void 0;
  const code = typeof value === "string" && /^[A-Z0-9_]+$/u.test(value) ? value : void 0;
  const codeDetail = code === void 0 ? "" : " (" + code + ")";
  return new Error(
    codexExecutableFailureMessage(
      codexPath,
      "could not start" + codeDetail,
      context
    ) + "\n" + error.message,
    { cause: error }
  );
}
function codexExecutableExitError(codexPath, code, signal, context) {
  const operation = context === "parent-config" ? "the configuration read" : "permission-profile verification";
  const detail = code !== null ? `exited before ${operation} completed with code ${code}` : signal !== null ? `was terminated before ${operation} completed by signal ${signal}` : `exited before ${operation} completed`;
  return new Error(codexExecutableFailureMessage(codexPath, detail, context));
}
function codexExecutableStdioError(codexPath, context) {
  return new Error(
    codexExecutableFailureMessage(
      codexPath,
      "could not exchange app-server JSON-RPC over stdio",
      context
    )
  );
}
function codexExecutableFailureMessage(codexPath, detail, context) {
  if (context === "parent-config")
    return `${failedOperation(context)}. Codex executable ${JSON.stringify(codexPath)} ${detail}.`;
  return subject(context) + " cannot safely verify its read-only worker permission profile because the selected Codex executable " + JSON.stringify(codexPath) + " " + detail + ". Check that the named executable runs with --version, and check CODEX_CLI_PATH/PATH, then retry. " + subject(context) + " did not run.";
}
function deepScanPermissionProfileFallbackError(message) {
  if (typeof message !== "string") return void 0;
  if (!isPermissionProfileFallbackWarning(
    message,
    DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID
  ))
    return void 0;
  return new DeepScanNonRetryableError(
    `Deep Scan stopped a worker because organization policy rejected the required \`${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}\` permission profile after the turn started. The worker was stopped and its results were discarded. Ask your Codex administrator to define this read-only stub in a normal config layer:

[permissions.${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID}]
extends = ":read-only"

and add this entry to your existing allowlist in requirements.toml:

[allowed_permission_profiles]
${DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID} = true
${message}`
  );
}
function subject(context) {
  return context === "helper" ? "Read-only Codex helper" : "Deep Scan";
}
function isAbortError(error) {
  return error instanceof Error && error.name === "AbortError";
}
function abortError(reason, context) {
  if (reason instanceof Error) return reason;
  return new DOMException(
    context === "parent-config" ? "Deep Scan parent configuration read aborted." : "Deep Scan worker permission profile preflight aborted.",
    "AbortError"
  );
}
export {
  DEEP_SCAN_WORKER_PERMISSION_PROFILE_ID,
  deepScanPermissionProfileFallbackError,
  preflightDeepScanWorkerPermissionProfile,
  prepareCliDeepScanSession,
  readDeepScanParentCyberAccessProgram,
  readDeepScanRuntimeConfig,
  readDeepScanRuntimeConfigWithOrigins
};
