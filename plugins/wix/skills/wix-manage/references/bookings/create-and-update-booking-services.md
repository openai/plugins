---
name: "Create and Update Booking Services"
description: Full CRUD operations for Wix Bookings services using Services API. Covers service types (APPOINTMENT, CLASS, COURSE), pricing configuration, location setup, and schedule management.
---

# Technical Step-by-Step Instructions: Creating or Updating a Wix Bookings Service (Real-World, API-First)

## Description

Below are the recommended steps to successfully create or update a Wix Bookings service (or several at once) on Wix, with real-world troubleshooting and fixes for common API issues.

---

## Prerequisites

- **Wix Bookings app installed** (App ID: `13d21c63-b5ec-5912-8397-c3a5ddb27a97`)

> **Note:** If you receive errors from Bookings APIs, the Wix Bookings app may not be installed on the site. Use [List Installed Apps](../app-installation/list-installed-apps.md) to verify, and [Install Wix Apps](../app-installation/install-wix-apps.md) to install it if missing.

## Overview

A Bookings service defines a time based offering and includes the following considerations:

- type - for detailed information about service type - refer to the [article](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/about-service-types)
- `APPOINTMENT` - Appointments allow customers to book services at their preferred time during the business hours. For example, a hair salon might offer different appointment-based hair cutting and styling services. Appointments appear in the booking calendar once they're booked by a customer. Not-yet-booked times during the business hours are displayed as available slots to potential customers while booking. The availability of the service is based on the availability of the staff member providing it
- `CLASS` - A class is a single event or a series of recurring events that multiple customers can book. For example, a yoga studio might offer a twice-weekly vinyasa flow class. Classes may have a set end date or continue indefinitely. If a class includes more than a single event, customers can sign up for 1, several, or all of the events. Upon creation, classes are listed immediately in the booking calendar.
- `COURSE` - A course starts and ends on pre-defined dates with a limited number of events that multiple customers can book. For example, a yoga studio might offer a teacher training course with 5 events. In contrast to classes, customers must book the entire course. Upon creation, courses are displayed immediately in the booking calendar.
- Staff Member - a resource required in order to provide a service. [REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/create-staff-member) A staff member availability is defined by the schedule associated with the staff member, by default it is the main business schedule and cannot be modified by schedule APIs, but a staff member can have its own schedule by calling `assignWorkingHoursSchedule` which allows the staff member to have its own availability. The property `staffMember.usesDefaultWorkingHours` defines whether the default hours (business hours) are used.
- Schedule (availability) - availability is defined by `Events` ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/introduction)) defined on a schedule.
- The schedule which defines the service availability is based on the service type.
- For appointment service, it is based on the schedule of staff members which provides it (`service.staffMemberIds` which is mapped to `staffMember.resourceId`). In order to fetch the staff schedule you should retrieve the staff member with `RESOURCE_DETAILS` fieldmask and read the schedule id from the `staffMember.resource.eventsSchedule.id` - This is needed if you wish to define the staff member's availability as part of the process
- For classes and courses it is based on the schedule of the service itself (`service.schedule`)
- When creating an APPOINTMENT service and specifying `staffMemberIds`, ensure you are using the staff member's resourceId, not their primary staff member id.
- Service Images - the service may have several images - `service.media.mainMedia` - presented in the services list, `service.media.coverMedia` - presented in the service page and `service.media.items` - array of images presented as a gallery in the service page for site visitors.
- In order to add a media (image) to a service, it should first be defined in Wix Media Manager - search existing ([REST](https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/search-files)) or new ([REST](https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/bulk-import-file))
- You should only set the image id (for example `item.id` -> `service.media.mainMedia.id`) there is no need to set the entire object.

### Service Type Selection Guide

Choose based on these documented behaviors:

- **APPOINTMENT**: Customer picks available time slot. Availability based on staff schedules. One customer (or dedicated group) per booking.
- **CLASS**: Business sets recurring times. Multiple customers book same session. Customers can book 1, some, or all sessions in series.
- **COURSE**: Business sets fixed series. Multiple customers book. Customers must book entire course (all sessions).

When unsure, refer to [About Service Types](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/about-service-types).

### CRITICAL: Staff Assignment Behavior by Service Type

**APPOINTMENT Services:**

- **Staff assignment WORKS**: Can specify `staffMemberIds` array with staff member `resourceId` values
- **Behavior**: Service availability based on assigned staff schedules
- **Example**: Personal training session assigned to specific trainer

**CLASS and COURSE Services:**

- **Staff assignment IGNORED**: Setting `staffMemberIds` has no effect on service creation
- **Behavior**: Service uses its own schedule (`service.schedule`), not staff schedules
- **Workaround**: Staff association must be handled separately through calendar events or other mechanisms
- **Example**: Yoga class where any qualified instructor can teach

This is a critical API limitation that affects service planning and staff resource management.

### IMPORTANT NOTES

- I MUST read the full articles about [service types](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/about-service-types), [service payments](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/about-service-payments), [service location](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/about-service-locations) in order to fully understand how to set the service properties
- If the service type is `CLASS` or `COURSE` I MUST read the full articles service's _schedule_ and _events_ mentioned before
- If the service type is `APPOINTMENT` I MUST read the relevant full article about staff members ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/introduction)) in order to determine whether I should create a new staff member (or members)
- For free service I MUST set `service.payment.rateType` as `"NO_FEE"` and `service.payment.options.inPerson` as `true` (at least one payment option must be true)
- For paid service I MUST set the `service.payment.fixed.price.value` (must be above 0) as well as `service.payment.fixed.price.currency`
- When changing a free service to a paid service, I MUST update `service.payment.rateType` from `"NO_FEE"` to `"FIXED"` in the same request where I set `service.payment.fixed.price`; patching only `fixed.price` on a `NO_FEE` service fails validation.

### Payment Options Validation Rules

| rateType | `options.online` | `options.inPerson` | Valid?                            |
| -------- | ---------------- | ------------------ | --------------------------------- |
| FIXED    | true             | false              | ✓                                 |
| FIXED    | false            | true               | ✓                                 |
| FIXED    | true             | true               | ✓                                 |
| VARIED   | true             | false              | ✓                                 |
| VARIED   | false            | true               | ✓                                 |
| NO_FEE   | false            | true               | ✓                                 |
| NO_FEE   | true             | false              | ✗ (online not allowed for NO_FEE) |
| Any      | false            | false              | ✗ (at least one must be true)     |

- Always Prioritize Reading Full API Method Documentation: this overview article provides a general workflow. However, it repeatedly stresses the importance of reading the full documentation for each specific REST method you intend to use. This is critical for understanding detailed requirements.
- I should pay close attention to all required fields, data types, enum values, and specific ID types (e.g., resourceId vs. id) as defined in the detailed schema of each API endpoint. The overview article serves as a guide but doesn't replace the need to consult these specifics.

### Service Categories - CRITICAL for UI Visibility

**IMPORTANT**: Services without categories may not appear in category-based UI filters, which are commonly used in booking interfaces.

**Service Category Considerations:**

- **Default Behavior**: Services created without explicit category assignment may not be visible in filtered views
- **UI Impact**: Many booking interfaces filter services by `category.id`, hiding uncategorized services
- **Best Practice**: Always assign services to appropriate categories during creation

**Category Management Steps:**

1. **Query existing categories** using [Query Categories](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/categories-v2/query-categories) to see available options
2. **Create new category if needed** using [Create Category](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/categories-v2/create-category)
3. **Assign category during service creation** by including `category.id` in the service object
4. **Update existing services** using [Update Service](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/update-service) to add missing categories

**Common Category Filter Patterns:**

```json
{
  "filter": {
    "category.id": {
      "$exists": true
    }
  }
}
```

This filter will only show services with assigned categories, making uncategorized services invisible to users.

### Querying Existing Services

You can retrieve a list of existing booking services using the [Query Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/query-services) endpoint. This allows you to filter, sort, and page through up to 100 services at a time, making it easy to find and manage your current offerings.

---

## Steps

### 0. Query and Setup Categories (CRITICAL FIRST STEP)

1. **Query existing categories** using `queryCategories` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/categories-v2/query-categories)) to identify available categories
2. **Create category if needed** using `createCategory` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/categories-v2/create-category)) if no suitable category exists
3. **Record category ID** for use in service creation - this prevents services from being hidden in UI filters

**Query Categories:**

```bash
curl -X POST 'https://www.wixapis.com/bookings/v2/categories/query' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{ "query": {} }'
```

**Create Category (if none exist):**

```bash
curl -X POST 'https://www.wixapis.com/bookings/v2/categories' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{ "category": { "name": "General" } }'
```

### 1. Define staff member to use (REQUIRED for APPOINTMENT)

> **IMPORTANT:** For APPOINTMENT services, `staffMemberIds` is **required**. The API will return a 400 error without it. You must query staff members first to obtain a valid `resourceId`.

1. **Query existing staff members** to get their `resourceId` values
2. For new staff, create using `createStaffMember` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/create-staff-member)) and keep the response `staffMember.id` and `resourceId`
3. If you wish to update working hours, call `getStaffMember` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/get-staff-member)) to get `resource.eventsSchedule.id`

**Query Staff Members (to get resourceId):**

```bash
curl -X POST 'https://www.wixapis.com/bookings/v1/staff-members/query' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {},
    "fields": ["RESOURCE_DETAILS"]
  }'
```

Use the `resourceId` from the response (not `id`) in `staffMemberIds` when creating APPOINTMENT services.

**Staff Selection Strategy:**

- If a staff member has `default: true` → use it
- If only one staff member exists → use it
- If multiple exist → pick the first or most appropriate
- If none exist → create one using the [Staff Setup recipe](bookings-staff-setup.md)

**Service Type Requirements:**

- **APPOINTMENT**: `staffMemberIds` is **required** - API will fail without it
- **CLASS/COURSE**: `staffMemberIds` is ignored; use `service.schedule` instead

### 2. Creating or Updating a service

Based on the information gathered above, use the relevant API based on the desired outcome.

- **Create services**: `bulkCreateServices` endpoint ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-create-services))
- **Update single service**: `updateService` endpoint ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/update-service))
- **Update services (bulk)**: `bulkUpdateServices` ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-update-services))
- **Update by filter**: `bulkUpdateServicesByFilter` ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-update-services-by-filter))
- **Get single service**: `getService` endpoint ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/get-service))

**Create Service Example (paid APPOINTMENT, 60 minutes):**

```bash
curl -X POST 'https://www.wixapis.com/bookings/v2/bulk/services/create' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "services": [{
      "name": "Consultation",
      "type": "APPOINTMENT",
      "onlineBooking": { "enabled": true },
      "staffMemberIds": ["<RESOURCE_ID_FROM_STEP_1>"],
      "schedule": {
        "availabilityConstraints": {
          "sessionDurations": [60]
        }
      },
      "payment": {
        "rateType": "FIXED",
        "options": { "online": true, "inPerson": false },
        "fixed": {
          "price": { "value": "50", "currency": "USD" }
        }
      },
      "category": {
        "id": "<CATEGORY_ID_FROM_STEP_0>"
      }
    }]
  }'
```

> **Note:** Currency may default to the site's business currency regardless of what you specify. Verify the response if currency is critical.

**Create Service Example (free APPOINTMENT, 60 minutes):**

```bash
curl -X POST 'https://www.wixapis.com/bookings/v2/bulk/services/create' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "services": [{
      "name": "Free Consultation",
      "type": "APPOINTMENT",
      "onlineBooking": { "enabled": true },
      "staffMemberIds": ["<RESOURCE_ID_FROM_STEP_1>"],
      "schedule": {
        "availabilityConstraints": {
          "sessionDurations": [60]
        }
      },
      "payment": {
        "rateType": "NO_FEE",
        "options": { "online": false, "inPerson": true }
      },
      "category": {
        "id": "<CATEGORY_ID_FROM_STEP_0>"
      }
    }]
  }'
```

**Create Service Example (CLASS with capacity):**

> **Note:** CLASS services do not use `staffMemberIds` or `sessionDurations`. After creation, you must create events via `bulkCreateEvents` using the returned `service.schedule.id` to define when the class occurs.

```bash
curl -X POST 'https://www.wixapis.com/bookings/v2/bulk/services/create' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "services": [{
      "name": "Yoga Class",
      "type": "CLASS",
      "onlineBooking": { "enabled": true },
      "defaultCapacity": 20,
      "payment": {
        "rateType": "FIXED",
        "options": { "online": true, "inPerson": false },
        "fixed": {
          "price": { "value": "25", "currency": "USD" }
        }
      },
      "category": {
        "id": "<CATEGORY_ID_FROM_STEP_0>"
      }
    }]
  }'
```

After creation, use the `service.schedule.id` from the response to create class events with `bulkCreateEvents` (see Step 3).

**Required Fields:**

- `name` - Service name
- `type` - `APPOINTMENT`, `CLASS`, or `COURSE`
- `onlineBooking: { enabled: true }` - Required for all services
- `staffMemberIds` - **Required for APPOINTMENT only** (use `resourceId` values); ignored for CLASS/COURSE
- `schedule.availabilityConstraints.sessionDurations` - Duration in minutes (APPOINTMENT only)
- `defaultCapacity` - **Required for CLASS/COURSE** (max participants per session)
- `payment.options` - At least one of `online` or `inPerson` must be `true` (required for all services, including free; see validation table above)

**Service Type Specific Considerations:**

- **APPOINTMENT**: Must include `staffMemberIds` with staff `resourceId` values
- **CLASS/COURSE**: Omit `staffMemberIds`; configure `service.schedule` instead

**Update Service Example (PATCH):**

> **Note:** Updates require the current `revision` value (from a GET response) placed **inside** the `service` object, not at the top level.

```bash
# First, get current service to obtain revision
curl -X GET 'https://www.wixapis.com/bookings/v2/services/<SERVICE_ID>' \
  -H 'Authorization: <AUTH>'

# Then update with revision inside service object
curl -X PATCH 'https://www.wixapis.com/bookings/v2/services/<SERVICE_ID>' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "service": {
      "revision": "<REVISION_FROM_GET>",
      "category": {
        "id": "<CATEGORY_ID>"
      }
    }
  }'
```

**Update free service to fixed price:**

When an existing service has `payment.rateType: "NO_FEE"` and the user asks to set a price, convert it to `FIXED` and set the price in the same update.

```bash
# First, get current service to obtain revision and current payment settings
curl -X GET 'https://www.wixapis.com/bookings/v2/services/<SERVICE_ID>' \
  -H 'Authorization: <AUTH>'

curl -X PATCH 'https://www.wixapis.com/bookings/v2/services/<SERVICE_ID>' \
  -H 'Authorization: <AUTH>' \
  -H 'Content-Type: application/json' \
  -d '{
    "service": {
      "revision": "<REVISION_FROM_GET>",
      "payment": {
        "rateType": "FIXED",
        "options": { "online": false, "inPerson": true },
        "fixed": {
          "price": { "value": "200", "currency": "<SITE_CURRENCY>" }
        }
      }
    }
  }'
```

### 3. Set the availability of the service

Once the service and staff member are available, you can define when the service is available:

**3a. Determine the schedule to use** based on the service type:

- **APPOINTMENT**: The staff member working hours determine the service availability. If the staff member needs different hours from the business defaults, call `assignWorkingHoursSchedule` (`POST https://www.wixapis.com/bookings/v1/staff-members/<STAFF_MEMBER_ID>/assign-working-hours-schedule`) ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/assign-working-hours-schedule)). Use the `resource.eventsSchedule.id` as the `scheduleId`.
- **CLASS or COURSE**: Use the `service.schedule.id` from the service created/updated in Step 2.

**3b. Create events** using `bulkCreateEvents` (`POST https://www.wixapis.com/calendar/v3/bulk/events/create`) ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-create-event)) or update existing ones with `bulkUpdateEvents` (`POST https://www.wixapis.com/calendar/v3/bulk/events/update`) ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-update-event)).

**Event requirements**:

- `event.resources` array **must include at least one resource** (a staff member/room/etc.) using the `resourceId`. CLASS and COURSE events will fail with a 400 error if no resources are provided.
- `event.scheduleId` — use the staff member's events schedule ID for APPOINTMENT availability, or `service.schedule.id` for CLASS/COURSE.
- `event.type` — set to `WORKING_HOURS` for staff availability, `CLASS` for class sessions, or `COURSE` for course sessions.

### Troubleshooting Common Issues

**APPOINTMENT Service Creation Fails (staffMemberIds required):**

- **Error**: `"service of type appointment requires at least one staff member id"`
- **Cause**: APPOINTMENT services cannot be created without at least one staff member assigned
- **Solution**: Query staff members first (Step 1) to get a valid `resourceId`, then include it in `staffMemberIds`

**Service Creation Fails (payment.options required):**

- **Error**: `INVALID_PAYMENT_OPTIONS - "It is mandatory to specify either payment.options.online or payment.options.inPerson as true"`
- **Cause**: All services (including free) require at least one payment option to be `true`
- **Solution**: Add `"options": { "online": true, "inPerson": false }` (or `inPerson: true` for free services) to the `payment` object

**Free Service Fails with online=true:**

- **Error**: `INVALID_PAYMENT_OPTIONS - "Specifying payment.paymentOptions.online as true is applicable only to payments of types FIXED or VARIED"`
- **Cause**: `payment.options.online: true` is only valid for paid services (FIXED or VARIED)
- **Solution**: For free services (NO_FEE), use `"options": { "online": false, "inPerson": true }`

**Changing a free service price fails:**

- **Error**: `"Payment of type FREE cannot be used with payment.rate"`
- **Cause**: The service is still `NO_FEE` while the update tries to set `fixed.price`
- **Solution**: Change `payment.rateType` to `"FIXED"` and include `payment.fixed.price` in the same update request

**Services Not Appearing in UI Filters:**

- **Problem**: Services created without category assignment are invisible in category-based filters
- **Root Cause**: Many UI implementations filter by `category.id` existence or specific category values
- **Solution**: Query all services, identify those missing categories, and update them using bulk update operations
- **Prevention**: Always assign categories during service creation (Step 0)

**Staff Assignment Not Working for CLASS/COURSE Services:**

- **Problem**: Setting `staffMemberIds` in CLASS or COURSE services appears to be ignored
- **Solution**: This is expected behavior; use service schedules instead of staff assignments
- **Alternative**: Manage staff-to-class relationships through calendar events or custom data structures

**App Not Installed Errors:**

- **Problem**: 428 "App not installed" errors when creating services
- **Solution**: Install Wix Bookings app using Apps Installer API before creating services
- **Verification**: Query existing services to confirm app installation

**Resource ID vs Staff ID Confusion:**

- **Problem**: Using wrong ID type for `staffMemberIds` array
- **Solution**: Always use `staffMember.resourceId`, not `staffMember.id`
- **Verification**: Query staff with `RESOURCE_DETAILS` fieldMask to get correct IDs

**Service Schedule vs Staff Schedule Confusion:**

- **Problem**: Mixing up schedule IDs between service and staff schedules
- **Solution**:
  - APPOINTMENT: Use staff schedule ID (`staffMember.resource.eventsSchedule.id`)
  - CLASS/COURSE: Use service schedule ID (`service.schedule.id`)

**Update Service Fails with revision error:**

- **Error**: `revision must not be empty` or `service.revision is required`
- **Cause**: `revision` placed at top level of request body instead of inside `service` object
- **Solution**: Structure as `{ "service": { "revision": "...", ...fields } }` - get revision value from GET response first

### IMPORTANT NOTES

- I MUST read the full article about the REST method I wish to use
- `onlineBooking` Field: The onlineBooking object (e.g., {"enabled": true}) is a required field when creating services, even if not explicitly highlighted as mandatory in the high-level overview. This is a schema-level requirement.
- Event Creation (BulkCreateEvents): When specifying recurrenceRule.days, I MUST use full day names (e.g., "TUESDAY", "FRIDAY")
- The recurrenceRule.days field within an event object can only accept a single day of the week (e.g., ["TUESDAY"]).
- If I need to set up recurring events for multiple days of the week (e.g., a staff member working every Tuesday and Friday), I MUST define a separate event for each day and send them as separate items for BulkCreateEvents.
- Start Dates for Recurring Events: Recurring events must have a start.localDate that is today or in the future, relative to the server's current time. If I am not sure what the current date and time are I MUST check it.
- When setting `event.type` as `WORKING_HOURS` (APPOINTMENT) I MUST call `assignWorkingHoursSchedule` BEFORE CREATING THE EVENTS so that the staff member is no longer linked to the business working hours
- When setting `event.type` as `CLASS` or `COURSE` I MUST use the service schedule id, so the service has to exist (created/updated) before setting the availability of it

## Booking REST API Documentation Reference

- [Query Categories](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/categories-v2/query-categories)
- [Create Category](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/categories-v2/create-category)
- [Get Service](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/get-service)
- [Update Service](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/update-service)
- [Create Staff Member](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/create-staff-member)
- [Get Staff Member](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/get-staff-member)
- [Query Staff Members](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/staff-members/query-staff-members)
- [Bulk Create Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-create-services)
- [Bulk Update Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-update-services)
- [Bulk Update Services By Filter](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-update-services-by-filter)
- [Assign Working Hours Schedule](https://dev.wix.com/docs/api-reference/business-solutions/bookings/staff-members/assign-working-hours-schedule)
- [Bulk Create Events](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-create-event)
- [Bulk Update Events](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-update-event)
- [Media Manager: Search Files](https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/search-files)
- [Media Manager: Bulk Import File](https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/bulk-import-file)
- [Query Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/query-services)
- [Apps Installer API](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
