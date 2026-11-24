---
name: cognitivedb-manage-connections
description: >-
  List, inspect, check, and delete saved CognitiveDB cloud storage and database
  connections, collect database metadata, and prepare S3 IAM Role trust policies.
  Use for connections supporting Cloud or Database Ingestion.
metadata:
  version: "dev-1.0.5-external.3"
---

# Manage CognitiveDB Connections

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

## Boundaries

- Own saved Connection inspection, connectivity checks, deletion, database
  metadata collection, and S3 trust-policy preparation in the selected Space.
- For Connection creation or configuration changes, direct the user to the
  CognitiveDB platform's Connection settings. Resume with the saved Connection
  after the user completes the change.
- Route external source analysis to `cognitivedb-data-analysis`.
- Route source browsing for ingestion and task creation to
  `cognitivedb-manage-ingestion` with the verified Connection identity and scope.

## Core Instructions

- Bind the task's selected Space and supply `space_id` to each scoped Tool.
- For inventory, list cloud storage or database Connections with the requested
  provider filters. Continue pagination while `hasMore` is true. An inventory
  request needs no connectivity check or single-Connection selection.
- For one Connection, resolve its exact saved name and provider from list or
  show. Ask for a selection when names are ambiguous. For cloud storage, carry
  the name and `connectionType` together; for databases, retain the returned
  provider and metadata scope. Use the live Tool's supported provider set.
- Read saved details for inspection; use the dedicated check Tool for a live
  connectivity test. Cloud storage checks can update saved status and timestamp;
  database checks do not change saved settings. Report the returned test result.
- For MySQL driver compatibility, use `cognitivedb_mysql_driver_list`
  in the selected Space. Connection creation remains in platform settings.
- For database metadata collection, confirm the exact saved Connection and
  collection scope, submit once, and preserve the returned collection status.
  Read that Connection again for progress; an accepted request is not completed
  collection. Inspect an uncertain submission through saved state without
  resubmitting it.
- For S3 IAM Role trust preparation or repair, call
  `cognitivedb_s3_connection_generate_trust_policy`, reusing a supplied External ID.
  Show the returned policy for the user to apply in AWS. For Role setup, read
  [AWS IAM Role setup](references/aws-iam-role-setup.md); for requested S3
  permission guidance, read [S3 read policy](references/aws-s3-read-policy.md).
  Have the user save the resulting Connection settings in CognitiveDB, then
  check the exact saved Connection.
- Before deletion, show the exact Connection, provider, Space, and impact on
  dependent ingestion. Confirm deletion of the saved Connection; external
  storage, database data, and provider identities remain. Delete once, then
  verify absence through show or a complete scoped listing. If the outcome is
  uncertain, inspect the exact target. Retry at most once when that inspection
  proves deletion did not occur, the live contract permits retry, and the user
  gives fresh approval.
- Present required questions and approvals through the host's interaction
  mechanism. Carry only Connection identity, scope, status, and requested public
  details into ingestion handoffs. Keep credentials in the platform settings.

## Allowed MCP Tools

- `cognitivedb_cloud_storage_connection_check`
- `cognitivedb_cloud_storage_connection_delete`
- `cognitivedb_cloud_storage_connection_list`
- `cognitivedb_cloud_storage_connection_show`
- `cognitivedb_database_connection_check`
- `cognitivedb_database_connection_delete`
- `cognitivedb_database_connection_list`
- `cognitivedb_database_connection_metadata_collect`
- `cognitivedb_database_connection_show`
- `cognitivedb_mysql_driver_list`
- `cognitivedb_s3_connection_generate_trust_policy`
- `cognitivedb_space_current_get`
