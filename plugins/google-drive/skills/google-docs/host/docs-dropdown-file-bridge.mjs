/* Dependency-free file bridge for the Google Docs dropdown executor. */

const HASH_RE = /^[a-f0-9]{64}$/;
const TRUSTED_EXECUTOR_PATH = decodeURIComponent(new URL("./docs-dropdown-executor.mjs", import.meta.url).pathname);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'"'"'`)}'`;
}

function normalizePath(path) {
  assert(typeof path === "string" && path.startsWith("/"), "Bridge paths must be absolute");
  assert(!path.split("/").includes(".."), "Bridge paths must not contain ..");
  return path.replace(/\/+$/, "") || "/";
}

function assertWithin(root, path) {
  const normalizedRoot = normalizePath(root);
  const normalizedPath = normalizePath(path);
  assert(normalizedPath === normalizedRoot || normalizedPath.startsWith(`${normalizedRoot}/`), `${normalizedPath} is outside workspace root ${normalizedRoot}`);
  return normalizedPath;
}

function resolveTool(tools, names) {
  for (const name of names) if (typeof tools[name] === "function") return tools[name];
  throw new Error(`Required mounted tool is unavailable: ${names.join(", ")}`);
}

async function defaultIo(tools) {
  const exec = resolveTool(tools, ["exec_command", "mcp__exec_command"]);
  const patch = resolveTool(tools, ["apply_patch", "mcp__apply_patch"]);
  return {
    async exists(path) {
      const result = await exec({ cmd: `/usr/bin/test -e ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 1000 });
      return result.exit_code === 0;
    },
    async mkdir(path) {
      const result = await exec({ cmd: `/bin/mkdir -p ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 1000 });
      assert(result.exit_code === 0, `Could not create bridge directory: ${result.output ?? ""}`);
      const protectedResult = await exec({ cmd: `/bin/chmod 700 ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 1000 });
      assert(protectedResult.exit_code === 0, `Could not protect bridge directory: ${protectedResult.output ?? ""}`);
    },
    async readText(path) {
      const result = await exec({ cmd: `/bin/cat ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 100000 });
      assert(result.exit_code === 0, `Could not read ${path}: ${result.output ?? ""}`);
      return result.output;
    },
    async sha256(path) {
      const result = await exec({ cmd: `/usr/bin/shasum -a 256 ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 1000 });
      assert(result.exit_code === 0, `Could not hash ${path}: ${result.output ?? ""}`);
      const hash = String(result.output ?? "").trim().split(/\s+/)[0];
      assert(HASH_RE.test(hash), `Invalid SHA-256 output for ${path}`);
      return hash;
    },
    async writeNew(path, text) {
      assert(!(await this.exists(path)), `Refusing to overwrite ${path}`);
      const body = String(text).split("\n").map((line) => `+${line}`).join("\n");
      await patch(`*** Begin Patch\n*** Add File: ${path}\n${body}\n*** End Patch`);
      const result = await exec({ cmd: `/bin/chmod 600 ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 1000 });
      assert(result.exit_code === 0, `Could not protect ${path}: ${result.output ?? ""}`);
    },
    async seal(path) {
      const result = await exec({ cmd: `/bin/chmod -R a-w ${shellQuote(path)}`, workdir: "/", yield_time_ms: 1000, max_output_tokens: 1000 });
      assert(result.exit_code === 0, `Could not seal ${path}: ${result.output ?? ""}`);
    },
  };
}

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Invalid JSON in ${label}: ${error.message}`);
  }
}

function loadExecutor(source) {
  assert(typeof source === "string" && source.includes("executeDocsDropdownPlan"), "Executor source is incomplete");
  const normalized = source.replace(/^\s*export\s+/gm, "");
  return new Function(`${normalized}\nreturn { executeDocsDropdownPlan, reconcileUnknownDropdownMutation };`)();
}

function checkpointFileName(checkpoint, index) {
  const safe = String(checkpoint.phase ?? checkpoint.capability ?? `checkpoint-${index}`).replace(/[^a-zA-Z0-9_-]+/g, "-");
  return `${String(index + 1).padStart(2, "0")}-${safe}.json`;
}

async function persistResult(io, outputDir, execution, error = null) {
  const checkpoints = execution?.checkpoints ?? error?.checkpoints ?? [];
  const files = [];
  for (const [index, checkpoint] of checkpoints.entries()) {
    const path = `${outputDir}/${checkpointFileName(checkpoint, index)}`;
    await io.writeNew(path, `${JSON.stringify(checkpoint.result ?? checkpoint, null, 2)}\n`);
    files.push({ kind: "checkpoint", phase: checkpoint.phase ?? null, path });
  }
  const receipt = execution?.receipt ?? error?.receipt ?? {
    receiptVersion: 1,
    kind: "google-docs-v2-dropdown-execution",
    status: "bridge_failed",
    error: {
      name: error?.name ?? "Error",
      message: "Bridge validation or execution failed; inspect protected stage artifacts.",
    },
  };
  const receiptPath = `${outputDir}/receipt.json`;
  await io.writeNew(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`);
  files.push({ kind: "receipt", path: receiptPath });
  return { receipt, files };
}

export async function executeDocsDropdownPlanFromFiles({
  workspaceRoot,
  planPath,
  validationPath,
  contractPath,
  executionContextPath,
  executorPath,
  outputDir,
  tools,
  capabilityOverrides = {},
  io: ioOverride = null,
} = {}) {
  const root = normalizePath(workspaceRoot);
  const paths = {
    planPath: assertWithin(root, planPath),
    validationPath: assertWithin(root, validationPath),
    contractPath: assertWithin(root, contractPath),
    executionContextPath: assertWithin(root, executionContextPath),
    outputDir: assertWithin(root, outputDir),
  };
  const normalizedExecutorPath = normalizePath(executorPath);
  assert(normalizedExecutorPath === TRUSTED_EXECUTOR_PATH, "Only the checked-in Google Docs dropdown executor is trusted");
  const io = ioOverride ?? await defaultIo(tools);
  assert(!(await io.exists(paths.outputDir)), `Output directory already exists: ${paths.outputDir}`);
  await io.mkdir(paths.outputDir);

  let execution = null;
  let caught = null;
  try {
    const [planText, validationText, contractText, contextText, executorSource] = await Promise.all([
      io.readText(paths.planPath),
      io.readText(paths.validationPath),
      io.readText(paths.contractPath),
      io.readText(paths.executionContextPath),
      io.readText(normalizedExecutorPath),
    ]);
    const plan = parseJson(planText, paths.planPath);
    const validation = parseJson(validationText, paths.validationPath);
    const contract = parseJson(contractText, paths.contractPath);
    const context = parseJson(contextText, paths.executionContextPath);
    assert(context.version === 1 && context.kind === "google-docs-v2-dropdown-execution-context", "Invalid execution context");
    assert(context.workspaceRoot === root, "Execution context workspace root mismatch");
    assert(context.targetDocumentId === plan.target?.documentId, "Execution context target mismatch");
    assert(context.executorPath === normalizedExecutorPath, "Execution context executor path mismatch");
    const hashes = await Promise.all([
      io.sha256(paths.planPath),
      io.sha256(paths.validationPath),
      io.sha256(paths.contractPath),
      io.sha256(normalizedExecutorPath),
    ]);
    assert(validation.planFileSha256 === hashes[0], "Plan file hash mismatch");
    assert(validation.contractFileSha256 === hashes[2], "Contract file hash mismatch");
    assert(validation.executorFileSha256 === hashes[3], "Executor file hash mismatch");
    assert(HASH_RE.test(hashes[1]), "Validation file hash is invalid");
    const executor = loadExecutor(executorSource);
    execution = await executor.executeDocsDropdownPlan({ plan, contract, validation, tools, capabilityOverrides });
  } catch (error) {
    caught = error;
  }

  const persisted = await persistResult(io, paths.outputDir, execution, caught);
  const manifest = {
    manifestVersion: 1,
    kind: "google-docs-v2-dropdown-bridge-manifest",
    status: persisted.receipt.status,
    stageId: persisted.receipt.stageId ?? null,
    stageType: persisted.receipt.stageType ?? null,
    hashes: persisted.receipt.hashes ?? null,
    outputDir: paths.outputDir,
    receiptPath: `${paths.outputDir}/receipt.json`,
    files: persisted.files,
    checkpointCount: persisted.files.filter((file) => file.kind === "checkpoint").length,
    error: caught ? { name: caught.name ?? "Error", message: String(caught.message ?? caught) } : null,
    sanitized: true,
  };
  if (manifest.error) manifest.error.message = "Bridge execution failed; inspect the protected receipt and checkpoints.";
  const manifestPath = `${paths.outputDir}/manifest.json`;
  await io.writeNew(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  if (typeof io.seal === "function") await io.seal(paths.outputDir);
  if (caught) {
    const error = new Error("Google Docs dropdown bridge execution failed");
    error.manifest = manifest;
    throw error;
  }
  return { ...manifest, manifestPath };
}
