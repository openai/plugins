---
name: "External Calendar Integration"
description: OAuth-based integration with Google Calendar, Microsoft Outlook, and Apple Calendar. Covers authentication flows, sync configuration, and bidirectional event management.
---
# Technical Step-by-Step Instructions: Connecting External Calendars (Google, Microsoft, Apple) to Wix Bookings (Real-World, API-First)

## Description

Below are the recommended steps to successfully connect and sync external calendars (Google Calendar, Microsoft Outlook, Apple Calendar) with Wix Bookings, with real-world troubleshooting and fixes for common API issues. This recipe covers the complete OAuth flow, sync configuration, and verification procedures.


---

## Prerequisites

### Required Features and Apps

Before connecting external calendars, ensure the following requirements are met:

1. **Wix Bookings** - Core app must be installed and configured
2. **Premium Plan** - External calendar integration requires premium features enabled
3. **Active Staff or Business Schedule** - Target schedule must exist for connection

### Premium Feature Validation

**CRITICAL**: External calendar integration is a **premium feature**. If not enabled, you'll receive a 403 error with `"PREMIUM_FEATURE_NOT_ENABLED"` code.

**Verification Steps:**
1. Attempt to list providers - should return Google, Microsoft, Apple
2. If 403 error occurs, upgrade plan or enable premium features
3. Contact Wix support if premium features aren't accessible after upgrade

### App Installation Process

If you encounter app-related errors, install the required apps using the Apps Installer API.

**For detailed app installation procedures, refer to:**
- [Apps Installer API Documentation](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
- Business setup recipes for comprehensive app installation workflows

## Overview

Wix External Calendar integration allows bidirectional sync between Wix schedules and external calendar providers. The system supports:

- **Google Calendar** - OAuth authentication, primary calendar sync
- **Microsoft Outlook/365** - OAuth authentication, specific calendar selection
- **Apple Calendar** - Credential authentication, dedicated calendar creation

### CRITICAL API DISCOVERY

**❌ COMMON ENDPOINT MISTAKES**:
- `/bookings/v2/external-calendar/providers` (missing 's' in calendars)
- `/calendar/v3/external-calendars/` (wrong namespace)

**✅ CORRECT ENDPOINTS**:
- List Providers: `/bookings/v2/external-calendars/providers`
- Connect OAuth: `/bookings/v2/external-calendars/connections:connectByOAuth`
- List Connections: `/bookings/v2/external-calendars/connections`

### Key Discovery: Schedule Selection Strategy

**Schedule Types Available:**
- **Business Schedule**: Universal external ID `4e0579a5-491e-4e70-a872-d097eed6e520`
- **Staff Schedules**: Individual staff member schedules with unique IDs

**Recommendation:**
- Use **Staff Schedules** for personal calendar sync (individual staff members)
- Use **Business Schedule** for company-wide calendar integration
- **Never connect the same external calendar to multiple schedules** - causes conflicts

### IMPORTANT NOTES

* **Premium Feature Gate**: Always verify premium features are enabled before attempting connections
* **OAuth Flow Complexity**: The OAuth process requires user interaction - cannot be fully automated
* **Sync Configuration**: Default settings may not match your needs - always review `syncConfig` after connection
* **Provider-Specific Behaviors**: Google only syncs primary calendar, Microsoft allows specific calendar selection
* **Connection Ownership**: If schedule ownership changes, external calendar connection is automatically disconnected
* **Real-Time Limitations**: External Calendar API doesn't provide webhooks or real-time event notifications
* **Revision Numbers**: External calendar connections don't use revision numbers like other calendar entities

---

## Steps

### 1. Verify Premium Features and List Providers

First, confirm external calendar features are available and identify supported providers.

Use `listProviders` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/list-providers)):

**Expected Response Structure:**
- **Google Provider**: `name: "Google"`, `features.connectMethods: ["OAUTH"]`
- **Microsoft Provider**: `name: "Outlook or Office 365"`, `features.connectMethods: ["OAUTH"]`
- **Apple Provider**: `name: "Apple"`, `features.connectMethods: ["CREDENTIALS"]`

Save the `providerId` for your desired provider and note the required `connectMethods`.

### 2. Query Available Schedules

Identify which schedule to connect the external calendar to using `querySchedules` API ([REST](https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/query-schedules)):

**Schedule Selection Guide:**
- **Staff Schedule**: Use for individual staff member calendar sync
- **Business Schedule**: Use for company-wide availability sync
- **Multiple Schedules**: Create separate connections for each schedule if needed

Save the `scheduleId` for your chosen schedule.

### 3. Initiate OAuth Connection (Google/Microsoft)

For OAuth providers (Google, Microsoft), create a connection using `connectByOAuth` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/connect-by-o-auth)):

**Required Parameters:**
- `providerId`: From step 1
- `scheduleId`: From step 2
- `redirectUrl`: Where user returns after authorization (can be placeholder)

**Response Contains:**
- `oauthUrl`: URL to redirect user for authorization

**User Authorization Flow:**
1. Direct user to the `oauthUrl`
2. User completes Google/Microsoft authorization
3. User is redirected to `redirectUrl` with `connectionId` parameter
4. Extract `connectionId` from redirect URL query parameters

### 4. Alternative: Connect by Credentials (Apple)

For credential-based providers (Apple), use `connectByCredentials` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/connect-by-credentials)):

**Required Parameters:**
- `providerId`: Apple provider ID
- `scheduleId`: Target schedule ID
- `email`: Apple ID email
- `password`: Apple ID password

**Important**: This method requires collecting sensitive credentials from users.

### 5. Verify Connection and Configure Sync

After successful connection, verify the connection status and configure sync settings:

**Check Connection:**
Use `getConnection` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/get-connection)) with the `connectionId`.

**Review Sync Configuration:**
- **Connection Status**: Should show `"CONNECTED"` when successful
- **Import Settings**: `syncConfig.listEventFromCalendars.enabled` controls importing external events to Wix
- **Export Settings**: `syncConfig.syncToCalendar.enabled` controls exporting Wix events to external calendar

**Update Sync Settings (if needed):**
Use `updateSyncConfig` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/update-sync-config)) to modify import/export behavior.

### 6. Test Connection and List Events

Verify the integration is working by listing external calendar events:

Use `listEvents` API ([REST](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/list-events)) with date range filters:

**Required Parameters:**
- `from`: Start date (required)
- `to`: End date (required)
- `scheduleIds`: Optional filter by specific schedules

This should return events from the connected external calendar.

### IMPORTANT NOTES

* **OAuth Completion**: OAuth flow requires actual user interaction - cannot be automated
* **Connection Persistence**: Connections remain active until manually disconnected or ownership changes
* **Sync Timing**: Event synchronization is not real-time - may take several minutes
* **Calendar Permissions**: External calendar must grant appropriate read/write permissions
* **Multiple Connections**: Each schedule can connect to multiple external calendar providers
* **Error Recovery**: Failed OAuth attempts can be retried with new `connectByOAuth` calls

### Troubleshooting Common Issues

**"PREMIUM_FEATURE_NOT_ENABLED" Error (403):**
- Verify site has premium plan enabled
- Contact Wix support to enable external calendar features
- Cannot proceed without premium feature access

**"Not Found" Error (404) on Providers:**
- Check endpoint URL has 's' in 'calendars': `/external-calendars/providers`
- Verify Wix Bookings app is installed
- Ensure using correct API version (v2)

**OAuth Authorization Fails:**
- Check `redirectUrl` is accessible and properly formatted
- Verify user has appropriate permissions for external calendar
- Try incognito/private browsing to avoid cached authorization issues
- Check external calendar provider status (Google/Microsoft outages)

**OAuth Internal Server Errors:**
- **"Internal Server Error" during Google OAuth**: Common issue that can occur after account selection
- **Immediate retry strategy**: Try the same OAuth flow again - temporary server issues often resolve
- **Alternative schedule approach**: If business schedule fails, try connecting to a staff schedule instead (or vice versa)
- **Browser troubleshooting**: Clear cookies/cache for the calendar provider's domain, or use incognito/private mode
- **Different redirect URL**: Try using a different `redirectUrl` parameter (e.g., `https://www.wix.com` instead of custom URLs)
- **Account-specific issues**: Try a different Google/Microsoft account if available for testing
- **Timing-based retry**: Wait 5-10 minutes between failed attempts - OAuth rate limiting may be involved

**OAuth Flow Recovery Steps:**
1. **First attempt fails** → Retry immediately with same parameters
2. **Second attempt fails** → Try alternative schedule type (business ↔ staff)
3. **Third attempt fails** → Clear browser data and use incognito mode
4. **Fourth attempt fails** → Try different redirect URL parameter
5. **All attempts fail** → Switch to different calendar provider (Google → Microsoft → Apple)

**Connection Shows "DISCONNECTED" Status:**
- Schedule ownership may have changed
- External calendar permissions may have been revoked
- User may have disconnected from external calendar provider side
- Recreate connection with fresh OAuth flow

**Events Not Syncing:**
- Check `syncConfig` settings match intended behavior
- Verify date range filters in `listEvents` calls
- Allow 5-10 minutes for sync to complete
- Check external calendar permissions and sharing settings

**Multiple Calendar Connections Conflict:**
- Avoid connecting same external calendar to multiple Wix schedules
- Use specific calendar selection for Microsoft Outlook connections
- Document which staff schedules connect to which external calendars

**Apple Calendar Credential Issues:**
- Verify Apple ID supports third-party app access
- Check if two-factor authentication requires app-specific passwords
- Test credentials in Apple Calendar app before API calls

### Provider-Specific Notes

**Google Calendar:**
- Only syncs with primary calendar
- Requires Google account with calendar access
- OAuth scope: `https://www.googleapis.com/auth/calendar`

**Microsoft Outlook/365:**
- Allows specific calendar selection
- Supports both personal and business accounts
- May require additional organizational permissions

**Apple Calendar:**
- Uses credential authentication (email/password)
- Creates dedicated calendar for Wix events
- May require app-specific password if 2FA enabled

## API Documentation References

* [List Providers](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/list-providers)
* [Connect By OAuth](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/connect-by-o-auth)
* [Connect By Credentials](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/connect-by-credentials)
* [Get Connection](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/get-connection)
* [Update Sync Config](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/update-sync-config)
* [List Events](https://dev.wix.com/docs/api-reference/business-solutions/bookings/calendar/external-calendar-v2/list-events)
* [Query Schedules](https://dev.wix.com/docs/api-reference/business-management/calendar/schedules-v3/query-schedules)
* [Apps Installer API](https://dev.wix.com/docs/api-reference/business-management/app-installation/install-app)
