# Repository-Wide Validation Closure

Use this reference with `repository-wide-scan.md` to preserve repo-wide coverage through validation, attack-path analysis, and final reporting.

## Closure Dispositions

- Every applicable high-impact ledger row must finish as `reportable`, `suppressed`, `not_applicable`, or `deferred`. Do not claim full repository coverage while any applicable high-impact row remains `deferred`; instead state exactly what remains deferred and why.
- User/advisory/tag-seeded root-control rows remain validation input even when reachability is incomplete; validation must close them as `reportable`, `suppressed`, `not_applicable`, or `deferred` with the exact proof gap.
- Do not suppress an exact seed row only because a neighboring issue looks more dramatic or because full downstream deployment details are outside the repository; state those details as preconditions or proof gaps.
- Each in-scope row must be recorded even when no candidate is found. Candidate ids are optional links from coverage rows to findings, not the reason the row exists.
- `open_seed` is an interim disposition only; before final reporting, every row must become `reportable`, `suppressed`, `not_applicable`, or `deferred` with exact file:line evidence or a concrete proof-gap reason.

## Validation Budget And Coverage

- Before finalizing a high-impact finding in a large repository, check whether the same inventory shard has unreviewed sibling packages, wrappers, or root controls that could be the actual broken control. If so, finish that shard's sibling checks or mark the remaining rows `deferred` explicitly.
- After promoting one or two obvious hotspot findings in a large repository, run a short coverage-diversity check before finalization: inspect at least one disjoint seeded/advisory row or low-salience utility shard outside the current hotspot cluster, such as protocol/version utilities, central parser/object-model helpers, reusable auth/token validators, or shared deserializer controls. Record the checked disjoint shard in the ledger as `reportable`, `suppressed`, `not_applicable`, or `deferred`.
- For large repositories, do not equate top-level hotspot coverage with subsystem coverage. Within high-risk subsystems, sample leaf runtime validators, comparators, object-model helpers, and special-case operation branches because these are often where the security control is actually skipped.
- For query injection candidates, parser-control evidence is enough to keep the instance alive when attacker input crosses into query syntax or selector operators. Record later checks as constraints, but do not suppress the root injection until the exact query API, parser behavior, and post-query guard prove attacker input cannot change semantics or create a meaningful read/write/error side effect.
- For template and placeholder injection candidates, preserve the helper line that creates the placeholder/expression engine and the line that resolves model values through it. Recursive expansion or re-parsing of resolved values remains in scope when the resolved values are request, client, tenant, stored configuration, or error data. Suppress only with exact evidence that resolved values are constant/trusted or escaped before any second parse/evaluation.

## Suppression And Final Reporting

- Suppress a candidate only with exact counterevidence for that instance, such as a specific sanitizer, permission check, tenant filter, escaping context, safe parser/loader, path canonicalization check, egress allowlist, or deployment constraint that defeats the claimed source/sink path.
- A safe sibling implementation is useful negative control, but it does not suppress a different default factory, resource handler, generated adapter, protected action, parser operation, or shared-helper caller.
- Treat lack of an in-repository write endpoint as a precondition to state, not automatic suppression, unless repository evidence proves only trusted operators can set the value in the intended deployment.
- Include data exposure, hardcoded secrets, weak session/cookie/security config, CSRF, rate limits, and plaintext storage only after the high-impact ledger and file list are exhausted or when they directly enable code execution, injection, privilege escalation, meaningful auth bypass, or sensitive cross-boundary impact.
- The final markdown report may group related findings for readability, but each surviving instance must remain individually addressable with its own affected location, source, broken control, sink, impact, and counterevidence.
- Include suppressed candidates and deferred rows in phase artifacts with exact file/line and counterevidence or proof-gap reasons so false-positive controls and residual coverage gaps remain auditable.
