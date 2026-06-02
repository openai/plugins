# Common Wix Events for CLI Event Extensions

This reference lists common event types, SDK imports, permissions, and links. For full payload shapes and additional events, see the [JavaScript SDK reference](https://dev.wix.com/docs/sdk).

## CRM Events

| Event | Import | Handler Call | Permission | API Reference |
| --- | --- | --- | --- | --- |
| Contact created | `import { contacts } from "@wix/crm"` | `contacts.onContactCreated(handler)` | `SCOPE.DC-CONTACTS.READ-CONTACTS` | [onContactCreated](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/contact-v4/contact-created?apiView=SDK) |
| Contact updated | `import { contacts } from "@wix/crm"` | `contacts.onContactUpdated(handler)` | `SCOPE.DC-CONTACTS.READ-CONTACTS` | [onContactUpdated](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/contact-v4/contact-updated?apiView=SDK) |
| Contact deleted | `import { contacts } from "@wix/crm"` | `contacts.onContactDeleted(handler)` | `SCOPE.DC-CONTACTS.READ-CONTACTS` | [onContactDeleted](https://dev.wix.com/docs/api-reference/crm/members-contacts/contacts/contacts/contact-v4/contact-deleted?apiView=SDK) |

## eCommerce Events

| Event | Import | Handler Call | Permission | API Reference |
| --- | --- | --- | --- | --- |
| Order created | `import { orders } from "@wix/ecom"` | `orders.onOrderCreated(handler)` | `SCOPE.DC-STORES.READ-ORDERS` | [onOrderCreated](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/orders/orders/order-created?apiView=SDK) |
| Order approved | `import { orders } from "@wix/ecom"` | `orders.onOrderApproved(handler)` | `SCOPE.DC-STORES.READ-ORDERS` | [onOrderApproved](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/orders/orders/order-approved?apiView=SDK) |
| Cart created | `import { cart } from "@wix/ecom"` | `cart.onCartCreated(handler)` | `SCOPE.DC-STORES.READ-ORDERS` | [onCartCreated](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/purchase-flow/cart/cart/cart-created?apiView=SDK) |
| Cart updated | `import { cart } from "@wix/ecom"` | `cart.onCartUpdated(handler)` | `SCOPE.DC-STORES.READ-ORDERS` | [onCartUpdated](https://dev.wix.com/docs/api-reference/business-solutions/e-commerce/purchase-flow/cart/cart/cart-updated?apiView=SDK) |

## Bookings Events

| Event | Import | Handler Call | Permission | API Reference |
| --- | --- | --- | --- | --- |
| Booking confirmed | `import { bookings } from "@wix/bookings"` | `bookings.onBookingConfirmed(handler)` | `SCOPE.DC-BOOKINGS.READ-CALENDAR-WITH-PARTICIPANTS` | [onBookingConfirmed](https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-writer-v2/booking-confirmed?apiView=SDK) |
| Booking canceled | `import { bookings } from "@wix/bookings"` | `bookings.onBookingCanceled(handler)` | `SCOPE.DC-BOOKINGS.READ-CALENDAR-WITH-PARTICIPANTS` | [onBookingCanceled](https://dev.wix.com/docs/api-reference/business-solutions/bookings/bookings/bookings-writer-v2/booking-canceled?apiView=SDK) |

## Blog Events

| Event | Import | Handler Call | Permission | API Reference |
| --- | --- | --- | --- | --- |
| Post created | `import { posts } from "@wix/blog"` | `posts.onPostCreated(handler)` | `SCOPE.DC-BLOG.READ-BLOGS` | [onPostCreated](https://dev.wix.com/docs/api-reference/business-solutions/blog/posts-stats/post-created?apiView=SDK) |
| Post updated | `import { posts } from "@wix/blog"` | `posts.onPostUpdated(handler)` | `SCOPE.DC-BLOG.READ-BLOGS` | [onPostUpdated](https://dev.wix.com/docs/api-reference/business-solutions/blog/posts-stats/post-updated?apiView=SDK) |

## Payload Shape

The event envelope structure varies by API — the path to the main entity differs (e.g., `event.entity`, `event.data.order`). Use TypeScript and your IDE for autocomplete and type safety. See each event's API reference link above for the exact payload shape.

All envelopes include a **metadata** object with context such as event ID, entity ID, timestamp, and instance ID.
