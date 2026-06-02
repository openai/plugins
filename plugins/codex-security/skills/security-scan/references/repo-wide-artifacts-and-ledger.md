# Exhaustive Scan Artifacts And Ledger

Use this reference with `repository-wide-scan.md` for exhaustive repository or scoped-path ranking and coverage-ledger rules. Read `scan-artifacts-and-ledger.md` first for shared artifact, seed, subagent, scoped file-review, candidate-ledger, and dedupe rules.

## Exhaustive Scan Artifact Requirements

- Use the artifact paths from `../../../references/scan-artifacts.md` for `rank_input.csv`, `rank_output.csv` when ranking applies, `deep_review_input.csv`, `work_ledger.jsonl`, `raw_candidates.jsonl`, `dedupe_report.md`, `deduped_candidates.jsonl`, and `repository_coverage_ledger.md`.

## Exhaustive Scan Subagent Ownership

- Ranking-subagent ownership: one ranking subagent owns exactly one `rank_input.csv` row and returns only ranking JSON.
- Parent-agent ownership: the parent agent owns `rank_input.csv` generation when an upstream orchestrator did not already provide it, ranking-subagent dispatch when ranking is needed, `deep_review_input.csv` selection when an upstream orchestrator did not already provide it, global frontier/coverage work, and final exhaustive-scan closure.

## Files In Scope

- A parent orchestrator may provide authoritative in-scope worklists at the standard `<discovery_dir>/rank_input.csv` and `<discovery_dir>/deep_review_input.csv` paths before this workflow begins.
  - Treat the parent-provided worklists as authoritative only when the current scan instructions explicitly say they are authoritative and both files are present. A stale or partial artifact pair is not a valid scope contract.
  - When authoritative parent-provided worklists are present, use them exactly as supplied. Do not regenerate `rank_input.csv`, rerun ranking, overwrite `deep_review_input.csv`, or reinterpret `top-percent` inside this scan.
  - The parent orchestrator owns explaining whether its `deep_review_input.csv` is exhaustive or selected. This exhaustive workflow still owns full review receipts, candidate ledgers, coverage-ledger closure, and final closure for the supplied worklist.
- Otherwise, create a deterministic in-scope file worklist before subagent dispatch. Use `<plugin_dir>/scripts/generate_rank_input.py` to create `rank_input.csv`; do not ask the model to invent the file inventory.
  - Command shape: `python3 <plugin_dir>/scripts/generate_rank_input.py make-repo-rank-input --repo <repo_root> --scope <scope> --out <discovery_dir>/rank_input.csv`.
  - The generated CSV is the canonical candidate list for ranking subagents. It contains `path`, `area`, and `preview`.
  - The script only includes source-like text files and default-excludes tests, docs, examples, personal/dev-only trees, vendored trees, generated caches, and build artifacts unless the threat model explicitly makes one of those areas runtime-reachable or privilege-bearing.
  - If excluded content is added back manually, record the reason in the coverage ledger.
  - The Python script does not make the security ranking decision. Ranking is performed by ranking subagents over `rank_input.csv`.
- When authoritative parent-provided worklists are not present, convert the candidate list into the deep-review worklist:
  - Interpret `top-percent` as the percentage of ranked, included files that receive deep full-file audit.
  - If `top-percent` is below 100, dispatch ranking subagents with `spawn_agents_on_csv` on `<discovery_dir>/rank_input.csv`.
    - Ranking-subagent ownership: one ranking subagent owns exactly one `rank_input.csv` row. It decides only whether that file should enter deep review, and returns JSON with `path`, `include` true/false, `score` 1-10, and `reason`.
    - Ranking subagents do not perform deep review, validation, attack-path analysis, dedupe, or ledger closure.
  - Save ranking output to `<discovery_dir>/rank_output.csv`, then create `<discovery_dir>/deep_review_input.csv` with `select-deep-review-input`.
  - If `top-percent` is 100 or higher, skip ranking and copy every `rank_input.csv` row directly into `<discovery_dir>/deep_review_input.csv`.
  - Do not treat deterministic path order or broad grep hits as ranking evidence; the ranking-subagent output is the ranking source of truth.
- Deep-review every file selected into `deep_review_input.csv` using the shared scoped file-review rules in `scan-artifacts-and-ledger.md`.
- When `top-percent` is 100 or higher, or when an authoritative parent-provided worklist declares `deep_review_input.csv` exhaustive over `rank_input.csv`, do not stop until every `rank_input.csv` row has a completion receipt in the shared work ledger.

## Ranking Requirements

- Derive product and privileged surfaces from router declarations, OpenAPI or RPC metadata, public or anonymous endpoints, applied specs, ingress/service config, job/worker definitions, package exports, and privileged local or agent/tool surfaces before free-text sink search.
- Include HTTP, GraphQL, RPC, CLI, job, webhook, file-processing, message, template, package API, and agent/tool entrypoints; authn/authz/session middleware and decorators; database/query builders, ORM raw-query escapes, serializers/deserializers, shell/process/eval/template engines, filesystem APIs, network clients/fetchers, upload/download paths; first-party security/protocol namespaces such as SSO, SAML, OAuth, OIDC/JWT, LDAP, Kerberos, XML security, remoting, config import/export, protocol codecs, parser/converter registries, and version or feature gates.
- Rank files highly when they define, configure, or materially control those runtime/security surfaces; record the concrete surface in `reason`.
- Default-exclude tests, docs, examples, personal workspaces, lockfiles, vendored trees, generated caches, and one-off research tooling from the first pass unless repository evidence shows they are deployed, privilege-bearing, generated into shipped runtime code, or reachable from untrusted input. If excluded content is added back, record the reason in the ledger.

## Coverage Ledger

- Create a high-impact coverage ledger first across the vulnerability families most likely to produce serious bugs: command/code injection and RCE, SQL/NoSQL/LDAP/XPath/template injection, SSTI, unsafe deserialization, SSRF/callback abuse, path traversal/arbitrary file read or write, unsafe file upload, header injection/open redirect with credential or callback impact, and authz/tenant/object isolation bypasses that cross a meaningful privilege or data boundary.
- Build and save the ledger from the ranked runtime/security surfaces and deep-review evidence with one row per applicable boundary and serious vulnerability family before deep validation begins. The ledger must include: ledger row id, seed or root-control file:line when one is known, boundary, shard or area, files checked, applicable family, source or privileged boundary checked, sink/control checked, candidate ids when any were produced, disposition, evidence summary, prune reason or add-back trigger when applicable, and any deferred reason.
- Rows with no candidate are still required, seeded rows must close the exact seeded package/class family, and dominant runtime/product areas must have explicit rows or explicit repository-evidenced exclusions.
- For large repositories, partition the inventory into review shards by deployed or privileged area and vulnerability family before deep validation. A shard is a concrete boundary such as a service, router group, package API, parser family, job/worker family, deployment surface, CI/deploy path, or privileged local/agent tool surface.
- Shard by product module, package namespace, or protocol/security subsystem as well as by bug family. Do not let one reportable finding in a broad family close sibling modules such as separate SSO/SAML/OAuth/JWT, parser, protocol, config-import, or deserialization-wrapper packages.
- In a large monorepo, the coverage ledger must be materially broader than the promoted candidate list. If the ledger only contains candidate rows, only a handful of rows, or only global sink-count rows, the frontier pass is incomplete; add `not_applicable`, `suppressed`, or `deferred` rows for unresolved shards and families before continuing.
- The top product/runtime areas by tracked-file count or deployment significance must appear as shards in the ledger or be explicitly excluded with repository evidence. Global sink counts alone do not close coverage for a dominant area or family, and `no top candidate surfaced` is not a terminal disposition.
- Dominant ambiguous trees must be split by runtime, deployment, package, or privilege evidence before they can be left deferred. A single blob row such as "project", "server", "core", or "plugins" is incomplete unless it cites the concrete entrypoint/control files checked and explains why further subdivision is not possible from repository evidence.
- Treat broad sink searches as seed generation only. They do not count as coverage completion until the relevant files have been tied to an entrypoint or privileged boundary and the ledger row has a final disposition.
- Promote a seed into a reportable finding candidate only after it has a concrete source or privileged boundary, closest relevant guard/control, sink or broken control, and impact. Public or anonymous routes, upload/parser entrypoints, webhooks, build/job triggers, package APIs, and privileged internal workers count as first-class boundaries.
