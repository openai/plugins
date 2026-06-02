---
name: cron-jobs
description: Vercel Cron Jobs configuration and best practices. Use when adding, editing, or debugging scheduled tasks in vercel.json.
metadata:
  priority: 6
  docs:
    - "https://vercel.com/docs/cron-jobs"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'vercel.json'
    - 'apps/*/vercel.json'
  bashPatterns: []
---

# Vercel Cron Jobs

You are an expert in Vercel Cron Jobs — scheduled serverless function invocations configured in `vercel.json`.

## Configuration

Cron jobs are defined in the `crons` array of `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/daily-digest",
      "schedule": "0 8 * * *"
    }
  ]
}
```

## Key Rules

1. **Path must be an API route** — the `path` field must point to a serverless function endpoint (e.g., `/api/cron/...`)
2. **Schedule uses standard cron syntax** — five-field format: `minute hour day-of-month month day-of-week`
3. **Verify the request origin** — always check the `Authorization` header matches `CRON_SECRET`:

```ts
// app/api/cron/route.ts
export async function GET(request: Request) {
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response("Unauthorized", { status: 401 });
  }
  // ... your scheduled logic
  return Response.json({ ok: true });
}
```

4. **Hobby plan limits** — max 2 cron jobs, minimum interval of once per day
5. **Pro plan** — up to 40 cron jobs, minimum interval of once per minute
6. **Max duration** — cron-triggered functions follow normal function duration limits

## Common Patterns

- **Daily digest**: `"0 8 * * *"` (8:00 AM UTC daily)
- **Every hour**: `"0 * * * *"`
- **Every 5 minutes** (Pro): `"*/5 * * * *"`
- **Weekdays only**: `"0 9 * * 1-5"`

## Debugging

- Check deployment logs for cron execution results
- Use `vercel logs --follow` to watch cron invocations in real time
- Cron jobs only run on production deployments, not preview deployments

## References

- [Cron Jobs documentation](https://vercel.com/docs/cron-jobs)
