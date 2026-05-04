# Repository-Wide Review Guidance

Use this guidance when the security scan target is the entire checked-out repository.

## Required References

Before repository-wide discovery or validation, read this file and all of these same-directory references in order. They are mandatory extensions of this workflow, not optional background:

1. `repo-wide-artifacts-and-ledger.md` for runtime inventory, seed research, exhaustive file checklist, coverage ledger, subagent/file-pass, and closure artifact rules.
2. `repo-wide-high-impact-families.md` for high-impact vulnerability family heuristics and exact suppression boundaries.
3. `repo-wide-instance-expansion.md` for child-instance splitting, wrapper/root-control preservation, and per-operation reporting.
4. `repo-wide-validation-closure.md` for validation/report closure, deferred rows, secondary issue ordering, and false-positive controls.

Do not treat `repository-wide-scan.md` alone as the complete repo-wide scan procedure.

## Exhaustive Mode

Use an exhaustive instance-finding workflow rather than the diff-scan workflow's representative-finding bias.

Repository-wide scans must:

- Load the per-scan threat model path from `../../../references/scan-artifacts.md` as the repo-specific threat-model source of truth.
- Build an entrypoint and trust-boundary inventory before validation: routes, handlers, templates, serializers, deserializers, query builders, shell/process calls, file/path APIs, network fetches/callbacks, auth/authz middleware, session/cookie config, secret/config sources, IaC or policy resources, and agent/tool boundaries.
- Create `runtime_inventory.md`, `seed_research.md` when seed hints exist, `exhaustive-file-checklist.md`, and `repository_coverage_ledger.md` using the artifact paths from `../../../references/scan-artifacts.md`.
- Create a high-impact coverage ledger before deep validation. The ledger is a coverage artifact, not a list of potential findings, and must include rows without candidates as well as reportable candidates.
- Keep every applicable high-impact, user-seeded, advisory-seeded, or tag-seeded row open until that exact area is closed as `reportable`, `suppressed`, `not_applicable`, or `deferred` with exact evidence or proof-gap reasons.
- Enumerate every technically distinct high-impact vulnerable instance discovered under those families, not just one representative example per class.
- Preserve the line where the security control actually fails, including unsafe split/parse/canonicalize/normalize/compare/regex/selection/object-binding lines that create a bypass or feed a sink.
- Suppress a candidate only with exact counterevidence for that instance, such as a specific sanitizer, permission check, tenant filter, escaping context, safe parser/loader, path canonicalization check, egress allowlist, or deployment constraint that defeats the claimed source/sink path.

## Discovery Execution

During finding discovery, apply this repository-wide workflow instead of the diff-centered discovery workflow. Use `../../finding-discovery/SKILL.md` for the candidate output contract and `../../../references/scan-artifacts.md` for repository-wide artifact paths.

Run this broader but still bounded workflow:

1. Read the required references listed above.
2. Build and save `runtime_inventory.md` from entrypoints, trust boundaries, security-sensitive configuration, and product/runtime areas.
3. Build `exhaustive-file-checklist.md` before fan-out. Each line must start with `- [ ] ` and cannot be checked until the file has been fully read and reviewed.
4. Run advisory/seed research when the user or scan context includes CVE, GHSA, advisory, issue, release, package-version, or vulnerability-family identifiers. Save `seed_research.md` and create exact seed-target ledger rows.
5. Build and save `repository_coverage_ledger.md` with one row per applicable boundary and serious vulnerability family before deep validation begins.
6. Run one frontier pass across every applicable high-impact shard before prolonged validation or build/debug work on any single shard.
7. Run targeted control-hazard searches for parser/helper, deserializer, auth/token/assertion, protocol/version, and polymorphic-operation shards using `repo-wide-high-impact-families.md`.
8. Run high-impact fan-out passes before any secondary review. When one vulnerable pattern is found, search sibling files, routes, templates, handlers, models, and config variants before moving on.
9. When a high-impact instance flows through a wrapper into a shared parser, deserializer, path/archive helper, expression evaluator, or auth/authz control, record both the reachable wrapper and the underlying shared sink/control.
10. Iterate over every file in the in-scope checklist, using subagents when available as described in `repo-wide-artifacts-and-ledger.md`.
11. Split broad families and repeated same-family operations into child instances using `repo-wide-instance-expansion.md`.
12. Treat data exposure, hardcoded secrets, weak session/cookie/security config, CSRF, rate limits, and plaintext storage as secondary. Include them only after the high-impact ledger and file list are exhausted or when they directly enable code execution, injection, privilege escalation, meaningful auth bypass, or sensitive cross-boundary impact.
13. Preserve each validated or suppressed instance through validation, attack-path analysis, and final reporting using `repo-wide-validation-closure.md`.
