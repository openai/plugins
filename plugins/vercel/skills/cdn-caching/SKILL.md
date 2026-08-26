---
name: cdn-caching
description: Debug Vercel CDN caching — cache hit rate, stale content, revalidation behavior, ISR + PPR, per-request cache reasons (cacheReason), and costs.
metadata:
  priority: 6
  docs:
    - 'https://vercel.com/docs/caching'
    - 'https://vercel.com/docs/caching/cdn-cache'
    - 'https://vercel.com/docs/incremental-static-regeneration'
    - 'https://vercel.com/docs/cli/metrics'
  bashPatterns:
    - '\bvercel\s+cache\s+(purge|invalidate|dangerously-delete)\b'
  promptSignals:
    phrases:
      - 'cache hit rate'
      - 'isr cost'
      - 'isr read units'
      - 'isr write units'
      - 'stale content'
      - 'x-vercel-cache'
      - 'cache reason'
      - 'cacheReason'
      - 'x-vercel-cache-reason'
      - 'stale_time'
      - 'stale_tag'
      - 'stale_error'
      - 'draft_mode'
      - 'prerender_bypass'
    allOf:
      - [cache, debug]
      - [stale, cache]
      - [revalidation, count]
      - [cache, reason]
      - [why, stale]
      - [why, bypass]
      - [cache, miss]
    anyOf:
      - 'revalidate'
      - 'prerender'
      - 'invalidate'
      - 'draft mode'
      - 'crawler'
      - 'cold cache'
      - 'request collapsed'
    minScore: 6
---

# Vercel Caching

You are an expert in understanding Vercel's caching infrastructure, and how the CDN Cache, ISR, and PPR work.

## Core Knowledge

- ISR (and PPR, a rendering strategy built on it) is a framework feature — Next.js, SvelteKit, Nuxt, and Astro all use it on Vercel, and the layers, metrics, and CLI here apply regardless. (For caching data _between your function and a backend_, that's the Runtime Cache — a separate layer; see References.)
- **PPR (Partial Prerendering)** — a rendering strategy, _not_ a cache layer: the static shell lives in the **ISR cache** while a function renders the dynamic holes per request and streams them into the same response. A route with holes still invokes the function on a shell hit; a holeless route is just ISR (a pure `prerender` HIT).

### How caching works

Vercel caches at multiple layers between the visitor and your backend. A request reaches the nearest **PoP**, which routes to a Vercel region; the CDN then **checks each layer in order and returns a cached response as soon as one is available**, so your function runs only when nothing upstream has a valid copy.

#### Cache layers

- **CDN cache** — regional, ephemeral. On a hit the region returns the response with no function call. Reads/writes are **free**.
- **ISR cache** — durable, in a single [Function region](https://vercel.com/docs/functions/configuring-functions/region). On a CDN miss, Vercel reads here _before_ invoking your function (cache shielding), then replicates the result back to the CDN. Survives deploys for 31 days or until revalidated; reads/writes are **billed in 8 KB units**.
- **Function invocation** — runs only if neither cache has a valid copy. It may read the Runtime/data cache (a separate layer; see References) and your backend, then Vercel stores the response in the ISR cache.
- **Image cache** — optimized images, cached on the CDN after the first transform.
- Purges propagate globally in ~300 ms.

**Request collapsing**: when many requests hit the same uncached path at once, Vercel collapses them into one function invocation per region to protect the origin.

#### Key concepts

- **Cache hit rate** — share served from cache (`HIT`/`STALE`/`PRERENDER`) versus origin (`MISS`/`REVALIDATED`). Measure it over _cacheable_ requests — exclude `BYPASS` and `(not set)` (redirects, errors, uncacheable methods), or they drag the ratio down for non-cache reasons. Low hit rate means more origin load and higher latency.
- **Revalidation** — refreshing cached content. **Time-based** runs automatically after an interval; **on-demand** runs when you call an API. Both use stale-while-revalidate: visitors keep getting the cached version while the new one regenerates in the background.
- **Invalidate vs. dangerously-delete** — two ways to clear content, with very different blast on hit rate:
  - _Invalidate_ (`invalidateByTag`, Next.js `revalidateTag`/`revalidatePath`) = stale-while-revalidate. Keeps serving stale while refreshing in the background → response shows `x-vercel-cache: STALE`.
  - _Dangerously-delete_ (`dangerouslyDeleteByTag`, Next.js `updateTag` or a revalidate with no lifetime) = hard removal. The next request blocks in the **foreground** to regenerate → `x-vercel-cache: REVALIDATED`.
- **Cache tags & blast radius** — tags group cached entries so one call can clear many. A coarse tag attached to thousands of paths has a large _blast radius_: a single write drops them all and the hit rate collapses until they re-warm. Prefer granular tags (`product-${id}`) plus a roll-up tag.
- **Cache status** (`x-vercel-cache` response header) — the _outcome_:

  | Value         | Meaning                                                          |
  | ------------- | ---------------------------------------------------------------- |
  | `HIT`         | Served from cache; no function ran                               |
  | `MISS`        | Not cached; origin/function ran                                  |
  | `STALE`       | Served stale while revalidating in background (SWR / invalidate) |
  | `PRERENDER`   | Served a prerendered ISR/PPR shell                               |
  | `REVALIDATED` | Foreground revalidation after a delete (or `Pragma: no-cache`)   |
  | `BYPASS`      | Caching skipped (`no-store`, `private`, cookies, etc.)           |

- **Cache reason** (`cacheReason`) — the finer _explanation_ of that outcome for a single request. The `cache_result` metric lumps all `MISS`es (and all `STALE`s) together; the reason is the only thing that tells them apart. Nine values, three per group:

  | `cacheReason`      | Refines  | Meaning                                                                       |
  | ------------------ | -------- | ----------------------------------------------------------------------------- |
  | `cold`             | MISS     | Cache empty for this key/variant (first request or evicted); the function ran |
  | `collapsed`        | MISS     | Concurrent requests to one uncached path collapsed into a single invocation   |
  | `error`            | MISS     | An error prevented serving from cache                                         |
  | `draft_mode`       | → BYPASS | Next.js Draft Mode active — bypassed so editors see live content              |
  | `prerender_bypass` | → BYPASS | Prerender-bypass cookie/token present                                         |
  | `crawler`          | → BYPASS | SEO-crawler UA — full response served so bots index real content              |
  | `stale_time`       | STALE    | Time-based `revalidate` interval elapsed; regenerating in background (SWR)     |
  | `stale_tag`        | STALE    | Tag invalidated (`revalidateTag` / `invalidateByTag`); regenerating           |
  | `stale_error`      | STALE    | A revalidation attempt **failed**; serving the last-good copy (a bug signal)  |

  A raw `MISS` with reason `draft_mode` / `prerender_bypass` / `crawler` is **displayed as `BYPASS`** (all usually expected). The three `stale_*` reasons separate a healthy time refresh (`stale_time`) from a broad-tag blast (`stale_tag`) from a failing regen (`stale_error`). Read `cacheReason` from `vercel logs` or the dashboard Logs "Reason" row — the `x-vercel-cache-reason` header is internal-only and not visible via `curl`.

## Investigating cache issues

Reach for the Vercel CLI. `vercel metrics` gives aggregate numbers (requires [Observability Plus](https://vercel.com/docs/observability/observability-plus)); `vercel logs` shows per-request behavior.

Metrics need to be queried by team and project (`-S <team> -p <project>`). Filter production with `-f "environment eq 'production'"` (there is no `--prod` flag). Run `vercel metrics schema <metric>` to discover dimensions; use `-F json` for machine-readable output. With `-g`, remember **`--limit` is per time bucket** — omit `-g` when you need totals across the whole window.

### Cache hit rate

Start here for an overall picture of how well caching is working.

**Step 1 — overall split.** Group `vercel.request.count` by `cache_result`. Treat `HIT`, `STALE`, and `PRERENDER` as cache-served; focus investigation on `MISS`. Exclude `BYPASS` and `(not set)` when computing a hit rate over _cacheable_ traffic (see [Debugging BYPASS traffic](#debugging-bypass-traffic)). `STALE` means stale-while-revalidate is working — dig into revalidation frequency in [Analyzing ISR costs](#analyzing-isr-costs), not here.

```bash
vercel metrics vercel.request.count -S <team> -p <project> \
  -f "environment eq 'production'" --group-by cache_result --since 24h
```

**Step 2 — where misses concentrate.** Split the `MISS` bucket (and optionally `STALE`) by `path_type`, then by `route` or `request_path`:

```bash
vercel metrics vercel.request.count -S <team> -p <project> \
  -f "environment eq 'production' and cache_result eq 'MISS'" \
  --group-by path_type --since 24h

vercel metrics vercel.request.count -S <team> -p <project> \
  -f "environment eq 'production' and cache_result eq 'MISS' and path_type eq 'prerender'" \
  --group-by request_path --since 24h
```

**What to expect:** `prerender` routes (static shells, ISR pages) should show a high share of `HIT`/`PRERENDER`. A `prerender` path with a disproportionate `MISS` count is your short list for per-path header inspection (`curl` above) and code review.

`streaming_func` routes render dynamically by default, but you can still cache them with `Cache-Control` headers — matching requests are cached on the CDN. Each cache entry varies by `Vary` headers (cookies, RSC, etc.) as well as path and query parameters, so expect more cache keys and a lower hit rate than a fully static `prerender` route.

### Analyzing ISR costs

Once you know hit rate, quantify ISR spend and whether revalidation — not traffic volume — is driving it.

**Utilization vs. ISR billing.** **Utilization** is `vercel.request.count` — total request volume. **ISR cost** is billed separately in 8 KB units: `read_units` when the regional CDN misses and falls through to the ISR cache, and `write_units` on every revalidation/regeneration. The regional CDN shields ISR heavily — most requests never touch the ISR layer, so **read_units will be far below request count**. Do not compare read_units to write_units as a utilization check; focus on **write_units** (revalidation cost) and how they relate to total traffic.

```bash
vercel metrics vercel.request.count -S <team> -p <project> -a sum --since 24h
vercel metrics vercel.isr_operation.write_units -S <team> -p <project> -a sum --since 24h
```

**Write utilization = cache serves ÷ ISR writes** — cached reads per regeneration.

```bash
# numerator: cache serves — sum the HIT + STALE + PRERENDER buckets
vercel metrics vercel.request.count -S <team> -p <project> \
  -f "environment eq 'production' and (cache_result eq 'HIT' or cache_result eq 'STALE')" \
  --group-by route -a sum --since 24h
# denominator: ISR writes
vercel metrics vercel.isr_operation.write_units -S <team> -p <project> \
  -f "environment eq 'production'" --group-by route -a sum --since 24h
```

High is good; near or below ~1 means you regenerate about as fast as the page is read (wasted writes) → lengthen the revalidate interval or move time-based to on-demand tag revalidation.

**Which routes revalidate most.** Break write units down by `route` and `request_path` to find paths that regenerate often relative to traffic:

```bash
vercel metrics vercel.isr_operation.write_units -S <team> -p <project> \
  -a sum --group-by route --since 24h

vercel metrics vercel.isr_operation.write_units -S <team> -p <project> \
  -a sum --group-by request_path --since 24h
```

**Regeneration vs. serving.** Group write units by `path_type` — concentration in `background_func` confirms revalidation (not per-request dynamic work) is the cost driver.

**Time-based vs. tag-based revalidation.** Time-based intervals regenerate on a schedule whether or not content changed — often inefficient. Tag-based on-demand revalidation is usually better, but an **overly broad tag** has a large blast radius: one invalidate drops every entry that carries it.

- **Tag blast radius** — group write units by `cache_tags`. If many _unrelated_ routes show near-identical write counts, a shared hot tag is invalidating them in lockstep (e.g. every blog post rewriting at the same rate because they share one broad `blogPost` tag):

```bash
vercel metrics vercel.isr_operation.write_units -S <team> -p <project> \
  -a sum --group-by cache_tags --since 24h
```

- **What triggered revalidation** — group `vercel.request.count` by `triggering_tag` to see which tags fire most often (`triggering_tag` is on request count only, not ISR operation metrics. It is one of the tags that triggered the page to be stale):

```bash
vercel metrics vercel.request.count -S <team> -p <project> \
  -f "triggering_tag ne null" --group-by triggering_tag --since 24h
```

Tags with a large blast radius that revalidate frequently are the usual root cause of high write_units. Prefer granular tags (`product-${id}`) and on-demand invalidation over short time-based intervals for event-driven content.

**Confirm in code.** Metrics tell you _which_ tag is hot; the repo tells you _why_. Grep for the tag's invalidation call site — `revalidateTag(`, `invalidateByTag(`, `updateTag(`, `dangerouslyDeleteByTag(` — and read the trigger. A CMS webhook or a sync cron that invalidates a **broad** tag on every event (instead of a specific `${type}:${id}`) is the classic amplifier.

### Debugging BYPASS traffic

The largest legitimate sources of `BYPASS` are **Draft Mode** and **SEO crawlers**. Draft Mode must bypass cache so editors see live content. SEO bots must receive the **full response** — especially on PPR routes where the static shell and dynamic holes are assembled at request time — so crawlers index what users actually see. That BYPASS is expected, not a misconfiguration.

Before tuning headers or revalidate intervals, confirm what's left after those two buckets:

```bash
vercel metrics vercel.request.count -S <team> -p <project> \
  -f "cache_result eq 'BYPASS'" --group-by bot_category --since 24h

vercel metrics vercel.request.count -S <team> -p <project> \
  -f "cache_result eq 'BYPASS'" --group-by user_agent --since 24h

vercel metrics vercel.request.count -S <team> -p <project> \
  -f "cache_result eq 'BYPASS'" --group-by request_method --since 24h
```

The **Firewall/WAF** with the `vercel-firewall` skill can be used to manage verified SEO crawlers, block abusive bots, and rate-limit junk traffic before it distorts your hit-rate picture.

## Reducing ISR cost

- **Prefer tag-based over time-based revalidation.** Replace short `revalidate` intervals with on-demand `revalidateTag` / `invalidateByTag` when content changes — time-based regeneration runs whether or not anything changed. If using Cache Components, analyze `cacheLife` calls with the `next-cache-components` skill.
- **Scope tags to specific IDs.** Invalidate `blogPost:<id>`, not a generic `blogPost`/`page` tag — one broad invalidate regenerates everything that carries it.
- Tune the revalidate interval where your framework declares it (Next.js `revalidate` / `cacheLife`, SvelteKit `isr`, Nuxt `routeRules`, Astro). For Next.js Cache Components, see the `next-cache-components` skill.
- Use `CDN-Cache-Control` headers to cache dynamic functions.

### Inspect one path

```bash
curl -sSI https://<host>/<path> | grep -iE 'x-vercel-cache|x-matched-path|cache-control|vary|age|set-cookie'
```

This zero-dependency first reach shows the status (`x-vercel-cache`), the cache directives (`Cache-Control` / `CDN-Cache-Control` / `Vercel-CDN-Cache-Control`), and — crucially — **`x-matched-path`**, which reveals rewrites like `/precomputed/exp~.../...` that expose experiment/flag precomputation. `vary` flags personalization (RSC, cookies); `set-cookie` forces `BYPASS`. For a per-phase timing breakdown, `vercel httpstat /some/path` (CLI v48.9.0+; needs the `httpstat` tool installed) adds latency stats. A path that should cache but shows `MISS`/`BYPASS` usually has `private`, `no-store`, `max-age=0`, a per-request input (cookies/headers/`searchParams`), or an uncacheable method (see FAQ).

**Inspect one request.** When metrics or headers give you a request ID, pull the full log record:

```bash
vercel logs --request-id <request-id> --json
```

Use `--json` so the agent can parse cache status, path, and timing fields programmatically.

## FAQ

- **What are prerender variant misses?** When a route uses a dynamic param, each distinct cache-key variant is prerendered and cached separately, so each variant misses on its first hit per region and low-traffic ones rarely stay warm. The most common modern cause is **feature-flag / experiment precomputation** — middleware picks a variant per request (`/precomputed/exp~.../...` paths), and flags × routes × PPR segments multiply into thousands of ISR entries (also a middleware-invocation cost). Fix: collapse the variant matrix (retire finished experiments), or accept the cost.
- **Does PPR avoid function invocations?** No — a PPR route has dynamic holes by definition, so the cached shell hit still runs the function to fill them. (A route with _no_ holes is just ISR and serves a pure `prerender` HIT — see Key concepts.)
- **Why are there more function invocations than PPR requests?** PPR requests have a static shell and a dynamic function invocation. When the static shell needs to be regenerated, it incurs a function invocation on top of the dynamic function for the content.

## Related skills

- `vercel-firewall` — manage verified SEO crawlers, block abusive bots, and rate-limit junk BYPASS traffic.
- `runtime-cache` — caching data _between your function and a backend_ (per-region key-value / data cache). A different layer from the CDN/ISR caches; use it to cache an API response or query result inside a function.
- `next-cache-components` — Next.js `use cache`, `cacheLife`, `cacheTag`, and `revalidate` tuning (one framework's ISR/PPR controls).

## References:

- Caching overview: https://vercel.com/docs/caching
- ISR: https://vercel.com/docs/incremental-static-regeneration
- Partial Prerendering (PPR): https://vercel.com/docs/partial-prerendering
- Cache-Control headers: https://vercel.com/docs/caching/cache-control-headers
- Diagnosing and fixing cache issues (full runbook): https://vercel.com/docs/caching/cdn-cache/debug-cache-issues
- vercel metrics CLI: https://vercel.com/docs/cli/metrics
- vercel logs CLI: https://vercel.com/docs/cli/logs
