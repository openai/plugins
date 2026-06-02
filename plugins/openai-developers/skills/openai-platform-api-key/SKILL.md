---
name: openai-platform-api-key
description: Use for building, running, testing, debugging, or configuring apps, UIs, scripts, CLIs, generators, and tools that use AI, including AI-powered apps, apps that generate output with AI, and user-input-driven AI features. Treat unspecified AI in build requests as OpenAI API usage unless the user names another provider or says not to use OpenAI. First inspect credentials safely, then ask whether to reuse an existing key or create one before API-dependent implementation. Also use for OPENAI_API_KEY or sk-proj setup requests. Never expose plaintext.
---

# OpenAI API Key

Use this skill only in Codex local/app sessions. Create keys through the secure OpenAI Platform connector, keep plaintext out of normal tool output, and write secrets only to a confirmed local destination.

## When To Use

Use this skill as the credential gate for API-backed work, not as the app, docs, or frontend implementation skill.

Use it when:

- The user asks for an OpenAI API key, `OPENAI_API_KEY`, or an `sk-proj` key.
- Codex will build, implement, run, test, debug, or configure an app, script, CLI, generator, UI, or tool that calls the OpenAI API, even before a live request and even if a usable key already exists.
- The user asks Codex to build, implement, run, or configure an app, script, CLI, generator, or tool that uses AI to produce outputs from user input.
- The user asks for an AI-powered app or UI that generates output from one or more input fields, forms, prompts, files, or other user-provided values.
- The user says "using AI" in an app/script/build request and does not name a different provider.

Do not use it when:

- The user only wants documentation, citations, model or API guidance, conceptual explanation, or code examples without asking Codex to build, run, configure, or debug an API-backed artifact.
- The user asks for a static frontend, visual mockup, design concept, or placeholder UI with no API-backed behavior.
- The user only asks Codex to write a one-off output directly and no app, script, generator, or API-backed tool is being built or run.
- The user names a different AI provider for the artifact.

If API access is needed and no usable key is found, offer secure key provisioning instead of leaving only placeholder docs or manual setup steps.

## Coordination With Implementation Skills

When another implementation skill also applies, this skill runs first only to inspect credentials safely and send the credential decision message. Do not use this skill to design the UI, generate visual concepts, choose app architecture, inspect API examples, write code, or run smoke tests before the credential gate is resolved.

For API-backed app or UI requests, this credential gate takes precedence over design-first and implementation-first workflows, including `build-web-apps:frontend-app-builder`, until the reuse-existing-key vs create-new-key decision is resolved.

After the user answers the credential decision, continue with the appropriate implementation, docs, or frontend skill for the actual build.

## Safety Rules

- Never request, print, summarize, quote, or paste a plaintext API key.
- Never inspect credentials with commands that can print secret values, such as `cat .env*`, `grep OPENAI_API_KEY .env*`, or `rg OPENAI_API_KEY .env*`. Use silent exit-status checks or redacted summaries only.
- Use `create_encrypted_openai_api_key`; do not use the browser/widget key setup flow from Codex.
- Only pass public JWK material (`kty`, `n`, `e`) to the connector.
- Before creating a key or writing any secret, ask for explicit confirmation in a standalone user-facing message that states the action, keeps supporting detail in separate bullets, then wait.
- Prefer ignored or untracked env files. In git repos, avoid tracked targets unless the user explicitly confirms that choice.
- The local helper may handle plaintext in memory and write it to the confirmed file. Its stdout/stderr must not include the key.
- When decrypting in a repo, pass the repo root as `--workspace`; the helper refuses symlink targets and targets outside that workspace.
- Keep user-facing messages concise. Do not narrate internal keypair, public JWK, ciphertext, or decrypt steps unless the user asks or a failure requires explanation; say only that Codex will create the key securely and write it to the confirmed env file.
- Report only safe metadata: path, env var name, key name, org/project names, and whether an existing env var was updated.

## Mandatory First Step

Before editing, testing, running, debugging, or configuring any code that calls the OpenAI API:

1. Inspect for a usable `OPENAI_API_KEY` without printing it.
2. Unless the user explicitly asked for a new key, ask whether to reuse an existing key or create a new one. If none exists, ask whether to create one.
3. Stop until the user answers.

This applies even if:

- a usable key already exists
- no live API call will be made
- no secret will be written
- the task is "just create a script"

Finding an existing key is not permission to proceed. It only changes the question you ask.

The credential decision is a hard stop. Before the user answers, do not create directories, scaffold files, draft implementation plans, wire API-dependent code, run smoke tests, or give placeholder/manual key setup instructions. The only allowed pre-gate work is safe repo convention discovery and credential presence checks that do not print secrets.

## Credential Decision Messages

After inspecting credentials, the next user-facing message must be the credential decision message. Do not send interim user-facing messages about env files, key presence, API docs, file plans, implementation shape, or setup instructions before this decision.

Use one of these branches:

- Existing usable key found, and the user did not explicitly ask for a new key: make clear that the OpenAI API will power the app, script, or project, say that an existing usable `OPENAI_API_KEY` was found without revealing it, then ask whether to reuse that key or create a new one.
- No usable key found: make clear that the OpenAI API will power the app, script, or project, say that no usable `OPENAI_API_KEY` was found, then ask whether to create one securely.
- User explicitly asked for a new key: skip the reuse question and use the key-creation confirmation message below.

After sending the credential decision message, stop until the user answers.

## Workflow

1. Inspect before acting:
   - look for a usable key without printing secret values in the current environment and likely local env files such as `.env.local`, `.env`, and ignored framework-specific env files
   - inspect env files only with no-output checks that reveal presence/absence, never with commands that echo matching lines or whole files
   - check README/setup docs, `OPENAI_BASE_URL`, and framework-specific env docs for repo conventions separately from secret-bearing env files
   - prefer ignored or untracked env files; avoid tracked targets unless the user explicitly confirms that choice
   - default to `.env.local` and `OPENAI_API_KEY` when no stronger convention exists
2. Based on that inspection:
   - for tasks that will call the OpenAI API, when asking this up-front question, mention that the OpenAI API will power the app, script, or project before mentioning whether an existing key was found in the environment or local env files
   - if the user explicitly asked for a new key, no reuse decision is needed
   - otherwise, before building, implementing, running, testing, debugging, or configuring an app or script that calls the OpenAI API, ask up front whether to reuse an existing usable key or create a new one
   - if no usable key exists, ask whether to create one before building the rest of the app
   - after asking the up-front credential question, stop; do not include an app plan, file list, code sketch, manual `OPENAI_API_KEY` instructions, or fallback placeholder setup in the same response
   - ask this up-front question even when Codex has not yet made a live request; do not defer it until verification or smoke testing
   - do not silently reuse a detected key for implementation, verification, smoke tests, or other live requests just because the user did not ask about credentials
   - treat requests to create or configure a key as ambiguous unless the user says they want a new key
   - if the user chooses reuse and a persistent file write is still needed, confirm the destination file/env var before writing
3. If creation is still needed and the user has not already explicitly asked for a new key, ask whether to create one. Before writing, confirm the destination file/env var. In the Codex app, use one bold confirmation line, short bullets for setup details, and one plain confirmation sentence so the decision point is easy to notice:

   **I need to create an OpenAI API key for this project. Want me to set it up for you?**
   - I'll name it `<repo name> Codex`.
   - I'll save it in `<confirmed env file path>` as `OPENAI_API_KEY`.

   Reply yes to continue with this setup, or suggest a different one.

   Use that confirmation sentence exactly as written: no bullet, no backticks around `yes`, and no rewritten second clause.

   Prefer this over a single long sentence that buries the decision point beside the key name and file path.
4. After confirmation, run the app tool preflight:
   - use `tool_search` to load `create_encrypted_openai_api_key`
   - if missing and `tool_suggest` is available, suggest installing connector `connector_2de447f3f15448ebab48783d7e4f5d81`
   - if unavailable or auth fails, ask the user to connect OpenAI Platform from `/apps` or the `$` app picker, then retry `tool_search` after they finish
5. Run `prepare`, keep `private_key_path`, and send only `recipient_public_key_jwk` to the connector.
6. Call `create_encrypted_openai_api_key` with the confirmed key name.
7. Run `decrypt` with the encrypted ciphertext, confirmed target path, env var name, and repo root as `--workspace`.
8. Verify by running the relevant project command when practical. Do not reveal or inspect the secret value directly.

## Final Summary

After successfully creating and writing a new key, include this bullet in the final summary, replacing `<key name>` with the created key name:

- I created an API Key named `<key name>` to call OpenAI APIs. Manage OpenAI API use on [platform.openai.com](https://platform.openai.com).

Keep the rest of the summary to safe metadata only. Do not reveal the key value.

## Helper

Use the helper by absolute path:

```bash
node "<plugin root>/scripts/openai-platform-api-key.mjs" prepare --name "Codex"
```

The `prepare` command creates a temporary private key file and a request JSON file containing only the public JWK and requested key name.

After the connector returns `encrypted_api_key.ciphertext`, decrypt and write the key locally:

```bash
node "<plugin root>/scripts/openai-platform-api-key.mjs" decrypt \
  --private-key "<private key path from prepare>" \
  --ciphertext "<encrypted_api_key.ciphertext from connector result>" \
  --target "<confirmed env file path>" \
  --workspace "<repo root>" \
  --env-name OPENAI_API_KEY
```

The decrypt command updates or appends the env var and prints only safe write metadata. It refuses to write through symlink targets or outside the selected workspace.

Common defaults:

- Env var: `OPENAI_API_KEY`
- File: `.env.local`
- Key name: `<repo name> Codex`

## References

- `references/evals.md`: trigger and routing eval cases for this skill.
