# Code Diff Review Guidance

Use this guidance when the security scan target is a specific code-diff or PR.

## Workflow

1. Load the per-scan threat model path from `../../../references/scan-artifacts.md` as the repo-specific threat-model source of truth.
2. Investigate the actual diff and any supporting files the patch relies on. You must enumerate ALL plausible security finding candidates. Continue reviewing until you have covered the diff and its immediate supporting code comprehensively enough that no additional distinct plausible candidates remain.
3. Follow the chain of files needed to understand the effects of the change.
4. Trace attacker-controlled inputs through the minimal surrounding code needed to understand propagation and controls.
5. Identify all security vulnerabilities that are valid given the threat model. Non-exaustive list of some common failures to look for (but you should read all the code to find other vulnerabilities):
   - authentication
   - authorization
   - tenant isolation
   - input handling into interpreters, queries, or filesystem paths
   - unsafe network fetch or callback behavior
   - privilege-bearing state transitions
   - secret handling
   - security-sensitive config or policy enforcement
   - etc
6. Look for multiple distinct findings caused by different root causes.
7. For each candidate, prioritize technical plausibility rather than final reportability.
8. If there are no plausible candidates, stop and return a no-findings result immediately.

### Diff-Scoped Sibling Expansion

For diff scans, stay anchored to the changed code, but do not stop at one representative instance when the diff introduces, modifies, or makes reachable a repeated vulnerable pattern.

Apply sibling expansion when a changed route, handler, template, query helper, deserializer, filesystem/network sink, authz guard, config block, or wrapper has nearby changed or directly supporting siblings with the same security-relevant shape. In that case:

- enumerate each changed or newly reachable sibling instance with its own source, closest control, sink, and affected location
- search the immediate pattern family needed to determine whether the diff made additional siblings vulnerable, such as adjacent routes in the same router, templates rendered by the changed handler, call sites of the changed helper, or policy checks sharing the changed guard
- when the diff adds, removes, or reshapes a guard around an existing parser, deserializer, expression evaluator, filesystem/path helper, archive utility, or auth/authz helper, use the adjacent pre-existing sink/control as supporting context for the changed behavior; keep the candidate anchored to the changed guard or newly exposed path unless the user explicitly asks for wider instance expansion
- when a changed wrapper, guard, or API delegates to a shared parser/deserializer/path/archive/auth helper, keep both the wrapper call site and the underlying shared sink/control line addressable; do not replace the root sink/control evidence with wrapper-only evidence
- keep unchanged siblings as context or negative controls unless the diff newly routes attacker input to them, weakens their shared control, or changes a shared sink/helper they depend on
- suppress only the exact sibling instance that has counterevidence, and do not let one safe sibling suppress another vulnerable sibling
- stop expansion once the changed pattern family and its directly supporting call sites are exhausted; do not turn a diff scan into an unrelated repository-wide scan

## Discovery Checklist

Use this checklist to keep discovery specific without turning it into validation or attack-path analysis:

- Use tools to inspect the changed files and the minimum supporting files they rely on before deciding anything.
- Treat the commit message and title as potentially incomplete or misleading; trust the actual code path more than the narrative.
- Follow the entire changed-code chain far enough to understand how the diff affects authorization, trust boundaries, dangerous sinks, or security controls.
- Prefer multiple distinct findings only when they come from different root causes; do not split one issue into cosmetic variants.
- When the diff changes a shared helper, guard, route pattern, template pattern, or sink wrapper, fan out to sibling call sites that the changed code directly affects, and keep each vulnerable instance addressable.
- Look for attacker-controlled input, broken enforcement, or dangerous sinks introduced or made reachable by the change.
- Stay anchored to the diff and the supporting files it depends on rather than drifting into unrelated repository scanning.
- Do not group many vulnerable files under one candidate when the files have separate line-level source/sink/control evidence.
- When a dangerous sink has multiple call sites, enumerate each call site with its own source and closest control.
- When source/sink evidence crosses a wrapper into a shared sink/control helper, include both locations in the candidate so validation can test reachability without losing the root vulnerable line.
- Do not collapse separate high-impact proof tuples into one candidate only because they share a route or helper. Split command execution, SSRF, path/file impact, XML/parser behavior, XSS/template execution, and authz/state-change impact when the sink, closest control, or impact differs.
- In XML/parser/deserializer surfaces, enumerate default parser factories, converters, validators, transformers, unmarshal/parse calls, and handler entrypoints independently. A safe sibling parser path is negative control for that sibling, not suppression evidence for a different default factory or converter.
- In auth/authz surfaces, enumerate public webhook, status, callback, and API endpoints that read protected objects, trigger builds/jobs, or mutate protected state independently from nearby credential or configuration bugs.
- When a template or config pattern appears repeatedly, enumerate each affected file/line and note any nearby safe control that should not be reported.
- Include `relevant_lines` only when the bug overlaps the diff and those lines are genuinely relevant to the issue.
- Include CWE IDs when known; use an empty list when the class is unclear.
