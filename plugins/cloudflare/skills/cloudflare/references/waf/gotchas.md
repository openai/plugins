# WAF Gotchas

Use observed requests and the deployed ruleset definitions to diagnose behavior before changing protection.

| Symptom or decision | Documentation to read |
|---------------------|-----------------------|
| A rule executes earlier or later than expected | [WAF phases and account/zone order](https://developers.cloudflare.com/waf/reference/phases/index.md) and [terminating actions](https://developers.cloudflare.com/ruleset-engine/rules-language/actions/index.md) |
| A skip rule leaves a protection active | [Skip scope, phases, products, and logging](https://developers.cloudflare.com/waf/custom-rules/skip/options/index.md) |
| Updating a ruleset removes unrelated rules | [Ruleset replacement semantics](https://developers.cloudflare.com/ruleset-engine/rulesets-api/update/index.md) |
| An expression fails to parse | [Rules language elements](https://developers.cloudflare.com/ruleset-engine/rules-language/index.md) |
| Score-based rules match unexpected traffic | [Attack score meaning, special values, and plan availability](https://developers.cloudflare.com/waf/detections/attack-score/index.md) |
| Managed overrides conflict | [Override precedence and scope](https://developers.cloudflare.com/ruleset-engine/managed-rulesets/override-managed-ruleset/index.md) |
| Legitimate traffic is blocked, or attacks reach the origin | [False-positive and false-negative investigation](https://developers.cloudflare.com/waf/managed-rules/troubleshooting/index.md) |
| Rate limits affect shared-IP users or count unexpected requests | [Characteristics, NAT support, and counting expressions](https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/index.md) |
| API creation fails or the request body is unclear | [Custom rule creation](https://developers.cloudflare.com/waf/custom-rules/create-api/index.md), [managed deployment](https://developers.cloudflare.com/waf/managed-rules/deploy-api/index.md), or [rate limit creation](https://developers.cloudflare.com/waf/rate-limiting-rules/create-api/index.md) |

Check account versus zone scope, rule position, and the action that actually handled the request. For rate limiting, inspect matching and counting criteria separately. Avoid broad exceptions as a shortcut for diagnosing a single false positive.

Return to [api.md](api.md) for operations and [configuration.md](configuration.md) for deployment ownership.
