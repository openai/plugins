# Database Debugging

Diagnose and fix PostgreSQL database issues on Render using MCP tools.

## When to Use Database Debugging

Use these techniques when you see:
- `ECONNREFUSED` or connection errors
- `ETIMEDOUT` on database operations
- Slow queries affecting application performance
- Connection pool exhaustion
- Database CPU/memory alerts

## Connection Debugging

### Check Database Status

```
list_postgres_instances()
```

Verify the database exists and note its ID.

### Get Database Details

```
get_postgres(postgresId: "<postgres-id>")
```

### Check Connection Metrics

```
get_metrics(
  resourceId: "<postgres-id>",
  metricTypes: ["active_connections"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

### Query Active Connections

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT state, count(*) FROM pg_stat_activity GROUP BY state"
)
```

**Connection states:**
| State | Meaning |
|-------|---------|
| `active` | Running a query |
| `idle` | Connected but not running query |
| `idle in transaction` | In a transaction, not running query (potential issue) |
| `idle in transaction (aborted)` | Transaction failed, connection stuck |

### Check Connection Limits

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT max_conn, used, res_for_super, max_conn - used - res_for_super AS available FROM (SELECT count(*) used FROM pg_stat_activity) t, (SELECT setting::int res_for_super FROM pg_settings WHERE name = 'superuser_reserved_connections') t2, (SELECT setting::int max_conn FROM pg_settings WHERE name = 'max_connections') t3"
)
```

**Connection limits by plan:**
| Plan | Max Connections |
|------|----------------|
| Free | 97 |
| Basic | 97 |
| Standard | 120-500 |
| Pro | 500+ |

### Fix Connection Issues

**Connection pool exhaustion:**
1. Implement connection pooling in your app
2. Reduce connection timeout
3. Close connections properly
4. Upgrade database plan

**Node.js connection pooling:**
```javascript
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,  // Maximum connections in pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

**Python connection pooling:**
```python
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
```

## Query Performance Debugging

### Find Slow Queries

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT query, calls, mean_exec_time, total_exec_time, rows FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"
)
```

**Note:** `pg_stat_statements` must be enabled (it is by default on Render).

### Find Queries by Total Time

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT query, calls, total_exec_time, mean_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10"
)
```

This finds queries that consume the most total time (even if individual executions are fast).

### Analyze Query Plans

For a specific slow query, run EXPLAIN ANALYZE (be careful in production):

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT * FROM users WHERE email = 'test@example.com'"
)
```

**Look for:**
- `Seq Scan` on large tables (missing index)
- High `rows` estimates vs actual rows (stale statistics)
- Nested loops with high row counts (N+1 pattern)

### Check Missing Indexes

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT schemaname, relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch FROM pg_stat_user_tables WHERE seq_scan > 0 ORDER BY seq_tup_read DESC LIMIT 10"
)
```

Tables with high `seq_scan` and low `idx_scan` may need indexes.

### Check Index Usage

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch FROM pg_stat_user_indexes ORDER BY idx_scan DESC LIMIT 20"
)
```

Indexes with `idx_scan = 0` are unused and could be removed.

## Lock Debugging

### Check for Lock Contention

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT blocked_locks.pid AS blocked_pid, blocked_activity.usename AS blocked_user, blocking_locks.pid AS blocking_pid, blocking_activity.usename AS blocking_user, blocked_activity.query AS blocked_statement, blocking_activity.query AS blocking_statement FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid AND blocking_locks.pid != blocked_locks.pid JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid WHERE NOT blocked_locks.granted LIMIT 10"
)
```

### Check Long-Running Queries

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '1 minute' AND state != 'idle' ORDER BY duration DESC"
)
```

## Storage Debugging

### Check Table Sizes

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT schemaname, relname, pg_size_pretty(pg_total_relation_size(relid)) AS total_size, pg_size_pretty(pg_relation_size(relid)) AS table_size, pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10"
)
```

### Check Database Size

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT pg_size_pretty(pg_database_size(current_database())) AS database_size"
)
```

### Check Table Bloat

```
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT schemaname, relname, n_live_tup, n_dead_tup, round(n_dead_tup::numeric / nullif(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_percentage FROM pg_stat_user_tables WHERE n_dead_tup > 1000 ORDER BY n_dead_tup DESC LIMIT 10"
)
```

Tables with high `dead_percentage` (>20%) may need `VACUUM`.

## Database Resource Metrics

### Check Database CPU

```
get_metrics(
  resourceId: "<postgres-id>",
  metricTypes: ["cpu_usage"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

High database CPU usually indicates:
- Slow queries doing full table scans
- Complex joins without proper indexes
- High query volume

### Check Database Memory

```
get_metrics(
  resourceId: "<postgres-id>",
  metricTypes: ["memory_usage"],
  startTime: "<1-hour-ago-ISO8601>"
)
```

## Quick Diagnosis Workflows

### "Database connection refused"

```
# 1. Check database exists and status
list_postgres_instances()

# 2. Check connection count (might be at limit)
get_metrics(resourceId: "<postgres-id>", metricTypes: ["active_connections"])

# 3. Check for stuck connections
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT state, count(*) FROM pg_stat_activity GROUP BY state"
)

# 4. Verify service has correct DATABASE_URL
get_service(serviceId: "<service-id>")
```

### "Database queries are slow"

```
# 1. Find slowest queries
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 5"
)

# 2. Check for missing indexes
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT relname, seq_scan, idx_scan FROM pg_stat_user_tables WHERE seq_scan > idx_scan ORDER BY seq_scan DESC LIMIT 5"
)

# 3. Check database CPU (might be overloaded)
get_metrics(resourceId: "<postgres-id>", metricTypes: ["cpu_usage"])
```

### "Database storage full"

```
# 1. Check current size
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT pg_size_pretty(pg_database_size(current_database()))"
)

# 2. Find largest tables
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 5"
)

# 3. Check for bloat
query_render_postgres(
  postgresId: "<postgres-id>",
  sql: "SELECT relname, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 5"
)
```
