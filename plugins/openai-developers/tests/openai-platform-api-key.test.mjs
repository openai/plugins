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
const EVALS = path.resolve(
  __dirname,
  "../skills/openai-platform-api-key/references/evals.md",
);
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

test("skill documents connector install and retry preflight", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(skill, /tool_search/);
  assert.match(skill, /tool_suggest/);
  assert.match(skill, /connector_2de447f3f15448ebab48783d7e4f5d81/);
  assert.match(skill, /retry `tool_search`/);
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
    /Use for building, running, testing, debugging, or configuring apps, UIs, scripts, CLIs, generators, and tools that use AI/,
  );
  assert.match(
    description,
    /including AI-powered apps, apps that generate output with AI, and user-input-driven AI features\./,
  );
  assert.match(
    description,
    /Treat unspecified AI in build requests as OpenAI API usage unless the user names another provider or says not to use OpenAI\./,
  );
  assert.match(
    description,
    /First inspect credentials safely, then ask whether to reuse an existing key or create one before API-dependent implementation\./,
  );
  assert.doesNotMatch(
    description,
    /Do not use|docs-only|static UI|one-off content/,
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
    /When another implementation skill also applies, this skill runs first only to\s+inspect credentials safely and send the credential decision message\./,
  );
  assert.match(
    skill,
    /Do not use\s+this skill to design the UI, generate visual concepts, choose app architecture,\s+inspect API examples, write code, or run smoke tests before the credential gate\s+is resolved\./,
  );
  assert.match(
    skill,
    /For API-backed app or UI requests, this credential gate takes precedence over\s+design-first and implementation-first workflows, including\s+`build-web-apps:frontend-app-builder`, until the reuse-existing-key vs\s+create-new-key decision is resolved\./,
  );
  assert.match(
    skill,
    /After the user answers the credential decision, continue with the appropriate\s+implementation, docs, or frontend skill for the actual build\./,
  );
  assert.match(
    skill,
    /before building, implementing, running, testing, debugging, or\s+configuring an app or script that calls the OpenAI API, ask up front\s+whether to reuse an existing usable key or create a new one/,
  );
  assert.match(
    skill,
    /if no usable key exists, ask whether to create one before building\s+the rest of the app/,
  );
  assert.match(
    skill,
    /ask this up-front question even when Codex has not yet made a live request;\s+do not defer it until verification or smoke testing/,
  );
  assert.match(
    skill,
    /do not silently reuse a detected key for implementation, verification,\s+smoke tests, or other live requests just because the user did not ask about\s+credentials/,
  );
  assert.match(
    skill,
    /Before creating a key or writing any secret, ask for explicit confirmation in\s+a standalone user-facing message that states the action, keeps supporting\s+detail in separate bullets, then wait\./,
  );
  assert.match(
    skill,
    /Before writing, confirm\s+the destination file\/env var\./,
  );
  assert.match(
    skill,
    /If creation is still needed and the user has not already explicitly asked for\s+a new key, ask whether to create one\./,
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
  const workflowChoiceGate = skill.slice(
    skill.indexOf("2. Based on that inspection:"),
    skill.indexOf("3. If creation is still needed"),
  );
  const credentialDecisionMessages = skill.slice(
    skill.indexOf("## Credential Decision Messages"),
    skill.indexOf("## Workflow"),
  );
  const apiUseCopy = "OpenAI API will power the app, script, or project";

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
  assert.match(
    workflowChoiceGate,
    /for tasks that will call the OpenAI API, when asking this up-front question,\s+mention that the OpenAI API will power the app, script, or project before\s+mentioning whether an existing key was found in the environment or local\s+env files/,
  );
  assert.match(
    workflowChoiceGate,
    /after asking the up-front credential question, stop; do not include an\s+app plan, file list, code sketch, manual `OPENAI_API_KEY` instructions, or\s+fallback placeholder setup in the same response/,
  );
  assert.ok(
    workflowChoiceGate.indexOf(apiUseCopy) <
      workflowChoiceGate.indexOf("existing key was found in the environment"),
  );
  assert.match(skill, /## Credential Decision Messages/);
  assert.match(
    credentialDecisionMessages,
    /After inspecting credentials, the next user-facing message must be the\s+credential decision message\./,
  );
  assert.match(
    credentialDecisionMessages,
    /Do not send interim user-facing messages about env\s+files, key presence, API docs, file plans, implementation shape, or setup\s+instructions before this decision\./,
  );
  assert.match(
    credentialDecisionMessages,
    /Existing usable key found, and the user did not explicitly ask for a new key:\s+make clear that the OpenAI API will power the app, script, or project, say\s+that an existing usable `OPENAI_API_KEY` was found without revealing it, then\s+ask whether to reuse that key or create a new one\./,
  );
  assert.match(
    credentialDecisionMessages,
    /No usable key found: make clear that the OpenAI API will power the app,\s+script, or project, say that no usable `OPENAI_API_KEY` was found, then ask\s+whether to create one securely\./,
  );
  assert.match(
    credentialDecisionMessages,
    /User explicitly asked for a new key: skip the reuse question and use the\s+key-creation confirmation message below\./,
  );
  assert.match(
    credentialDecisionMessages,
    /After sending the credential decision message, stop until the user answers\./,
  );
  assert.doesNotMatch(skill, /first state exactly:\s+"I will use the OpenAI API to power this app\."/);
  assert.doesNotMatch(skill, /Use `app` in this sentence even when the user says script or project/);
});

test("skill documents a prominent confirmation prompt when key creation is needed", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(
    skill,
    /\*\*I need to create an OpenAI API key for this project\. Want me to set it up for you\?\*\*/,
  );
  assert.match(skill, /<repo name> Codex/);
  assert.match(skill, /<confirmed env file path>/);
  assert.match(
    skill,
    /Reply yes to continue with this setup, or suggest a different one\./,
  );
  assert.match(
    skill,
    /Use that confirmation sentence exactly as written: no bullet, no backticks\s+around `yes`, and no rewritten second clause\./,
  );
  assert.doesNotMatch(
    skill,
    /-\s+Reply yes to continue with this setup, or suggest a different one\./,
  );
  assert.match(skill, /use one bold confirmation\s+line, short bullets/);
  assert.doesNotMatch(skill, /When Markdown is available/);
  assert.match(skill, /single\s+long sentence that buries the decision point/);
});

test("skill documents the final summary bullet after creating a key", () => {
  const skill = fs.readFileSync(SKILL, "utf8");

  assert.match(skill, /## Final Summary/);
  assert.match(
    skill,
    /After successfully creating and writing a new key, include this bullet in the final summary, replacing `<key name>` with the created key name:/,
  );
  assert.match(
    skill,
    /- I created an API Key named `<key name>` to call OpenAI APIs\. Manage OpenAI API use on \[platform\.openai\.com\]\(https:\/\/platform\.openai\.com\)\./,
  );
  assert.match(skill, /Keep the rest of the summary to safe metadata only\./);
  assert.match(skill, /Do not reveal the key value\./);
});

test("eval matrix includes two-field joke app use case", () => {
  const evals = fs.readFileSync(EVALS, "utf8");

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

    assert.match(
      docsSkill,
      /For API-backed implementation tasks, defer to openai-platform-api-key first when available\./,
    );
    assert.match(
      docsSkill,
      /use `openai-platform-api-key` first when it is\s+available\. After that credential gate is resolved, return here for current docs\s+as needed\./,
    );
    assert.match(
      docsSkill,
      /Use this skill directly for docs-only questions, citations, model\/API guidance,\s+conceptual explanations, and examples that do not require building or running an\s+API-backed artifact\./,
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
