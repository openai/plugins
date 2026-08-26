# Codex Security Config Preflight

Codex Security Standard and diff scan skills should run the read-only helper before substantive scan work. Deep scans have no parent capability requirements and do not run this helper.

Resolve `<python_command>` to the configured Python interpreter (`$PYTHON` when one is provided), otherwise use `python` on Windows and `python3` on Unix-like hosts. Before constructing the first helper command, inspect the current tool surface once and use that discovery result for both the runtime checks and `<verified-multi-agent-runtime-arguments>`. Do not omit active runtime facts from the first invocation and wait for an `incomplete` result before supplying them. The command is written on one line so it works in PowerShell, Command Prompt, and POSIX shells:

```text
<python_command> <plugin_dir>/scripts/config_preflight.py --profile <capability-profile> --cwd <scan-working-directory> --runtime-check delegation_available=<true|false> <verified-multi-agent-runtime-arguments>
```

Determine the runtime-check values from the current tool surface. Delegation tools may be deferred instead of appearing in the initial active tool list. If `tool_search` is available and delegation tools are not already active, search for subagent or multi-agent tools before passing `--runtime-check delegation_available=false`. Pass `false` only after tool discovery fails to expose a usable delegation tool. The `security_diff_scan` profile additionally retains its existing `--runtime-check goal_tools_available=<true|false>`; Standard and Deep profiles do not inspect or require goal tools. Consume the discovered tool namespace as runtime evidence too: when the current tool surface exposes `multi_agent_v1`, replace `<verified-multi-agent-runtime-arguments>` with `--multi-agent-runtime-owner native --multi-agent-runtime-version v1 --multi-agent-runtime-provenance tool-surface`. Do not pass a V2 session cap for V1. For other runtimes, use the verified owner, version, capacity when required, and provenance described below. When static config fully describes the active mode and no session-selected runtime overrides it, remove the placeholder. When the runtime exposes a more accurate effective config value than the user's base config file, add `--effective-config <path>=<json-value>`.

For standard and diff scans, a passed `delegated_workers` check means the runtime supports delegated review and the explicitly invoked scan authorizes it; a worker-slot result is the configured maximum, not a promise that every worker will start. If the runtime forbids delegation, pass `delegation_available=false`, continue on the documented parent fallback, and do not describe configured slots as running workers or reduced coverage.

When `CODEX_SECURITY_CONFIG_PATH` is set, add `--config "$CODEX_SECURITY_CONFIG_PATH"` to the helper command. The CLI provides this sanitized, shell-readable copy of the active worker configuration because the credential-bearing `CODEX_HOME` is intentionally inaccessible to repository-influenced commands. Do not substitute an ambient Codex home in that case.

Otherwise, the helper discovers Codex config paths itself from `--cwd`, which defaults to the current working directory. It reads `/etc/codex/config.toml` on Unix-like hosts or `%ProgramData%\OpenAI\Codex\config.toml` on Windows, then `$CODEX_HOME/config.toml`, resolves `project_root_markers`, checks the matching `[projects."<absolute-project-root>"].trust_level`, and loads trusted project `.codex/config.toml` layers from the project root down to `--cwd`. It does not load project layers unless the user config marks that project root as `trusted`.

When the current Codex CLI session selected `-p/--profile <name>`, pass `--codex-config-profile <name>`. Current Codex loads `$CODEX_HOME/<name>.config.toml` above the base user config and below trusted project config, so the helper uses that layer for project-root markers, trust, and capability values before it discovers project config. A missing profile file is an empty layer, matching the CLI. Embedded `[profiles.<name>]` lookup remains only for older Codex configs that select `profile` without the CLI flag. Project-local `profile` and `profiles` values are ignored. For session-only CLI overrides or other effective config values that cannot be recovered from config paths, pass `--effective-config <path>=<json-value>`.

For targeted tests or unusual runtimes, repeated `--config <path>` arguments override automatic discovery. Pass those manual layers from lower to higher precedence.

In Codex CLI, run the helper directly in the parent even when delegation is available. This keeps the exact command, exit code, and JSON result in the CLI event stream and avoids attributing an unobservable child result to the active runtime. In other hosts with delegation, run preflight in one dedicated worker before substantive scan work. Dispatch means a successful worker-spawn tool call that returns a concrete worker or thread id. Do not claim that a worker is running, or call a generic wait with no receiver, unless that spawn succeeded. Wait for the specific returned id and accept a result only from that worker. If spawning fails or returns no id, run the helper directly in the parent and report the spawn failure; never invent or reconstruct a helper result. The worker should return only a compact summary: the executed command and exit code, overall status, unmet or unknown capabilities, the returned `user_config_path`, and applicable remediation. Include the source path for any conflicting setting. Do not return the helper's raw JSON unless the parent needs it to resolve an ambiguity. This keeps preflight inspection out of the primary scan context.

The parent should pass only the runtime facts the worker cannot establish itself, such as a selected config profile or effective runtime-only config values. If delegation is unavailable after tool discovery, run the helper directly in the parent so the preflight can report the degraded or blocked path.

Multi-agent config mode is auto-detected when static config fully describes it. Model- or session-selected runtimes must additionally supply the verified runtime facts exposed by the active session. Keep protocol, owner, cap, and provenance separate:

```text
--multi-agent-runtime-owner native --multi-agent-runtime-version v2 --multi-agent-session-cap <count> --multi-agent-runtime-provenance <app-server|thread-context|tool-surface>
```

The V2 session cap includes the root thread. For profiles that evaluate current-session worker capacity, the helper subtracts that root thread when evaluating usable worker slots. For native V2 selected by static config, the documented Codex default session cap is four when no explicit cap is configured. Do not apply that static default to model- or session-selected V2 when a profile needs the active capacity: pass the observed runtime cap, or the result remains `incomplete`.

When the active session is actually managed by `codex_bridge`, provide explicit verified ownership. A backend config value alone is not ownership evidence:

```text
--multi-agent-runtime-owner codex-bridge --multi-agent-runtime-version v2 --multi-agent-runtime-provenance verified-bridge --effective-config multiagent_config.max_concurrency=<count>
```

Without `--multi-agent-runtime-owner codex-bridge` and `verified-bridge` provenance, passing `multiagent_config.max_concurrency` is an error. This prevents an assumed config value from reclassifying a native App session as bridge-owned.

Static native V2 accepts both `[features] multi_agent_v2 = true` and `[features.multi_agent_v2] enabled = true`. Native V2 cannot be combined with `agents.max_threads`; the helper rejects that invalid config. `agents.max_depth` applies to V1 only and is not required for V2. A runtime version and cap without verified ownership cannot produce `ready`. When runtime version, ownership, or capacity remains unknown, the helper returns `incomplete` where the selected profile needs that fact and omits unsafe concurrency patches.

The helper reads the routed capability profile from `../preflight/capability-profiles.toml`, discovers the applicable Codex config paths from `--cwd`, applies documented defaults where the registry provides them, and prints one JSON result.

Use the helper result as the preflight source of truth. Do not independently reinterpret profile requirements or compare raw config text for exact equality.

Interpret requirement severities this way:

- `block`: the requested workflow cannot be claimed honestly when unmet
- `warn`: the workflow can continue only with the documented degraded path
- `suggest`: the workflow can continue, but Codex should mention the improvement when it materially affects long-running scan quality or resumability

When a requirement is config-backed, compare the effective resolved value when the runtime exposes it. When the runtime does not expose an effective value, fall back to the loaded config value and documented Codex default from the profile when one is present.

When the profile includes remediation patches, present the concrete config delta. In an interactive session, ask before editing persistent user config. If the user approves, edit only the helper's `user_config_path`; never infer `~/.codex/config.toml` or another Codex home. A conflicting value from a higher-precedence project or profile layer must be resolved in the source reported by the helper rather than hidden with a lower-precedence edit. In a non-interactive session, follow the narrow automatic-remediation path below instead of waiting for an answer the runtime cannot provide. Never rewrite config beyond the helper's concrete patches.

Some remediation patches have `kind = "host_setting"`. Present those as host-level setup guidance, not as edits to persistent Codex config.

Deep Security Scan uses MCP-owned SDK sessions rather than the parent thread's worker pool. Its preflight does not require a particular parent delegation runtime, ownership, capacity, or depth. Discovery workers inherit the scan's model and use the reserved `codex_security_deep_scan_worker` permission profile with the parent's supported filesystem denials. The selected Codex executable must support permission-profile configuration and allowance checks. If that command fails to start or exits early, report its path and the tool's diagnostic; do not infer that its version is unsupported. If the tool identifies a missing API, ask the user to update the Codex installation at the reported path: the desktop app for an app-bundled executable, or the selected CLI otherwise. If Codex policy rejects the profile, report the tool's administrator guidance. Do not remove deny rules or select a broader sandbox to work around the error.

Do not warn merely because a user's value differs from the profile's suggested patch. Warn or block only when the evaluated capability requirement is unmet.

If a runtime capability is `unknown`, establish it from the current tool surface and rerun the helper with an explicit `--runtime-check`. Do not treat an `incomplete` result or unknown value as evidence that the capability is available.

## Readiness, Remediation, And Recovery

Continue only after a `ready` result. Explain material warnings and use the documented degraded path. For a blocked, incomplete, or error result, report the exact reason and preserve any durable running scan while recovery remains possible; do not review source or start workers early.

Classify the current session before requesting remediation. Treat `codex exec`, headless runs, automation, and any host that cannot actually pause for a human answer as non-interactive. In an interactive session, show the exact blocker and helper-provided config change, ask before editing persistent configuration, and wait for an explicit answer. Prefer native `request_user_input`; use ordinary chat when that tool is unavailable. A confirmed desktop host follows its additional remediation and progress rules in `desktop-config-preflight.md`.

In a non-interactive session, never request user input. Automatically apply only the helper's concrete `value` or `remove` patches to its writable `user_config_path`, preserving unrelated settings; never apply `host_setting` patches automatically. Rerun once with the same verified runtime facts and continue only if the result is `ready`. If remediation is unavailable, needs a new session, remains blocked, or errors, report the blocker without looping, canceling, or marking the scan failed; preserve a durable scan for later continuation.

Cancel only when the user explicitly chooses cancellation. Call `fail_codex_security_scan` only after the documented recovery path is exhausted and the blocker is confirmed unrecoverable. Desktop onboarding and progress details are host-specific: load `desktop-config-preflight.md` only after the host explicitly identifies itself as the desktop app.

## TAC Status Advisory

After capability preflight is `ready` and immediately before the workflow's first substantive scan action, use the hosted Codex Security Access app [$codex-security-access](app://connector_openai_codex_security_access) to call its `get_tac_status` action exactly once as the automatic pre-scan advisory. For Deep Security Scan, make this call immediately before `start_codex_security_deep_scan`. If this scan already performed the automatic advisory in an earlier continuation, reuse that result instead of calling it again. Report its exact `status` and TAC grant levels. When `status` is `not_granted`, before any other scan-start progress, present a separate, prominent warning that TAC access is not granted for this account and protected scan outputs may not be displayable. Include the returned `enrollmentUrl` as a clickable application link; if that field is absent, use `https://chatgpt.com/cyber`. Do not bury this warning in a routine status summary. When `status` is `unknown`, or the app or action is unavailable, instead warn that TAC access could not be verified and protected scan outputs may not be displayable. Then continue regardless. This result is advisory and must never authorize or gate the scan. Do not poll it or repeat it between scan phases. If the user explicitly asks to re-check after an account or TAC access change, call the action again for a fresh result; this user-requested refresh is the only repeat.
