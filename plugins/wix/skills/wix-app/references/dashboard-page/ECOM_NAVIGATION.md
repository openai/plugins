# Ecom Navigation Reference

Ecom Extensions Dashboard Pages destination builders for navigating to ecom-related dashboard pages (use with @wix/dashboard navigate).

## deliveryProfile()

Ecom Extensions Dashboard Pages 'deliveryProfile()' destination builder for navigating to the Delivery Profile dashboard page.

**Method parameters:**
- `options`: deliveryProfileOptions

**Delivery profile options:**
- `deliveryProfileId` (string): The ID of the delivery profile to open in the dashboard.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.deliveryProfile({
    deliveryProfileId: "delivery-profile-id",
  }),
);
```

## deliveryProfiles()

Ecom Extensions Dashboard Pages 'deliveryProfiles()' destination builder for navigating to the Delivery Profiles dashboard page.

**Request:**
This method does not take any parameters.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.deliveryProfiles(),
);
```

## editDraftOrder()

Ecom Extensions Dashboard Pages 'editDraftOrder()' destination builder for navigating to the Edit Draft Order dashboard page.

**Method parameters:**
- `options`: editDraftOrderOptions

**Edit draft order options:**
- `draftOrderId` (string): The ID of the draft order to open for editing in the dashboard.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.editDraftOrder({
    draftOrderId: "draft-order-id",
  }),
);
```

## editOrder()

Ecom Extensions Dashboard Pages 'editOrder()' destination builder for navigating to the Edit Order dashboard page.

**Method parameters:**
- `options`: editOrderOptions

**Edit order options:**
- `orderId` (string): The ID of the order to open for editing in the dashboard.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.editOrder({
    orderId: "order-id",
  }),
);
```

## newOrder()

Ecom Extensions Dashboard Pages 'newOrder()' destination builder for navigating to the New Order dashboard page.

**Request:**
This method does not take any parameters.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.newOrder(),
);
```

## orderDetails()

Ecom Extensions Dashboard Pages 'orderDetails()' destination builder for navigating to the Order Details dashboard page.

**Method parameters:**
- `options`: orderDetailsOptions

**Order details options:**
- `id` (string): The ID of the order whose details page to open in the dashboard.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.orderDetails({
    id: "order-id",
  }),
);
```

## orderList()

Ecom Extensions Dashboard Pages 'orderList()' destination builder for navigating to the Order List dashboard page.

**Request:**
This method does not take any parameters.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.orderList(),
);
```

## orderRefund()

Ecom Extensions Dashboard Pages 'orderRefund()' destination builder for navigating to the Order Refund dashboard page.

**Method parameters:**
- `options`: orderRefundOptions

**Order refund options:**
- `orderId` (string): The ID of the order to open the refund page for in the dashboard.

**Example:**
```typescript
import { dashboard } from "@wix/dashboard";
import { pages } from "@wix/ecom/dashboard";

dashboard.navigate(
  pages.orderRefund({
    orderId: "order-id",
  }),
);
```
