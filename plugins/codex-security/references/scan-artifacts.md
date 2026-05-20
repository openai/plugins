# Scan Artifact Paths

Use these shared path conventions for Codex Security scan workflows unless the user explicitly provides different input or output paths.

## Base Paths

- `repo_name=<basename of repo_root>`
- `security_scans_dir=/tmp/codex-security-scans/<repo_name>`
- `scan_id=<commit>_<scan timestamp>`
- `scan_dir=<security_scans_dir>/<scan_id>`
- `artifacts_dir=<scan_dir>/artifacts`

## Threat Model (Phase 1) Paths

- Repository-scoped threat model: `<security_scans_dir>/threat_model.md`
- Per-scan threat model copy: `<artifacts_dir>/threat_model.md`
- Later scan phases should treat `<artifacts_dir>/threat_model.md` as the source of truth.
- When a repository-scoped threat model already exists, copy it to `<artifacts_dir>/threat_model.md` without alteration for auditability.

## Finding Discovery (Phase 2) Paths

### Coverage Planning

- Advisory seed research: `<artifacts_dir>/seed_research.md`
- Scoped ranking input: `<artifacts_dir>/rank_input.csv` if applicable
- Scoped ranking output: `<artifacts_dir>/rank_output.csv` if applicable
- Scoped deep-review input: `<artifacts_dir>/deep_review_input.csv` if applicable
- Finding discovery report: `<artifacts_dir>/finding_discovery_report.md`

### Deep Review

- Scoped work ledger: `<artifacts_dir>/work_ledger.jsonl` if applicable
- Scoped raw candidates: `<artifacts_dir>/raw_candidates.jsonl` if applicable

### Candidate Reconciliation

- Candidate findings directory: `<artifacts_dir>/findings/`
- Per-finding directory: `<artifacts_dir>/findings/<candidate_id>/`
- Per-finding candidate ledger: `<artifacts_dir>/findings/<candidate_id>/candidate_ledger.jsonl`
- Scoped dedupe report: `<artifacts_dir>/dedupe_report.md` if applicable
- Scoped deduped candidates: `<artifacts_dir>/deduped_candidates.jsonl` if applicable
- Repository-wide coverage ledger: `<artifacts_dir>/repository_coverage_ledger.md`
  - This is a coverage artifact, not a findings list: it should include checked surfaces with not_applicable, suppressed, deferred, or reportable dispositions.

## Validation (Phase 3) Paths

- Per-finding validation report: `<artifacts_dir>/findings/<candidate_id>/validation_report.md`
- Per-finding validation artifacts: `<artifacts_dir>/findings/<candidate_id>/validation_artifacts/`

## Attack-Path Analysis (Phase 4) Paths

- Per-finding attack-path analysis report: `<artifacts_dir>/findings/<candidate_id>/attack_path_analysis_report.md`

## Final Report Paths

- Final scan report: `<scan_dir>/report.md`

## Fix Finding Paths

- Fix report, when using an existing scan artifact directory: `<artifacts_dir>/fix_report.md`

## Placement Rules

- Put phase outputs and supporting evidence under `artifacts_dir`.
- Put the final `report.md` directly under `scan_dir`.
- Keep the full scan bundle together under `scan_dir`.
