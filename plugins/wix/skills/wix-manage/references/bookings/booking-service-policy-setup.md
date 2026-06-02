---
name: "Booking Service Policy Setup"
description: Sets up booking policies, cancellation rules, and waitlist configuration using the Services API policy fields. Covers bookingPolicy, cancellationPolicy, and waitlist settings.
---

# Technical Step-by-Step Instructions: Configuring Wix Bookings Service Policies (Real-World, API-First)

## Description

Below are the recommended steps to successfully configure booking, cancellation, and waitlist policies for Wix Bookings services. This recipe covers policy inheritance, service-specific overrides, and common policy configurations for different business models.

---

## Overview

Wix Bookings policy configuration allows businesses to set rules for:

- **Booking policies**: When customers can book, how far in advance, booking deadlines
- **Cancellation policies**: Cancellation deadlines, refund rules, fees
- **Waitlist policies**: When waitlists are enabled, capacity handling
- **Group booking policies**: Maximum participants per booking

Policies can be configured at two levels:

- **Site-wide (business) policies**: Default rules that apply to all services
- **Service-specific policies**: Override rules for individual services

### IMPORTANT NOTES

- Services inherit from site-wide booking policies by default
- Service policies only override fields you explicitly specify - unspecified fields keep site defaults
- Policy options available may vary based on service type (APPOINTMENT, CLASS, COURSE)
- All policy configurations support the same core features across service types

---

## Steps

### 1. Configure Site-Wide Business Policy (Optional)

Set default policies that will apply to all services unless overridden. Use the Business Policy API to configure booking deadlines, cancellation rules, waitlist settings, and group booking limits.

### 2. Create or Update Service with Policy Overrides

When creating or updating a service, specify policy fields that should differ from business defaults. Only include the policy fields you want to override - unspecified fields will inherit from business defaults.

### 3. Configure Course-Specific Policies

Courses may have additional policy options such as `bookUntilXMinutesAfterStart` which allows customers to join courses even after they've started.

### 4. Verify Policy Application

Query the service to confirm policies are applied correctly. The service should show explicitly set policy fields with your specified values and unspecified fields inheriting from business defaults.

### IMPORTANT NOTES

- **Policy inheritance**: Only specify fields you want to override - leave others undefined to inherit business defaults
- **Partial updates**: When updating service policies, only include fields you want to change
- **Capacity requirements**: Waitlist policies require service capacity settings to be configured
- **Group booking considerations**: `maxParticipantsPerBooking` works with all service types
- **Time calculations**: Policy deadlines are calculated from booking start time in business timezone
- **Course flexibility**: Course services support additional policy options like `bookUntilXMinutesAfterStart`

### Troubleshooting Common Issues

**Policies not applying:**

- Verify you're setting policies on the service object, not as separate policy entities
- Check that policy fields are properly nested under `service.policy`
- Ensure you're updating the correct service ID

**Waitlist not working:**

- Confirm service has `maxParticipants` capacity set
- Verify `waitingListPolicy.enabled` is `true`
- Check that `waitingListPolicy.capacity` is set if you want limited waitlist size

**Cancellation policies not enforced:**

- Ensure `cancelRescheduleUpToInMinutes` is set to appropriate value
- Verify `cancelationAllowed` is `true` if cancellations should be permitted
- Check that payment and booking flow supports the configured policy

**Group booking limits not working:**

- Confirm `maxParticipantsPerBooking` is set to desired limit
- Verify service type supports group bookings (all types do)
- Check that booking UI respects the participant limit

## API Documentation References

- [Booking Policies API](https://dev.wix.com/docs/api-reference/business-solutions/bookings/policies/introduction)
- [Bulk Create Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-create-services) — `POST https://www.wixapis.com/bookings/v2/bulk/services/create`
- [Update Service](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/update-service) — `PATCH https://www.wixapis.com/bookings/v2/services/<SERVICE_ID>`
- [Query Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/query-services) — `POST https://www.wixapis.com/bookings/v2/services/query`
