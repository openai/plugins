# Final Report and Codex Review Directives

Use this guidance when assembling the final Codex Security markdown report and Codex app review directives.

## Final Output

The final output must be markdown.

Write the final markdown report to the final scan report path from `../../../references/scan-artifacts.md`. Keep the threat model and validation artifacts alongside it using that layout so the full scan bundle lives together.

When there are no reportable findings, include a short `No findings` section that explains why nothing survived discovery or the later reportability gates. For repository-wide scans with a coverage ledger, still include `Coverage Closure` so seeded, suppressed, not_applicable, and deferred rows remain auditable.

When there are reportable findings, render them as readable markdown findings rather than raw JSON or a dumped schema object.
Order findings from highest severity to lowest severity: `critical`, then `high`, then `medium`, then `low`.

Use a separate finding entry for each independently attackable source/control/sink instance. Do not combine sibling routes, templates, query builders, parser operations, auth/object-access endpoints, or shared-helper callers into one representative finding solely for readability; if grouping helps, add a short grouped summary after the individual finding entries.

If validation or attack-path analysis provides a broad family row with multiple independently triggerable sink, parser, helper, API-mode, or protected-action lines, split it into child final findings before writing the report. Multiple affected lines inside one finding are appropriate for one inseparable proof tuple, such as a wrapper plus its shared sink, but not as a substitute for separate findings when sibling operations can be triggered independently.

Set the finding category and CWE from the primary broken control. Do not add secondary support-impact CWEs, such as data exposure or missing authentication, to an injection/RCE/path/file/parser finding merely because they make exploitation worse; mention those impacts in prose or emit a separate finding if that secondary control is independently vulnerable.

Examples that should normally become separate final findings include SQL API modes such as `execute`, `executemany`, and `executescript`; deserializer variants such as `pickle.load`, `pickle.loads`, `yaml.load`, and `yaml.load_all`; distinct path/file helper calls; SSRF modes with different destination controls; and missing-auth protected actions such as create, delete, reset, admin, and job-trigger endpoints.

Before writing the report, reconcile the final findings against the saved validation closure table and repository coverage ledger when those artifacts exist. Start from validated rows marked `reportable` or `survives: yes`, not only from the most polished candidate narrative. Every `reportable` seeded or root-control ledger row must become a finding with the same root-control file:line. Rows closed as `suppressed`, `not_applicable`, or `deferred` should appear in a short `Coverage Closure` section with the exact file:line when known and the reason or proof gap. Do not silently drop a seeded/root-control row because a same-family neighboring finding survived. If attack-path analysis omitted a reportable validation row, assemble a concise attack path from the validation evidence and threat model rather than dropping the row.

Use a format close to:

`## Finding: <title>`

Then include:

- `Priority: P0|P1|P2|P3`
- `Severity: critical|high|medium|low`
- `Confidence: high|medium|low` or a short calibrated confidence label
- `CWE: <id and name list, or none>`
- `Affected lines: <path:line-range>`

Affected lines must include the root broken control or dangerous sink line when that line is identifiable, not only the public wrapper, route, or caller that makes it reachable. For wrapper-to-shared-helper findings, list both the reachable wrapper/entrypoint and the underlying parser, deserializer, path/archive helper, expression evaluator, or auth/authz control line. If a seeded file, class, package, or hunk shares the surviving proof tuple, keep that seed anchor in affected lines instead of replacing it with a broader sibling-only location. If the bug is caused by unsafe transformation or selection before the sink, include the split, parse, canonicalization, normalization, comparison, regex, object-selection, or object-binding line where the control fails. For parser, XML, deserialization, and object-construction findings, include the concrete codec, converter, deserializer, parser feature setup, resolver, class filter, or container handler line when that line performs recursive parsing, type resolution, object conversion, class filtering, or fail-open hardening. For central file-format object models, include low-level helper lines such as `to*Array`, `toList`, `getObject`, numeric conversion, iterator, size-based allocation, unchecked cast, or collection-to-array loops when those helpers are the broken malformed-input control. For recursive placeholder/template findings, include the helper/parser setup line that enables recursive expansion or expression evaluation, not only the later resolver or render call. For resource-serving findings, include the allowlist, path-matcher, URL decoding, canonicalization, or resource-selection line that decides whether the attacker-selected resource is allowed. For stateful authentication protocol findings, include the principal/credential/token/issuer installation, rebind/reauthentication, or validated-vs-consumed object-selection line that creates the auth bypass. For SSO/SAML/federation findings, include the response/assertion selection, signed-object lookup, cloned/returned assertion, subject, audience, recipient, destination, ACS URL, or issuer-binding line that determines which identity object is trusted. For polymorphic or request-selected handler, operation, converter, filter, validator, or strategy families, include the concrete subclass/implementation line that transforms, validates, canonicalizes, selects, or reinterprets attacker input before a shared sink/control, including specialized helper methods and branch predicates inside the concrete class when they perform or enable the unsafe transform. If a special-case branch such as append, wildcard, fallback, copy/move `from`, default-value, or type-resolution handling bypasses or narrows validation, include that branch-local root-control line even when a shared helper is also affected. If the finding text says a shared flaw affects "all", "every", or "any" concrete operation, codec, converter, handler, validator, filter, or resolver, the affected lines must include the concrete implementations identified during discovery or validation; do not rely on "and related classes" prose for independently reachable root-control lines. If equivalent resolver/filter controls are duplicated across core, server, client, remoting, plugin, or import packages, include the runtime/exported implementation that enforces the broken control. For repeated vulnerable templates, routes, query builders, parser operations, or auth/object-access endpoints, keep each independently vulnerable file and line as its own affected instance; do not hide sibling instances as extra context on one representative finding when they can be attacked independently. The Codex review directive should point at the tightest root-cause line unless the wrapper or concrete implementation line is the actual broken control.

Then render these sections for each finding:

- `### Summary`
  - Explain why the issue matters, what the vulnerable path is, and why the current controls are insufficient.
- `### Validation`
  - Include method, checklist items, evidence, and remaining uncertainty.
- `### Reachability Analysis`
  - Explain whether the issue crosses a real trust boundary, whether it is self-only or reaches a meaningful target, and why it is or is not in scope.
- `### Attack Path`
  - Present the attacker story as numbered steps with evidence under each step when possible.
- `### Attack Path Facts`
  - Render the key attack-path-analysis facts in markdown form rather than leaving them implicit.
- `### Severity Analysis`
  - Include impact, likelihood, final severity, and the resulting priority.
- `### Remediation`
  - Give concrete minimal fixes, tests, and preventive controls.

For repository-wide scans with a coverage ledger, include a concise `## Coverage Closure` section after the findings. Keep it brief, but include seeded/root-control rows that were suppressed, not applicable, or deferred so an auditor can see why they did not become findings.

For broad scans where the completed coverage is useful for triage but too large for high-precision review, include a concise `## Follow Up Prompts` section near the end of the report. Use concrete, copyable prompt ideas that narrow the next review to individual commits from the current scan. Do not include this section for precise scans where the requested scope was already sufficient.

Follow-up prompts should be tailored to the actual scan results:

- use exact commit SHAs, PR numbers, short titles, file paths, or component names from the report
- focus each prompt on the specific boundary that made the commit worth follow-up, such as auth, plugin/MCP exposure, artifact downloads, signed URLs, or gateway routing
- avoid generic placeholders

Each finding should make it easy for an application security engineer or software engineer to answer:

- what changed or what path is vulnerable
- what attacker-controlled input or trust boundary matters
- what direct evidence supports the claim
- what counterevidence or uncertainty remains
- why the severity and priority landed where they did
- what the smallest safe fix is

Use the final priority mapping:

- `critical` -> `P0`
- `high` -> `P1`
- `medium` -> `P2`
- `low` -> `P3`

The threat model is not part of the final output.

Include the final report path in the response so the user can find it easily.

## Codex Review Directives

For Codex app rendering, emit one `::code-comment{...}` directive per surviving finding in the final response. The markdown report and review directives should agree on title, priority, file, line range, and core explanation.

For each reportable finding, emit a Codex review directive in this form:

`::code-comment{title="[P2] Example title (medium)" body="One-paragraph review explanation." file="/absolute/path/to/file" start=10 end=12 priority=2 confidence=0.55}`

Directive requirements:

- `title`, `body`, and `file` are required
- `title` should include both the final priority and severity, formatted like `[P1] Example title (high)`
- `file` should be an absolute path
- `start` and `end` should be tight 1-based line numbers
- `priority` should match the final priority mapping
- `confidence` should be numeric when available
- emit one directive per finding and none when there are no findings
- inline Markdown code spans are allowed and encouraged for short identifiers, flags, function names, and config keys, such as `git -c`, `--config`, and `diff.external`
- do not put double quote characters inside quoted attribute values, including escaped quotes like `\"`; rewrite quoted command examples without quotes or leave them only in the markdown report
