# Setup Report Schema

Use this structure for the final response after applying or reviewing instrumentation.

```markdown
**OpenAI Ads Conversions Setup Report**

Setup mode: pixel | capi | pixel+capi | review-only
Detected stack: <framework/runtime/package manager>

Changed files:
- <path>: <what changed>

Existing instrumentation found:
- <OpenAI Ads Pixel/CAPI helper, event call site, config, test, or none found>

Existing ad platform patterns used:
- <Meta/Google/TikTok/Segment/etc. pattern used as local evidence, or none found>

Events instrumented:
- <event name>: <success boundary, file/function, data payload family, and new vs existing coverage>

Events already covered:
- <event name>: <existing helper/call site that already covers this flow>

Events/surfaces skipped:
- <supported event or platform>: <why skipped or deferred>

Optional follow-up events:
- <supported event>: <why it is plausible, what boundary to confirm, and offer to add if desired>

Pixel:
- Pixel ID/config: <id or config key>
- Initialization point: <file/function>
- Docs syntax source: <current docs checked, existing SDK wrapper, or fallback reference used>
- debug behavior: <local/test only, not configured, or why enabled>
- Pixel user data: <fields sent through init, when late init runs, or why omitted>
- Pixel opt_out: <mapped in measure options, existing consent gate used, omitted because no pattern exists, or not applicable>
- Consent handling: <existing gate used or follow-up>

CAPI:
- Server boundary: <file/function>
- Secret reference: <env var or secret path, never raw value>
- Request/auth docs verified from: <docs/source>
- validate_only behavior: <default false/blank, local smoke-test toggle, or why validation-only was requested>
- action_source/source_url: <documented action_source value and, for web, HTTP(S)-only origin+path sanitization strategy>
- Browser-provided source_url validation: <trusted origin rule, configured canonical origin fallback behavior, or not applicable>
- timestamp_ms: <current event-time source and any stale/future-event guard>
- oppref handling: <raw cookie preferred, raw request-context fallback, or why omitted>
- user data: <fields sent, hashing/normalization source, or why not sent>
- opt_out handling: <existing consent/personalization opt-out mapped, omitted because no pattern exists, or not applicable>
- Failure behavior: <non-blocking/blocking and why>

Deduplication:
- event_id source: <order id/payment id/lead id/generated id/not applicable>
- Pixel+CAPI pairing: <how same Pixel ID, event name, and event_id reach both paths>

Verification:
- <command/check>: passed | failed | not run (<reason>)

Manual follow-ups:
- <secret provisioning, dashboard config, deployment, QA, event mapping>

Risks / unknowns:
- <remaining ambiguity or operational risk>

Deployment review warning:
- Before deploying, review that this implementation satisfies your privacy, security, consent, and data handling requirements.
```

Never paste raw CAPI keys, customer data, or sensitive advertiser code snippets into the report.
