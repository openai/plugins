import { execFileSync, spawnSync } from "node:child_process";
import { webcrypto } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import assert from "node:assert/strict";
import test from "node:test";
import { fileURLToPath } from "node:url";

const { subtle } = webcrypto;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT = path.resolve(
  __dirname,
  "../scripts/openai-platform-api-key.mjs",
);
const SKILL = path.resolve(
  __dirname,
  "../skills/openai-platform-api-key/SKILL.md",
);
const SKILL_AGENT_METADATA = path.resolve(
  __dirname,
  "../skills/openai-platform-api-key/agents/openai.yaml",
);
const EVALS = path.resolve(
  __dirname,
  "../skills/openai-platform-api-key/references/evals.md",
);
const PLUGIN_MANIFEST = path.resolve(__dirname, "../.codex-plugin/plugin.json");
const MCP_MANIFEST = path.resolve(__dirname, "../.mcp.json");
const MCP_SERVER = path.resolve(__dirname, "../mcp/server.mjs");
const OPENAI_DOCS_SKILL = path.resolve(
  __dirname,
  "../../../skills/skills/openai-docs/SKILL.md",
);
const APPLIED_OPENAI_DOCS_SKILL = path.resolve(
  __dirname,
  "../../../lib/applied/applied_skills/applied_skills/example_skills/openai-docs/current/SKILL.md",
);
const PLUGIN_ICON = path.resolve(
  __dirname,
  "../assets/openai-platform.png",
);
const APP_ICON = path.resolve(
  __dirname,
  "../../../chatgpt/web/public/images/ecosystem/apps/openai_platform/icon.png",
);
const SECRET = "sk-proj-test-secret-value";

function runScript(args) {
  return execFileSync(process.execPath, [SCRIPT, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function runScriptFailure(args) {
  return spawnSync(process.execPath, [SCRIPT, ...args], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function runMcpServer(requests) {
  const result = spawnSync(process.execPath, [MCP_SERVER], {
    encoding: "utf8",
    input: `${requests.map((request) => JSON.stringify(request)).join("\n")}\n`,
    stdio: ["pipe", "pipe", "pipe"],
    timeout: 5_000,
  });

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, "");
  return result.stdout
    .split(/\r?\n/u)
    .filter((line) => line.trim().length > 0)
    .map((line) => JSON.parse(line));
}

function base64url(bytes) {
  return Buffer.from(bytes).toString("base64url");
}

async function encryptWithPublicJwk(publicJwk, plaintext) {
  const publicKey = await subtle.importKey(
    "jwk",
    publicJwk,
    {
      name: "RSA-OAEP",
      hash: "SHA-256",
    },
    false,
    ["encrypt"],
  );
  const ciphertext = await subtle.encrypt(
    {
      name: "RSA-OAEP",
    },
    publicKey,
    new TextEncoder().encode(plaintext),
  );
  return base64url(ciphertext);
}

test("prepare writes private key locally and emits a public connector request", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--name", "Unit Test", "--dir", dir]));
  const request = JSON.parse(fs.readFileSync(output.request_path, "utf8"));
  const privateKey = JSON.parse(fs.readFileSync(output.private_key_path, "utf8"));

  assert.equal(request.name, "Unit Test");
  assert.deepEqual(Object.keys(request.recipient_public_key_jwk).sort(), ["e", "kty", "n"]);
  assert.equal(request.recipient_public_key_jwk.kty, "RSA");
  assert.equal(request.recipient_public_key_jwk.e, "AQAB");
  assert.equal(Boolean(privateKey.d), true);
  assert.equal(output.recipient_public_key_jwk.d, undefined);
});

test("skill documents picker lookup and local destination confirmation", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(skill, /tool_search/);
  assert.match(skill, /`open_codex_api_key_setup` tool/);
  assert.match(skill, /call `open_codex_api_key_setup` directly with no arguments \(`\{\}`\)/);
  assert.match(skill, /local destination confirmation/);
  assert.match(skill, /OpenAI Developers MCP `confirm_openai_api_key_local_destination` tool/);
  assert.match(skill, /if the picker tool is unavailable or fails before the widget opens/);
  assert.match(skill, /`create_encrypted_openai_api_key`/);
  assert.match(skill, /## Helper/);
});

test("plugin registers the editable local destination confirmation MCP tool", () => {
  const pluginManifest = JSON.parse(fs.readFileSync(PLUGIN_MANIFEST, "utf8"));
  const manifest = JSON.parse(fs.readFileSync(MCP_MANIFEST, "utf8"));
  const responses = runMcpServer([
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-11-25",
        capabilities: {},
        clientInfo: { name: "openai-developers-test", version: "0.1.0" },
      },
    },
    {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/list",
      params: {},
    },
  ]);

  assert.equal(pluginManifest.mcpServers, "./.mcp.json");
  assert.deepEqual(
    manifest.mcpServers["openai-api-key-local-confirmation"].args,
    ["./mcp/server.mjs"],
  );
  assert.equal(responses[0].result.serverInfo.name, "OpenAI Developers MCP");
  assert.deepEqual(
    responses[1].result.tools.map((tool) => tool.name),
    ["confirm_openai_api_key_local_destination"],
  );
});

test("local destination confirmation suggests a path and accepts an override", () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-mcp-test-"));
  const responses = runMcpServer([
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-11-25",
        capabilities: {},
        clientInfo: { name: "openai-developers-test", version: "0.1.0" },
      },
    },
    {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/call",
      params: {
        name: "confirm_openai_api_key_local_destination",
        arguments: {
          workspacePath: workspace,
          targetPath: ".env.local",
          envName: "OPENAI_API_KEY",
        },
      },
    },
    {
      jsonrpc: "2.0",
      id: "server-1",
      result: {
        action: "accept",
        content: {
          targetPath: ".env.test",
        },
      },
    },
  ]);

  const elicitation = responses.find((response) => response.method === "elicitation/create");
  const result = responses.find((response) => response.id === 2);
  const targetField = elicitation.params.requestedSchema.properties.targetPath;

  assert.equal(elicitation.params.mode, "form");
  assert.equal(targetField.default, path.join(workspace, ".env.local"));
  assert.equal(Object.hasOwn(targetField, "description"), false);
  assert.equal(result.result.structuredContent.status, "approved");
  assert.equal(result.result.structuredContent.targetPath, path.join(workspace, ".env.test"));
});

test("local destination confirmation rejects an out-of-workspace override", () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-mcp-test-"));
  const responses = runMcpServer([
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-11-25",
        capabilities: {},
        clientInfo: { name: "openai-developers-test", version: "0.1.0" },
      },
    },
    {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/call",
      params: {
        name: "confirm_openai_api_key_local_destination",
        arguments: {
          workspacePath: workspace,
          targetPath: ".env.local",
        },
      },
    },
    {
      jsonrpc: "2.0",
      id: "server-1",
      result: {
        action: "accept",
        content: {
          targetPath: "../.env",
        },
      },
    },
  ]);

  const result = responses.find((response) => response.id === 2);

  assert.equal(result.error.code, -32602);
  assert.match(result.error.message, /inside the selected workspace/);
});

test("local destination confirmation stops when the developer cancels", () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-mcp-test-"));
  const responses = runMcpServer([
    {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-11-25",
        capabilities: {},
        clientInfo: { name: "openai-developers-test", version: "0.1.0" },
      },
    },
    {
      jsonrpc: "2.0",
      id: 2,
      method: "tools/call",
      params: {
        name: "confirm_openai_api_key_local_destination",
        arguments: {
          workspacePath: workspace,
          targetPath: ".env.local",
        },
      },
    },
    {
      jsonrpc: "2.0",
      id: "server-1",
      result: {
        action: "cancel",
      },
    },
  ]);

  const result = responses.find((response) => response.id === 2);

  assert.equal(result.result.structuredContent.status, "not_approved");
  assert.equal(result.result.structuredContent.action, "cancel");
});

test("skill metadata describes safe API key setup", () => {
  const metadata = fs.readFileSync(SKILL_AGENT_METADATA, "utf8");

  assert.match(metadata, /Create and configure OpenAI API keys safely/);
  assert.doesNotMatch(metadata, /for any app, script, tool, or UI using AI or OpenAI API/);
  assert.doesNotMatch(metadata, /allow_implicit_invocation/);
});

test("plugin and app tiles use the same OpenAI Platform logo", (t) => {
  if (!fs.existsSync(APP_ICON)) {
    t.skip("monorepo OpenAI Platform app icon is not available in this repository");
    return;
  }

  assert.deepEqual(fs.readFileSync(PLUGIN_ICON), fs.readFileSync(APP_ICON));
});

test("skill asks before building API-backed apps when any usable key exists", () => {
  const skill = fs.readFileSync(SKILL, "utf8");
  const description = skill.match(/description: (.*)/)?.[1] ?? "";

  assert.match(
    description,
    /Use when Codex is asked to build, run, test, debug, or configure an OpenAI-backed or provider-unspecified AI app, UI, script, CLI, generator, or tool/,
  );
  assert.match(
    description,
    /especially requests phrased only as "using AI" or generators driven by forms\/user input/,
  );
  assert.match(
    description,
    /also use for OPENAI_API_KEY or sk-proj setup/,
  );
  assert.match(
    description,
    /Treat this as the credential gate: inspect safely, ask reuse-vs-new before API work/,
  );
  assert.match(
    skill,
    /Use this skill as the credential gate for API-backed work, not as the app,\s+docs, or frontend implementation skill\./,
  );
  assert.match(
    skill,
    /Codex will build, implement, run, test, debug, or configure an app, script,\s+CLI, generator, UI, or tool that calls the OpenAI API, even before a live\s+request and even if a usable key already exists\./,
  );
  assert.match(
    skill,
    /The user asks Codex to build, implement, run, or configure an app, script, CLI,\s+generator, or tool that uses AI to produce outputs from user input\./,
  );
  assert.match(
    skill,
    /The user asks for an AI-powered app or UI that generates output from one or\s+more input fields, forms, prompts, files, or other user-provided values\./,
  );
  assert.match(
    skill,
    /The user says "using AI" in an app\/script\/build request and does not name a\s+different provider\./,
  );
  assert.match(
    skill,
    /The user only wants documentation, citations, model or API guidance,\s+conceptual explanation, or code examples without asking Codex to build, run,\s+configure, or debug an API-backed artifact\./,
  );
  assert.match(
    skill,
    /The user asks for a static frontend, visual mockup, design concept, or\s+placeholder UI with no API-backed behavior\./,
  );
  assert.match(
    skill,
    /The user only asks Codex to write a one-off output directly and no app,\s+script, generator, or API-backed tool is being built or run\./,
  );
  assert.match(
    skill,
    /The user names a different AI provider for the artifact\./,
  );
  assert.match(
    skill,
    /When another implementation skill also applies, run this skill first only to inspect\s+credentials safely and send the credential decision message\./,
  );
  assert.match(
    skill,
    /do not design UI, choose architecture, inspect API examples, write code, or run\s+smoke tests\./,
  );
  assert.match(
    skill,
    /Until reuse-existing-key vs create-new-key is resolved, it outranks design-first\s+and implementation-first flows, including\s+`build-web-apps:frontend-app-builder`;/,
  );
  assert.match(
    skill,
    /After the user answers, hand off to the appropriate implementation, docs, or\s+frontend skill\./,
  );
  assert.match(
    skill,
    /before building, implementing, running, testing, debugging, or configuring an app\s+or script that calls the OpenAI API, ask up front whether to reuse an existing\s+usable key or create a new one/,
  );
  assert.match(
    skill,
    /do not silently reuse a detected key for implementation, verification,\s+smoke tests, or other live requests just because the user did not ask about\s+credentials/,
  );
  assert.match(
    skill,
    /Before creating a key or writing any secret, obtain explicit confirmation\.\s+Prefer the hosted Platform picker plus local destination confirmation when it is\s+available; if it is unavailable, fall back to a typed local destination question,\s+then wait\./,
  );
  assert.match(
    skill,
    /When creation is the chosen path, confirm the destination file\/env var before writing\./,
  );
  assert.match(
    skill,
    /If the user has not already explicitly asked for a new key, ask whether to create one first\./,
  );
  assert.match(
    skill,
    /If API access is needed and no usable key is found, offer secure key provisioning\s+instead of leaving only placeholder docs or manual setup steps\./,
  );
});

test("skill forbids credential inspection that can print secrets", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(
    skill,
    /Never inspect credentials with commands that can print secret values, such as\s+`cat \.env\*`, `grep OPENAI_API_KEY \.env\*`, or `rg OPENAI_API_KEY \.env\*`\./,
  );
  assert.match(
    skill,
    /inspect env files only with no-output checks that reveal presence\/absence,\s+never with commands that echo matching lines or whole files/,
  );
});

test("skill makes the key-choice gate impossible to miss", () => {
  const skill = fs.readFileSync(SKILL, "utf8");
  const credentialDecisionMessages = skill.slice(
    skill.indexOf("## Credential Decision Messages"),
    skill.indexOf("## Workflow"),
  );

  assert.match(skill, /## Mandatory First Step/);
  assert.match(
    skill,
    /Before editing, testing, running, debugging, or configuring any code that calls\s+the OpenAI API:\s+1\. Inspect for a usable `OPENAI_API_KEY` without printing it\.\s+2\. Unless the user explicitly asked for a new key, ask whether to reuse an\s+existing key or create a new one\. If none exists, ask whether to create one\.\s+3\. Stop until the user answers\./,
  );
  assert.match(
    skill,
    /This applies even if:\s+- a usable key already exists\s+- no live API call will be made\s+- no secret will be written\s+- the task is "just create a script"/,
  );
  assert.match(
    skill,
    /Finding an existing key is not permission to proceed\. It only changes the\s+question you ask\./,
  );
  assert.match(
    skill,
    /The credential decision is a hard stop\. Before the user answers, do not create\s+directories, scaffold files, draft implementation plans, wire API-dependent\s+code, run smoke tests, or give placeholder\/manual key setup instructions\./,
  );
  assert.match(
    skill,
    /The\s+only allowed pre-gate work is safe repo convention discovery and credential\s+presence checks that do not print secrets\./,
  );
  assert.match(skill, /## Credential Decision Messages/);
  assert.match(
    credentialDecisionMessages,
    /Required progress updates before or during credential inspection may be brief\s+and limited to saying that Codex is checking credentials or opening secure key\s+setup\./,
  );
  assert.match(
    credentialDecisionMessages,
    /They must not describe implementation plans, architecture, file choices,\s+local destination details, or credential conclusions before the credential\s+decision or picker handoff\./,
  );
  assert.match(
    credentialDecisionMessages,
    /After inspecting credentials, the next substantive user-facing message must be\s+the credential decision message\./,
  );
  assert.match(
    credentialDecisionMessages,
    /Existing usable key found, and the user did not explicitly ask for a new key:\s+make clear that the OpenAI API will power the app, script, or project, say that\s+an existing usable `OPENAI_API_KEY` was found without revealing it, then ask\s+whether to reuse that key or create a new one\./,
  );
  assert.match(
    credentialDecisionMessages,
    /No usable key found: make clear that the OpenAI API will power the app, script,\s+or project, say that no usable `OPENAI_API_KEY` was found, then ask whether to\s+create one securely\./,
  );
  assert.match(
    credentialDecisionMessages,
    /User explicitly asked for a new key: skip the reuse question and open the\s+Platform picker directly when available\./,
  );
});

test("skill documents the connector-owned picker boundary", () => {
  const skill = fs.readFileSync(SKILL, "utf8");
  const workflow = skill.slice(skill.indexOf("## Workflow"), skill.indexOf("## Helper"));

  assert.match(skill, /Prefer the hosted Platform picker/);
  assert.match(skill, /`open_codex_api_key_setup`/);
  assert.match(skill, /automatically loads organization\/project choices/);
  assert.match(skill, /sends a later widget-authored follow-up with the confirmed key name plus selected opaque ids/);
  assert.match(skill, /tool_search/);
  assert.match(
    skill,
    /call `open_codex_api_key_setup` directly with no arguments \(`\{\}`\)\. Do not send a key name, local paths, workspace arguments, or target arrays\./,
  );
  assert.match(
    skill,
    /after `open_codex_api_key_setup` returns without an error, end the current turn immediately and wait for the widget-generated follow-up prompt\. Do not inspect or interpret the launch payload, search for connector contract details, run local-save steps, make another tool call, or send any non-empty user-facing message, including a picker-open confirmation, in that turn/,
  );
  assert.match(skill, /picker-confirmed `organization_id` and `project_id`/);
  assert.doesNotMatch(workflow, /list_openai_api_key_targets|open_openai_api_key_setup/);
});

test("skill keeps deterministic mechanics out of the hosted-picker branch", () => {
  const skill = fs.readFileSync(SKILL, "utf8");
  const hostedPickerFlow = skill.slice(
    skill.indexOf("   - Prefer the hosted Platform picker:"),
    skill.indexOf("   - After the widget follow-up"),
  );

  assert.doesNotMatch(hostedPickerFlow, /recipient_public_key_jwk/);
  assert.doesNotMatch(hostedPickerFlow, /encrypted_api_key\.ciphertext/);
});

test("skill keeps secure setup narration brief", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(skill, /Keep user-facing messages concise\./);
  assert.match(skill, /Do not narrate deterministic mechanics such as helper discovery/);
  assert.match(
    skill,
    /say only that Codex will create the key securely and write it to the confirmed env file\./,
  );
});

test("skill prefers ignored env files and warns before tracked secret writes", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(skill, /Prefer ignored or untracked env files\./);
  assert.match(skill, /The form shows the recommended location and lets the user replace it before continuing\./);
  assert.match(skill, /If the local destination tool returns `approved`, use its returned `targetPath` exactly and do not ask a second destination question\./);
  assert.match(skill, /ask exactly one short question and stop: `Save the new key to <path>\? Reply yes to continue, another workspace-relative env-file path to change it, or decline\.`/);
  assert.match(
    skill,
    /Silently check whether the selected target is tracked\. If it is tracked, stop and obtain explicit confirmation that a secret will be written there\./,
  );
});

test("eval matrix includes local picker boundary and two-field joke app use case", () => {
  const evals = fs.readFileSync(EVALS, "utf8");
  const k2RunnerRow = evals
    .split(/\r?\n/u)
    .find((line) => line.startsWith("| K2 |"));

  assert.match(
    evals,
    /should open the Platform connector-owned picker with no arguments/,
  );
  assert.match(
    evals,
    /after any non-error picker launch, should not inspect or interpret its launch payload, make another tool call, or send a non-empty user-facing message in that turn/,
  );
  assert.match(
    evals,
    /brief progress updates should be allowed only when limited to credential-gate activity and should not describe implementation plans, architecture, file choices, local destination details, or credential conclusions before the credential decision or picker handoff/,
  );
  assert.match(k2RunnerRow, /brief progress updates should be allowed only when limited to credential-gate activity/);
  assert.match(
    evals,
    /Grade the original case assertions as the product result\. Report runner-injected\s+freshness, artifact, and generic result-validity assertions separately/,
  );
  assert.match(evals, /### K5 - Two-field joke app/);
  assert.match(
    evals,
    /build an app that generates jokes using AI when i input 2 fields\. the joke should use those fields/,
  );
  assert.match(
    evals,
    /should invoke the `openai-platform-api-key` skill even though the user did not\s+mention keys/,
  );
  assert.match(
    evals,
    /should stop at the credential decision point until the user answers and should not\s+require a two-field app plan or implementation in the same rollout/,
  );
  assert.match(
    evals,
    /if the rollout proceeds after a confirmed key decision, the app plan or implementation\s+should collect two user input fields and send both fields into the AI joke-generation request/,
  );
});

test("openai-docs defers to API key skill for implementation tasks", (t) => {
  const docsSkillPaths = [OPENAI_DOCS_SKILL, APPLIED_OPENAI_DOCS_SKILL].filter(
    fs.existsSync,
  );
  if (docsSkillPaths.length === 0) {
    t.skip("monorepo OpenAI docs skill paths are not available in this repository");
    return;
  }

  for (const docsSkillPath of docsSkillPaths) {
    const docsSkill = fs.readFileSync(docsSkillPath, "utf8");

    assert.match(docsSkill, /## API Key Setup/);
    assert.match(
      docsSkill,
      /For requests to build, run, configure, debug, or implement an API-backed app, script, CLI, generator, or tool, use `openai-platform-api-key` first when available\./,
    );
    assert.match(
      docsSkill,
      /use `openai-platform-api-key` first when available\. After that credential gate is resolved, return here for current docs as needed\./,
    );
    assert.match(
      docsSkill,
      /Use this skill directly for docs-only questions, citations, model\/API guidance, conceptual explanations, and examples that do not require building or running an API-backed artifact\./,
    );
  }
});

test("decrypt writes the API key to the env file without printing it", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(dir, ".env.local");
  const decryptOutput = runScript([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--env-name",
    "OPENAI_API_KEY",
    "--workspace",
    dir,
  ]);

  assert.equal(decryptOutput.includes(SECRET), false);
  assert.equal(fs.readFileSync(target, "utf8"), `OPENAI_API_KEY=${SECRET}\n`);
});

test("decrypt updates an existing env var without printing the API key", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(dir, ".env.local");
  fs.writeFileSync(target, "OTHER=value\nOPENAI_API_KEY=old\n");

  const decryptOutput = JSON.parse(
    runScript([
      "decrypt",
      "--private-key",
      output.private_key_path,
      "--ciphertext",
      ciphertext,
      "--target",
      target,
      "--workspace",
      dir,
    ]),
  );

  assert.equal(decryptOutput.updated_existing, true);
  assert.equal(decryptOutput.wrote_plaintext_to_stdout, false);
  assert.equal(fs.readFileSync(target, "utf8"), `OTHER=value\nOPENAI_API_KEY=${SECRET}\n`);
});

test("decrypt tightens permissions on an existing env file", async () => {
  if (process.platform === "win32") {
    return;
  }

  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(dir, ".env.local");
  fs.writeFileSync(target, "OPENAI_API_KEY=old\n", { mode: 0o644 });
  fs.chmodSync(target, 0o644);

  runScript([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.equal(fs.statSync(target).mode & 0o777, 0o600);
});

test("decrypt preserves export when updating an exported env var", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(dir, ".env.local");
  fs.writeFileSync(target, "OTHER=value\nexport OPENAI_API_KEY=old\n");

  const decryptOutput = JSON.parse(
    runScript([
      "decrypt",
      "--private-key",
      output.private_key_path,
      "--ciphertext",
      ciphertext,
      "--target",
      target,
      "--workspace",
      dir,
    ]),
  );

  assert.equal(decryptOutput.updated_existing, true);
  assert.equal(decryptOutput.wrote_plaintext_to_stdout, false);
  assert.equal(fs.readFileSync(target, "utf8"), `OTHER=value\nexport OPENAI_API_KEY=${SECRET}\n`);
});

test("decrypt rejects unsafe plaintext before writing env files", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(
    output.recipient_public_key_jwk,
    "sk-proj-safe\nOTHER=value",
  );
  const target = path.join(dir, ".env.local");

  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not a safe OpenAI API key literal/);
  assert.equal(fs.existsSync(target), false);
});

test("decrypt rejects symlink env targets without writing through them", async () => {
  if (process.platform === "win32") {
    return;
  }

  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const outsideDir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-outside-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(dir, ".env.local");
  const symlinkDestination = path.join(outsideDir, "tracked-file.ts");
  fs.writeFileSync(symlinkDestination, "ORIGINAL\n");
  fs.symlinkSync(symlinkDestination, target);

  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /symlink target/);
  assert.equal(fs.readFileSync(symlinkDestination, "utf8"), "ORIGINAL\n");
});

test("decrypt rejects hard-linked env targets without writing through them", async () => {
  if (process.platform === "win32") {
    return;
  }

  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const outsideDir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-outside-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(dir, ".env.local");
  const hardlinkDestination = path.join(outsideDir, "tracked-file.ts");
  fs.writeFileSync(hardlinkDestination, "ORIGINAL\n");
  try {
    fs.linkSync(hardlinkDestination, target);
  } catch {
    return;
  }

  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /hard-linked target/);
  assert.equal(fs.readFileSync(hardlinkDestination, "utf8"), "ORIGINAL\n");
});

test("decrypt rejects targets outside the selected workspace", async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const outsideDir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-outside-"));
  const output = JSON.parse(runScript(["prepare", "--dir", workspace]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const target = path.join(outsideDir, ".env.local");

  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--workspace",
    workspace,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /inside the workspace/);
  assert.equal(fs.existsSync(target), false);
});

test("decrypt rejects symlinked parent directories that escape the workspace", async () => {
  if (process.platform === "win32") {
    return;
  }

  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const outsideDir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-outside-"));
  const output = JSON.parse(runScript(["prepare", "--dir", workspace]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const linkedParent = path.join(workspace, "linked-parent");
  const target = path.join(linkedParent, ".env.local");
  fs.symlinkSync(outsideDir, linkedParent, "dir");

  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    ciphertext,
    "--target",
    target,
    "--workspace",
    workspace,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /inside the workspace/);
  assert.equal(fs.existsSync(path.join(outsideDir, ".env.local")), false);
});

test("decrypt treats ciphertext values that start with hyphens as values", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const target = path.join(dir, ".env.local");
  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    "--AA",
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Failed to decrypt encrypted API key/);
  assert.doesNotMatch(result.stderr, /Provide --ciphertext or --encrypted-result/);
});

test("decrypt rejects unknown options and missing option values", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const target = path.join(dir, ".env.local");

  const unknown = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    "abc",
    "--target",
    target,
    "--workspace",
    dir,
    "--envname",
    "FOO",
  ]);
  assert.notEqual(unknown.status, 0);
  assert.match(unknown.stderr, /Unknown option: --envname/);

  const missing = runScriptFailure(["prepare", "--dir", "--name", "Unit Test"]);
  assert.notEqual(missing.status, 0);
  assert.match(missing.stderr, /Missing value for --dir/);
});

test("decrypt rejects impossible base64url lengths before decrypting", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const target = path.join(dir, ".env.local");
  const result = runScriptFailure([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--ciphertext",
    "a",
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Encrypted ciphertext must be base64url/);
});

test("decrypt accepts a structured connector result file", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "openai-platform-helper-test-"));
  const output = JSON.parse(runScript(["prepare", "--dir", dir]));
  const ciphertext = await encryptWithPublicJwk(output.recipient_public_key_jwk, SECRET);
  const encryptedResultPath = path.join(dir, "connector-result.json");
  const target = path.join(dir, ".env.local");
  fs.writeFileSync(
    encryptedResultPath,
    JSON.stringify({
      structuredContent: {
        encrypted_api_key: {
          version: 1,
          ciphertext,
        },
      },
    }),
  );

  const decryptOutput = runScript([
    "decrypt",
    "--private-key",
    output.private_key_path,
    "--encrypted-result",
    encryptedResultPath,
    "--target",
    target,
    "--workspace",
    dir,
  ]);

  assert.equal(decryptOutput.includes(SECRET), false);
  assert.equal(fs.readFileSync(target, "utf8"), `OPENAI_API_KEY=${SECRET}\n`);
});
