
# Wix Service Plugin (SPI) Builder

Service plugins are a set of APIs defined by Wix that let you inject custom logic into the existing backend flows of Wix business solutions or introduce entirely new flows. When you implement a service plugin, Wix calls your custom functions during specific flows. Common use cases include eCommerce customization (shipping, fees, payment settings, validations) and Bookings customization (staff sorting).

## Scaffold

Use `wix generate --params` with `extensionType: SERVICE_PLUGIN`. `pluginType` is one of:

| Value | SPI |
| --- | --- |
| `ECOM_ADDITIONAL_FEES` | Additional Fees |
| `ECOM_SHIPPING_RATES` | Shipping Rates |
| `ECOM_DISCOUNTS_TRIGGER` | Discount Triggers |
| `ECOM_VALIDATIONS` | Validations |
| `ECOM_PAYMENT_SETTINGS` | Payment Settings |
| `GIFT_CARDS_PROVIDER` | Gift Cards Provider |
| `STAFF_SORTING_PROVIDER` | Bookings Staff Sorting |
| `REALTIME_PERMISSIONS_PROVIDER` | Realtime Permissions Provider |

`name` must be lowercase alphanumeric + hyphens, max 19 characters. The CLI generates the folder, `plugin.ts`, the builder file, the UUID, and the `src/extensions.ts` registration with the appropriate builder method for the SPI type. Some SPI types (e.g., `ECOM_SHIPPING_RATES`) get a `description` placeholder field in the generated builder — replace it with your real copy.

## References

**You MUST read the relevant reference document before implementing an SPI**, and **call `ReadFullDocsMethodSchema`** with the docs URL it points at to get the exact request/response types — **do NOT edit code until you have the schema**. If the schema alone isn't enough, follow up with `ReadFullDocsArticle` on the same URL for prose explanations and additional code examples. Each reference also contains the correct imports, handler signatures, response structures, and a worked example.

| SPI Type | Reference |
| --- | --- |
| Additional Fees | [ADDITIONAL-FEES.md](service-plugin/ADDITIONAL-FEES.md) |
| Discount Triggers | [DISCOUNT-TRIGGERS.md](service-plugin/DISCOUNT-TRIGGERS.md) |
| Gift Cards | [GIFT-CARDS.md](service-plugin/GIFT-CARDS.md) |
| Payment Settings | [PAYMENT-SETTINGS.md](service-plugin/PAYMENT-SETTINGS.md) |
| Shipping Rates | [SHIPPING-RATES.md](service-plugin/SHIPPING-RATES.md) |
| Validations | [VALIDATIONS.md](service-plugin/VALIDATIONS.md) |
| Bookings Staff Sorting | [BOOKINGS-STAFF-SORTING.md](service-plugin/BOOKINGS-STAFF-SORTING.md) |

## Implementation Pattern

The scaffolded `plugin.ts` imports the relevant module from the SPI's package (`@wix/ecom/service-plugins`, `@wix/bookings/service-plugins`, etc.) and calls `provideHandlers({...})`. Each handler is invoked by Wix on the relevant flow with a `{ request, metadata }` payload and must return the SPI-specific response shape — see the per-SPI reference (Shipping Rates, Validations, etc.) for the exact request/response types and a worked example.

## Implementation Requirements

- Implement ALL required handler functions for the chosen SPI with complete business logic. Focus on the EXACT business logic the user asked for.
- Validate inputs: required fields present, correctly formatted, business constraints met (minimum order amounts, valid addresses, etc.). Handle missing or malformed data gracefully.
- Return the exact response shape documented for the SPI; handler responses must match Wix's documented structure.
- Handle errors gracefully — return appropriate error responses, don't throw unhandled exceptions.
- Test edge cases (empty carts, missing addresses, invalid data) before reporting completion.
- If a required capability isn't documented or available in the SDK, surface the gap to the user explicitly — do not fabricate.

## Elevating Permissions for API Calls

When making Wix API calls from service plugins, wrap the SDK method with `auth.elevate` from `@wix/essentials` before calling it. The pattern is identical for every Wix SDK module (`@wix/data`, `@wix/ecom`, `@wix/stores`, etc.):

```typescript
import { auth } from "@wix/essentials";
import { items } from "@wix/data";

const elevated = auth.elevate(items.query);
const response = await elevated("myCollection");
```

## Builder field overrides

The CLI generates a builder with `id`, `name`, and `source`. Some SPI types accept additional optional fields you may want to set in the generated builder file:

| SPI Type | Builder Method | Additional Optional Fields |
| --- | --- | --- |
| Shipping Rates | `ecomShippingRates()` | `description`, `learnMoreUrl`, `dashboardUrl`, `fallbackDefinitionMandatory`, `thumbnailUrl` |
| Validations | `ecomValidations()` | `validateInCart` |
| Payment Settings | `ecomPaymentSettings()` | `fallbackValueForRequires3dSecure` |
| Bookings Staff Sorting | `bookingsStaffSortingProvider()` | `methodName` (required), `methodDescription` (required, max 100 chars), `dashboardPluginId` |

Only `ecomShippingRates()` accepts `description`. Passing unsupported fields to other builders causes TypeScript errors. `bookingsStaffSortingProvider()` requires `methodName` and `methodDescription` fields — set these in the generated builder file after scaffolding.

> **Performance:** keep handler logic efficient. Most SPIs run on hot paths (every cart view, every checkout step, etc.).

## Testing Service Plugins

To test your service plugin extension:

1. **Release a version** with your changes - new service plugins or changes to existing ones won't take effect until you've built and released your project
2. **Trigger the call** to your service plugin by performing the relevant action (e.g., add items to cart and view cart to test Additional Fees)
