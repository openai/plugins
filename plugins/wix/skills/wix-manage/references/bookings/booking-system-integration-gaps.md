---
name: "Booking System Integration Gaps"
description: Documents undocumented API patterns for booking payments. Covers Bookings→Ecommerce integration, booking ID transformation to catalog items, and async payment confirmation flows.
---
# Technical Step-by-Step Instructions: Wix Bookings System Integration Gaps - Complete API Documentation Analysis

## Description

This recipe addresses **critical undocumented API patterns and business integration gaps** across the entire Wix Bookings ecosystem. While Wix extensively documents individual booking creation APIs, there exist fundamental undocumented integration patterns that are essential for any payment-enabled booking business but completely absent from all official documentation sources.


---

## Prerequisites

### Required App Installations

Before implementing any booking integration, ensure the following requirements are met:

1. **Wix Bookings** - Core app must be installed and configured
2. **Wix Ecommerce** - Required for payment processing (undocumented dependency)
3. **Services Created** - At least one bookable service must exist on the site
4. **Staff Resources** - Staff members must be available for service delivery
5. **Business Schedule** - Operating hours must be configured

### App Installation Process

If you encounter service-related errors, install the required apps using the Apps Installer API.

**For detailed app installation procedures, refer to:**
- [Apps Installer API Documentation](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
- Business setup recipes for comprehensive app installation workflows

## Overview

The Wix Bookings system contains **fundamental undocumented integration patterns** that affect every booking scenario requiring payment processing. These gaps create confusion and implementation barriers across all booking types:

- **Single Appointment Bookings**: How booking payments actually work
- **Class Bookings**: Payment processing for group services
- **Course Bookings**: Complex dual-API requirements for scheduling
- **Multi-Service Packages**: Completely undocumented unified booking endpoint

### CRITICAL API DOCUMENTATION GAPS

**The Universal Undocumented Pattern**: **Bookings→Ecommerce Integration Architecture**

**Documentation Status Across ALL Booking Types**:
- ❌ **NOT** documented how booking IDs become catalog items
- ❌ **NOT** documented that ecom system handles all pricing/tax calculations
- ❌ **NOT** documented async payment confirmation patterns
- ❌ **NOT** documented booking status vs order status separation
- ❌ **NOT** documented service properties preservation in checkout
- ❌ **NO** mention of `BACKOFFICE_MERCHANT` channel requirement
- ❌ **NO** explanation of why checkout/order APIs are needed for bookings

**Additional Service-Specific Gaps**:
- ❌ **Courses**: Dual API requirement (booking + calendar events) completely undocumented
- ❌ **Multi-Service**: Entire endpoint missing from all documentation
- ❌ **Payment Flow**: Universal integration pattern affects all booking types

### Key Discovery: Universal Architecture Gap

**What Developers Expect** (Based on Documentation):
- Create booking → Booking system handles payment → Done
- Payment status managed within booking system
- Booking APIs contain all necessary functionality

**Actual Undocumented Architecture**:
- Create booking → Booking system creates reservation only
- Use booking ID as catalog item in ecom system
- Ecom system handles all pricing, tax, discount calculations
- Create checkout and order for actual payment processing
- Async messaging system handles payment confirmation
- Booking status (CONFIRMED) independent of payment status

**Reality Check**:
```
Standard Documentation Shows: Booking API → Payment ✓
Actual Required Flow: Booking API → Ecom Integration → Payment ✓
```

### Business Impact of These Gaps

**Without Understanding Universal Integration Patterns:**
- Developers assume booking creation includes payment processing
- No knowledge that ecom system handles all financial calculations
- Missing understanding of async payment confirmation architecture
- Confusion about booking status vs payment status separation
- Unknown relationship between booking system and ecommerce system

**Without Service-Specific Knowledge:**
- Course businesses cannot create functioning course delivery schedules
- Package-based businesses cannot create unified booking experiences
- Payment implementation becomes trial-and-error process
- Integration projects fail due to missing critical steps

**Current Developer Confusion Patterns:**
- "Why do I need ecommerce APIs for booking payments?"
- "How do booking payments actually work?"
- "Why are my course bookings invisible on the calendar?"
- "How do I create spa day packages?"
- "What's the difference between booking status and payment status?"

### IMPORTANT NOTES

* **Universal Integration Gap**: Every booking requiring payment uses undocumented ecom integration
* **Service Type Complexity**: Different booking structures but same payment patterns
* **Async Architecture**: Payment confirmation decoupled from booking creation
* **Status Separation**: Booking confirmation independent of payment processing
* **Hidden Dependencies**: Ecommerce system required for all booking payments
* **Business Model Impact**: Documentation gaps prevent entire business models

---

## Steps

### 1. Understand Universal Booking→Payment Architecture

**CRITICAL DISCOVERY**: All Wix booking payments flow through undocumented ecommerce integration.

**The Hidden Architecture**:
- **Booking System**: Handles time slot reservations, service coordination, scheduling
- **Ecommerce System**: Handles pricing, tax calculations, discount processing, payment collection
- **Integration Bridge**: Booking IDs automatically become catalog item IDs

**Universal Pattern** (Works for ALL Service Types):
```
Create Booking → Extract Booking ID → Use as Catalog Item ID → Create Checkout → Create Order → Process Payment
```

### 2. Identify Service Type-Specific Booking Patterns

Different service types use different booking structures but same payment integration:

**Appointments**: Use `bookedEntity.slot` with all required fields
```json
{
  "booking": {
    "bookedEntity": {
      "slot": {
        "serviceId": "<SERVICE_ID>",
        "scheduleId": "<SCHEDULE_ID>",
        "startDate": "2024-06-14T14:00:00",
        "endDate": "2024-06-14T15:15:00",
        "timezone": "America/New_York",
        "resource": { "id": "<RESOURCE_ID>" },
        "location": { "locationType": "OWNER_BUSINESS" }
      }
    },
    "contactDetails": {
      "firstName": "John",
      "email": "john@example.com"
    },
    "totalParticipants": 1
  }
}
```

> **Critical**: All slot fields (`scheduleId`, `resource.id`, `location.locationType`, `timezone`) are **required** for appointments. Omitting any of them returns a 400 error. The `locationType` must be `OWNER_BUSINESS` (not `BUSINESS` which is what Time Slots V2 returns).

**Classes**: Use `bookedEntity.slot` with `eventId` (auto-derives other fields)
```json
{
  "booking": {
    "bookedEntity": {
      "slot": {
        "serviceId": "<SERVICE_ID>",
        "eventId": "<EVENT_ID>"
      }
    },
    "contactDetails": {
      "firstName": "Jane",
      "email": "jane@example.com"
    },
    "totalParticipants": 1
  }
}
```

**Courses**: Use `bookedEntity.schedule` structure + require separate calendar events
```json
{
  "booking": {
    "bookedEntity": {
      "schedule": {
        "scheduleId": "<SCHEDULE_ID>",
        "serviceId": "<SERVICE_ID>",
        "timezone": "America/New_York",
        "location": { "locationType": "OWNER_BUSINESS" }
      }
    },
    "contactDetails": {
      "firstName": "Bob",
      "email": "bob@example.com"
    },
    "totalParticipants": 1
  }
}
```

### 3. Create Booking Using Appropriate Service Pattern

Use standard booking creation APIs with service-specific structures:

**Standard Booking Endpoint**: `POST https://www.wixapis.com/_api/bookings-service/v2/bookings` ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-writer-v2/create-booking))

**Critical Parameters for All Types**:
- `booking.contactDetails` — at minimum `firstName` and `email`
- `booking.totalParticipants` — number of participants
- `selectedPaymentOption: "OFFLINE"` — for ecom integration flows
- `flowControlSettings.skipBusinessConfirmation: true` — for administrative bookings
- Service-appropriate `bookedEntity` structure (see Step 2 above)

### 4. Handle Course-Specific Calendar Requirements

**MAJOR DISCOVERY**: Courses require dual API implementation - booking alone is insufficient.

**Course Booking Problem**: Creating course booking without calendar sessions results in:
- Participant enrollment and payment processing works
- No visible sessions on business calendar
- Staff unaware of when/where to conduct sessions
- Course delivery schedule missing

**Required Additional Step for Courses**:
Create calendar events using `POST https://www.wixapis.com/calendar/v3/bulk/events/create` ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/events-v3/bulk-create-event)):
```json
{
  "events": [{
    "event": {
      "type": "COURSE",
      "scheduleId": "<COURSE_SCHEDULE_ID>",
      "externalScheduleId": "<STAFF_RESOURCE_ID>",
      "start": { "localDate": "2025-06-16T09:00:00" },
      "end": { "localDate": "2025-06-16T10:00:00" },
      "resources": [{ "id": "<STAFF_RESOURCE_ID>" }],
      "recurrenceRule": {
        "frequency": "WEEKLY",
        "interval": 1,
        "days": ["MONDAY"],
        "until": { "localDate": "2025-08-11T23:59:59" }
      }
    }
  }]
}
```

> **Critical**: Each element in the `events` array must be wrapped in `{ "event": {...} }`. The `resources` array with at least one resource ID is **required** for CLASS/COURSE events — without it the API returns 400. `start`/`end` fields and `externalScheduleId` are also required.

### 5. Implement Multi-Service Package Bookings (Advanced)

**CRITICAL UNDOCUMENTED ENDPOINT**: For businesses requiring unified package experiences.

**Endpoint**: `POST https://manage.wix.com/_api/bookings-service/v2/multi_service_bookings`

**Business Use Cases**:
- Spa packages (massage + facial + manicure as single booking)
- Beauty services (cut + color + styling as unified experience)
- Wellness programs (consultation + treatment + follow-up coordination)

**Undocumented Requirements**:
- Identical contact information across all services in package
- Sequential service timing coordination (second service start = first service end)
- `skipAvailabilityValidation: true` for back-to-back scheduling

### 6. Process Payment Through Universal Ecom Integration

**MAJOR DISCOVERY**: ALL booking payments use identical ecommerce integration pattern.

**Step 6A: Create Checkout with Booking ID as Catalog Item**

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/checkouts` ([REST](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/purchase-flow/checkout/checkout/create-checkout))

```json
{
  "lineItems": [{
    "catalogReference": {
      "catalogItemId": "<BOOKING_ID>",
      "appId": "13d21c63-b5ec-5912-8397-c3a5ddb27a97"
    },
    "quantity": 1
  }],
  "channelType": "WEB"
}
```

**Step 6B: Create Order for Payment Processing**

**Endpoint**: `POST https://www.wixapis.com/ecom/v1/checkouts/{checkoutId}/createOrder`

**Critical Architecture Discoveries**:
- **Automatic ID Transformation**: Booking IDs automatically valid as catalog item IDs
- **Service Properties Preserved**: Booking context (scheduledDate, numberOfParticipants) maintained
- **Pricing Calculation**: Ecom system handles all financial calculations (not booking system)
- **Item Type Assignment**: `"preset": "SERVICE"` automatically applied

### 7. Understand Async Payment Confirmation Architecture

**Payment Processing Architecture**:
```
Booking (CONFIRMED) → Checkout → Order → Payment Processing (async)
                                              ↓
                                        Messaging System
                                              ↓
                                    Final Status Updates
```

**Status Management Patterns**:
- **Booking Status**: CONFIRMED (reserves time slot regardless of payment)
- **Order Status**: PAID/NOT_PAID (reflects payment processing outcome)
- **Business Logic**: Time slot reservation independent of payment success

**Operational Benefits**:
- Payment failures don't lose reserved time slots
- Supports multiple payment models (prepaid, deposits, invoicing)
- Retry payment without recreating complex booking coordination

### 8. Implement Business-Specific Integration Patterns

**Single Appointments**: Basic booking + ecom integration
**Group Classes**: Booking with participant count + ecom integration
**Course Programs**: Booking + calendar events + ecom integration
**Service Packages**: Multi-service booking + ecom integration

**Universal Integration Considerations**:
- All service types use same checkout/order creation pattern
- Pricing calculations always handled by ecom system
- Async payment confirmation applies to all booking types
- Service properties preserved across all integration points

### IMPORTANT NOTES

* **Universal Integration Required**: Every booking payment flows through ecommerce system
* **Service-Specific Booking Creation**: Different booking structures for different service types
* **Courses Require Dual APIs**: Booking system + calendar events system
* **Multi-Service Endpoint Undocumented**: Complete gap for package-based businesses
* **Async Payment Architecture**: Payment confirmation decoupled from booking creation
* **Status Independence**: Booking confirmation separate from payment processing
* **Hidden Ecommerce Dependency**: Not mentioned in any booking documentation

### Troubleshooting Universal Integration Issues

**Booking ID Not Working as Catalog Item**:
- Verify booking was created successfully and has valid ID
- Ensure using correct Wix Bookings app ID in catalog reference
- Check that booking status is CONFIRMED before attempting checkout

**Course Bookings Not Visible on Calendar**:
- Course bookings handle enrollment only, not session scheduling
- Must create calendar events separately using calendar API
- Session scheduling independent of participant enrollment

**Payment Status Confusion**:
- Booking status (CONFIRMED) indicates time slot reservation
- Order status (PAID/NOT_PAID) indicates payment processing outcome
- These statuses operate independently through async messaging

**Multi-Service Booking Failures**:
- Contact details must be identical across all services in package
- Service timing must be precisely coordinated (end time = next start time)
- Resource allocation requires manual verification with `skipAvailabilityValidation`

**Ecommerce Integration Errors**:
- Verify ecommerce app is installed and enabled
- Ensure using `"BACKOFFICE_MERCHANT"` channel type for owner flows
- Check that service pricing is properly configured in booking system

### Cross-Platform Implementation Challenges

**Headless Implementation**:
- No documented SDK methods for booking→ecom integration
- Manual API orchestration required for payment processing
- Frontend developers must understand backend integration patterns

**Mobile Integration**:
- Booking creation patterns differ across service types
- Payment flow design requires understanding async confirmation
- Course management requires dual API coordination

**Third-Party Integration**:
- Booking export may not include payment status information
- External calendar systems may not receive course session details
- CRM integration requires understanding booking vs payment status separation

### Business Architecture Considerations

**Payment Model Planning**:
- Booking system reserves capacity, ecom system processes payments
- Multiple payment models supported (full prepaid, deposits, invoicing)
- Refund processing requires coordination between both systems

**Service Type Planning**:
- Appointments: Immediate booking and payment
- Classes: Group bookings with participant management
- Courses: Long-term enrollment with session scheduling
- Packages: Unified experience across multiple services

**Scaling Considerations**:
- Integration complexity increases with service variety
- Payment processing load handled by ecommerce system
- Booking coordination managed by booking system
- Analytics require data from both systems

## API Documentation References

**Documented APIs** (That Don't Explain Integration Requirements):
* [Standard Booking Flow](https://dev.wix.com/docs/api-reference/business-solutions/bookings/flow-single-service-booking) - Missing payment integration
* [Create Booking](https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-writer-v2/create-booking) - No payment processing guidance
* [Service Types](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/about-service-types) - Missing integration patterns
* [Ecommerce Checkout](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/purchase-flow/checkout/introduction) - No booking integration mention

**Completely Undocumented**:
* **Booking→Ecom Integration**: Universal pattern affecting all booking payments
* **Multi-Service Bookings**: `https://manage.wix.com/_api/bookings-service/v2/multi_service_bookings`
* **Course Calendar Requirements**: Dual API necessity for course functionality
* **Async Payment Confirmation**: Messaging system architecture
* **Status Separation Patterns**: Booking vs payment status independence
