# Metrics-Based Debugging

Use Render metrics to diagnose performance issues, resource constraints, and application health problems.

## When to Use Metrics

Use metrics debugging when you see:
- Out of memory errors (OOM, exit code 137)
- Slow response times
- Service crashes or restarts
- Health check timeouts
- Autoscaling issues

## CPU Metrics

### Get CPU Usage

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "cpu_limit"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

### Interpreting CPU

| CPU Usage | Status | Action |
|-----------|--------|--------|
| <70% | Healthy | No action needed |
| 70-85% | Warning | Monitor trends |
| >85% sustained | Critical | Optimize or upgrade plan |

**High CPU causes:**
- Inefficient algorithms
- Missing database indexes (N+1 queries)
- Synchronous blocking operations
- Large JSON parsing/serialization

**CPU Fixes:**
1. Profile code to find hot paths
2. Add caching for repeated computations
3. Optimize database queries
4. Use async/non-blocking operations
5. Upgrade to higher plan

## Memory Metrics

### Get Memory Usage

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage", "memory_limit"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

### Interpreting Memory

| Memory % of Limit | Status | Action |
|-------------------|--------|--------|
| <70% | Healthy | No action needed |
| 70-85% | Warning | Monitor for leaks |
| 85-95% | Danger | Investigate immediately |
| >95% | Critical | OOM imminent |

**Memory limits by plan:**
| Plan | Memory |
|------|--------|
| Free/Starter | 512 MB |
| Standard | 2 GB |
| Pro | 4 GB |

**High memory causes:**
- Memory leaks (objects not garbage collected)
- Large in-memory caches
- Processing large files/datasets in memory
- Too many concurrent connections

**Memory Fixes:**

**Node.js:**
```javascript
// Increase heap size (if on paid plan)
// Set NODE_OPTIONS=--max-old-space-size=2048

// Process data in streams
const stream = fs.createReadStream('large-file.json');
stream.pipe(parser).on('data', processChunk);
```

**Python:**
```python
# Process data in chunks
for chunk in pd.read_csv('large_file.csv', chunksize=1000):
    process(chunk)

# Use generators instead of lists
def process_items():
    for item in large_dataset:
        yield transform(item)
```

## HTTP Performance Metrics

### Get Latency

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpLatencyQuantile: 0.95,
  startTime: "<1-hour-ago-ISO8601>"
)
```

**Common quantiles:**
- `0.5` (p50) - Median, typical experience
- `0.95` (p95) - Most users' worst experience
- `0.99` (p99) - Tail latency, outliers

### Interpreting Latency

| p95 Latency | Status | Likely Cause |
|-------------|--------|--------------|
| <200ms | Excellent | - |
| 200-500ms | Good | Complex queries |
| 500ms-1s | Concerning | DB or external API |
| 1-2s | Poor | Multiple slow operations |
| >2s | Critical | Major bottleneck |

### Get Request Count

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

**Aggregate by status code to find error rates:**
```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count"],
  aggregateHttpRequestCountsBy: "statusCode"
)
```

**Calculate error rate:**
```
error_rate = 5xx_count / total_count * 100
```
Target: <0.1% error rate

### Filter by Endpoint

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_latency"],
  httpPath: "/api/users",
  httpHost: "api.example.com"
)
```

## Instance Metrics

### Get Instance Count

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["instance_count"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

### Interpreting Instance Changes

| Pattern | Meaning |
|---------|---------|
| Increasing | Autoscaling up (traffic increase) |
| Decreasing | Autoscaling down (traffic decrease) |
| Stuck at 1 | Autoscaling may not be enabled |
| Rapid fluctuation | Possible instability |

### Check Autoscaling Targets

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_target", "memory_target"]
)
```

## Bandwidth Metrics

### Get Bandwidth Usage

```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["bandwidth_usage"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

**High bandwidth causes:**
- Large API responses
- Uncompressed responses
- File downloads
- Verbose logging to external services

**Bandwidth fixes:**
1. Enable gzip/brotli compression
2. Paginate large responses
3. Use CDN for static assets
4. Optimize image sizes

## Correlation Analysis

### Correlate Metrics with Deploys

```
# Get deploy times
list_deploys(serviceId: "<service-id>", limit: 10)

# Check metrics around deploy time
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["cpu_usage", "memory_usage", "http_latency"],
  startTime: "<deploy-time-minus-1-hour>",
  endTime: "<deploy-time-plus-1-hour>"
)
```

### Correlate with Errors

```
# Get error timestamps
list_logs(
  resource: ["<service-id>"],
  level: ["error"],
  limit: 50
)

# Check metrics at error time
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage", "cpu_usage"],
  startTime: "<error-time-minus-10-min>",
  endTime: "<error-time-plus-10-min>"
)
```

## Quick Diagnostics

### OOM Diagnosis

```
# 1. Check if memory was at limit before crash
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["memory_usage", "memory_limit"],
  startTime: "<crash-time-minus-30-min>"
)

# 2. Look for memory growth pattern
# Steady growth = memory leak
# Sudden spike = large request or data load
```

### Slow Response Diagnosis

```
# 1. Check if CPU-bound
get_metrics(resourceId: "<id>", metricTypes: ["cpu_usage"])

# 2. Check latency percentiles
get_metrics(resourceId: "<id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.5)
get_metrics(resourceId: "<id>", metricTypes: ["http_latency"], httpLatencyQuantile: 0.99)

# 3. If p99 >> p50, you have outlier requests causing issues
# 4. Check slow endpoints
get_metrics(resourceId: "<id>", metricTypes: ["http_latency"], httpPath: "/api/slow-endpoint")
```

### Crash Loop Diagnosis

```
# 1. Check instance count for restarts
get_metrics(resourceId: "<id>", metricTypes: ["instance_count"])

# 2. Check memory at crash times
get_metrics(resourceId: "<id>", metricTypes: ["memory_usage"])

# 3. Check logs for crash reason
list_logs(resource: ["<id>"], level: ["error"], limit: 100)
```
