# Scan Artifact Paths

Use these shared path conventions for Codex Security scan workflows unless the user explicitly provides different input or output paths.

## Base Paths

- `plugin_dir=<codex-security plugin root>`
- `repo_name=<basename of repo_root>`
- `system_temp_dir=<platform temporary directory>`
- `security_scans_dir=<system_temp_dir>/codex-security-scans/<repo_name>`
- `scan_id=<commit>_<scan timestamp>`
- `scan_dir=<security_scans_dir>/<scan_id>`
- `artifacts_dir=<scan_dir>/artifacts`
- `context_dir=<artifacts_dir>/01_context`
- `discovery_dir=<artifacts_dir>/02_discovery`
- `coverage_dir=<artifacts_dir>/03_coverage`
- `reconciliation_dir=<artifacts_dir>/04_reconciliation`
- `findings_dir=<artifacts_dir>/05_findings`

The MCP app resolves the platform temporary directory automatically. For a manual workflow, use the active process temporary directory (for example, `%TEMP%` on Windows or `$TMPDIR` when configured on Unix-like hosts) instead of hardcoding `/tmp`.

Resolve `<python_command>` to the configured Python interpreter (`$PYTHON` when one is provided), otherwise use `python` on Windows and `python3` on Unix-like hosts.

## Threat Model (Phase 1) Paths

- Repository-scoped threat model: `<security_scans_dir>/threat_model.md`
- Per-scan threat model copy: `<context_dir>/threat_model.md`
- Later scan phases should treat `<context_dir>/threat_model.md` as the source of truth.
- When a repository-scoped threat model already exists, copy it to `<context_dir>/threat_model.md` without alteration for auditability.

## Finding Discovery (Phase 2) Paths

### Coverage Planning

- Advisory seed research: `<context_dir>/seed_research.md`
- Scoped ranking input: `<discovery_dir>/rank_input.jsonl` if applicable
- Scoped ranking shards: `<discovery_dir>/rank_shards/rank-shard-NNNN.input.jsonl` and matching worker-local `.output.jsonl` files if ranking applies
- Scoped ranking output: `<discovery_dir>/rank_output.jsonl` if applicable
- Scoped deep-review input: `<discovery_dir>/deep_review_input.jsonl` if applicable
- Finding discovery report: `<discovery_dir>/finding_discovery_report.md`

### Deep Review

- Scoped work ledger: `<discovery_dir>/work_ledger.jsonl` if applicable
- Scoped raw candidates: `<discovery_dir>/raw_candidates.jsonl` if applicable

### Candidate Reconciliation

- Candidate findings directory: `<findings_dir>/`
- Per-finding directory: `<findings_dir>/<candidate_id>/`
- Per-finding candidate ledger: `<findings_dir>/<candidate_id>/candidate_ledger.jsonl`
- Scoped dedupe report: `<reconciliation_dir>/dedupe_report.md` if applicable
- Scoped deduped candidates: `<reconciliation_dir>/deduped_candidates.jsonl` if applicable

### Coverage

- Repository-wide coverage ledger: `<coverage_dir>/repository_coverage_ledger.md`
  - This is a coverage artifact, not a findings list: it should include checked surfaces with not_applicable, suppressed, deferred, or reportable dispositions.
- Reviewed surfaces summary: `<coverage_dir>/reviewed_surfaces.md` if applicable

## Validation (Phase 3) Paths

- Scan-level validation summary: `<findings_dir>/validation_summary.md` if applicable
- Per-finding validation report: `<findings_dir>/<candidate_id>/validation_report.md`
- Per-finding validation artifacts: `<findings_dir>/<candidate_id>/validation_artifacts/`

## Attack-Path Analysis (Phase 4) Paths

- Scan-level attack-path analysis report: `<findings_dir>/attack_path_analysis_report.md` if applicable
- Per-finding attack-path analysis report: `<findings_dir>/<candidate_id>/attack_path_analysis_report.md`

## Final Report Paths

- Final scan report: `<scan_dir>/report.md`
- Final report validation notes, when validation fails: `<scan_dir>/report_validation.md`

## Fix Finding Paths

- Fix report, when using an existing scan artifact directory: `<artifacts_dir>/fix_report.md`

## Placement Rules

- Put scan phase outputs and supporting evidence under the numbered artifact subdirectories above.
- Keep fix-finding outputs outside the numbered scan phases because fix-finding can run standalone or against an existing scan.
- Do not author the final report directly. Put complete report semantics in the canonical JSON files; finalization deterministically writes the unsealed `report.md` projection directly under `scan_dir` after validating and sealing the canonical JSON and evidence artifacts.
- Keep the full scan bundle together under `scan_dir`.
