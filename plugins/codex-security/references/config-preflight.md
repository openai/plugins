# Codex Security Config Preflight

Codex Security top-level scan skills should run the read-only helper before substantive scan work:

Resolve `<python_command>` to the configured Python interpreter (`$PYTHON` when one is provided), otherwise use `python` on Windows and `python3` on Unix-like hosts. The command is written on one line so it works in PowerShell, Command Prompt, and POSIX shells:

```text
<python_command> <plugin_dir>/scripts/config_preflight.py --profile <capability-profile> --cwd <scan-working-directory> --runtime-check delegation_available=<true|false> --runtime-check goal_tools_available=<true|false> --available-plugin-skill <skill-name>
```

Determine the runtime-check values from the current tool surface. Delegation tools may be deferred instead of appearing in the initial active tool list. If `tool_search` is available and delegation tools are not already active, search for subagent or multi-agent tools before passing `--runtime-check delegation_available=false`. Pass `false` only after tool discovery fails to expose a usable delegation tool. When the runtime exposes a more accurate effective config value than the user's base config file, add `--effective-config <path>=<json-value>`.

The helper discovers Codex config paths itself from `--cwd`, which defaults to the current working directory. It reads `/etc/codex/config.toml`, then `$CODEX_HOME/config.toml`, resolves `project_root_markers`, checks the matching `[projects."<absolute-project-root>"].trust_level`, and loads trusted project `.codex/config.toml` layers from the project root down to `--cwd`. It does not load project layers unless the user config marks that project root as `trusted`.

When the current Codex CLI session selected `-p/--profile <name>`, pass `--codex-config-profile <name>`. Current Codex loads `$CODEX_HOME/<name>.config.toml` above the base user config and below trusted project config, so the helper uses that layer for project-root markers, trust, and capability values before it discovers project config. A missing profile file is an empty layer, matching the CLI. Embedded `[profiles.<name>]` lookup remains only for older Codex configs that select `profile` without the CLI flag. Project-local `profile` and `profiles` values are ignored. For session-only CLI overrides or other effective config values that cannot be recovered from config paths, pass `--effective-config <path>=<json-value>`.

For targeted tests or unusual runtimes, repeated `--config <path>` arguments override automatic discovery. Pass those manual layers from lower to higher precedence.

Repeat `--available-plugin-skill <skill-name>` only for skills from the capability's plugin when the selected profile checks skill dependencies. For the `deep_security_scan` profile, expose only the plugin-local names of available `codex-security` skills, such as `security-scan`; do not pass unrelated session skills. Use the current session's Available skills surface, not files found on disk. The helper reports unavailable skills as a runtime problem and a missing runtime plugin skill list as `incomplete`.

In Codex CLI, run the helper directly in the parent even when delegation is available. This keeps the exact command, exit code, and JSON result in the CLI event stream and avoids attributing an unobservable child result to the active runtime. In other hosts with delegation, run preflight in one dedicated worker before substantive scan work. Dispatch means a successful worker-spawn tool call that returns a concrete worker or thread id. Do not claim that a worker is running, or call a generic wait with no receiver, unless that spawn succeeded. Wait for the specific returned id and accept a result only from that worker. If spawning fails or returns no id, run the helper directly in the parent and report the spawn failure; never invent or reconstruct a helper result. The worker should return only a compact summary: the executed command and exit code, overall status, unmet or unknown capabilities, and applicable remediation. Do not return the helper's raw JSON unless the parent needs it to resolve an ambiguity. This keeps preflight inspection out of the primary scan context.

The parent should pass only the runtime facts the worker cannot establish itself, such as a selected config profile or effective runtime-only config values. If delegation is unavailable after tool discovery, run the helper directly in the parent so the preflight can report the degraded or blocked path.

Multi-agent config mode is auto-detected when static config fully describes it. Model- or session-selected runtimes must additionally supply the verified runtime facts exposed by the active session. Keep protocol, owner, cap, and provenance separate:

```text
--multi-agent-runtime-owner native --multi-agent-runtime-version v2 --multi-agent-session-cap <count> --multi-agent-runtime-provenance <app-server|thread-context|tool-surface>
```

The V2 session cap includes the root thread. The helper subtracts that root thread when evaluating usable worker slots. A recommended eight-worker setup therefore uses a session cap of nine. For native V2 selected by static config, the documented Codex default session cap is four when no explicit cap is configured. Do not apply that static default to model- or session-selected V2: pass the observed runtime cap, or the result remains `incomplete`.

When the active session is actually managed by `codex_bridge`, provide explicit verified ownership. A backend config value alone is not ownership evidence:

```text
--multi-agent-runtime-owner codex-bridge --multi-agent-runtime-version v2 --multi-agent-runtime-provenance verified-bridge --effective-config backend_config.max_multiagent_concurrency=<count>
```

Without `--multi-agent-runtime-owner codex-bridge` and `verified-bridge` provenance, passing `backend_config.max_multiagent_concurrency` is an error. This prevents an assumed backend value from reclassifying a native App session as bridge-owned.

Static native V2 accepts both `[features] multi_agent_v2 = true` and `[features.multi_agent_v2] enabled = true`. Native V2 cannot be combined with `agents.max_threads`; the helper rejects that invalid config. `agents.max_depth` applies to V1 only and is not required for V2. A runtime version and cap without verified ownership cannot produce `ready`. When runtime version, ownership, or capacity remains unknown, the helper returns `incomplete` where the selected profile needs that fact and omits unsafe concurrency patches.

The helper reads the routed capability profile from `../preflight/capability-profiles.toml`, discovers the applicable Codex config paths from `--cwd`, applies documented defaults where the registry provides them, and prints one JSON result.

Use the helper result as the preflight source of truth. Do not independently reinterpret profile requirements or compare raw config text for exact equality.

Interpret requirement severities this way:

- `block`: the requested workflow cannot be claimed honestly when unmet
- `warn`: the workflow can continue only with the documented degraded path
- `suggest`: the workflow can continue, but Codex should mention the improvement when it materially affects long-running scan quality or resumability

When a requirement is config-backed, compare the effective resolved value when the runtime exposes it. When the runtime does not expose an effective value, fall back to the loaded config value and documented Codex default from the profile when one is present.

When the profile includes remediation patches, present the concrete config delta and ask before editing persistent user config. Do not silently rewrite `~/.codex/config.toml` from a scan skill.

Some remediation patches have `kind = "host_setting"`. Present those as host-level setup guidance, not as edits to persistent Codex config.

Native V2 remediation removes `agents.max_threads`, sets `features.multi_agent_v2.enabled = true`, and then sets the V2 session cap. Codex rejects the legacy V1 thread setting and explicit V2 mode together.

Do not warn merely because a user's value differs from the profile's suggested patch. Warn or block only when the evaluated capability requirement is unmet.

If a runtime capability is `unknown`, establish it from the current tool surface and rerun the helper with an explicit `--runtime-check`. Do not treat an `incomplete` result or unknown value as evidence that the capability is available.

## MCP App onboarding handoff

The onboarding workspace opens before capability preflight and does not display or enforce configuration capability results. If `open_codex_security_workspace` returns a workspace with `setup.submitted=false`, that is the app setup wait state. Do not run this helper, do not call `set_codex_security_capability_preflight`, do not create or adopt a scan goal, and do not reclassify the scan as terminal/chat fallback merely because no `scanId` exists yet. Stop and wait for the user to review setup and press Start scan.

After the user submits setup and the app-generated handoff provides a `scanId`, load the authoritative scan context with `get_codex_security_scan_context`, then run this preflight for the validated target and selected scan mode. The dedicated preflight worker described above is allowed and should finish before goal setup, threat modeling, scan/discovery worker creation, or other substantive analysis.

Continue after a `ready` result. Explain warn or suggest issues when they materially affect scan quality, capacity, or resumability, and use the documented degraded path. If the result is `blocked` or `incomplete`, follow the remediation handling below. If the helper cannot run or returns its top-level `status: "error"` envelope, report the exact blocker and retry the documented recovery path when possible. Do not call `fail_codex_security_scan` merely because the helper is temporarily unavailable or errors; leave the durable scan running and hand off for a later retry while recovery may still be possible.

When blocked or incomplete preflight includes actionable remediation, present the exact reasons and config delta in the Codex thread, ask whether to apply the remediation, and stop for the user's answer before creating or adopting a scan goal. Do not call `fail_codex_security_scan` while waiting for that answer. For any non-ready result, do not fail automatically. If the user declines required remediation, explain that the scan cannot continue under the current configuration and ask whether to cancel or leave it running for a later retry. If remediation is unavailable, the helper cannot run, the helper returns an error envelope, or a rerun remains blocked or incomplete, preserve the running scan and retry or hand off while recovery may still be possible. Call `fail_codex_security_scan` with the exact reasons only after the documented recovery path is exhausted and the blocker is confirmed unrecoverable, or when the user explicitly cancels.

Present applicable remediation in the Codex thread and ask before editing persistent user configuration. Do not pass capability preflight to `open_codex_security_workspace`, depend on the setup UI to display it, or require `set_codex_security_capability_preflight` before the user can start a scan.

Codex CLI and hosts without MCP Apps use the same prompt-based preflight before substantive work. This fallback applies only when the host cannot use the setup app at all; once an app workspace has opened, remain on the app handoff path until the user submits setup or cancels it. Explain the exact reasons and remediation in chat and ask before editing persistent config.
