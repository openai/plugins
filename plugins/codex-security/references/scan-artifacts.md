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

- Runtime inventory: `<artifacts_dir>/runtime_inventory.md`
- Advisory seed research: `<artifacts_dir>/seed_research.md`
- Finding discovery report: `<artifacts_dir>/finding_discovery_report.md`
- Repository-wide exhaustive file checklist: `<artifacts_dir>/exhaustive-file-checklist.md` if applicable
- Repository-wide coverage ledger: `<artifacts_dir>/repository_coverage_ledger.md`
  - This is a coverage artifact, not a findings list: it should include checked surfaces with not_applicable, suppressed, deferred, or reportable dispositions.

## Validation (Phase 3) Paths

- Validation report: `<artifacts_dir>/validation_report.md`
- Validation artifacts: `<artifacts_dir>/validation_artifacts/`

## Attack-Path Analysis (Phase 4) Paths

- Attack-path analysis report: `<artifacts_dir>/attack_path_analysis_report.md`

## Final Report Paths

- Final scan report: `<scan_dir>/report.md`

## Fix Finding Paths

- Fix report, when using an existing scan artifact directory: `<artifacts_dir>/fix_report.md`

## Placement Rules

- Put phase outputs and supporting evidence under `artifacts_dir`.
- Put the final `report.md` directly under `scan_dir`.
- Keep the full scan bundle together under `scan_dir`.
