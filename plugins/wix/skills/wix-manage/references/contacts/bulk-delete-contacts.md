---
name: "Bulk Delete Contacts"
description: Deletes multiple contacts using filter-based bulk delete. Covers safe deletion patterns, GDPR compliance, soft delete alternatives, and batch processing strategies.
---
# Bulk Delete Contacts

## Description
Deletes multiple contacts using the Wix Contacts REST API.

All contacts that meet the specified `filter` and `search` criteria are deleted.
The request should contain a `filter` value or a `search` value, or both.
To perform a dry run, call [Query Contacts](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/contact-v4/query-contacts) with the intended filter options.

When this method is called, a bulk job is started and the job ID is returned.
The job might not complete right away, depending on its size.
The job's status can be retrieved with [Get Bulk Job](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/bulk-job/get-bulk-job).

**IMPORTANT NOTE:** When specific contacts are to be deleted, they should be filtered by id.

## API Endpoint
`POST https://www.wixapis.com/contacts/v4/bulk/contacts/delete`

## Request Example

```bash
curl -X POST \
  'https://www.wixapis.com/contacts/v4/bulk/contacts/delete' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "filter": {
      "info.name.last": "Smith"
    }
  }'
```

## Request Parameters

- `filter` (object, optional): Filter criteria to identify contacts. When specific contacts are to be deleted, filter by `id`.
- `search` (string, optional): Search query to identify contacts.

**Note:** The request should contain a `filter` value or a `search` value, or both.

## Response

The response includes a `jobId` which can be used to track the bulk job status:

```json
{
  "jobId": "00000000-0000-0000-0000-000000000001"
}
```

Use the [Get Bulk Job](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/bulk-job/get-bulk-job) endpoint to check the job status.

## Common Errors

The following errors might occur during the bulk processing and will appear in the bulk job:

- `CANNOT_DELETE_SITE_MEMBERS` - Contact is a site member and can't be deleted. Member must be deleted first.
- `CANNOT_DELETE_CONTACT_WITH_BILLING_SUBSCRIPTION` - Contact has a valid billing subscription and can't be deleted.
- `CANNOT_DELETE_MEMBER_OWNER_OR_CONTRIBUTOR` - Member is a Wix user and can't be deleted. This can happen only if the request indicated to delete the member.
- `FAILED_DELETE_CONTACT_AFTER_MEMBER_DELETION` - Member was deleted, but contact was not. This can happen only if the request indicated to delete the member.
- `FAILED_DELETE_CONTACT` - Contact could not be deleted.

## Permissions Required
- `CONTACTS.MODIFY`
- `MEMBERS.MEMBER_DELETE` (if deleting members)

## Related Documentation
- [Bulk Delete Contacts API Reference](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/contact-v4/bulk-delete-contacts)
- [Query Contacts](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/contact-v4/query-contacts)
- [Get Bulk Job](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/bulk-job/get-bulk-job)
