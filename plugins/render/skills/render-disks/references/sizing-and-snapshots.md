# Disk Sizing and Snapshots

## Sizing Guidance

| Use case | Suggested starting size | Notes |
|----------|------------------------|-------|
| File uploads (small app) | 1-5 GB | Grow as needed |
| CMS media (WordPress, Ghost) | 5-10 GB | Depends on media volume |
| Self-managed database (MySQL, MongoDB) | 10-50 GB | Match expected data volume |
| Infrastructure (Elasticsearch, Kafka) | 20-100 GB | Plan for index/log growth |

**Key rule:** Start small. You can increase disk size at any time without downtime. You **cannot** decrease disk size.

Increasing disk size:
1. Dashboard > service > Disks > edit size
2. Additional storage becomes available within seconds
3. No deploy or restart needed

## Snapshot Lifecycle

| Property | Value |
|----------|-------|
| Frequency | Every 24 hours (automatic) |
| Retention | At least 7 days |
| Scope | Full disk contents |
| Encryption | Encrypted at rest |
| Restore type | Full restore only (no partial/file-level restore) |

## Restore Procedure

1. Go to Dashboard > service > Disks
2. Select the snapshot to restore
3. Confirm the restore

**Warnings:**
- All changes after the snapshot are **permanently lost**
- The service restarts during restore
- Restore is **not suitable for database recovery** — use database-native tools

## Cost Patterns

Persistent disks are billed based on provisioned size, not used size. Billing starts when the disk is created and continues until it's removed.

Minimize cost by:
- Starting with the smallest viable size
- Not provisioning "just in case" capacity
- Using managed services (Postgres, Key Value) instead of self-managed databases on disk where possible

## When NOT to Use a Disk

| Scenario | Better alternative |
|----------|--------------------|
| Relational database | **Render Postgres** (managed backups, PITR, replicas) |
| Cache or queue | **Render Key Value** (managed, no disk management) |
| Large file storage (S3-like) | **External object storage** (AWS S3, Cloudflare R2) |
| Temporary build artifacts | Ephemeral filesystem (default, no disk needed) |
| Shared storage across services | External storage service (disks are single-service only) |
