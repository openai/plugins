---
name: "Configure Default Business Hours"
description: Uses Calendar Events API to create WORKING_HOURS events on the business schedule. Covers the critical distinction between Calendar Events API (correct) vs Site Properties API (incorrect) for setting base availability.
---
# Technical Step-by-Step Instructions: Setting Up Wix Bookings Default Business Hours (Real-World, API-First)

## Description

Below are the recommended steps to successfully configure default business hours for Wix Bookings, which control the base availability shown in the "Set default hours" dashboard. This recipe covers the correct API usage, common pitfalls, and cleanup procedures for managing business schedule events.

---

## Prerequisites

- **Wix Bookings app installed** (App ID: `13d21c63-b5ec-5912-8397-c3a5ddb27a97`)

> **Note:** If you receive errors from Bookings APIs, the Wix Bookings app may not be installed on the site. Use [List Installed Apps](../app-installation/list-installed-apps.md) to verify, and [Install Wix Apps](../app-installation/install-wix-apps.md) to install it if missing.

## Overview

Wix Bookings default business hours define the base availability for your booking system and appear in the Bookings dashboard under "Set default hours". These hours:

- **Control base availability**: Set when your business is generally available for bookings
- **Apply to new staff**: Default working hours that new staff members inherit
- **Display in dashboard**: Show as time slots in the "Set default hours" interface

### 🚨 CRITICAL: Default Hours Upon Installation

**IMPORTANT**: When Wix Bookings is first installed on a site, it automatically creates DEFAULT business hours (typically 9 AM - 5 PM, Monday through Friday). You CANNOT simply create new hours without handling these existing default hours first.

**You MUST either:**
1. **Update the existing default hours** to your desired schedule, OR
2. **Delete the existing default hours** and create new ones

**Failure to handle existing hours will result in:**
- Duplicate time slots in the dashboard
- Conflicting availability schedules
- Unexpected booking behavior

### CRITICAL API DISCOVERY

**❌ WRONG API**: Site Properties API (`/site-properties/v4/properties/business-schedule`)
- This sets general site business schedule, NOT Bookings default hours

**✅ CORRECT API**: Calendar Events V3 API (`/calendar/v3/events`)
- Creates `WORKING_HOURS` events on the business schedule
- Each `MASTER` event creates one time slot in the dashboard
- Uses fixed business resource ID: `4e0579a5-491e-4e70-a872-d097eed6e520`

### Key Discovery: Universal Business Schedule External ID

**VERIFIED**: The business schedule external ID `"4e0579a5-491e-4e70-a872-d097eed6e520"` is **universal across all Wix sites**.

This has been tested and confirmed on multiple different Wix sites:
- All sites have a business schedule with this exact external ID
- The schedule name is consistently `"business"`
- While the internal schedule `id` varies per site, the `externalId` is constant
- This makes the recipe reliable without requiring site-specific discovery

### IMPORTANT NOTES

* **Universal External ID**: The business schedule external ID `"4e0579a5-491e-4e70-a872-d097eed6e520"` is verified to work across all Wix sites
* **Default Hours Always Exist**: Every Wix Bookings installation creates default hours automatically
* **Event Scheduling Flexibility**: Businesses can create multiple time slots per day or complex schedules as needed - there are no restrictions on number of events per day
* **MASTER vs INSTANCE Events**: Based on observed behavior, MASTER events appear to generate INSTANCE events automatically, but always verify current event state when working with recurring events
* **Query Patterns**: Use `"recurrenceType": ["MASTER"]` to focus on the primary recurring event definitions
* **Revision Numbers**: Calendar events require current revision numbers for updates - always get fresh revision before bulk operations

---

## Steps

### 1. Find Business Schedule

Query the business schedule that controls default hours using the fixed external ID.

**Endpoint**: `POST https://www.wixapis.com/calendar/v3/schedules/query`

Use `querySchedules` API ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/query-schedules)) with filter:
- `externalId`: `"4e0579a5-491e-4e70-a872-d097eed6e520"`

Keep the returned `schedule.id` for creating events.

### 2. Query Existing Working Hours (MANDATORY)

**🚨 CRITICAL STEP**: You MUST query for existing `WORKING_HOURS` events because Wix Bookings automatically creates default hours upon installation.

**Endpoint**: `POST https://www.wixapis.com/calendar/v3/events/query`

Use `queryEvents` API ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/query-events)):

Query pattern:
```json
{
    "recurrenceType": ["MASTER"],
    "query": {
        "filter": {
            "scheduleId": "business-schedule-id",
            "type": "WORKING_HOURS"
        }
    }
}
```

**Important**: Always query for MASTER events specifically to see actual recurring schedules.

**Expected Result**: You will typically find 5 existing MASTER events (Monday through Friday, 9 AM - 5 PM) from the default Bookings installation.

### 3. Choose Your Strategy: Update OR Replace

Based on the existing hours found in Step 2, choose one approach:

#### Strategy A: Update Existing Hours (Recommended)
If you want to modify the times but keep the same days, update the existing events.

#### Strategy B: Replace All Hours
If you want completely different days/times, delete existing events and create new ones.

### 4A. Update Existing Business Hours (Strategy A)

**Endpoint**: `POST https://www.wixapis.com/calendar/v3/bulk/events/update`

Use `bulkUpdateEvents` API ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-update-event)) with `fieldmask` pattern:

Update fields:
- `start`/`end`: New times
- `revision`: Current revision number (from Step 2 query)
- `fieldmask`: `"start,end"`

**Example**: Change Monday hours from 9 AM-5 PM to 12 AM-4 PM:
```json
{
  "events": [{
    "event": {
      "id": "existing-monday-event-id",
      "start": {"localDate": "2025-06-16T00:00:00"},
      "end": {"localDate": "2025-06-16T16:00:00"},
      "revision": "current-revision-number"
    }
  }],
  "fieldmask": "start,end"
}
```

### 4B. Replace All Business Hours (Strategy B)

#### Step 4B.1: Delete Existing Hours
Cancel existing MASTER events using `bulkCancelEvents` API (`POST https://www.wixapis.com/calendar/v3/bulk/events/cancel`) ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-cancel-event)):

```json
{
  "eventIds": ["event-id-1", "event-id-2", "event-id-3", "event-id-4", "event-id-5"]
}
```

#### Step 4B.2: Create New Business Hours
Create `WORKING_HOURS` events for each day using `bulkCreateEvents` API (`POST https://www.wixapis.com/calendar/v3/bulk/events/create`) ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-create-event)).

**Each event pattern**:
- `type`: `"WORKING_HOURS"`
- `scheduleId`: Business schedule ID from step 1
- `scheduleOwnerId`: `"4e0579a5-491e-4e70-a872-d097eed6e520"`
- `externalScheduleId`: `"4e0579a5-491e-4e70-a872-d097eed6e520"`
- `recurrenceRule`: Weekly recurring with single day
- `start`/`end`: Business hours times

**Note**: Create separate events for each day of the week (Monday, Tuesday, etc.).

### 5. Verify Final Configuration

Query the business schedule events again to confirm:
1. No duplicate time slots exist
2. Each desired day has exactly one MASTER event
3. Times match your requirements

### IMPORTANT NOTES

* **Future dates required**: Recurring events must start today or in the future
* **Revision management**: Always use current revision numbers when updating events
* **MASTER vs INSTANCE**: Based on observed behavior, MASTER events appear to control recurring patterns while INSTANCE events are auto-generated, but always verify current event state
* **Default Hours Impact**: Remember that these hours will be inherited by any new staff members created after this configuration

### Troubleshooting Common Issues

**"App not installed" Error (428):**
- Install Wix Bookings app using Apps Installer API
- Verify installation by querying existing services

**Duplicate time slots in dashboard:**
- **Root Cause**: You created new events without handling existing default hours
- **Solution**: Query MASTER events to find duplicates and cancel unwanted ones
- Each day should have only one MASTER event unless split hours are needed

**Updates not reflecting in dashboard:**
- Verify you're updating MASTER events, not INSTANCE events
- Check that revision numbers are current
- Confirm `fieldmask` includes the fields you're changing

**Cannot create events in the past:**
- Set `start.localDate` to current date or future
- Recurring events automatically generate past INSTANCE events

**Business schedule not found:**
- Query schedules using the fixed external ID: `4e0579a5-491e-4e70-a872-d097eed6e520`
- Ensure Wix Bookings is installed (schedule is created when Bookings is installed)

**Working hours not affecting staff/services:**
- Default hours only apply to staff using `usesDefaultWorkingHours: true`
- Services with custom schedules ignore default business hours
- Staff with assigned custom schedules override default hours

### Common Gotchas

1. **Skipping the Query Step**: Never assume no hours exist - always query first
2. **Creating Without Cleaning**: Adding new hours without removing defaults creates duplicates
3. **Wrong Event Type**: Using INSTANCE instead of MASTER events for queries/updates
4. **Missing Revision Numbers**: Updates require current revision numbers from the query response

## API Documentation References

* [Query Schedules](https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/query-schedules)
* [Query Events](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/query-events)
* [Bulk Create Events](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-create-event)
* [Bulk Update Events](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-update-event)
* [Bulk Cancel Events](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-cancel-event)
* [Apps Installer API](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
