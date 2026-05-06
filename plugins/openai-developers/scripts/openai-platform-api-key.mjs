#!/usr/bin/env node

import { randomUUID, webcrypto } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const { subtle } = webcrypto;
const ENCRYPTED_API_KEY_VERSION = 1;
const DEFAULT_ENV_NAME = "OPENAI_API_KEY";
const BASE64URL_PATTERN = /^[A-Za-z0-9_-]+$/;
const SAFE_OPENAI_API_KEY_PATTERN = /^sk-[A-Za-z0-9_-]+$/;
const OPTIONS_WITH_VALUES = new Set([
  "ciphertext",
  "dir",
  "encrypted-result",
  "env-name",
  "name",
  "private-key",
  "target",
  "workspace",
]);
const VALID_OPTIONS = new Set(OPTIONS_WITH_VALUES);
const OPTIONS_ALLOWING_DASH_VALUES = new Set(["ciphertext"]);

function usage() {
  return `Usage:
  openai-platform-api-key.mjs prepare [--name <key name>] [--dir <state dir>]
  openai-platform-api-key.mjs decrypt --private-key <path> --target <path> (--ciphertext <value> | --encrypted-result <path>) [--env-name OPENAI_API_KEY] [--workspace <repo root>]

Commands:
  prepare   Generate a local RSA-OAEP keypair and public connector request.
  decrypt   Decrypt connector ciphertext locally and upsert an env var file.

The helper never prints the plaintext API key.`;
}

function fail(message, code = 1) {
  process.stderr.write(`${message}\n`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith("--")) {
      args._.push(arg);
      continue;
    }
    const key = arg.slice(2);
    if (!VALID_OPTIONS.has(key)) {
      fail(`Unknown option: --${key}.`);
    }
    const value = argv[index + 1];
    if (OPTIONS_WITH_VALUES.has(key)) {
      if (value == null) {
        fail(`Missing value for --${key}.`);
      }
      if (value.startsWith("--") && !OPTIONS_ALLOWING_DASH_VALUES.has(key)) {
        fail(`Missing value for --${key}.`);
      }
      args[key] = value;
      index += 1;
      continue;
    }
  }
  return args;
}

function printJson(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

function ensureUsableNodeCrypto() {
  if (subtle == null) {
    fail("This helper requires Node.js WebCrypto support.");
  }
}

function resolveOutputDir(rawDir) {
  if (rawDir) {
    const dir = path.resolve(String(rawDir));
    fs.mkdirSync(dir, { mode: 0o700, recursive: true });
    chmodBestEffort(dir, 0o700);
    return dir;
  }
  return fs.mkdtempSync(path.join(os.tmpdir(), "codex-openai-platform-"));
}

function chmodBestEffort(target, mode) {
  try {
    fs.chmodSync(target, mode);
  } catch {
    // Best effort only; chmod is not available on every filesystem.
  }
}

function unlinkBestEffort(target) {
  try {
    fs.unlinkSync(target);
  } catch {
    // Best effort cleanup for temporary files.
  }
}

const NOFOLLOW_OPEN_FLAG = fs.constants.O_NOFOLLOW ?? 0;

function isPathInside(parent, child) {
  const relative = path.relative(parent, child);
  return (
    relative === "" ||
    (relative !== ".." &&
      !relative.startsWith(`..${path.sep}`) &&
      !path.isAbsolute(relative))
  );
}

function realpathSyncOrFail(filePath, label) {
  try {
    return fs.realpathSync(filePath);
  } catch (error) {
    fail(`Failed to resolve ${label}: ${error.message}`);
  }
}

function statDirectoryOrFail(filePath, label) {
  let stat;
  try {
    stat = fs.statSync(filePath);
  } catch (error) {
    fail(`Failed to access ${label}: ${error.message}`);
  }
  if (!stat.isDirectory()) {
    fail(`${label} is not a directory: ${filePath}`);
  }
}

function resolveWorkspaceRoot(rawWorkspace) {
  const workspacePath = path.resolve(rawWorkspace || process.cwd());
  statDirectoryOrFail(workspacePath, "Workspace");
  return {
    requested_path: workspacePath,
    real_path: realpathSyncOrFail(workspacePath, "workspace"),
  };
}

function resolveSafeTarget(targetPath, workspace) {
  const resolvedTarget = path.isAbsolute(targetPath)
    ? path.resolve(targetPath)
    : path.resolve(workspace.requested_path, targetPath);
  const parentPath = path.dirname(resolvedTarget);
  statDirectoryOrFail(parentPath, "Target parent directory");
  const parentRealPath = realpathSyncOrFail(parentPath, "target parent directory");

  if (!isPathInside(workspace.real_path, parentRealPath)) {
    fail(
      `Target env file must be inside the workspace. Workspace: ${workspace.real_path}. Target: ${resolvedTarget}`,
    );
  }

  return path.join(parentRealPath, path.basename(resolvedTarget));
}

function lstatTarget(filePath) {
  try {
    return fs.lstatSync(filePath);
  } catch (error) {
    if (error.code === "ENOENT") {
      return null;
    }
    fail(`Failed to inspect target env file: ${error.message}`);
  }
}

function validateTargetFileType(filePath, stat) {
  if (stat == null) {
    return;
  }
  if (stat.isSymbolicLink()) {
    fail(`Refusing to write API key through symlink target: ${filePath}`);
  }
  if (!stat.isFile()) {
    fail(`Refusing to write API key to non-file target: ${filePath}`);
  }
  if (stat.nlink > 1) {
    fail(`Refusing to write API key to hard-linked target: ${filePath}`);
  }
}

function openNoFollow(filePath, flags, mode, action) {
  try {
    return fs.openSync(filePath, flags | NOFOLLOW_OPEN_FLAG, mode);
  } catch (error) {
    if (error.code === "ELOOP") {
      fail(`Refusing to ${action} symlink target: ${filePath}`);
    }
    if (error.code === "EEXIST") {
      fail(`Target env file changed while writing; refusing to overwrite: ${filePath}`);
    }
    fail(`Failed to ${action} target env file safely: ${error.message}`);
  }
}

function readFileNoFollow(filePath) {
  const fd = openNoFollow(filePath, fs.constants.O_RDONLY, undefined, "read");
  let contents = "";
  let failure = null;
  try {
    const stat = fs.fstatSync(fd);
    if (!stat.isFile()) {
      failure = `Refusing to read non-file target env file: ${filePath}`;
    } else {
      contents = fs.readFileSync(fd, "utf8");
    }
  } catch (error) {
    failure = `Failed to read target env file safely: ${error.message}`;
  } finally {
    fs.closeSync(fd);
  }
  if (failure) {
    fail(failure);
  }
  return contents;
}

function writeFileNoFollow(filePath, contents) {
  const tempPath = path.join(
    path.dirname(filePath),
    `.${path.basename(filePath)}.${process.pid}.${randomUUID()}.tmp`,
  );
  const flags = fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL;
  const fd = openNoFollow(tempPath, flags, 0o600, "create temporary");
  let failure = null;
  try {
    const stat = fs.fstatSync(fd);
    if (!stat.isFile()) {
      failure = `Refusing to write API key to non-file temporary target: ${tempPath}`;
    } else {
      fs.writeFileSync(fd, contents, { encoding: "utf8" });
    }
  } catch (error) {
    failure = `Failed to write target env file safely: ${error.message}`;
  } finally {
    fs.closeSync(fd);
  }
  if (failure) {
    unlinkBestEffort(tempPath);
    fail(failure);
  }

  try {
    fs.renameSync(tempPath, filePath);
  } catch (error) {
    unlinkBestEffort(tempPath);
    fail(`Failed to replace target env file safely: ${error.message}`);
  }
  chmodBestEffort(filePath, 0o600);
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, {
    encoding: "utf8",
    flag: "wx",
    mode: 0o600,
  });
  chmodBestEffort(filePath, 0o600);
}

function minimalPublicJwk(publicJwk) {
  if (publicJwk.kty !== "RSA" || !publicJwk.n || !publicJwk.e) {
    fail("Generated keypair did not produce an RSA public JWK.");
  }
  return {
    kty: "RSA",
    n: publicJwk.n,
    e: publicJwk.e,
  };
}

async function prepare(args) {
  ensureUsableNodeCrypto();

  const name = typeof args.name === "string" && args.name.trim() ? args.name.trim() : "Codex";
  const outputDir = resolveOutputDir(args.dir);
  const privateKeyPath = path.join(outputDir, "recipient-private-key.jwk.json");
  const requestPath = path.join(outputDir, "connector-request.json");

  const keyPair = await subtle.generateKey(
    {
      name: "RSA-OAEP",
      modulusLength: 4096,
      publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
      hash: "SHA-256",
    },
    true,
    ["encrypt", "decrypt"],
  );

  const publicJwk = minimalPublicJwk(await subtle.exportKey("jwk", keyPair.publicKey));
  const privateJwk = await subtle.exportKey("jwk", keyPair.privateKey);
  const request = {
    recipient_public_key_jwk: publicJwk,
    name,
  };

  writeJson(privateKeyPath, privateJwk);
  writeJson(requestPath, request);

  printJson({
    request_path: requestPath,
    private_key_path: privateKeyPath,
    recipient_public_key_jwk: publicJwk,
    name,
  });
}

function readJson(filePath, label) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    fail(`Failed to read ${label}: ${error.message}`);
  }
}

function encryptedPayloadFromArgs(args) {
  if (typeof args.ciphertext === "string") {
    return {
      version: ENCRYPTED_API_KEY_VERSION,
      ciphertext: args.ciphertext,
    };
  }

  if (typeof args["encrypted-result"] === "string") {
    const raw = readJson(path.resolve(args["encrypted-result"]), "encrypted result JSON");
    const payload =
      raw?.encrypted_api_key ??
      raw?.structuredContent?.encrypted_api_key ??
      raw?.structured_content?.encrypted_api_key;
    if (payload && typeof payload === "object") {
      return payload;
    }
  }

  fail("Provide --ciphertext or --encrypted-result.");
}

function base64urlToBytes(value) {
  if (
    typeof value !== "string" ||
    !BASE64URL_PATTERN.test(value) ||
    value.length % 4 === 1
  ) {
    fail("Encrypted ciphertext must be base64url.");
  }
  return Buffer.from(value, "base64url");
}

async function decryptPayload(privateKeyPath, encryptedPayload) {
  ensureUsableNodeCrypto();

  if (encryptedPayload.version !== ENCRYPTED_API_KEY_VERSION) {
    fail(`Unsupported encrypted API key version: ${encryptedPayload.version}`);
  }

  const privateJwk = readJson(privateKeyPath, "private key JWK");
  const privateKey = await subtle.importKey(
    "jwk",
    privateJwk,
    {
      name: "RSA-OAEP",
      hash: "SHA-256",
    },
    false,
    ["decrypt"],
  );

  try {
    const plaintext = await subtle.decrypt(
      {
        name: "RSA-OAEP",
      },
      privateKey,
      base64urlToBytes(encryptedPayload.ciphertext),
    );
    return new TextDecoder().decode(plaintext);
  } catch {
    fail("Failed to decrypt encrypted API key.");
  }
}

function validateEnvName(envName) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(envName)) {
    fail(`Invalid env var name: ${envName}`);
  }
}

function validateOpenAIApiKey(value) {
  if (!SAFE_OPENAI_API_KEY_PATTERN.test(value)) {
    fail("Decrypted API key is not a safe OpenAI API key literal.");
  }
}

function upsertEnvValue(targetPath, envName, value, workspacePath) {
  validateEnvName(envName);
  validateOpenAIApiKey(value);

  const workspace = resolveWorkspaceRoot(workspacePath);
  const resolvedTarget = resolveSafeTarget(targetPath, workspace);
  const targetStat = lstatTarget(resolvedTarget);
  validateTargetFileType(resolvedTarget, targetStat);

  const existed = targetStat != null;
  const original = existed ? readFileNoFollow(resolvedTarget) : "";
  const newline = original.includes("\r\n") ? "\r\n" : "\n";
  const lines = original.length > 0 ? original.split(/\r?\n/) : [];
  let updatedExisting = false;
  const envPattern = new RegExp(`^(export\\s+)?${envName}=`);

  const updatedLines = lines.map((line) => {
    const match = line.match(envPattern);
    if (match) {
      updatedExisting = true;
      return `${match[1] ?? ""}${envName}=${value}`;
    }
    return line;
  });

  let nextContent;
  if (updatedExisting) {
    nextContent = updatedLines.join(newline);
  } else if (original.length === 0) {
    nextContent = `${envName}=${value}${newline}`;
  } else if (original.endsWith("\n")) {
    nextContent = `${original}${envName}=${value}${newline}`;
  } else {
    nextContent = `${original}${newline}${envName}=${value}${newline}`;
  }

  writeFileNoFollow(resolvedTarget, nextContent);

  return {
    target_path: resolvedTarget,
    env_name: envName,
    existed,
    updated_existing: updatedExisting,
  };
}

async function decrypt(args) {
  if (typeof args["private-key"] !== "string") {
    fail("Missing --private-key.");
  }
  if (typeof args.target !== "string") {
    fail("Missing --target.");
  }

  const envName =
    typeof args["env-name"] === "string" && args["env-name"].trim()
      ? args["env-name"].trim()
      : DEFAULT_ENV_NAME;
  const workspacePath =
    typeof args.workspace === "string" && args.workspace.trim()
      ? args.workspace.trim()
      : process.cwd();
  const encryptedPayload = encryptedPayloadFromArgs(args);
  const plaintextApiKey = await decryptPayload(path.resolve(args["private-key"]), encryptedPayload);
  const writeResult = upsertEnvValue(args.target, envName, plaintextApiKey, workspacePath);

  printJson({
    ...writeResult,
    wrote_plaintext_to_stdout: false,
  });
}

async function main() {
  const [command, ...rest] = process.argv.slice(2);
  if (command == null || command === "--help" || command === "-h") {
    process.stdout.write(`${usage()}\n`);
    return;
  }

  const args = parseArgs(rest);
  if (command === "prepare") {
    await prepare(args);
    return;
  }
  if (command === "decrypt") {
    await decrypt(args);
    return;
  }

  fail(`Unknown command: ${command}\n${usage()}`);
}

main().catch((error) => {
  process.stderr.write(`openai-platform-api-key failed: ${error.message}\n`);
  process.exit(1);
});
