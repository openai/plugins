# Heroku → Render Service Mapping

## How to Use This Reference

Look up the Heroku plan from `ps_list` (dyno size) or `list_addons` (add-on plan slug) and use the corresponding Render plan in the Blueprint or MCP creation call. If the Heroku plan is unknown, use the fallback default.

## Compute (Dynos → Services)

Match by RAM to avoid out-of-memory issues. Worker and cron dynos use the same size mapping as web dynos.

| Heroku dyno | Heroku RAM | Heroku $/mo | Render `plan` value | Render RAM | Render $/mo |
|---|---|---|---|---|---|
| Eco | 512 MB | $5 | `starter` | 512 MB | $7 |
| Basic | 512 MB | $7 | `starter` | 512 MB | $7 |
| Standard-1X | 512 MB | $25 | `starter` | 512 MB | $7 |
| Standard-2X | 1 GB | $50 | `standard` | 2 GB | $25 |
| Performance-M | 2.5 GB | $250 | `pro` | 4 GB | $85 |
| Performance-L | 14 GB | $500 | `pro max` | 16 GB | $225 |
| Performance-L-RAM | 30 GB | $500 | `pro ultra` | 32 GB | $450 |
| Performance-XL | 62 GB | $750 | Custom | 64 GB | ~$712 |
| Performance-2XL | 126 GB | $1,500 | Custom | 128 GB | ~$1,426 |

**Fallback default:** `starter` (when Heroku dyno size is unknown)

**Notes:**
- Worker dynos on Heroku can be any size (Standard-1X, Performance-M, etc.) — use the same mapping based on the dyno size reported by `ps_list`
- Cron jobs use the same mapping — Render cron plans match web/worker plans
- Performance-L-RAM has 4 CPU (half of Pro Ultra's 8 CPU). For non-enterprise customers, default to `pro ultra`. Enterprise customers may negotiate custom pricing (~$356) with Render for a closer CPU match.
- For Performance-XL and Performance-2XL, instruct the user to [contact Render](https://render.com/contact) for custom sizing. The estimates above (~$712, ~$1,426) are based on proportional custom pricing and may vary.
- Enterprise contracts change per-dyno pricing — the "units per dyno" multiplier varies (e.g., Performance-M = 8 units, Performance-L = 16 units of a Standard-1X). Heroku prices above reflect pay-as-you-go rates.

## Postgres (Heroku Postgres → Render Postgres)

Heroku has deprecated Mini and Basic plans. Current tiers are Essential, Standard, and Premium.

Render has three Postgres tiers:
- **Basic** — entry-level, for development and low-traffic apps
- **Pro** — balanced CPU-to-RAM ratio (1:4), for production workloads
- **Accelerated** — memory-optimized CPU-to-RAM ratio (1:8), for high-performance and memory-intensive workloads

Map Heroku Essential → Render Basic. For Standard and Premium, both map to the **same Render plan per tier** — Standard as a single instance, Premium with HA enabled (doubling the Render cost). Tiers 0 and 2 map to Render Pro; tiers 3 through 9 map to Render Accelerated.

### Essential and legacy plans → Render Basic

| Heroku plan | Heroku disk | Heroku $/mo | Render `plan` value | Render `diskSizeGB` | Render $/mo |
|---|---|---|---|---|---|
| Essential-0 | 1 GB | $5 | `basic-256mb` | 1 | $6 + storage |
| Essential-1 | 10 GB | $9 | `basic-256mb` | 10 | $6 + storage |
| Essential-2 | 32 GB | $20 | `basic-1gb` | 32 | $19 + storage |
| Mini (legacy, EOL) | 1 GB | $5 | `basic-256mb` | 1 | $6 + storage |
| Basic (legacy, EOL) | 10 GB | $9 | `basic-256mb` | 10 | $6 + storage |

### Standard and Premium plans → Render Pro / Accelerated

Heroku Standard and Premium share the same tier numbering (X-0 through X-9) with identical vCPU, RAM, and storage specs. The difference is that **Premium includes HA by default**. On Render, both map to the same plan — enable HA on Render to match Premium (which doubles the Render base price for a separate replica).

| Heroku tier | Heroku Standard $/mo | Heroku Premium $/mo | vCPU | RAM | Storage | Render `plan` value | Render `diskSizeGB` | Render $/mo | Render HA $/mo |
|---|---|---|---|---|---|---|---|---|---|
| X-0 | $50 | $200 | 2 | 4 GB | 64 GB | `pro-4gb` | 65 | $55 + storage | $110 + storage |
| X-2 | $200 | $350 | 2 | 8 GB | 256 GB | `pro-8gb` | 256 | $100 + storage | $200 + storage |
| X-3 | $400 | $750 | 2 | 15 GB | 512 GB | `accelerated-16gb` | 512 | $160 + storage | $320 + storage |
| X-4 | $750 | $1,200 | 4 | 30 GB | 768 GB | `accelerated-32gb` | 770 | $350 + storage | $700 + storage |
| X-5 | $1,400 | $2,500 | 8 | 61 GB | 1 TB | `accelerated-64gb` | 1024 | $750 + storage | $1,500 + storage |
| X-6 | $2,000 | $3,500 | 16 | 122 GB | 1.5 TB | `accelerated-128gb` | 1536 | $1,500 + storage | $3,000 + storage |
| X-7 | $3,500 | $6,000 | 32 | 244 GB | 2 TB | `accelerated-256gb` | 2048 | $2,500 + storage | $5,000 + storage |
| X-8 | $4,500 | $8,500 | 64 | 488 GB | 3 TB | `accelerated-512gb` | 3072 | $6,000 + storage | $12,000 + storage |
| X-9 | $5,800 | $11,000 | 96 | 768 GB | 4 TB | `accelerated-768gb` | 4096 | $9,000 + storage | $18,000 + storage |

**How to read the tier number:** The add-on plan slug from `list_addons` looks like `heroku-postgresql:standard-0` or `heroku-postgresql:premium-4` — the number after the hyphen is the tier (X-0, X-4, etc.). Both Standard-4 and Premium-4 map to the same Render plan (`accelerated-32gb`); Premium just needs HA enabled.

**HA pricing note:** Heroku Premium pricing includes HA by default. To match this on Render, enable HA in the Dashboard or Blueprint, which adds a standby replica at the same cost as the primary (effectively 2x). This significantly impacts pricing competitiveness on larger instances — present both the single-instance and HA costs to the user so they can make an informed decision.

### Disk sizing

On Render, storage is billed separately at **$0.30/GB/month** and configured via the `diskSizeGB` field in the Blueprint. Storage is provisioned in **5 GB increments** (minimum 1 GB) and **cannot be scaled down** once provisioned.

**Heuristic:** Carry over the Heroku disk size as the `diskSizeGB` value. Since `diskSizeGB` must be 1 or a multiple of 5, round up to the nearest valid value.

**Disclaimer to present to the user:** Heroku bundles a fixed storage allocation with each plan (e.g., Standard-4 includes 768 GB). On Render, compute and storage are billed separately — compute is the plan price above, and storage is $0.30/GB/month in 5 GB increments. Storage cannot be scaled down once provisioned, so right-size based on actual usage rather than the Heroku allocation. Check your current disk usage with `heroku pg:info` (look for `Data Size`) — if your actual data is much smaller than the allocated disk, start with a smaller `diskSizeGB` to save on storage costs. You can always expand later from the Render Dashboard.

**Fallback default:** `basic-1gb` with no `diskSizeGB` (when Heroku Postgres plan is unknown — Render uses a default disk size)

**Notes:**
- Render Pro and Accelerated both support HA (enable separately in Dashboard or Blueprint)
- For databases beyond tier X-9, contact Render support
- Get actual disk usage from `pg_info` (`Data Size` field) to inform the `diskSizeGB` recommendation

## Key Value (Heroku Redis / Key-Value Store → Render Key Value)

Heroku has rebranded Redis as "Key-Value Store" (Valkey-based). Heroku Redis plans use non-sequential numbering (0, 1, 2, 3, 5, 7, 9, 10, 12, 14). Match by the exact plan number from `list_addons`.

| Heroku plan | Heroku memory | Heroku connections | Heroku $/mo | Render `plan` value | Render RAM | Render connections | Render $/mo |
|---|---|---|---|---|---|---|---|
| Mini | 25 MB | 20 | $3 | `free` | 25 MB | 50 | $0 |
| Premium-0 | 50 MB | 40 | $15 | `starter` | 256 MB | 250 | $10 |
| Premium-1 | 100 MB | 80 | $30 | `starter` | 256 MB | 250 | $10 |
| Premium-2 | 250 MB | 200 | $60 | `starter` | 256 MB | 250 | $10 |
| Premium-3 | 500 MB | 400 | $120 | `standard` | 1 GB | 1,000 | $32 |
| Premium-5 | 1 GB | 1,000 | $200 | `standard` | 1 GB | 1,000 | $32 |
| Premium-7 | 7 GB | 10,000 | $750 | `pro plus` | 10 GB | 10,000 | $250 |
| Premium-9 | 10 GB | 25,000 | $1,450 | `pro max` | 20 GB | 20,000 | $550 |
| Premium-10 | 25 GB | 40,000 | $3,500 | Custom | — | — | Contact Render |
| Premium-12 | 50 GB | 65,000 | $6,500 | Custom | — | — | Contact Render |
| Premium-14 | 100 GB | 65,000 | $12,500 | Custom | — | — | Contact Render |

**Fallback default:** `starter` (when Heroku Redis plan is unknown)

**Notes:**
- Redis pricing heavily favors Render — most tiers cost significantly less on Render than the Heroku equivalent.
- The add-on plan slug from `list_addons` looks like `heroku-redis:mini` or `heroku-redis:premium-0` — use the part after the colon to look up the mapping. Plans 4, 6, 8, 11, and 13 do not exist on Heroku.
- Render Key Value requires `ipAllowList` in the Blueprint (use `0.0.0.0/0` for public access)
- Neither Heroku nor Render supports Redis HA.
- For Premium-10 and above, instruct the user to [contact Render](https://render.com/contact) for custom sizing.

## Runtime Mapping

| Heroku Buildpack | Render Runtime | `runtime` param |
|---|---|---|
| heroku/nodejs | Node | `node` |
| heroku/python | Python | `python` |
| heroku/go | Go | `go` |
| heroku/ruby | Ruby | `ruby` |
| heroku/java | Docker | `docker` |
| heroku/php | Docker | `docker` |
| heroku/scala | Docker | `docker` |
| Multi-buildpack | Docker | `docker` |

## Region Mapping

| Heroku Region | Render Region | `region` param |
|---|---|---|
| us | Oregon (default) | `oregon` |
| eu | Frankfurt | `frankfurt` |

## Not Directly Mappable (Manual)

These Heroku features require manual alternatives on Render:
- **Heroku Pipelines** → Use Render Preview Environments + manual promotion
- **Review Apps** → Render Pull Request Previews
- **Heroku Add-ons Marketplace** → Find equivalent third-party services
- **Heroku ACM (SSL)** → Render auto-provisions TLS for custom domains
- **Private Spaces** → Contact Render for private networking options
- **Heroku Kafka** → Not supported on Render. Recommend cloud providers (Confluent Cloud, AWS MSK, etc.)
- **Hirefire** → Not supported on Render. Recommend Render's native [horizontal autoscaling](https://render.com/docs/scaling) or JudoScale (which is supported).
- **Bandwidth** → Heroku allows ~2 TB/app/month (rarely enforced). Render bandwidth varies by workspace plan: 100 GB (Hobby), 500 GB (Professional), 1 TB (Organization). Additional bandwidth is billed at $0.10/GB.

## Environment Variables to Filter

Always exclude these when migrating env vars:

**Render auto-generates:**
- `DATABASE_URL`
- `REDIS_URL`, `REDIS_TLS_URL`

**Heroku-specific (no Render equivalent):**
- `HEROKU_APP_NAME`
- `HEROKU_SLUG_COMMIT`
- `HEROKU_SLUG_DESCRIPTION`
- `HEROKU_DYNO_ID`
- `HEROKU_RELEASE_VERSION`
- `PORT` (Render sets its own)

**Add-on connection strings (replace with new service URLs):**
- `PAPERTRAIL_*`
- `SENDGRID_*`
- `CLOUDAMQP_*`
- `BONSAI_*`
- `FIXIE_*`
- Any other `*_URL` vars pointing to Heroku add-on services
