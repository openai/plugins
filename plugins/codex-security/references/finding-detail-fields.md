# Rich Finding Detail Fields

For every reportable finding in `findings.json`, preserve the validated reasoning and the exact source snippets that prove it. The Codex Security workspace renders these fields directly; it does not recover missing analysis from `report.md` or read source files after the scan.

## Writing Rules

- Wrap RPC names, functions, types, fields, parameters, configuration keys, literal identifiers, and short expressions in single backticks. For example: `environment/add`, `environmentId`, `execServerUrl`, and `EnvironmentManager::upsert_environment()`.
- Keep code out of prose. Put source snippets in `codeEvidence[].code`, then reference them from the section that explains why the snippet matters.
- Give each code-evidence item a stable `id`, a concise `label`, an exact source location, the smallest useful snippet, and an `explanation` that connects the snippet to the finding.
- Do not use location-only filler such as "the root cause is tied to the broken control at path:line." The source table already records locations. Explain the violated invariant and show the code that violates it.
- Validation must connect attacker-controlled input, the missing or bypassed control, and the security-relevant state change or sink. Do not replace that proof with a list of file names and line numbers.
- Attack-path analysis must be concise. Record the realistic attacker boundary, the minimum trigger sequence, and the concrete outcome. Use code evidence for the important transitions instead of repeating the full validation narrative.
- Populate only evidence-backed fields. Omit unknown values instead of adding placeholders.

## Structured Example

The following shape shows how to encode the `environment/add` reserved-environment overwrite finding:

```json
{
  "summary": "The runtime `environment/add` method forwards caller-controlled `environmentId` and `execServerUrl` to `EnvironmentManager::upsert_environment()`. Startup rejects the reserved `local` identifier, but the runtime mutation path accepts it and replaces the map entry used by default environment lookup.",
  "codeEvidence": [
    {
      "id": "rpc-input",
      "label": "Caller-controlled environment fields",
      "path": "codex-rs/app-server-protocol/src/protocol/v2/environment.rs",
      "startLine": 6,
      "endLine": 12,
      "language": "rust",
      "code": "#[serde(rename_all = \"camelCase\")]\npub struct EnvironmentAddParams {\n    pub environment_id: String,\n    pub exec_server_url: String,\n}",
      "explanation": "`environmentId` and `execServerUrl` are accepted as caller-controlled strings."
    },
    {
      "id": "rpc-forward",
      "label": "RPC forwards both fields without validation",
      "path": "codex-rs/app-server/src/request_processors/environment_processor.rs",
      "startLine": 15,
      "endLine": 22,
      "language": "rust",
      "code": "self.environment_manager\n    .upsert_environment(params.environment_id, params.exec_server_url)\n    .map_err(|err| invalid_request(err.to_string()))?;",
      "explanation": "The handler passes both values directly to `upsert_environment()` and performs no reserved-ID check."
    },
    {
      "id": "startup-reserved-check",
      "label": "Startup protects the reserved local identifier",
      "path": "codex-rs/exec-server/src/environment.rs",
      "startLine": 167,
      "endLine": 176,
      "language": "rust",
      "code": "if id == LOCAL_ENVIRONMENT_ID {\n    return Err(ExecServerError::Protocol(format!(\n        \"environment id `{LOCAL_ENVIRONMENT_ID}` is reserved for EnvironmentManager\"\n    )));\n}",
      "explanation": "Initial environment construction enforces the invariant that `local` belongs to `EnvironmentManager`."
    },
    {
      "id": "runtime-upsert",
      "label": "Runtime upsert omits the reserved-ID check",
      "path": "codex-rs/exec-server/src/environment.rs",
      "startLine": 253,
      "endLine": 281,
      "language": "rust",
      "code": "if environment_id.is_empty() {\n    return Err(ExecServerError::Protocol(\n        \"environment id cannot be empty\".to_string(),\n    ));\n}\n// ... build remote environment ...\nself.environments\n    .write()\n    .unwrap_or_else(std::sync::PoisonError::into_inner)\n    .insert(environment_id, Arc::new(environment));",
      "explanation": "`upsert_environment()` rejects only an empty ID before inserting into the shared map. Passing `local` replaces the protected entry."
    },
    {
      "id": "default-lookup",
      "label": "Default selection reads the overwritten map entry",
      "path": "codex-rs/exec-server/src/environment.rs",
      "startLine": 205,
      "endLine": 210,
      "language": "rust",
      "code": "pub fn default_environment(&self) -> Option<Arc<Environment>> {\n    self.default_environment\n        .as_deref()\n        .and_then(|environment_id| self.get_environment(environment_id))\n}",
      "explanation": "Default lookup resolves the stored `local` ID through the mutable environment map, so the replacement affects later operations."
    }
  ],
  "rootCause": {
    "summary": "The violated invariant is that `local` must always identify the manager-owned local runtime. Startup enforces that invariant, but `EnvironmentManager::upsert_environment()` does not reuse the reserved-ID check and inserts a remote `Environment` under the caller-supplied key.",
    "evidenceRefs": [
      "startup-reserved-check",
      "runtime-upsert"
    ]
  },
  "validation": {
    "method": "static source trace",
    "summary": "The source trace confirms that an `environment/add` caller controls both inputs, the RPC forwards them unchanged, and runtime insertion accepts `local`.",
    "evidenceRefs": [
      "rpc-input",
      "rpc-forward",
      "runtime-upsert"
    ],
    "assertions": [
      "The runtime path lacks the reserved-ID check present during startup.",
      "Inserting `local` replaces the existing `HashMap` entry."
    ],
    "limitations": [
      "The finding was validated by source review; no live JSON-RPC reproduction was run."
    ]
  },
  "attackPath": {
    "summary": "A lower-trust app-server client opts into the experimental API, calls `environment/add` with `environmentId: \"local\"`, and points `execServerUrl` at an attacker-controlled executor. Later default environment selection resolves the replaced map entry.",
    "dataflow": {
      "summary": "`environment/add` parameters -> `environment_add()` -> `upsert_environment()` -> shared environment map -> `default_environment()`",
      "source": "caller-controlled `environmentId` and `execServerUrl`",
      "sink": "the shared environment map",
      "outcome": "default `local` selection resolves to the attacker-controlled remote executor"
    },
    "reachability": {
      "summary": "The attacker must be able to act as an app-server client and enable `experimentalApi`; default stdio and private Unix-socket transports reduce exposure.",
      "attacker": "lower-trust app-server client",
      "entrypoint": "experimental `environment/add` RPC",
      "outcome": "future operations selected for `local` are routed to the remote executor"
    },
    "evidenceRefs": [
      "rpc-forward",
      "runtime-upsert",
      "default-lookup"
    ],
    "impact": {
      "level": "medium",
      "why": "Later commands and filesystem requests selected for `local` can be routed to the attacker-controlled remote executor."
    },
    "likelihood": {
      "level": "medium",
      "why": "Exploitation requires access to the app-server client boundary and the experimental method."
    },
    "limitations": [
      "This overwrite does not directly execute code on the victim host."
    ]
  }
}
```

`rootCause.code` and `rootCause.language` remain supported for older producers that can provide only one snippet. New producers should use the shared `codeEvidence` catalog and section `evidenceRefs` so the same exact source can support Root Cause, Validation, and Attack-path analysis without copying it into several fields.
