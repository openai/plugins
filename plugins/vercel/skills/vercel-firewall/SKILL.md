---
name: vercel-firewall
description: Vercel Firewall expert guidance — automatic DDoS mitigation, the Vercel WAF (custom rules, IP blocking, managed rulesets, rate limiting), Attack Mode, system bypass, bot management, and the `vercel firewall` CLI. Use when configuring platform-level security, responding to attacks, or staging firewall rules.
metadata:
  priority: 7
  docs:
    - 'https://vercel.com/docs/vercel-firewall'
    - 'https://vercel.com/docs/cli/firewall'
  bashPatterns:
    - '\bvercel\s+firewall\b'
  promptSignals:
    phrases:
      - 'vercel firewall'
      - 'vercel waf'
      - 'attack mode'
      - 'ddos protection'
      - 'ip block'
      - 'managed ruleset'
      - 'bot protection'
      - 'system bypass'
      - 'rate limit rule'
    allOf:
      - [firewall, vercel]
      - [waf, vercel]
      - [ddos, vercel]
      - [challenge, vercel]
      - ['rate limit', vercel]
      - ['system bypass', vercel]
      - ['ip block', vercel]
    noneOf: []
    minScore: 6
---

# Vercel Firewall

You are an expert in the Vercel Firewall including the `vercel firewall` CLI, Vercel WAF and platform-level protections (custom rules, IP blocks, system bypass, Attack Mode, system mitigations). You follow all the [best practices](#best-practices) outlined below.

## Core Knowledge

- **Vercel ships a multi-layered firewall**, not just a CDN. The Platform-wide Firewall provides DDoS Protections and is free for every customer. Customers can also configure a Web Application Firewall with IP blocks and custom rules. Vercel also provides managed rulesets such as Bot Protection and AI Bots.
- **Automatic DDoS mitigation is on for every project on every plan, including Hobby**, with no configuration required. It covers L3/L4/L7 attacks.
- **Vercel does not bill for traffic blocked by DDoS mitigations or WAF.** Usage is only incurred for requests served before mitigation kicked in or not classified as an attack. You do not pay for requests or bandwidth for denies, challenges, or rate-limits from WAF custom rules or managed rules.
- **Custom rules** allows the user to define their own Firewall rules. Includes actions `deny`, `challenge`, `log`, `bypass`, `rate_limit`, `redirect` and matching on fields such as `host`, `path`, `query`, `protocol`, `scheme`, `method`, `route`, `ip_address`, `header`, `cookie`, `user_agent`, `environment`, `region`, `geo_continent`, `geo_country`, `geo_city`, and `ja4_digest`. See https://vercel.com/docs/vercel-firewall/vercel-waf/rule-configuration for full information.

## Overview

Project must be linked first (`vercel link`).

```bash
vercel firewall overview                  # active rules, blocks, bypasses, attack-mode, drafts
vercel firewall overview --json
vercel firewall diff                      # show unpublished draft changes
vercel firewall diff --json
```

`rules` and `ip-blocks` changes are **staged** as drafts — run `vercel firewall publish --yes` to make them live. `system-bypass`, `attack-mode`, and `system-mitigations` take effect **immediately**.

## Custom rules

[Custom rules](https://vercel.com/docs/vercel-firewall/vercel-waf/custom-rules) define traffic policies based on request attributes. Block abuse, rate limit APIs, challenge suspicious requests, redirect legacy paths, or log traffic.

### View

```bash
vercel firewall rules list                          # table of all rules
vercel firewall rules list --expand                 # show conditions + actions
vercel firewall rules list --json
vercel firewall rules inspect "My Rule"             # full detail of one rule
vercel firewall rules inspect "My Rule" --json
```

### Create — four modes

```bash
# AI — TTY only, BLOCKED FOR AGENTS/SCRIPTS
vercel firewall rules add --ai "Rate limit /api to 100 requests per minute by IP"

# Interactive wizard — TTY only, BLOCKED FOR AGENTS/SCRIPTS
vercel firewall rules add

# Flags — works in scripts and agents
vercel firewall rules add "Block crawlers" \
  --condition '{"type":"user_agent","op":"sub","value":"crawler"}' \
  --action deny --yes

# JSON — works in scripts and agents
vercel firewall rules add --json '{"name":"Block crawlers","conditionGroup":[{"conditions":[{"type":"user_agent","op":"sub","value":"crawler"}]}],"action":{"mitigate":{"action":"deny"}}}' --yes
```

### Multiple conditions (AND) and OR groups

```bash
# AND — multiple --condition flags in the same group
vercel firewall rules add "Secure admin" \
  --condition '{"type":"path","op":"pre","value":"/admin"}' \
  --condition '{"type":"geo_country","op":"eq","neg":true,"value":"US"}' \
  --action deny --yes

# OR — use --or to start a new group
vercel firewall rules add "Block dangerous methods" \
  --condition '{"type":"method","op":"eq","value":"DELETE"}' \
  --or \
  --condition '{"type":"method","op":"eq","value":"PATCH"}' \
  --action challenge --yes
```

### Edit and manage

```bash
vercel firewall rules edit "My Rule" --action challenge --yes      # change action
vercel firewall rules edit "My Rule" --name "New Name" --yes       # rename
vercel firewall rules edit "My Rule" --enabled --yes               # enable
vercel firewall rules edit "My Rule" --disabled --yes              # disable
vercel firewall rules edit "My Rule" \
  --condition '{"type":"path","op":"pre","value":"/new"}' --yes    # replace conditions

vercel firewall rules enable  "My Rule"
vercel firewall rules disable "My Rule"
vercel firewall rules remove  "My Rule" --yes                      # aliases: rm, delete
vercel firewall rules reorder "My Rule" --first  --yes             # move to highest priority
vercel firewall rules reorder "My Rule" --last   --yes
vercel firewall rules reorder "My Rule" --position 3 --yes         # 1-based
```

Rules are evaluated in priority order (top to bottom). Reorder to control which rule matches first.

NOTE: When using `edit` with `--condition`, it will overwrite all conditions listed in the rule. Make sure to specify all conditions when editing a rule.

### Condition format

Each `--condition` is a JSON object:

```json
{
  "type": "path", // condition type (required)
  "op": "pre", // operator (required)
  "value": "/api", // value (required for most operators; omit for ex/nex)
  "key": "Authorization", // required for header / cookie / query types
  "neg": true // negate the condition (optional, default false)
}
```

Conditions within a group are **AND'd**. Multiple groups (separated by `--or`) are **OR'd**.

### Operators

`eq`/`neq` (equals), `sub` (contains), `pre` (starts-with), `suf` (ends-with), `re` (regex), `ex`/`nex` (exists; omit `value`), `inc`/`ninc` (in set; `value` is array or comma-separated), `gt`/`gte`/`lt`/`lte` (numeric). Set `neg: true` to negate any operator.

### Condition types

- **Request shape**: `path`, `raw_path` (pre-rewrite), `target_path` (post-rewrite), `route` (e.g., `/blog/[slug]`), `server_action`, `method`, `host`, `protocol`, `scheme`, `environment` (preview|production), `region`
- **Client**: `ip_address` (IP or CIDR), `user_agent`, `geo_country`, `geo_continent`, `geo_country_region`, `geo_city`, `geo_as_number`
- **Headers / cookies / queries** — require `key`: `header`, `cookie`, `query`
- **TLS fingerprints**: `ja4_digest` (all plans), `ja3_digest` (Enterprise only)

### Actions

- `deny` — block (403)
- `challenge` — show verification page
- `log` — log without blocking (use to tune before enforcing)
- `bypass` — skip remaining WAF custom rules + managed rulesets
- `rate_limit` — throttle by counting key (see Rate limit example for flags)

All actions accept `--duration` (Pro/Enterprise): `1m`, `5m`, `15m`, `30m`, `1h`. Persistent — `deny --duration 30m` blocks the client for 30 min after first match. Without a duration the action evaluates per-request. Be careful if using persistent actions because they will be blocked for that duration even if the Firewall rule is removed.

### Rate limit example

```bash
vercel firewall rules add "Rate limit API" \
  --condition '{"type":"path","op":"pre","value":"/api"}' \
  --action rate_limit \
  --rate-limit-window 60 \
  --rate-limit-requests 100 \
  --rate-limit-keys ip \
  --rate-limit-action deny \
  --yes
```

- `--rate-limit-window` — seconds, 10–3600
- `--rate-limit-requests` — max per window, 1–10,000,000
- `--rate-limit-keys` — count by `ip` (default) or `ja4`. `header:<name>` Enterprise only. Repeatable.
- `--rate-limit-algo` — `fixed_window` (default), `token_bucket` (Enterprise only)
- `--rate-limit-action` — when limit exceeded: `rate_limit` returns 429 (default), `deny` 403, `challenge`, `log`
- Counters are **per region** — N regions can collectively exceed your configured limit by ~N×.

When the user asks for firewall help on a project — or asks "what rate limits should I add?" — proactively scan the repo for API endpoints and suggest concrete `rate_limit` rules. Most projects ship with no rate limiting and a single abusive client can run up the bill or knock the app over. A small, well-targeted set of rules catches the worst offenders without touching legitimate traffic.

Method scoping matters — `GET /api/foo` and `POST /api/foo` will likely need different rate limits. Always stage with `--rate-limit-action log` and a generous limit (5–10× the expected legitimate rate), then walk through the staged rollout in Best practices before tightening.

For more sophisticated counting (custom buckets, hashing identifiers from headers/cookies, sliding windows from your own code) point the user at the **Rate Limiting SDK**: https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting-sdk.

## IP blocks

[IP blocking](https://vercel.com/docs/vercel-firewall/vercel-waf/ip-blocking) blocks IPs or CIDRs entirely. Staged — requires `publish`.

```bash
vercel firewall ip-blocks list
vercel firewall ip-blocks list --json
vercel firewall ip-blocks block 1.2.3.4 --yes
vercel firewall ip-blocks block 10.0.0.0/24 --hostname example.com --yes   # scoped to a host
vercel firewall ip-blocks block 1.2.3.4 --notes "Abuse report #123" --yes
vercel firewall ip-blocks unblock 1.2.3.4 --yes
vercel firewall ip-blocks unblock 1.2.3.4 --hostname example.com --yes     # disambiguate when blocked on multiple hosts
vercel firewall ip-blocks unblock ip_abc123 --yes                          # by rule ID
```

## System bypass

[System bypass rules](https://vercel.com/docs/vercel-firewall/vercel-waf/system-bypass-rules) exempt trusted IPs/CIDRs from **all** firewall checks (office, CI servers, uptime monitors). Immediate — no publish.

```bash
vercel firewall system-bypass list
vercel firewall system-bypass list --json
vercel firewall system-bypass add 10.0.0.1 --yes
vercel firewall system-bypass add 10.0.0.0/24 --yes
vercel firewall system-bypass add 10.0.0.1 --domain example.com --yes
vercel firewall system-bypass add 10.0.0.1 --domain "*.example.com" --yes  # wildcard domain
vercel firewall system-bypass add 10.0.0.1 --notes "Office IP" --yes
vercel firewall system-bypass remove 10.0.0.1 --yes
```

System bypass does **not** override your own custom rules — for that, use a custom rule with `--action bypass`.

## Attack mode

[Attack Mode](https://vercel.com/docs/vercel-firewall/attack-mode) is the emergency response for active attacks. Unverified visitors see a challenge page; verified bots and search crawlers are exempt. Immediate — no publish. **Requires interactive confirmation; blocked for agents/scripts due to severity.**

```bash
vercel firewall attack-mode enable --duration 1h --yes    # 1h (default)
vercel firewall attack-mode enable --duration 6h --yes
vercel firewall attack-mode enable --duration 24h --yes
vercel firewall attack-mode disable --yes
```

## System mitigations

Vercel automatically [mitigates DDoS attacks](https://vercel.com/docs/vercel-firewall/ddos-mitigation). In rare cases (debugging false positives) you may need to pause them. Auto-resumes after 24h. Immediate. **Blocked for agents/scripts due to severity — pausing removes DDoS protection.**

```bash
vercel firewall system-mitigations pause  --yes    # 24h, auto-resume
vercel firewall system-mitigations resume --yes
```

## Publishing

```bash
vercel firewall diff                      # review staged changes
vercel firewall publish --yes             # push drafts to production
vercel firewall discard --yes             # throw away drafts
```

## Querying firewall metrics from the CLI

If the project has **Observability Plus**, `vc metrics` returns firewall counters that you can analyze without leaving the terminal — useful for the "review traffic" step in the staged rollout, or for spotting which rules are doing real work.

```bash
vc metrics vercel.firewall_action.count \
  --group-by waf_rule_id \
  --group-by waf_action \
  --since 3d \
  --granularity 4h \
  --format json
```

- `--group-by waf_rule_id` — break out hits per rule. Match the IDs to `vercel firewall rules list --json` to see which rule fired.
- `--group-by waf_action` — splits `log` / `deny` / `challenge` / `rate_limit` / `bypass` so you can tell what actually got enforced versus only logged.
- `--since` accepts `1h`, `24h`, `3d`, `7d`, etc.; `--granularity` is the bucket size.
- `--format json` is best for programmatic review; drop it for a human-readable table.

For an **active-attack triage** lens — "is something happening right now?" — narrow the window and tighten the granularity:

```bash
vc metrics vercel.firewall_action.count \
  --group-by waf_action \
  --since 1h \
  --granularity 5m \
  --format json
```

Other dimensions and metric names exist; run `vc metrics --help` to discover them, and check https://vercel.com/docs/cli/metrics for the full catalog. If the command errors with "metrics not enabled" or similar, the project isn't on Observability Plus — fall back to the dashboard URL (`/firewall/traffic?filter=<ruleId>`) for the same data.

## Best practices

The firewall sits in front of every request. A misconfigured rule can block real users, kill SEO crawlers, or break checkout. Treat changes like a production database migration: stage, review, and let the user pull the trigger.

- **Roll new rules out in stages, not in one shot.** A new rule's blast radius is unpredictable until real traffic hits it. Walk every meaningful rule through the stages below, asking the user to `vercel firewall publish --yes` between each. Don't skip stages even if a rule "obviously" matches only attackers — common JA4s and user agents collide with real users far more often than they look like they will.
  1. **Log everywhere.** Add the rule with `--action log` so it records hits to the Firewall dashboard but blocks nothing.

     ```bash
     vercel firewall rules add "Block exploit probes" \
       --condition '{"type":"path","op":"inc","value":["/wp-admin","/.env","/.git/config","/phpmyadmin"]}' \
       --action log --yes
     ```

  2. **Have the user review traffic in the dashboard.** Get the rule ID from the `rules add` output or `vercel firewall rules list --json` (look for the `id` field — rule IDs start with `rule_`). Read the team and project slugs from `.vercel/project.json` (`orgSlug` / `projectName`) or via `vercel project ls`. Construct the filtered traffic URL and ask the user to open it:

     ```
     https://vercel.com/<team>/<project>/firewall/traffic?filter=<ruleId>
     ```

     Have them confirm only the intended traffic is matching (no real users, no SEO crawlers, no internal tools) before moving on.

  3. **Block in preview first.** Edit the rule to `deny` (or `challenge`) and add an `environment = preview` condition so production stays in log mode. This lets the user hit a preview deployment and confirm the block fires correctly without exposing real users:

     ```bash
     vercel firewall rules edit "Block exploit probes" \
       --action deny \
       --condition '{"type":"path","op":"inc","value":["/wp-admin","/.env","/.git/config","/phpmyadmin"]}' \
       --condition '{"type":"environment","op":"eq","value":"preview"}' \
       --yes
     ```

     Have the user publish, then test the affected paths in a preview URL. Re-check the dashboard URL filtered by rule ID to see the blocks land.

  4. **Block in production.** Once the user is satisfied with the production log data, edit to `deny` / `challenge` and have them publish. Keep the dashboard URL handy for the first 24h in case you need to roll back with `--action log` or `rules disable`.

- **Stage drafts; let the user publish.** Mutating commands (`rules add/edit/enable/disable/remove/reorder`, `ip-blocks block/unblock`) only stage. Run `vercel firewall diff` to show what will change, then **ask the user to run `vercel firewall publish --yes` themselves** — don't push to production on their behalf. Use `discard --yes` only if the user asks to abandon staged changes.

- **Don't run commands the CLI blocks for agents.** Surface what the user needs to do instead:
  - `vercel firewall rules add --ai "..."` and `vercel firewall rules add` (wizard) — TTY-only. Use `--condition` flags or `--json`.
  - `vercel firewall attack-mode enable` — requires explicit interactive confirmation; have the user run it.
  - `vercel firewall system-mitigations pause` — pauses platform DDoS protection across the project; have the user run it and resume ASAP.

- **Inspect before recommending publish.** A `deny` with a loose condition (e.g., `path` starts with `/`) blocks the entire site. Always `vercel firewall rules inspect "Name" --expand` and `vercel firewall diff` before handing the publish step to the user.

- **Tune rate limits gently.** Start with a generous `--rate-limit-requests` (5–10× the expected legitimate rate) and `--rate-limit-action log`. After the user reviews dashboard data, tighten the limit and switch the action to `rate_limit`, `challenge`, or `deny`.

- **Keep bypasses narrow.** When unblocking trusted automation, scope by a shared-secret header **plus** an IP or CIDR. Avoid wide-open bypasses (e.g., a single header with a known value an attacker could guess).

- **Don't over-block.** User agents, JA4, and IP addresses may collide with real users far more than they look like they will:
  - **JA4 fingerprints are shared across millions of clients.** A single Chrome point release, a single iOS version, or a popular mobile SDK all produce the same JA4. "Block this JA4" can silently take out an entire browser cohort. Before recommending a JA4 rule, run it through the staged log → preview → log-prod → block flow above and have the user confirm the dashboard shows only attacker behavior (high request rate, suspicious paths, anomalous geos) — not just "this JA4 hit `/login` once."
  - **User-agent substring rules over-match constantly.** `sub` matches like `crawler`, `bot`, `python`, `curl`, or `headless` will block legitimate tools (uptime monitors, link previewers, SEO auditors, partner integrations, the user's own CI). For known-good crawlers (Googlebot, Bingbot, Slack/Discord/X unfurlers, etc.) prefer Vercel's verified-bot signals over UA strings, and pair UA conditions with another condition (path, geo, rate) so a single UA token can't take down a whole class of clients.
  - **Sanity-check before staging.** Before adding a block, ask the user: "Does this fingerprint also match Chrome on macOS / our mobile app / a partner's webhook?" If you don't know, the answer is "log first, decide later."

## External reverse proxies

External proxies in front of Vercel reduce firewall and Bot Protection accuracy: real client IPs become opaque, signal reliability drops, legitimate users may be repeatedly challenged. Avoid when you can. If required, use **Verified Proxy** so Vercel trusts your proxy's headers from a known egress range. https://vercel.com/docs/security/reverse-proxy

## Official Documentation

- [Vercel Firewall](https://vercel.com/docs/vercel-firewall)
- [Bot management](https://vercel.com/docs/bot-management)
- [Vercel CLI](https://vercel.com/docs/cli/firewall)
