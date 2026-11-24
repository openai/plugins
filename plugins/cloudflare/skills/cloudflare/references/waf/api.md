# WAF API Reference

Read the matching workflow before writing API calls or translating them into the project's installed SDK. Retrieve identifiers from the target account or zone; do not reuse example IDs.

| Task | Documentation |
|------|---------------|
| Inspect the entry point and add custom rules | [Create a custom rule via API](https://developers.cloudflare.com/waf/custom-rules/create-api/index.md) |
| Discover managed rulesets and deploy them | [Deploy managed rules via API](https://developers.cloudflare.com/waf/managed-rules/deploy-api/index.md) |
| Create rate limits with the current request schema | [Create a rate limiting rule via API](https://developers.cloudflare.com/waf/rate-limiting-rules/create-api/index.md) |
| Select counting characteristics, expressions, periods, and mitigation behavior | [Rate limiting parameters](https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/index.md) |
| Replace a ruleset deliberately or choose an additive operation | [Update or deploy a ruleset](https://developers.cloudflare.com/ruleset-engine/rulesets-api/update/index.md) |
| Construct expressions using supported fields, operators, and functions | [Rules language](https://developers.cloudflare.com/ruleset-engine/rules-language/index.md) |
| Choose actions and understand terminating behavior | [Actions reference](https://developers.cloudflare.com/ruleset-engine/rules-language/actions/index.md) |
| Override managed rules, tags, or a ruleset | [Managed ruleset overrides](https://developers.cloudflare.com/ruleset-engine/managed-rulesets/override-managed-ruleset/index.md) |
| Choose exactly what a skip rule bypasses | [Skip options](https://developers.cloudflare.com/waf/custom-rules/skip/options/index.md) |

For an addition, prefer the workflow's operation that adds a rule to an existing ruleset. When replacing a ruleset, include every rule that must remain; review the resulting rule list before applying it. See [gotchas.md](gotchas.md) for scope and evaluation checks.
