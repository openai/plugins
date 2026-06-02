---
name: "Multi-Resource Service Creation"
description: Creates resource types and individual resources using Resources API. Enables services that require multiple resources (rooms + equipment + staff) with automatic allocation.
---
# Technical Step-by-Step Instructions: Creating Multi-Resource Bookings Services (Rooms, Equipment, Staff) - Real-World, API-First

## Description

Below are the recommended steps to successfully create Wix Bookings services that require multiple resource types (e.g., Room + Equipment + Instructor). This recipe covers the **gaps** in individual API documentation: resource architecture planning, entity relationship patterns, availability dependencies, and real-world coordination challenges that aren't clear from reading individual API references.


---

## Prerequisites

### Required App Installations

Before creating multi-resource services, ensure the following requirements are met:

1. **Wix Bookings** - Core app must be installed and configured
2. **Premium Plan** - Advanced resource management typically requires premium features
3. **Business Location** - At least one business location must be configured

### App Installation Process

If you encounter resource-related errors, install the required apps using the Apps Installer API.

**For detailed app installation procedures, refer to:**
- [Apps Installer API Documentation](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
- Business setup recipes for comprehensive app installation workflows

## Overview

Multi-resource services allow businesses to create bookings that require multiple types of resources simultaneously. Common examples:
- **Fitness Classes**: Room + Equipment + Instructor
- **Meeting Services**: Conference Room + AV Equipment + Catering Staff
- **Spa Treatments**: Treatment Room + Specialized Equipment + Therapist

The system involves three independent entity types that can be connected:
1. **Resource Types** - Category definitions (Room, Equipment, Staff) - independent entities
2. **Resources** - Individual resource instances with their own schedules and availability - independent entities
3. **Services** - Booking services that can optionally reference resource types - independent entities

**Key Architecture Principle**: Resources and Services are **separate, independent entities**. Resources exist independently but their availability depends on business location hours (for non-staff resources) or working hour schedules (for staff resources). Services can optionally connect to resource types (not individual resources) to require resource allocation during booking, but this connection is loose and flexible.

### CRITICAL API DISCOVERY

**❌ COMMON ARCHITECTURE MISTAKES** (Not Clear in Individual Docs):
- Creating resources without resource types first (creation sequence matters)
- Assuming resources automatically inherit business hours (availability dependency isn't clear)
- Thinking you can connect same resource to conflicting schedules

**✅ CORRECT RESOURCE ARCHITECTURE**:
- **Independent Creation**: Resource Types → Resources (both exist independently)
- **Optional Service Connection**: Services can reference resource types when resource allocation is needed
- **Loose Coupling**: Resources maintain their own schedules and availability regardless of service connections
- **Type-Based References**: Services connect to `resourceType.id`, not individual resource IDs
- **Resource Autonomy**: Resources function independently - services simply request allocation from available resources of specified types

### Key Discovery: Resource Schedule Behavior

**Resource Availability Behavior:**
- Each resource automatically gets a dedicated `eventsSchedule` for tracking bookings
- **Non-staff resources**: Availability depends on business location hours (not 24/7)
- **Staff resources**: Have working hour schedules in addition to event schedules
- **Working hours override**: When `workingHoursSchedules` is configured, it takes precedence over location hours

**Schedule Sharing Patterns:**
- `shared: false` = Dedicated schedule per resource (recommended for most cases)
- `shared: true` = Multiple resources use same working hours schedule
- Business schedule is always `shared: true` among staff

### Key Discovery: Service-Resource Connection Pattern

**Service Configuration Pattern:**
```json
"serviceResources": [
  {"resourceType": {"id": "room-type-id"}},
  {"resourceType": {"id": "equipment-type-id"}},
  {"resourceType": {"id": "staff-type-id"}}
]
```
**Critical**: Services specify resource **types**, not individual resources. This creates a **loose coupling** where:
- Resources exist independently but availability follows business location hours (non-staff) or working hours (staff)
- Services request allocation from available resources of specified types during booking
- No direct binding between individual resources and services
- Resource management (updates, working hours) is independent of service configuration

### IMPORTANT NOTES

* **Entity Independence**: Resources and Services are separate entities - you can create and manage resources without any services, and vice versa
* **Optional Connection**: Services only need to reference resource types if they require resource allocation for bookings
* **Location Complexity**: `availableInAllLocations: true` is simplest; specific location configuration is complex and often unnecessary
* **Service Pricing**: Multi-resource services often justify higher pricing due to resource coordination complexity

---

## Steps

### 1. Plan Resource Type Architecture

Before creating anything, plan your resource type structure. Each type should represent a category of resources that can be substituted for each other in bookings.

**Common Resource Type Patterns:**
- **Physical Spaces**: Room, Studio, Meeting Room, Treatment Room
- **Equipment Categories**: AV Equipment, Medical Equipment, Sports Equipment
- **Human Resources**: Instructor, Therapist, Consultant, Technician

**Design Principle**: If resources are interchangeable for a service, they belong to the same type.

### 2. Create Resource Types

Create resource types using `createResourceType` API (`POST https://www.wixapis.com/bookings/v2/resources/resource-types`) ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resource-types-v2/create-resource-type)):

**Key Requirements:**
- `name` must be unique across the site
- Keep `name` descriptive but concise (appears in booking interface)
- Save the returned `resourceType.id` for resource creation

**Important**: Cannot change `name` after creation if conflicts occur - plan carefully.

### 3. Create Individual Resources

For each resource type, create the individual resource instances using `createResource` API (`POST https://www.wixapis.com/bookings/v2/resources`) ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resources-v2/create-resource)):

**Gap Not in Docs**: The docs don't clearly explain that `availableInAllLocations: true` is the simplest approach and that specific location configuration is complex and often unnecessary.

**Advanced Configuration (Gap):**
- Custom working hours override business location hours (this behavior isn't clearly documented)
- Specific locations: Use `specificLocationOptions` (complex - avoid unless required)

**Critical**: Each resource automatically gets its own `eventsSchedule` for booking management (this is documented but the implications for multi-resource coordination aren't clear).

### 4. Create Multi-Resource Service (Optional Connection)

Create the service that optionally connects to multiple resource types using `bulkCreateServices` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-create-services)):

**Service Resource Configuration:**
```json
"serviceResources": [
  {"resourceType": {"id": "room-type-id"}},
  {"resourceType": {"id": "equipment-type-id"}},
  {"resourceType": {"id": "instructor-type-id"}}
]
```

**Key Principle**: This creates a **loose connection** where the service requests resource allocation during booking, but resources remain independent entities with their own lifecycle and management.

**Pricing Strategy**: Multi-resource services typically command premium pricing due to coordination complexity.

### 5. Understand Resource Allocation Behavior (Gap in Docs)

The docs don't explain how multi-resource allocation actually works during booking. Key behaviors to understand:
- **Peak time conflicts**: When Room 1 is booked, Wix automatically tries Room 2 for the same resource type
- **Equipment maintenance**: Blocking specific resources affects all services requiring that resource type
- **Cross-resource dependencies**: If ANY required resource type has no availability, the entire booking fails

**Architecture Implication**: Plan resource quantities based on expected concurrent demand across all services.

### IMPORTANT NOTES

* **Resource Allocation Logic**: Wix automatically handles resource selection during booking - you specify types, not individual resources
* **Conflict Resolution**: If any required resource type has no available resources, the entire booking fails
* **Service Modification**: Adding/removing resource type requirements from existing services may affect existing bookings
* **Performance Consideration**: Complex multi-resource services may have slower booking availability calculation

### Troubleshooting Common Issues

**"Resource type not found" Error:**
- Verify resource type was created successfully before creating resources
- Check that `typeId` exactly matches the resource type `id`
- Ensure you're not using resource type `name` when `id` is required

**"Resource type name already exists" Error (409):**
- Resource type names must be unique across the site
- Query existing resource types to avoid duplicates
- Consider using more specific names (e.g., "Meeting Room" vs "Room")

**Service doesn't show resource requirements:**
- Verify `serviceResources` array includes all required resource types
- Check that resource type IDs are correct
- Confirm service creation was successful with proper resource configuration

**Resources showing as unavailable:**
- Check if `workingHoursSchedules` is too restrictive
- Verify `locationOptions` matches your business location setup
- Test with `availableInAllLocations: true` to eliminate location issues

**Resource updates failing:**
- Handle revision conflicts with retry logic (revision requirement is documented but conflict handling strategies aren't)

**Complex location availability issues:**
- Start with `availableInAllLocations: true` for all resources
- Only add location restrictions if absolutely necessary
- Location configuration is complex and often causes more problems than it solves

**Resource deletion concerns:**
- Deleting resources with active bookings may cause issues (deletion cleanup is documented but impact on existing bookings isn't clear)
- Consider disabling/hiding resources instead of deletion

### Resource Architecture Best Practices

**Resource Type Design:**
- Keep types broad enough to allow flexibility but specific enough to be meaningful
- Plan for growth - easier to split types later than merge them
- Use clear, customer-facing names (they appear in booking interfaces)

**Resource Naming:**
- Include location/identifier in resource names for easy management
- Be consistent with naming patterns across resource types
- Consider how names appear in booking confirmations and staff interfaces

**Availability Strategy:**
- Default to 24/7 availability unless business rules require restrictions
- Use working hours sparingly - they add complexity without always adding value
- Test availability scenarios thoroughly before going live

**Service Design:**
- Start with simpler single-resource services before attempting multi-resource
- Consider premium pricing for multi-resource services due to coordination complexity
- Plan for resource substitution scenarios (what if preferred room is unavailable?)

## API Documentation References

* [Create Resource Type](https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resource-types-v2/create-resource-type)
* [Create Resource](https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resources-v2/create-resource)
* [Update Resource](https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resources-v2/update-resource)
* [Bulk Create Services](https://dev.wix.com/docs/api-reference/business-solutions/bookings/services/services-v2/bulk-create-services)
* [Query Resources](https://dev.wix.com/docs/api-reference/business-solutions/bookings/resources/resources-v2/query-resources)
* [Calendar Schedules API](https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/introduction)
* [Apps Installer API](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
