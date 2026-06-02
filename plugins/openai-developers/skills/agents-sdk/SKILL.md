---
name: agents-sdk
description: Build, run, deploy, and evaluate OpenAI Agents SDK apps from Codex. Use when the user asks to create or adapt an Agents SDK app, build from a prompt or Codex thread, prepare a runnable agent prototype, add a focused eval harness, or deploy locally through the Agents SDK Deployment Manager.
---

# Agents SDK

Use this skill to turn an idea, repo, or prior Codex thread into a small runnable Agents SDK app. Verify it locally, then deploy it through the local Deployment Manager when the user wants a running service. Prefer Python unless the user asks for TypeScript.

## References

- Agents guide: https://developers.openai.com/api/docs/guides/agents
- Sandbox Agents guide: https://developers.openai.com/api/docs/guides/agents/sandboxes
- Python SDK: https://github.com/openai/openai-agents-python
- TypeScript SDK: https://github.com/openai/openai-agents-js
- Deployment Manager: https://github.com/openai/openai-cookbook/tree/main/examples/agents_sdk/deployment_manager
- Agent evals guide: https://developers.openai.com/api/docs/guides/agent-evals

## Rules

- Read the Agents guide before creating or changing an Agents SDK implementation.
- Read the Sandbox Agents guide before choosing `SandboxAgent`, workspace manifests, shell/file access, skills, or sandbox backend behavior.
- If a docs MCP/tool is unavailable, read the official docs URLs directly instead of skipping the docs gate.
- Follow current docs for SDK semantics and the target repo for packaging, naming, and command conventions.
- Keep generated app files, eval files, and deployment-generated files separate in the final summary.

## Intake

Classify the request before editing:

- New app from prompt or idea: build the smallest runnable Agents SDK app that proves the workflow.
- Existing app or demo: inspect the repo and add the smallest Agents SDK layer needed to make the workflow agentic.
- Prior Codex work: turn thread IDs, session links, rollout JSONL paths, or pasted summaries into a short build brief before writing code.
- Evals request: add a focused local eval harness against the real agent path.
- Deployment-only request: deploy the existing app without rebuilding unless deployment reveals a small required fix.

## API Access

Agents SDK apps need `OPENAI_API_KEY` to run. Before building, running, or testing an app that calls the OpenAI API, use the `openai-platform-api-key` skill in this plugin as the credential gate. Follow that skill's confirmation flow and never print, summarize, or commit secret values.

## Build Workflow

1. Inspect the target repo.
   Read `README.md`, dependency files, app entrypoints, existing examples, and any domain-specific `skills/` or policy files.

2. Define the app contract.
   Capture the agent goal, input shape, expected output, tools, state, approval gates, and the local command that proves the workflow.

3. Set up dependencies using the repo's existing package manager.
   For Python projects, prefer `uv`; add `openai-agents` when the project owns dependencies.

4. Start with one agent.
   Use a single `Agent` with clear static `instructions` and `Runner.run` until the workflow proves it needs specialists, handoffs, structured outputs, or sandbox execution.

5. Add tools deliberately.
   Use `@function_tool` for deterministic local actions such as lookups, calculations, file transforms, API calls, or validation. Keep side effects narrow and schemas explicit.

6. Add sandbox only for workspace tasks.
   Use `SandboxAgent` when the agent must inspect files, run shell commands, use workspace skills, or create artifacts in an isolated environment. Keep ordinary business workflows on normal `Agent` plus tools.

7. Make it runnable.
   Provide a local smoke command, sample input, and expected observable output. If there is a UI, wire it to the agent path and verify the core workflow, not just rendering.

For HTTP apps that may be deployed, make `uv run python main.py` start the web service when `PORT` is present, keep CLI-only smoke behavior behind explicit arguments or the no-`PORT` path, and expose `/health` for readiness.

For every new prototype or substantial app build, prefer:

```text
<project>/
  agent.py              # Agent definition, tools, and run helper
  main.py               # API/server/CLI entrypoint if needed
  pyproject.toml        # includes openai-agents if the project owns deps
  docs/
    prompt.md           # runtime prompt or instructions used by the app agent
    agent-interactions.png
    agent-sequence.png
  data/                 # small sample inputs or fixtures
  skills/<domain>/      # optional domain instructions or reusable policy
  README.md             # local run instructions if the project already uses READMEs
```

Generate diagrams directly as PNG files. Do not create SVG diagram sources or rely on browser screenshots of SVGs unless the user explicitly asks for editable vector sources. For one-off diagram generation, prefer a small script under `scripts/generate_diagrams.py` and run extra drawing dependencies with `uv run --no-project --with ...` so the app dependency file stays focused.

## Build From Codex

When the source is prior Codex work, create a compact brief before building:

- confirmed facts from the source threads;
- inferences and open questions;
- app goal, agent behavior, tools, state, UI, approvals, sandbox needs, and deployment assumptions;
- a standalone build prompt that can drive the implementation.

Prefer the newest user direction when threads conflict. Keep secrets out of the brief and mention missing environment variable names only.

If the user already asked to build after planning, continue from the brief into the build workflow. Otherwise ask for approval before implementing.

## Eval Workflow

Add evals when requested. Default to a local harness that exercises the real agent workflow rather than a mock or contract-only path.

Before creating or changing evals, read the Agents guide and Agent evals guide. Read trace grading, evals, and graders docs before generating platform eval configs, grader JSON, or dataset upload scripts.

Prefer an `evals/` folder unless the repo already has a stronger convention:

```text
<project>/
  evals/
    README.md
    cases.jsonl
    graders.py
    run_local.py
    results/
      .gitignore
```

Design a small case matrix around meaningful behavior: happy path, missing evidence, escalation boundary, required or forbidden tool calls, approval gates, state updates, and regressions from observed bugs. Grade behavior such as structured output, tool calls, handoffs, guardrails, trace IDs, event logs, state changes, and approval behavior instead of volatile IDs or exact prose unless wording is contractual.

`evals/run_local.py` should load cases, add the app root to `sys.path`, run each case through the app's real agent path, isolate or reset state, require needed environment variable names up front, write `evals/results/latest.json`, and exit non-zero on failures.

## Deploy Workflow

Use the Deployment Manager from `openai-cookbook` for local deployments. Default to `local-docker` unless the user or app requires a different local target.

1. Check deployable app signals:
   - an app/orchestrator entrypoint, usually `main.py`;
   - dependency metadata, preferably `pyproject.toml`;
   - `openai-agents` in the app dependencies;
   - `PORT` support for local app startup, with `uv run python main.py` starting the HTTP service when `PORT` is set;
   - `/health` readiness endpoint;
   - optional `SANDBOX_BACKEND` support for sandbox-backed apps;
   - optional `docs/prompt.md`, `docs/agent-interactions.png`, and `docs/agent-sequence.png` for manager app details.

2. Resolve the manager directory.
   Prefer `DEPLOYMENT_MANAGER_ROOT` when set. Otherwise use `$HOME/code/openai-cookbook/examples/agents_sdk/deployment_manager`. If the cookbook checkout is missing, clone `https://github.com/openai/openai-cookbook`. If it exists, update it with `git pull --ff-only` unless the user asked to avoid updating local checkouts. Stop and report local changes or diverged history instead of forcing the checkout. Verify `$MANAGER_DIR/Makefile` exists before deploying.

3. Deploy through the manager:

   ```bash
   make -C "$MANAGER_DIR" deploy PROJECT_PATH=<absolute-app-path>
   ```

   Useful options:

   ```bash
   make -C "$MANAGER_DIR" deploy PROJECT_PATH=/path/to/app APP_PORT=8421
   make -C "$MANAGER_DIR" deploy PROJECT_PATH=/path/to/app TARGET=local-process
   make -C "$MANAGER_DIR" deploy PROJECT_PATH=/path/to/app SANDBOX_BACKEND=docker
   make -C "$MANAGER_DIR" start
   make -C "$MANAGER_DIR" health
   ```

4. Let the manager own extraction and deployment records.
   The helper imports the project, creates or reuses a matching deployment, starts it, and prints JSON with `manager_url`, `deployment`, and `app_url`. For `local-docker`, it may generate or reuse an app-level `Dockerfile`. If that changes the app worktree, report it and do not revert user files.

5. Verify the result.
   Check manager health, the app `/health` readiness endpoint, and deployment sessions/containers when available.

   ```bash
   curl -fsS http://127.0.0.1:8732/api/health
   curl -fsS <app-url>/health
   curl -fsS http://127.0.0.1:8732/api/deployments/<deployment-id>/sessions
   curl -fsS http://127.0.0.1:8732/api/deployments/<deployment-id>/containers
   ```

   Run `git -C <app-path> status --short` when the app path is inside a git checkout so generated Dockerfiles or other local edits are visible.

## Done Criteria

Before handing back:

- the app has a clear local run command and smoke result, or a clear blocker;
- deployment was attempted when requested and the manager/app URLs are reported;
- any missing credentials, model access, port conflicts, Docker issues, or layout warnings are explicit;
- generated app files, eval files, and deployment-generated files are separated in the summary.
