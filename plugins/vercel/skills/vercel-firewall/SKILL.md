---
name: vercel-firewall
description: Vercel Firewall and security expert guidance. Use when configuring DDoS protection, WAF rules, rate limiting, bot filtering, IP allow/block lists, OWASP rulesets, Attack Challenge Mode, or any security configuration on the Vercel platform.
metadata:
  priority: 5
  docs:
    - "https://vercel.com/docs/security/vercel-firewall"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - '.vercel/firewall/**'
  bashPatterns:
    - '\bvercel\s+firewall\b'
  promptSignals:
    phrases:
      - 'rate limit'
      - 'rate limiting'
      - 'firewall'
      - 'WAF'
      - 'DDoS protection'
    minScore: 6
---

# Vercel Firewall

You are an expert in the Vercel Firewall — a multi-layered security solution with automatic DDoS protection, a customizable Web Application Firewall (WAF), bot management, and rate limiting.

## Architecture & Rule Execution Order

1. DDoS mitigation rules (automatic, platform-wide)
2. WAF IP blocking rules
3. WAF custom rules (in priority order)
4. WAF Managed Rulesets (OWASP, Bot Protection, AI Bots)

Changes propagate globally in under **300ms**. No redeployment required.

## DDoS Protection (Automatic, All Plans)

- Layer 3/4 mitigation (automatic, always on)
- Layer 7 protection (proprietary, tailored to web apps)
- **Protectd**: Vercel's DoS mitigation infrastructure analyzes ~550K events/sec globally with median mitigation time of **2.5 seconds**
- 40x faster detection with real-time stream processing
- Handles 1B+ suspicious TCP connections per week
- Proven to mitigate 1.37 Tbps attacks with zero downtime

No configuration needed — DDoS protection is always active.

## WAF Custom Rules

### Rule JSON Structure

```json
{
  "name": "Block WordPress scanners",
  "description": "Block common WordPress probe paths",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        {
          "type": "path",
          "op": "re",
          "value": "^/wp-(admin|login|content|includes)/"
        }
      ]
    }
  ],
  "action": {
    "mitigate": {
      "action": "deny"
    }
  }
}
```

**Logic**: Each object in `conditionGroup` is an **OR** group. Conditions within a single group are **AND**ed. Multiple groups are **OR**ed.

### Condition Types (25 available)

| Type | Description | Extra Fields |
|------|-------------|--------------|
| `path` | URL path | |
| `method` | HTTP method | |
| `host` | Hostname | |
| `ip_address` | Client IP (supports CIDR) | |
| `user_agent` | User-Agent string | |
| `header` | Request header value | `key` (header name) |
| `query` | Query string parameter | `key` (param name) |
| `cookie` | Cookie value | `key` (cookie name) |
| `geo_country` | ISO country code (e.g., `US`) | |
| `geo_continent` | Continent code (e.g., `NA`) | |
| `geo_country_region` | State/province code | |
| `geo_city` | City name | |
| `geo_as_number` | ASN | |
| `ja4_digest` | JA4 TLS fingerprint | |
| `ja3_digest` | JA3 TLS fingerprint | |
| `target_path` | Resolved path after routing | |
| `route` | Matched route pattern | |
| `raw_path` | Raw unparsed path | |
| `region` | Vercel edge region code | |
| `protocol` | http/https | |
| `scheme` | URL scheme | |
| `environment` | Deployment environment | |
| `bot_name` | Specific bot name | |
| `bot_category` | Bot category | |
| `server_action` | Next.js Server Action ID | |

### Condition Operators

| Op | Meaning |
|----|---------|
| `eq` | Equals |
| `neq` | Not equals |
| `re` | Regex match |
| `pre` | Starts with |
| `suf` | Ends with |
| `sub` | Contains |
| `inc` | In array |
| `ninc` | Not in array |
| `ex` | Exists |
| `nex` | Not exists |
| `gt` / `gte` | Greater than (or equal) |
| `lt` / `lte` | Less than (or equal) |

Additional optional fields: `neg: true` negates the condition, `key` required for `header`/`query`/`cookie` types.

### Mitigation Actions

| Action | Description |
|--------|-------------|
| `log` | Log only, allow traffic |
| `deny` | Block request (403) |
| `challenge` | JavaScript browser challenge |
| `bypass` | Skip all subsequent WAF rules |
| `rate_limit` | Apply rate limiting (requires `rateLimit` config) |
| `redirect` | Redirect (requires `redirect` config) |

### Persistent Actions

By default each request is evaluated individually. With **persistent actions**, rules are applied to all matching requests for a customizable duration (`actionDuration`), allowing the firewall to remember malicious behavior and block it earlier in the lifecycle.

### Action Options

```json
{
  "action": {
    "mitigate": {
      "action": "deny",
      "actionDuration": "1h",
      "bypassSystem": false,
      "logHeaders": ["user-agent", "x-forwarded-for"],
      "redirect": {
        "location": "https://example.com/blocked",
        "permanent": false
      }
    }
  }
}
```

## Practical Rule Examples

### Block Sanctioned Countries

```json
{
  "name": "Block OFAC Sanctioned Countries",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        {
          "type": "geo_country",
          "op": "inc",
          "value": ["CU", "IR", "KP", "RU", "SY"]
        }
      ]
    }
  ],
  "action": {
    "mitigate": { "action": "deny" }
  }
}
```

### Require API Key Header on /api/ Routes

```json
{
  "name": "Require API Key",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        {
          "type": "header",
          "op": "nex",
          "key": "x-api-key"
        },
        {
          "type": "path",
          "op": "pre",
          "value": "/api/"
        }
      ]
    }
  ],
  "action": {
    "mitigate": { "action": "deny" }
  }
}
```

### Block by JA4 TLS Fingerprint

```json
{
  "name": "Block Known Malicious JA4",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        {
          "type": "ja4_digest",
          "op": "eq",
          "value": "t13d1516h2_8daaf6152771_b0da82dd1658"
        }
      ]
    }
  ],
  "action": {
    "mitigate": { "action": "deny", "actionDuration": "1h" }
  }
}
```

### Block Datacenter ASNs

```json
{
  "name": "Block Known Datacenter ASNs",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        {
          "type": "geo_as_number",
          "op": "inc",
          "value": ["14618", "16509", "15169"]
        }
      ]
    }
  ],
  "action": {
    "mitigate": { "action": "deny" }
  }
}
```

### Challenge cURL Requests

```json
{
  "name": "Challenge cURL",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        { "type": "user_agent", "op": "re", "value": "^curl/" }
      ]
    }
  ],
  "action": {
    "mitigate": { "action": "challenge" }
  }
}
```

## Rate Limiting

### Rate Limit Rule

```json
{
  "name": "API Rate Limit - 100 req/min",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        { "type": "path", "op": "pre", "value": "/api/" }
      ]
    }
  ],
  "action": {
    "mitigate": {
      "action": "rate_limit",
      "rateLimit": {
        "algo": "fixed_window",
        "window": 60,
        "limit": 100,
        "keys": ["ip"],
        "action": "deny"
      }
    }
  }
}
```

### Login Endpoint Protection

```json
{
  "name": "Login Rate Limit",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        { "type": "path", "op": "eq", "value": "/api/auth/login" },
        { "type": "method", "op": "eq", "value": "POST" }
      ]
    }
  ],
  "action": {
    "mitigate": {
      "action": "rate_limit",
      "rateLimit": {
        "algo": "fixed_window",
        "window": 60,
        "limit": 10,
        "keys": ["ip"],
        "action": "challenge"
      }
    }
  }
}
```

### Rate Limit Configuration Options

| Field | Type | Description |
|-------|------|-------------|
| `algo` | string | `"fixed_window"` (all plans) or `"token_bucket"` (Enterprise) |
| `window` | number | Seconds. Min 10, max 600 (Pro), max 3600 (Enterprise) |
| `limit` | number | Max requests per window |
| `keys` | array | Count per: `"ip"`, `"ja4"`, `"user_agent"`, custom headers (Enterprise) |
| `action` | string | When exceeded: `"deny"`, `"log"`, `"challenge"` |

When exceeded with `deny`, returns HTTP 429 with `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers.

## Bot Management

### Bot Protection (GA — Free on All Plans)

Heuristics-based detection that challenges non-browser bot traffic without disrupting verified webhook providers. Formerly "Bot Filter" during beta — renamed to Bot Protection at GA. Enable in log-only mode first to preview traffic impact:

```json
{
  "action": "managedRules.update",
  "id": "bot_protection",
  "value": { "active": true, "action": "challenge" }
}
```

> **Note**: The older `bot_filter` ID is deprecated. Use `bot_protection` in new configurations.

### AI Bot Blocking

Block known AI crawlers (GPTBot, ClaudeBot, etc.):

```json
{
  "action": "managedRules.update",
  "id": "ai_bots",
  "value": { "active": true, "action": "deny" }
}
```

### Allow a Specific Bot (Bypass Rule)

Place this higher in priority than Bot Protection managed rules:

```json
{
  "name": "Allow My Monitoring Bot",
  "active": true,
  "conditionGroup": [
    {
      "conditions": [
        { "type": "user_agent", "op": "eq", "value": "MyMonitorBot/1.0" }
      ]
    }
  ],
  "action": {
    "mitigate": { "action": "bypass" }
  }
}
```

### Enable BotID (Traffic Visibility)

```json
{ "botIdEnabled": true }
```

## IP Allow/Block Lists

### Block an IP

```json
{
  "action": "ip.insert",
  "value": {
    "hostname": "my-site.com",
    "ip": "203.0.113.45",
    "action": "deny",
    "notes": "Malicious scraper"
  }
}
```

### Block a CIDR Range

```json
{
  "action": "ip.insert",
  "value": {
    "hostname": "my-site.com",
    "ip": "203.0.113.0/24",
    "action": "deny",
    "notes": "Bad actor CIDR block"
  }
}
```

### Allow an IP (Bypass All Rules)

```json
{
  "action": "ip.insert",
  "value": {
    "hostname": "my-site.com",
    "ip": "198.51.100.1",
    "action": "bypass",
    "notes": "Internal monitoring IP"
  }
}
```

### IP Rule Actions

| Action | Effect |
|--------|--------|
| `deny` | Block the IP |
| `challenge` | Serve JS challenge |
| `log` | Log traffic only |
| `bypass` | Allow through all rules (allowlist) |

**Note**: `hostname` must match the exact domain. Add separate entries per subdomain.

## OWASP Core Ruleset (CRS)

### Individual CRS Rules

| ID | Protection |
|----|-----------|
| `sqli` | SQL Injection |
| `xss` | Cross-Site Scripting |
| `rce` | Remote Code Execution |
| `lfi` | Local File Inclusion |
| `rfi` | Remote File Inclusion |
| `sd` | Scanner Detection |
| `ma` | Multipart Attack |
| `php` | PHP-specific exploits |
| `gen` | Generic attack patterns |
| `sf` | Session Fixation |
| `java` | Java-specific exploits |

### Enable OWASP Rules

```json
{
  "action": "crs.update",
  "id": "sqli",
  "value": { "active": true, "action": "deny" }
}
```

### Full OWASP + Bot Configuration (PUT)

```json
{
  "firewallEnabled": true,
  "crs": {
    "sqli": { "active": true, "action": "deny" },
    "xss": { "active": true, "action": "deny" },
    "rce": { "active": true, "action": "deny" },
    "lfi": { "active": true, "action": "deny" },
    "rfi": { "active": true, "action": "deny" },
    "sd": { "active": true, "action": "log" },
    "ma": { "active": true, "action": "deny" },
    "gen": { "active": true, "action": "deny" },
    "sf": { "active": true, "action": "deny" },
    "php": { "active": false, "action": "log" },
    "java": { "active": false, "action": "log" }
  },
  "managedRules": {
    "owasp": { "active": true, "action": "deny" },
    "bot_protection": { "active": true, "action": "challenge" },
    "ai_bots": { "active": true, "action": "deny" }
  },
  "botIdEnabled": true
}
```

## Firewall REST API

Base URL: `https://api.vercel.com`
Auth: `Authorization: Bearer <VERCEL_TOKEN>`
Query params: `?projectId=<id>&teamId=<id>`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/security/firewall/config/active` | Read current config |
| `PATCH` | `/v1/security/firewall/config` | Incremental update (add/remove/update rules) |
| `PUT` | `/v1/security/firewall/config` | Full config replacement |
| `POST` | `/v1/security/firewall/bypass` | Create temporary bypass rule |

### PATCH Actions

| Action | Description |
|--------|-------------|
| `firewallEnabled` | Enable/disable firewall (value: boolean) |
| `rules.insert` | Add a custom rule |
| `rules.update` | Update rule (requires `id`) |
| `rules.remove` | Delete rule (requires `id`) |
| `rules.priority` | Reorder rule (requires `id`, value = index) |
| `ip.insert` | Add IP rule |
| `ip.update` | Update IP rule |
| `ip.remove` | Delete IP rule |
| `crs.update` | Enable/configure OWASP CRS rule |
| `crs.disable` | Disable entire CRS |
| `managedRules.update` | Configure managed ruleset |

### Add a Rule via cURL

```bash
curl -X PATCH "https://api.vercel.com/v1/security/firewall/config?projectId=prj_xxx&teamId=team_xxx" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "rules.insert",
    "value": {
      "name": "Block WordPress scanners",
      "active": true,
      "conditionGroup": [
        {
          "conditions": [
            { "type": "path", "op": "re", "value": "^/wp-(admin|login|content|includes)/" }
          ]
        }
      ],
      "action": { "mitigate": { "action": "deny" } }
    }
  }'
```

### Vercel SDK Usage

```ts
import { Vercel } from '@vercel/sdk'

const vercel = new Vercel({ bearerToken: process.env.VERCEL_TOKEN })

// Read current firewall config
const config = await vercel.security.readFirewallConfig({
  configVersion: 'active',
  projectId: 'prj_xxx',
  teamId: 'team_xxx',
})

// Add a rule
await vercel.security.updateFirewallConfig({
  projectId: 'prj_xxx',
  teamId: 'team_xxx',
  requestBody: {
    action: 'rules.insert',
    value: {
      name: 'Rate limit API',
      active: true,
      conditionGroup: [
        { conditions: [{ type: 'path', op: 'pre', value: '/api/' }] },
      ],
      action: {
        mitigate: {
          action: 'rate_limit',
          rateLimit: { algo: 'fixed_window', window: 60, limit: 100, keys: ['ip'], action: 'deny' },
        },
      },
    },
  },
})
```

### Create Temporary Bypass (Attack Challenge Mode)

```bash
curl -X POST "https://api.vercel.com/v1/security/firewall/bypass?projectId=prj_xxx&teamId=team_xxx" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "my-site.com",
    "sourceIp": "198.51.100.42",
    "ttl": 3600000,
    "note": "Temporary bypass for load testing"
  }'
```

## vercel.json WAF Rules

Declaratively define firewall rules in `vercel.json` using the `mitigate` key:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "routes": [
    {
      "src": "/api/(.*)",
      "missing": [
        { "type": "header", "key": "x-internal-token" }
      ],
      "mitigate": { "action": "deny" }
    },
    {
      "src": "/(.*)",
      "has": [
        { "type": "header", "key": "user-agent", "value": "(?i)^curl/" }
      ],
      "mitigate": { "action": "challenge" }
    }
  ]
}
```

Supported actions in `vercel.json`: `"challenge"`, `"deny"` only. Rate limiting, `log`, and `bypass` require the Vercel Firewall dashboard at `https://vercel.com/{team}/{project}/firewall` or the REST API.

## Attack Challenge Mode

- Available on all plans (free)
- Shows browser verification challenge to all visitors during active attacks
- Legitimate bots (Googlebot, webhook providers) automatically pass through
- Internal Function-to-Function calls within the same account bypass automatically
- Blocked requests don't count toward CDN/traffic usage
- Configured via dashboard only: open `https://vercel.com/{team}/{project}/firewall` → **Bot Management** → **Attack Challenge Mode**

## Plan Availability

| Feature | Hobby | Pro | Enterprise |
|---------|-------|-----|-----------|
| DDoS Protection | All | All | All |
| Custom Rules | 5 | 40 | 1000 |
| Rate Limiting | 1 rule | 40 rules | 1000 rules |
| Bot Protection (GA) | Yes | Yes | Yes |
| OWASP CRS | — | — | Yes |
| Token Bucket algo | — | — | Yes |
| Custom rate limit keys | — | — | Yes |

## Observability

- Security event logs in the Firewall tab
- **IP enrichment** — hover any IP in the Firewall dashboard to see ASN, location, and metadata
- Create custom WAF rules directly from dashboard traffic charts (select "Create Custom Rule" from the actions menu)
- Linkable to Monitoring queries for investigations
- DDoS mitigation notifications (alerts on detection)
- BotID traffic visibility when enabled

## Official Documentation

- [Vercel Firewall Overview](https://vercel.com/docs/vercel-firewall)
- [Custom Rules](https://vercel.com/docs/vercel-firewall/vercel-waf/custom-rules)
- [Rate Limiting](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting)
- [IP Blocking](https://vercel.com/docs/vercel-firewall/vercel-waf/ip-blocking)
- [Managed Rulesets](https://vercel.com/docs/vercel-firewall/vercel-waf/managed-rulesets)
- [Attack Challenge Mode](https://vercel.com/docs/vercel-firewall/attack-challenge-mode)
- [Firewall API Guide](https://vercel.com/docs/vercel-firewall/firewall-api)
- [REST API Reference](https://vercel.com/docs/vercel-firewall/firewall-api)
