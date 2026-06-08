
# Wix Dashboard Plugin Builder

Dashboard plugins are interactive widgets that embed into predefined **slots** on dashboard pages managed by Wix first-party business apps (Wix Stores, Wix Bookings, Wix Blog, Wix eCommerce, etc.). They occupy the full width of their slot and maintain dynamic height based on content.

## Scaffold

Use `wix generate --params` with `extensionType: DASHBOARD_PLUGIN`. `extendsSlotId` is the back-office extension container component ID from the host Wix app — see [Slots Reference](dashboard-plugin/SLOTS.md). The CLI generates the folder, the React component, the builder file, the UUID, and the `src/extensions.ts` registration.

## Architecture

Dashboard plugins operate through two mechanisms:

1. **Visual Integration** — Embedding plugin UI inside a supported dashboard page slot
2. **Logical Integration** — Implementing communication between the plugin and the host page's data via `observeState()`

## The `extendsSlotId` field

Specifies which dashboard page slot hosts your plugin. Each Wix business app exposes slots on its dashboard pages. You must provide the exact slot ID.

**Important:** Some slots with the same ID appear on different pages within the dashboard. If you create a plugin for a slot that exists on multiple pages, the plugin is displayed on all of those pages.

For the complete list of available slot IDs, see [Slots Reference](dashboard-plugin/SLOTS.md).

## Available Resources in Plugin Components

- **React** — Component logic and state management
- **Wix SDK** — Access Wix business solutions and site data
- **Wix Dashboard SDK** (`@wix/dashboard`) — Interact with the dashboard page's data passed to the slot
- **Wix Design System** (`@wix/design-system`) — Native-looking React components matching Wix's own dashboard UI

## Interacting with Dashboard Data

Use `observeState()` from the Dashboard SDK to receive data from the host dashboard page:

```typescript
import { dashboard } from "@wix/dashboard";
import { useEffect, useState } from "react";

const Plugin: FC = () => {
  const [params, setParams] = useState<Record<string, unknown>>({});

  useEffect(() => {
    dashboard.observeState((componentParams) => {
      setParams(componentParams);
    });
  }, []);

  return (
    <WixDesignSystemProvider features={{ newColorsBranding: true }}>
      <Card>
        <Card.Content size="medium">
          <Text>Received data: {JSON.stringify(params)}</Text>
        </Card.Content>
      </Card>
    </WixDesignSystemProvider>
  );
};
```

### Typed Props from Host Apps

Some Wix apps expose typed interfaces for their slot parameters. Import them from the app's dashboard package:

```typescript
import type { plugins } from "@wix/blog/dashboard";

type Props = plugins.BlogPosts.PostsBannerParams;

const Plugin: FC<Props> = (props) => {
  // props are typed according to the Blog Posts slot contract
};
```

> **Note:** Typed props availability varies by Wix app. Consult the specific app's SDK documentation. Not all slots provide typed parameter interfaces.

## Sizing Behavior

- Dashboard plugins take the **full width** of their slot
- **Height** adjusts dynamically based on content within slot boundaries
- When using Dashboard SDK or dashboard-react SDK, dimensions change dynamically based on contents


## Examples

### Blog Posts Banner Plugin

**Request:** "Create a plugin for the Wix Blog posts page that shows a promotional banner"

**Output:** Plugin targeting slot `46035d51-2ea9-4128-a216-1dba68664ffe` (Blog Posts page) with a Card component displaying promotional content, using `observeState()` to access blog post data.

### Bookings Staff Calendar Widget

**Request:** "Add a plugin to the Wix Bookings staff page that shows weekly availability"

**Output:** Plugin targeting slot `261e84a2-31d0-4258-a035-10544d251108` (Bookings Staff page) with a schedule display component, using `observeState()` to receive staff data.

### Order Details Plugin

**Request:** "Create a plugin on the eCommerce order page showing fulfillment status"

**Output:** Plugin targeting slot `cb16162e-42aa-41bd-a644-dc570328c6cc` (eCommerce Order page) with status badges and fulfillment details, using `observeState()` to access order data.

