---
name: "Bookings Staff Setup"
description: "Creates staff members and configures custom working hours using Staff API + Calendar Events API. Critical two-step process: create staff → assign schedule → create working hours events."
---
# Technical Step-by-Step Instructions: Setting Up Wix Bookings Staff Members with Custom Working Hours (Real-World, API-First)

## Description

Below are the recommended steps to successfully set up Wix Bookings staff members and configure their custom working schedules on Wix, with real-world troubleshooting and fixes for common API issues.

---

## Prerequisites

- **Wix Bookings app installed** (App ID: `13d21c63-b5ec-5912-8397-c3a5ddb27a97`)

> **Note:** If you receive errors from Bookings APIs, the Wix Bookings app may not be installed on the site. Use [List Installed Apps](../app-installation/list-installed-apps.md) to verify, and [Install Wix Apps](../app-installation/install-wix-apps.md) to install it if missing.

---

## Overview

A Wix Bookings staff member setup involves multiple interconnected steps that must be executed in the correct sequence. This recipe covers the complete workflow from foundation setup to custom working hours configuration.

### 🚨 CRITICAL: Staff Inheritance Timing

**STAFF INHERIT BUSINESS HOURS AT CREATION TIME**: When you create a new staff member, they immediately inherit whatever business hours exist at that moment. This inheritance is NOT dynamic - it's a one-time copy during creation.

**Order of Operations Matters**:
1. **Option A (Recommended)**: Fix business hours FIRST, then create staff (staff inherit correct hours)
2. **Option B**: Create staff first, then detach them from default hours and configure custom schedules

**Understanding the Impact**:
- If you create staff when business hours are 9 AM - 5 PM, staff inherit 9 AM - 5 PM
- If you later change business hours to 8 AM - 6 PM, existing staff STILL have 9 AM - 5 PM
- New staff created after the change would inherit 8 AM - 6 PM

Staff schedule configuration includes:
- **Default behavior**: Staff inherit business hours and are available at all business locations
- **Custom schedules**: Staff can have individual working hours different from business defaults
- **Working hours creation**: Custom hours are created as events with `"type": "WORKING_HOURS"` and recurrence rules

### Key Concepts

* **Staff Member**: An individual providing services within Wix Bookings. Each staff member has an associated resource with schedules for working hours and events.
* **Working Hours Schedule**: Defines when a staff member is available to provide services. Can be either business default hours or custom hours.
* **Event Schedule**: The actual calendar events that define specific working time blocks (WORKING_HOURS events).
* **Resource ID**: Each staff member has a `resourceId` that links them to their schedules and availability.
* **Inheritance Timestamp**: The exact moment when a staff member is created determines which business hours they inherit.

### Critical Workflow Requirements

The complete custom working hours setup requires understanding three distinct ID types and their relationships:
- **Staff Member ID**: Used for staff updates and schedule assignment
- **Resource ID**: Used for linking to services and events (`externalScheduleId` and `resources` array)
- **Events Schedule ID**: Used for creating working hours events (`scheduleId`)

The most common mistake is confusing which ID to use in which API call, leading to "Resource not found" or "Invalid scheduleId" errors.

### 🚨 INHERITANCE WARNINGS

* **One-Time Inheritance**: Business hours are copied (not linked) to staff at creation time
* **Creation Order Impact**: The state of business hours when you create staff determines their initial schedule
* **Retroactive Changes**: Changing business hours does NOT affect existing staff schedules
* **Multiple Staff Issue**: If you create multiple staff at different times, they may inherit different business hours

### IMPORTANT NOTES

* **Two-Step Requirement**: Custom working hours requires both `assignWorkingHoursSchedule` AND creating `WORKING_HOURS` events. Only doing the first step results in staff with no actual working hours.
* **Foundation Dependencies**: Staff operations require Wix Bookings app installation and proper business schedule configuration. "Business schedule not found" errors indicate missing foundation setup.
* **Event Field Requirements**: When creating `WORKING_HOURS` events, several fields that appear optional in documentation are actually required: `externalScheduleId`, `adjustedStart`, `adjustedEnd`, `resources` array, and `appId`.
* **Revision Numbers**: Event updates ALWAYS require the current revision number. Fetch current event details before any update operation.
* **Time Format Precision**: All date/time fields must use precise ISO 8601 format (`YYYY-MM-DDTHH:mm:ss`) without timezone indicators.
* **Separate Events for Each Day**: Each working day requires a separate event with single-day recurrence rules. You cannot specify multiple days in one event's `recurrenceRule.days` array.

---

## Steps

### Step 0: Choose Your Strategy (CRITICAL DECISION)

Before proceeding, decide your approach based on business hour requirements:

#### Strategy A: Fix Business Hours First (Recommended)
**When to use**: All staff will have the same working hours or similar schedules
1. Configure correct business hours (see business hours recipe)
2. Create staff members (they inherit correct hours automatically)
3. Only customize specific staff if needed

**Advantages**:
- Staff inherit correct hours immediately
- Minimal post-creation configuration
- Consistent scheduling across staff

#### Strategy B: Create Staff First, Configure Later
**When to use**: Each staff member needs completely different schedules
1. Create staff with whatever business hours exist
2. Detach each staff from business hours
3. Configure individual custom schedules for each

**Disadvantages**:
- Requires more API calls per staff member
- Risk of forgetting to configure some staff
- Temporary period with incorrect availability

### 1. Verify Foundation Setup (Prerequisites - Optional if Already Configured)

**Note**: If your site already has Wix Bookings properly configured with business schedules, you can skip this step and go directly to Step 2.

Before creating staff members, ensure the foundation is properly configured:

**Check Wix Bookings Installation**: Query staff members (`POST https://www.wixapis.com/bookings/v1/staff-members/query`) to test if Bookings is installed. If you receive "Business schedule not found" errors, the foundation needs setup.

**Install Wix Bookings App** (if needed): Use the App Installer API with Wix Bookings app ID: `13d21c63-b5ec-5912-8397-c3a5ddb27a97`.

**Configure Business Schedule**: Set up site properties with business operating hours using the Site Properties API.

**Create Calendar Schedule and Working Hours**: Create a calendar schedule for Wix Bookings integration and populate it with business `WORKING_HOURS` events.

### 2. Verify Current Business Hours (CRITICAL)

Before creating any staff, query the current business hours (`POST https://www.wixapis.com/calendar/v3/events/query`) to understand what staff will inherit:

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

**Document the current hours** - this is what your staff will inherit!

### 3A. Strategy A: Configure Business Hours First

If following Strategy A, ensure business hours are set correctly BEFORE creating staff:
1. Update or replace existing business hours (follow business hours recipe)
2. Verify the final business hours configuration
3. Proceed to create staff (they'll inherit these correct hours)

### 3B. Strategy B: Create Staff with Current Hours

If following Strategy B, accept that staff will inherit current (possibly incorrect) hours and plan to configure them individually later.

### 4. Create Staff Members

Create staff members using the Staff API (`POST https://www.wixapis.com/bookings/v1/staff-members`) with required information:
- Name (required)
- Email (optional but recommended)
- Phone (optional)
- Description/Professional bio (optional)

**⚠️ INHERITANCE MOMENT**: The moment this API call completes, the staff member inherits the current business hours. There's no "undo" for this inheritance.

**Save Critical IDs from Response**:
- `staffMember.id` for updates and schedule assignment
- `staffMember.resourceId` for services and event resources
- `staffMember.resource.eventsSchedule.id` for working hours events
- `staffMember.resource.usesDefaultWorkingHours` (should be `true` initially)

### 5. Set Up Custom Working Hours (Two-Step Process)

**Only needed if**: You want staff to have different hours than what they inherited, OR you followed Strategy B.

**Step 5A: Assign Custom Working Hours Schedule**

Get staff member details (`GET https://www.wixapis.com/bookings/v1/staff-members/<STAFF_MEMBER_ID>?fields=RESOURCE_DETAILS`) to extract the events schedule ID. Call `assignWorkingHoursSchedule` (`POST https://www.wixapis.com/bookings/v1/staff-members/<STAFF_MEMBER_ID>/assign-working-hours-schedule`) using the staff member ID and their events schedule ID. This detaches the staff member from business default hours.

Verify the response shows `"usesDefaultWorkingHours": false`.

**Step 5B: Create WORKING_HOURS Events**

Use the Events API (`POST https://www.wixapis.com/calendar/v3/bulk/events/create`) to create working hours events for each working day. Each event must include:
- `scheduleId`: Staff member's events schedule ID
- `externalScheduleId`: Staff member's resource ID
- `type`: `"WORKING_HOURS"`
- `resources` array: Staff member's resource ID
- `appId`: Wix Bookings app ID
- Proper recurrence rules with single-day specification

Create separate events for each day of the week the staff member works.

### 6. Verify Setup

Query the staff member to confirm:
- `"usesDefaultWorkingHours": false` (if you set custom hours)
- Query working hours events to verify proper creation with correct `type` and resource associations
- Test booking availability to ensure hours are applied correctly

### IMPORTANT NOTES

* **ID Relationship Critical**: Use staff member ID for assignment, events schedule ID for event `scheduleId`, and resource ID for `externalScheduleId` and `resources` array
* **Foundation First**: Complete foundation setup before staff operations to avoid "Business schedule not found" errors
* **Complete Two-Step Process**: Both schedule assignment AND event creation are mandatory for custom working hours
* **Event Field Requirements**: Include all required fields even if they appear optional in basic documentation
* **Revision Management**: Always fetch current revision numbers before updating events
* **Date Format Strict**: Use precise ISO 8601 format without timezone indicators
* **Inheritance is Permanent**: Once inherited, business hours changes don't affect existing staff

### Troubleshooting Common Issues

**"Business schedule not found" Error**:
Execute systematic diagnosis: check app installation, site properties, calendar schedule, and working hours events in sequence. Fix the first failed component before proceeding.

**Staff Member Still Shows Default Hours**:
Completed assignment but missing event creation. Create `WORKING_HOURS` events using the Bulk Create Events API.

**Staff Inherited Wrong Hours**:
- **Root Cause**: Business hours were incorrect when staff was created
- **Solution**: Either update business hours first (affects future staff) or configure each existing staff member individually

**Multiple Staff Have Different Inherited Hours**:
- **Root Cause**: Business hours changed between staff creation times
- **Solution**: Standardize by configuring custom hours for all staff, or recreate staff after fixing business hours

**"Invalid scheduleId" or "Resource not found" Errors**:
Using wrong ID type in API calls. Verify you're using events schedule ID for `scheduleId`, resource ID for `externalScheduleId` and `resources` array, and staff member ID for updates.

**Event Update Fails with Revision Error**:
Get current event details first and include the revision number in update requests.

**Cannot Create Events for Past Dates**:
Use current or future dates for recurring event start dates.

**Events Not Linked to Staff Member**:
Ensure `resources` array contains staff member's resource ID and `externalScheduleId` is properly set.

### Working with Existing Staff

If working with existing staff members, first retrieve their details using `queryStaffMembers` with `RESOURCE_DETAILS` fieldmask to get the necessary IDs for schedule configuration. This allows you to configure custom working hours for staff members that were created previously.

**Check Their Current Inheritance**:
- Look at `usesDefaultWorkingHours` field
- If `true`: They're still using business hours they inherited at creation
- If `false`: They have custom hours (may have been configured previously)

### Common Gotchas

1. **Wrong Order**: Creating staff before fixing business hours leads to incorrect inheritance
2. **Inheritance Assumption**: Thinking business hour changes affect existing staff
3. **Incomplete Custom Setup**: Only doing schedule assignment without creating events
4. **Mixed Timing**: Creating staff at different times when business hours are changing
5. **ID Confusion**: Using wrong ID types in API calls

## API Documentation References

* [Create Staff Member](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/create-staff-member)
* [Query Staff Members](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/query-staff-members)
* [Assign Working Hours Schedule](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/assign-working-hours-schedule)
* [Schedules and Sessions API](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/schedules-and-sessions/schedule-and-sessions/introduction)
* [Apps Created by Wix](https://dev.wix.com/docs/api-reference/articles/work-with-wix-apis/platform/about-apps-created-by-wix)
