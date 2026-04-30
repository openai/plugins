---
name: finding-discovery
description: Use when Codex is already in the finding-discovery phase of a security scan or the user explicitly asks to discover candidate security findings in a repository or code change. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.
metadata:
  short-description: Discover security findings
---

# Security Finding Discovery

## Objective

Investigate the proposed code or code changes for technically plausible security vulnerabilities using the threat model as context.

## Artifact Resolution

The path references in this skill are the default locations for this phase.
If the user explicitly provides a different path for a required input or output, use the user-provided path instead of the corresponding default path referenced in this skill.
If a required input is still missing, stop and ask the user for it before continuing.
Use the shared scan artifact path conventions in `../../references/scan-artifacts.md`.

### Code Diff Workflow
If the scan target is for a targeted code-diff, follow the procedure in `../security-scan/references/code-diff-scan.md`.

### Repository-Wide Workflow

If the scan target is repository-wide, follow the procedure in `../security-scan/references/repository-wide-scan.md` and every required reference it lists.

## Discovery Checklist

Use this checklist to keep discovery specific without turning it into validation or attack-path analysis:

- Use tools to inspect the changed files and the minimum supporting files they rely on before deciding anything.
- Treat the commit message and title as potentially incomplete or misleading; trust the actual code path more than the narrative.
- Follow the entire changed-code chain far enough to understand how the diff affects authorization, trust boundaries, dangerous sinks, or security controls.
- Prefer multiple distinct finding families only when they come from different root causes; do not split one issue into cosmetic variants, but keep independently reachable instances as separate candidate entries.
- When the diff changes a shared helper, guard, route pattern, template pattern, or sink wrapper, fan out to sibling call sites that the changed code directly affects, and keep each vulnerable instance addressable.
- Look for attacker-controlled input, broken enforcement, or dangerous sinks introduced or made reachable by the change.
- Stay anchored to the diff and the supporting files it depends on rather than drifting into unrelated repository scanning.
- For repository-wide scans, stay anchored to the runtime inventory and coverage ledger rather than drifting into arbitrary text search.
- Do not group many vulnerable files under one candidate when the files have separate line-level source/sink/control evidence.
- When a dangerous sink has multiple call sites, enumerate each call site with its own source and closest control.
- When repeated templates, query builders, parser operations, auth/object endpoints, or shared-helper callers are independently reachable, keep each vulnerable file and sink/control line as its own candidate instance even if the final report later groups related prose.
- When source/sink evidence crosses a wrapper into a shared sink/control helper, include both locations in the candidate so validation can test reachability without losing the root vulnerable line.
- When a concrete operation, strategy, converter, validator, or handler subclass selects the attacker-controlled operation semantics and delegates into a shared broken control or sink, include that subclass method or constructor as an affected candidate location alongside the shared helper. Do not replace it with only the abstract base class or shared helper.
- If a candidate claim says that a shared parser, loader, evaluator, auth guard, or operation family affects "all", "every", or "any" concrete implementation, enumerate the concrete implementations that make that claim true. Do not leave concrete vulnerable classes only in prose.
- When a broad candidate bucket names a whole operation family such as "all SQL trigger variants", "all deserialization variants", "all path traversal helpers", "all SSRF modes", "all generated framework adapters", or "all unauthenticated mutation endpoints", expand it into child candidates keyed by the concrete exported function, route branch, sink statement, API mode, parser/deserializer variant, or protected action before handing the set to validation.
- If one route or helper exposes multiple dangerous operations in the same family, such as `execute`/`executemany`/`executescript`, `pickle.load`/`pickle.loads`/`yaml.load`/`yaml.load_all`, separate path/file helper methods, insert/select/delete/update query builders, or create/delete/reset/admin/job actions without auth, keep those operations as separate candidate instances when attackers can trigger them independently.
- Treat shared or generated wrappers as reachability evidence, not as a reason to collapse child sink variants. The wrapper can be a shared affected location, but each independent sink, control, or protected action still needs its own candidate id.
- When the scan context or evidence seeds a specific boundary package, class family, or vulnerability family, keep that seeded row open until that exact package or class family is closed. A nearby same-family finding is supporting context, not a replacement for the seeded root control.
- When CVE, GHSA, advisory, release, issue, or package-version context is provided, use any advisory seed research artifact as discovery input. Preserve seed-researched files/functions/classes/hunks as ledger rows until local code evidence closes them as reportable, suppressed, not applicable, or deferred.
- When CVE/advisory context has a generic or unhelpful category, do not fall back directly to broad hotspot findings. First derive a seed shortlist from advisory/fix/release/security-test sources when available; if that is unavailable, run a local regression-seed pass over project-specific protocol, parser, validator, utility, and version/comparison helpers plus the CVE/advisory terms.
- If discovery opens or greps a seed-target file, class, package, or hunk, create an explicit closure row for it. Do not leave the exact seed only in tool output, background context, or suppressed-candidate prose. If a broader sibling finding shares the same proof tuple, keep the seed anchor file/line as an affected location; otherwise close the seed row separately.
- For advisory-led rows, do not replace the exact seeded construct with a neighboring hotspot just because the neighboring issue is easier to exploit or validate. Keep the seeded row open until local repository evidence independently supports or disproves the same source, broken control, and impact tuple.
- For shared deserialization, class-resolution, template, and auth controls, treat the resolver/filter/allowlist/denylist/guard line as a candidate location when downstream transports or callers prove reachability. Do not anchor only on the more dramatic transport if the broken control is reusable.
- For deserialization and object-construction families, enumerate concrete codec, deserializer, converter, and container handlers registered by the parser or serialization config, including array, collection, map, bean, enum, throwable, and generic-object handlers. A top-level parser/config finding does not close a concrete codec row when that codec recursively invokes parsing, type resolution, conversion, or object construction on attacker-controlled data.
- For file-format object models, enumerate primitive/container helper methods that convert or traverse attacker-controlled document structures, including `to*Array`, `get*`, `getObject`, numeric conversion, `parse*`, iterator, `size`, unchecked casts, and allocation loops. Treat these helpers as candidate root controls when malformed documents can trigger type confusion, exceptions, unbounded traversal, or memory/CPU exhaustion.
- If the runtime inventory names a central object-model package for an untrusted format, include that package's array, dictionary, node, collection, and primitive conversion helpers as discovery rows before closing the parser family. A parser, filter, or codec finding in a neighboring package does not close unchecked conversion helpers in the core object model.
- Object-model helper sweeps create mandatory discovery rows first, not automatic reportable findings. Promote them only when malformed or adversarial input plausibly reaches the helper and the missing type, size, shape, recursion, numeric, or conversion guard can cause crash, denial of service, parser confusion, authorization bypass, or another concrete security impact.
- Do not suppress deterministic parser/helper crashes as mere robustness when untrusted remote, protocol, document, archive, or package input can reach the missing guard and abort a service, request worker, parser pipeline, or security negotiation. Suppression needs exact containment evidence such as caller-side recovery, input prevalidation equivalent to the missing guard, or a non-security-only boundary.
- For structured patch/edit/apply APIs such as JSON Patch, Graph Patch, document edits, or config mutations, enumerate concrete request-selected operations like add, remove, replace, move, copy, and test. Keep operation-specific path transforms, array append handling, wildcard selection, or object-binding lines candidate-visible when they feed a shared evaluator or binder.
- In concrete operation classes, inspect specialized helper methods and not only the top-level `perform`, `handle`, or `apply` override. If the operation-specific helper splits, filters, canonicalizes, or rebuilds attacker-controlled paths before delegating to a shared evaluator or binder, use that helper line as the candidate root control.
- When a concrete operation has special-case branches such as append, wildcard, fallback, copy/move `from`, default-value, or type-resolution paths, keep the branch predicate and branch-local transform lines as affected locations when they bypass or narrow the shared validator. A shared helper finding does not close branch-specific root controls.
- When class-filter, allowlist, denylist, blacklist, whitelist, or resolver logic is duplicated across core, server, client, remoting, plugin, or import packages, include the runtime/exported equivalents as candidate locations when they implement the same broken control. A transport callsite proves reachability, but it does not replace the reusable resolver implementation.
- In framework or library scans, stored client, tenant, application, identity-provider, exception, or imported-configuration values are cross-boundary inputs when later rendered, evaluated, parsed, or used for authorization and the instance has a plausible runtime path from an application, tenant, identity provider, import, or other boundary. Do not suppress solely because the writer is outside the current repository unless repository evidence proves the value is trusted-only for normal deployments.
- For SQL/NoSQL/LDAP/XPath and similar query APIs, do not suppress a candidate solely because the endpoint already accepts user-controlled data, because the operation is an insert/update, or because a later business check appears to limit the final application effect. If attacker-controlled input reaches query syntax or selector operators through a plausible runtime path, carry the candidate to validation with the later check recorded as possible counterevidence.
- Do not collapse separate high-impact proof tuples into one candidate only because they share a route or helper. Split command execution, SSRF, path/file impact, XML/parser behavior, XSS/template execution, and authz/state-change impact when the sink, closest control, or impact differs.
- In XML/parser/deserializer surfaces, enumerate default parser factories, converters, validators, transformers, unmarshal/parse calls, and handler entrypoints independently. A safe sibling parser path is negative control for that sibling, not suppression evidence for a different default factory or converter.
- For XML parser and converter candidates, include feature-setup and resolver lines when hardening is best-effort, fail-open, or incomplete. `FEATURE_SECURE_PROCESSING` alone, swallowed/logged `setFeature` failures, or a safe default parser does not suppress caller-supplied parser factories/readers or converter paths that create SAX/DOM/StAX/Transformer sources from untrusted data.
- For resource-serving and static-file paths, include the allowlist, matcher, canonicalization, URL decoding, and resource-selection line that decides whether an attacker-chosen path is allowed. Do not replace a vulnerable legacy or package API handler with a safer sibling handler.
- In framework or library scans, do not suppress a high-impact candidate solely because the affected API is deprecated, opt-in, or documented as dangerous. State that as a precondition; keep the candidate when the shipped runtime code contains a bypassable control in the restricted or normal usage path and the instance has a plausible cross-boundary source and runtime/deployment path.
- In auth/authz surfaces, enumerate public webhook, status, callback, and API endpoints that read protected objects, trigger builds/jobs, or mutate protected state independently from nearby credential or configuration bugs.
- For stateful authentication protocols, include the line that installs or reuses principals, credentials, tokens, issuers, or protocol state after a pre-authentication, TLS-upgrade, redirect, assertion, or identity-provider transition. Missing rebind/reauthentication or validated-vs-consumed mismatches are candidate controls when they can authenticate the wrong identity.
- In SSO/SAML/federation packages, keep response/assertion validators distinct from generic claims authorizers and service-method authorization. Include assertion selection, list indexing, `getDOM`, `cloneNode`, signed-object lookup, subject confirmation, recipient, audience, destination, ACS URL, and issuer-binding lines when they decide which assertion is trusted or returned.
- In auth/token/assertion validators, watch for a validation loop or `foundValid*` flag followed by a separate fixed-index, first/last-element, clone, serialization, or return path. Treat the later object-selection line as the broken control until exact counterevidence proves the validated object and consumed object are identical and equally bound.
- For realm/authenticator packages, enumerate concrete implementations such as LDAP, Kerberos, PAM, SAML, OAuth/OIDC, or custom `Realm` classes before promoting a nearby generic HTTP auth finding. In TLS-upgraded or multi-step binds, keep the bind/rebind and principal/credential installation line candidate-visible.
- In protocol-heavy repositories, inspect low-level version, capability, feature, and negotiation utility classes even if the most obvious candidates are REST/upload/admin hotspots. Search for helper names such as `Version`, `VersionUtil`, `versionCompare`, `versionMatch`, `Capability`, `Feature`, `Negotiation`, `parseInt`, `split`, `matches`, and comparator methods, then close paired validator/parser rows explicitly.
- For self-service update routes, include guard or predicate methods that compare requested objects against persisted objects. Treat missing checks on security-sensitive scalar fields and collection aliases as candidate locations when they can change identity, trust state, tenant membership, roles, groups, or account recovery properties.
- When a template or config pattern appears repeatedly, enumerate each affected file/line and note any nearby safe control that should not be reported.
- In large repository scans, do not let one hotspot cluster consume the whole discovery pass. After promoting one or two obvious findings in the same route, upload, parser, or auth cluster, inspect a disjoint seeded row or low-salience utility/control shard such as protocol/version helpers, central object-model helpers, shared validators, or class-resolution controls before finalizing discovery.
- In large repositories, bias early coverage inside high-risk subsystems toward leaf runtime validators, comparators, object-model helpers, and operation branches that parse or select untrusted values. Top-level controllers, uploads, admin endpoints, and XML hotspots are entrypoints, not sufficient coverage of the subsystem.
- For diff-scoped scans, include `relevant_lines` only when the bug overlaps the diff and those lines are genuinely relevant to the issue.
- For recursive placeholder or template findings, include the helper/parser setup line that enables recursive expansion or expression evaluation along with the resolver/evaluation/render line.
- Include CWE IDs when known; use an empty list when the class is unclear.

## Finding Bar

Prefer findings such as:

- authz bypass
- confused deputy
- SSRF
- path traversal
- injection with a real sink
- cross-tenant data exposure
- sensitive state change without correct enforcement
- sandbox or trust-boundary escape

- Credible RCE or arbitrary code execution (command injection, LFI exec, trivial memory corruption exploits, etc); Requires actual proof that attacker input cause this from in-scope attack surface
- Real XSS with meaningful proven impact (for example session/token theft, account compromise, privileged action execution, etc)
- Account takeover or strong authentication bypass, especially if it is 0-click
- Missing authorization checks / authorization bypass / tenant-boundary break (trivial IDOR, easy to swap out org or use ids with no authz, etc)
- Severe sensitive data leak (LFI, path traversal, bad scoping of file downloads, access to data without authorization, trivial side-channels) with realistic attacker access (proof the attacker can read secrets, PII, signing keys, credential stores, private keys, classified or highly confidential information (model weights etc))
- Trivial memory corruption exploits with known exploit patterns which require little effort to exploit
- SQL or other Database or query injection with clear proof of path from attacker input from in-scope attack surface and impact of the injection (leaks sensitive data, inserts dangerous records)
- Sandbox, container, VM, browser, or interpreter escape that breaks an intended isolation boundary
- Server-side-template-injection when it leads to RCE or leaking of secrets; with actual proof that the templating library can be exploited to do this (RCE escape or secrets/credentials in scope); with actual proof that this can be reached from in-scope attack surface
- Arbitrary file write in executable, startup, config, or firmware paths with a realistic path to persistence or code execution. Requires proof that an attacker can actually trigger this from in-scope attack surface.
- Logic flaws that allow irreversible or broad compromise of integrity at scale, such as unauthenticated deletion of other users' data, cross-tenant tampering with sensitive records, or unauthorized modification of security-critical configuration, when the impact is clearly demonstrated and severe enough to be compromise-equivalent; when there is actual proof that this logic can be exercised from in-scope attack-surface.
- etc, other bugs not listed which follow this level of critical severity and impact; with actual proof that these bugs are reachable from in-scope attack-surface.

- Sever Side Request Forgery where there is actual proof of both 1. Attacker can control the url being requested (bypassing protections around that) from in-scope attack-surface and 2. That there are likely other local/lan/cloud services which can be reached to show actual impact. Be careful with reporting webhooks unless there is clear proof that it is dangerous.
- Exploitable memory corruption with clear, major impact or ease of exploitation
- Arbitrary file read that exposes less-sensitive user data or source code (if you have actual proof it reveals env secrets, then it is critical)
- Arbitrary file write in executable, startup, config, or firmware paths with a realistic path to persistence or code execution
- CSRF when it enables important state-changing actions such as credential changes, permission changes, payment / billing changes, security-setting changes, or other materially harmful actions, and the victim interaction required is realistic, and is not mitigated by any of these : `same-site strict cookies, auth headers, csrf tokens, PUT/PATCH/DELETE, enforced json request body content type`.
- Hardcoded or default credentials that are valid and reachable and give meaningful access, but not sufficiently broad or privileged to justify high.
- Cryptographic failures that allow signature forgery, token forgery, trusted artifact forgery, secure-channel bypass, or decryption of highly sensitive data in a way that directly enables compromise; with actual proof that these are practical attacks and reachable and doable from in-scope attack-surface.
- Supply-chain or update-channel compromise that allows malicious code or malicious trusted artifacts to be delivered to users, servers, agents, or endpoints, including signing bypass or package source substitution with real impact. This should focus on actual supply-chain risk and risk around CI actions, not just "does npm report outdated packages"
- Authorization bypass, IDOR, or privilege escalation that exposes or modifies meaningful sensitive data or privileged functionality, but is narrower in scope, limited to a smaller set of objects, limited to same-tenant boundaries, or otherwise less catastrophic than the critical cases above.
- XXE with clear proof that an attacker can control the XML document through in-scope attack-surface and that the XML engine is vulnerable to XXE
- etc, other bugs not listed which follow this level of high severity and impact; with actual proof that these bugs are reachable from in-scope attack-surface.
- Dangerous upload / file handling issues that enable stored active content, trusted-origin script execution, or meaningful content-type confusion with real security impact; with actual proof that both the upload and access are reachable through in-scope attack-surface.
- Deserialization, SSTI, plugin abuse, macro / template abuse, or interpreter abuse where dangerous primitives are clearly reachable and impactful, but code execution or compromise is not fully proven to the standard needed for critical.


Avoid:

- generic "needs more validation" comments with no exploit path
- maintainability complaints
- duplicate variants of the same root issue

## Output Contract

If there are no plausible candidates, return a no-findings result.

Otherwise, for each candidate include:

- title
- affected locations, with labels when more than one applies: `entrypoint/wrapper`, `root_control`, `sink`, and `concrete_implementation`
- instance key in the form `<family>:<file>:<line>` for repository-wide scans
- seed or ledger row id for repository-wide seeded/root-control rows when available
- advisory/source reference for advisory-seeded rows when available
- attacker-controlled source
- vulnerable sink or broken control
- impact
- why the issue is plausible from the current code
- closest apparent control and why it is absent, bypassed, mis-scoped, or incomplete
- whether validation is recommended
- `relevant_lines` for diff-scoped scans when the bug overlaps the diff and those lines are relevant to the bug
- taxonomy with CWE IDs when known
- enough evidence that a later reviewer can understand why the candidate is technically plausible before validation


## Hard Rules

- Use the tools to examine repository files before making decisions.
- Focus on the actual changes, not the commit message.
- Stay anchored to the diff and the files it relies on for diff-scoped scans. For repository-wide scans, treat the checked-out repository as in scope and ignore diff-overlap restrictions for affected locations.
- Candidate discovery is about plausibility, not final severity.
- Do not add `relevant_lines` when no bug exists. For diff-scoped scans, add `relevant_lines` only when the bug overlaps the diff and those lines are relevant to the bug.
- Do not turn discovery into full validation or full severity calibration.
- Continue reviewing until no additional distinct plausible candidates remain.
- Save a final visible report using the finding discovery report path from `../../references/scan-artifacts.md`.
