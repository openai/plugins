# Monitoring & Debugging

## Logs

```bash
vercel logs <deployment-url>                   # view logs
vercel logs --follow                           # stream live
vercel logs --level error --level warn         # filter by severity
vercel logs --source lambda                    # filter by source (lambda, edge, static)
vercel logs --since 2024-01-01                 # filter by time
vercel logs --query "timeout"                  # search
```

## Metrics

```bash
vercel metrics schema                                                    # list available metrics
vercel metrics schema vercel.function_invocation                         # inspect a metric prefix
vercel metrics vercel.function_invocation.count --since 1h               # query linked project
vercel metrics vercel.request.count --group-by http_status --since 6h    # group by schema dimension
vercel metrics vercel.function_invocation.request_duration_ms -a avg --group-by route --since 1h
vercel metrics vercel.ai_gateway_request.cost -a sum --group-by ai_provider --since 7d
vercel metrics vercel.speed_insights_metric.lcp -a p75 --group-by route --since 7d
vercel metrics --all vercel.function_invocation.count --group-by project_id --since 24h
vercel metrics vercel.function_invocation.count -f "http_status ge 500" --group-by error_code --since 1h --format=json
```

## Inspecting Deployments

```bash
vercel inspect <url>               # deployment details
vercel inspect <url> --wait        # wait for completion
vercel inspect <url> --logs        # show build logs
```

## `vercel curl` — Access Preview Deployments

**Use `vercel curl` to access preview deploys.** It handles deployment protection automatically — no need to disable protection or manage bypass secrets.

```bash
vercel curl /api/health --deployment $PREVIEW_URL
vercel curl /api/data --deployment $PREVIEW_URL -- -X POST -d '{"key":"value"}'
```

**Do not disable deployment protection.** Use `vercel curl` instead.

## Finding Regressions

`vercel bisect` performs a binary search across deployments to find which one introduced a problem:

```bash
vercel bisect --good <url> --bad <url> --path /api/users
vercel bisect --run ./test-script.sh    # automated testing
```

## Cache

```bash
vercel cache purge                    # purge CDN cache
vercel cache invalidate --tag mytag   # invalidate by cache tag
```
