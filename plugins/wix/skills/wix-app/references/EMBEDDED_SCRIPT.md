
# Wix Embedded Script Builder

Embedded scripts are HTML code fragments injected into the DOM of Wix sites — for integration with third-party services, analytics tracking, advertising, and custom JavaScript functionality.

## Scaffold

Use `wix generate --params` with all 5 required fields:

```bash
wix generate --params '{"extensionType":"EMBEDDED_SCRIPT","name":"<name>","folder":"<folder>","scriptType":"<scriptType>","placement":"<placement>"}'
```

| Field | Constraint |
| --- | --- |
| `name` | Display name, any string. |
| `folder` | Lowercase alphanumeric, hyphens, slashes (for sub-paths). |
| `scriptType` | One of: `ESSENTIAL`, `FUNCTIONAL`, `ANALYTICS`, `ADVERTISING`. |
| `placement` | One of: `HEAD`, `BODY_START`, `BODY_END`. |

The CLI generates the folder, `<folder>.html` (the actual script HTML), the builder file, the UUID, and the `src/extensions.ts` registration. (It may also drop a sample `<other>.ts` module to demonstrate `<script type="module" src="./xxx.ts">` imports — feel free to delete or repurpose it.)

After implementation, the app developer must enable `SCOPE.DC-APPS.MANAGE-EMBEDDED-SCRIPTS` in the Wix Dev Center — see [Enable Embedded Script Permission](#enable-embedded-script-permission).

## Script Types

Embedded scripts must declare a type for consent management:

| Type          | Description                                      | Use Cases                               |
| ------------- | ------------------------------------------------ | --------------------------------------- |
| `ESSENTIAL`   | Core functionality crucial to site operation     | Authentication, security features       |
| `FUNCTIONAL`  | Remembers user choices to improve experience     | Language preferences, UI customization  |
| `ANALYTICS`   | Provides statistics on how visitors use the site | Google Analytics, Hotjar, Mixpanel      |
| `ADVERTISING` | Provides visitor data for marketing purposes     | Facebook Pixel, Google Ads, retargeting |

**Selection rule:** If a script falls into multiple types, choose the option closest to the bottom of the list (most restrictive). For example, a script with both Analytics and Advertising aspects should be typed as `ADVERTISING`.

## Placement Options

| Placement    | Where in HTML                            | Best for                                                                |
| ------------ | ---------------------------------------- | ----------------------------------------------------------------------- |
| `HEAD`       | Between `<head>` and `</head>` tags      | Analytics, tracking, early initialization                               |
| `BODY_START` | Immediately after opening `<body>` tag   | Critical functionality, `<noscript>` fallback                           |
| `BODY_END`   | Immediately before closing `</body>` tag | Advertising pixels, non-critical features (non-blocking, better perf)   |

## Dynamic Parameters and Dashboard Configuration

**Every embedded script requires a companion dashboard page** to configure its parameters. Scaffold a separate `DASHBOARD_PAGE` extension and use `embeddedScripts` from `@wix/app-management` to load/save parameters (see [DASHBOARD_PAGE.md](DASHBOARD_PAGE.md)). Wix stores the parameters and injects them as `{{templateVars}}` into the HTML at render time.

### Parameter Types

| Type       | Description              | Dashboard Component    |
| ---------- | ------------------------ | ---------------------- |
| `TEXT`     | Single-line text         | Input                  |
| `NUMBER`   | Numeric value            | Input type="number"    |
| `BOOLEAN`  | True/false toggle        | ToggleSwitch, Checkbox |
| `IMAGE`    | Image from media manager | ImagePicker            |
| `DATE`     | Date only                | DatePicker             |
| `DATETIME` | Date with time           | DatePicker + TimeInput |
| `URL`      | URL with validation      | Input                  |
| `SELECT`   | Dropdown options         | Dropdown               |
| `COLOR`    | Color value              | ColorPicker            |

### Template Variable Syntax

`{{parameterKey}}` placeholders are substituted at injection time, **but only inside HTML attribute values** — not inside `<script>` bodies. The required pattern is: render every parameter as a data attribute on a config element, then read it from `dataset` in JS.

```html
<div id="config"
  data-api-key="{{apiKey}}"
  data-enabled="{{enabled}}"
  data-headline="{{headline}}"
></div>
<script>
  const { apiKey, enabled, headline } = document.getElementById("config").dataset;
  // ...
</script>
```

**Type handling (all `dataset` values are strings):**
- `NUMBER` → `Number(value)` or `parseInt(value, 10)`
- `BOOLEAN` → compare against `"true"` / `"false"`
- `DATE` / `DATETIME` → `new Date(value)`

**Other rules:**
- Template variable names must match the parameter keys exactly.
- Required parameters always have values; optional parameters may be empty — provide fallbacks.
- Only use parameters that are relevant to the use case; don't reference parameters you don't implement.

### Common Parameters

Every embedded script should have at minimum an **enable/disable toggle** parameter:

| Parameter    | Type      | Purpose                              |
| ------------ | --------- | ------------------------------------ |
| `enabled`    | `BOOLEAN` | Allow site owner to activate/disable |
| `apiKey`     | `TEXT`    | Third-party service credentials      |
| `trackingId` | `TEXT`    | Analytics/pixel identifiers          |
| `headline`   | `TEXT`    | Customizable display text            |
| `color`      | `COLOR`   | UI customization                     |

## Module-script Rules

The `<script type="module">` block runs at module scope, where Rollup (used by Astro) **disallows `return` statements**.

- Use `throw new Error(...)` for early exits at module scope (e.g., "script disabled" / "config element not found").
- Wrap the main logic in a named `async function` and call it from a `DOMContentLoaded` listener (or directly if `document.readyState !== "loading"`); `return` is valid inside the function.

See the [Complete Example](#complete-example-coupon-popup) below for the full skeleton.

## Examples

### Analytics Tracking

**Request:** "Add Google Analytics tracking to my site"

**Output:**

- Script type: `ANALYTICS`
- Placement: `HEAD`
- Template variables: `{{trackingId}}`
- Implements: gtag.js initialization, page view tracking

### Popup/Modal

**Request:** "Create a coupon popup that shows when cart value exceeds $50"

**Output:**

- Script type: `FUNCTIONAL`
- Placement: `BODY_END`
- Template variables: `{{couponCode}}`, `{{minimumCartValue}}`, `{{enablePopup}}`
- Implements: Cart value detection, popup display logic, localStorage for "don't show again"

### Third-Party Chat Widget

**Request:** "Integrate Intercom chat widget"

**Output:**

- Script type: `FUNCTIONAL`
- Placement: `BODY_END`
- Template variables: `{{appId}}`, `{{userEmail}}`, `{{userName}}`
- Implements: Intercom SDK initialization, user identification

## Best Practices

- **Always create a dashboard page:** Every embedded script needs a configuration UI
- **Include enable/disable toggle:** Let site owners control activation without removing the script
- **Performance:** Minimize impact - scripts should be lightweight and non-blocking
- **Security:** Avoid inline event handlers, validate data, escape user input
- **Error handling:** Fail silently when appropriate - don't break the site
- **Module scope early exits:** Use `throw new Error()` for early exits at module scope, not `return`. Rollup (used by Astro) doesn't allow `return` statements at module scope. Wrap main logic in a named async function where `return` is valid.
- **Type conversions:** Parameters are always strings - convert in JavaScript as needed
- **API calls:** Only create fetch() calls to /api/\* endpoints that exist in the API spec
- **Scoping:** Prefix CSS classes and IDs to avoid conflicts with site styles
- **Cleanup:** Remove event listeners and intervals when appropriate

## Complete Example: Coupon Popup

### 1. Define Parameters

```
Parameters for "cart-coupon-popup":
- couponCode (TEXT, required) - The coupon code to display
- popupHeadline (TEXT, required) - Headline text
- popupDescription (TEXT, required) - Description text
- minimumCartValue (NUMBER) - Minimum cart value to show popup
- enablePopup (BOOLEAN, required) - Enable/disable toggle
```

### 2. Embedded Script (`<folder>.html`)

```html
<div
  id="popup-config"
  data-coupon-code="{{couponCode}}"
  data-popup-headline="{{popupHeadline}}"
  data-minimum-cart-value="{{minimumCartValue}}"
  data-enable-popup="{{enablePopup}}"
></div>
<div id="popup-container"></div>

<script type="module">
  // Get configuration from data attributes
  const config = document.getElementById("popup-config");
  if (!config) throw new Error("Config element not found");

  const { couponCode, popupHeadline, minimumCartValue, enablePopup } =
    config.dataset;

  // Exit early if disabled (use throw at module scope, not return)
  if (enablePopup !== "true") {
    throw new Error("Popup disabled");
  }

  // Main logic in a function (return is allowed here)
  async function initializePopup() {
    const minValue = Number(minimumCartValue) || 0;
    // ... popup implementation
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePopup);
  } else {
    initializePopup();
  }
</script>
```

### 3. Dashboard Page (See the DASHBOARD_PAGE.md reference)

Uses `embeddedScripts` API from `@wix/app-management`:

```typescript
import { embeddedScripts } from "@wix/app-management";

// Load parameters
const script = await embeddedScripts.getEmbeddedScript();
const params = script.parameters; // { couponCode: "...", ... }

// Save parameters (all values must be strings)
await embeddedScripts.embedScript({
  parameters: {
    couponCode: "SAVE20",
    minimumCartValue: "50", // Number as string
    enablePopup: "true", // Boolean as string
  },
});
```

## Enable Embedded Script Permission

After implementation, the app developer must manually enable the embedded script permission:

1. Go to [https://manage.wix.com/apps/{app-id}/dev-center-permissions](https://manage.wix.com/apps/{app-id}/dev-center-permissions) (replace `{app-id}` with your actual app ID)
2. Add the `SCOPE.DC-APPS.MANAGE-EMBEDDED-SCRIPTS` permission
3. Save the changes

**Note:** This is a manual step in the Wix Dev Center. Without this permission, embedded scripts will not function on the site.
