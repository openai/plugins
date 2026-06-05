---
name: "Setup: Shipping Regions"
description: Configures delivery profiles and regions — creating profiles, adding regions with destinations, assigning carriers, enabling backup rates, and handling externally managed regions.
layer: config
---
# Shipping Regions

## Creating Delivery Profiles

- The first profile is auto-created when Stores is installed.
- Up to **99 profiles** per site.

## Adding Regions

- Up to **100 regions** per profile.
- Each region requires: `name`, `destinations` (array of country codes), `active` flag.

### Domestic Region

Set `countryCode` to match `site_context.country`.

### International Region

Use multiple country codes, or leave `destinations` empty to represent "Rest of World."

## Assigning Carriers

- Up to **25 carriers** per region.
- Use `appId` to identify the carrier.

## Enabling Backup Rates

CRITICAL -- set `backupRate.active = true` on each carrier. The backup rate amount should be **5-10% of effective AOV**.

Without a backup rate, if the carrier service fails the shipping option silently disappears from checkout.

## External Carrier Detection

- Shippo `appId`: `2b1943e2-3fc2-47bc-be56-3d402e5966d7`
- If **ALL** carriers in a region are external, skip that region -- it is externally managed.
- If the region has a mix of external and Wix-native carriers, treat it as hybrid and only configure the Wix-native carriers.

## Business Context Filter for International (MANDATORY)

Check the site's industry. If it matches any of the following categories, DO NOT recommend international shipping:

food, restaurant, grocery, bakery, catering, perishable, fresh, meat, produce, dairy, drink, beverage

Perishable goods require cold chain logistics that standard international shipping does not support.

## Identifying International Regions

A region is considered "international" if any of the following are true:
- Region name contains "international" or "internacional" (case-insensitive)
- `destinations[]` is empty (Rest of World)
- `destinations` include countries OTHER than the site country
