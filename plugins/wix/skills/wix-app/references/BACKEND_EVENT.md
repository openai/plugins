
# Wix CLI Backend Event Extension

Event extensions run custom logic when something happens on a site — a contact is created, an order is placed, a booking is confirmed, a blog post is published. Each extension is built on a Wix JavaScript SDK webhook; the CLI subscribes your project to it.

Common use cases: react to CRM events, sync data on order creation, send notifications when a booking is confirmed.

## Scaffold

Use `wix generate --params` with all required fields:

```bash
wix generate --params '{"extensionType":"EVENT","folder":"<folder>"}'
```

`folder` must be lowercase alphanumeric and hyphens. The CLI generates the folder, both files, the UUID, and the `src/extensions.ts` registration. The scaffolded handler file imports a sample SDK event (CRM Contact Created) — replace the import and the handler body with the event you actually want.

## References

| Topic | Reference |
| --- | --- |
| Common events (CRM, eCommerce, Bookings, Blog) | [COMMON-EVENTS.md](backend-event/COMMON-EVENTS.md) |

## Handler implementation

Each handler imports an event from the relevant `@wix/*` SDK module and is `default`-exported (e.g., `export default contacts.onContactCreated((event) => { ... })`). See [COMMON-EVENTS.md](backend-event/COMMON-EVENTS.md) for the SDK module, handler name, payload shape, and required permission for each common event. Handlers can be `async`; wrap logic in try/catch so one failing handler doesn't break others.

## Elevating Permissions for API Calls

When calling Wix APIs from inside an event handler, use `auth.elevate` from `@wix/essentials` so the call runs with the right permissions.

```typescript
import { contacts } from "@wix/crm";
import { auth } from "@wix/essentials";
import { items } from "@wix/data";

export default contacts.onContactCreated(async (event) => {
  const elevatedQuery = auth.elevate(items.query);
  const result = await elevatedQuery("MyCollection").find();
  // Use result
});
```

## Key Constraints

- **One handler per event** – You cannot have two event extensions for the same event in the app (local or dashboard).
- **Permissions** – Each event may require specific permission scopes; configure them in the app dashboard (Permissions page).
- **Testing** – Release a version with your changes, then perform the action that triggers the event. Some events are not fully testable in local dev.
- **Backend limits** – Event handlers run under backend extension limits (e.g. 1000 CPU ms per request, 20 sub-requests). See [About Backend Extensions](https://dev.wix.com/docs/wix-cli/guides/extensions/backend-extensions/about-backend-extensions).

## Best Practices

- **Error handling:** Wrap handler logic in try/catch; log and optionally rethrow or report.
- **Idempotency:** Events may be delivered more than once; design handlers to be idempotent where possible.
- **Logging:** Use `console.log` for debugging; keep production logs minimal and non-sensitive.
- **Performance:** Finish within backend limits; offload heavy work to queues or background jobs if needed.

## Testing Event Extensions

1. **Release** a version with your changes.
2. **Trigger** the event by taking an action.
