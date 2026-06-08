# Analytics Module

Track custom events and user activity via `base44.analytics`.

## Contents
- [Methods](#methods)
- [Examples](#examples)
- [Automatic Tracking](#automatic-tracking)
- [Best Practices](#best-practices)

## Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `track(params)` | `void` | Track a custom event |

## Examples

### Track Custom Event

```javascript
// Track a simple event
base44.analytics.track({
  eventName: "button_clicked"
});

// Track event with properties
base44.analytics.track({
  eventName: "purchase_completed",
  properties: {
    product_id: "prod-123",
    amount: 99.99,
    currency: "USD"
  }
});
```

### Track User Actions

```javascript
// Track page view
base44.analytics.track({
  eventName: "page_view",
  properties: {
    page: "/dashboard",
    referrer: document.referrer
  }
});

// Track feature usage
base44.analytics.track({
  eventName: "feature_used",
  properties: {
    feature: "export_data",
    format: "csv"
  }
});
```

## Automatic Tracking

The analytics module automatically tracks:
- **Initialization events**: When the app loads
- **Heartbeat events**: Periodic activity signals
- **Session duration**: Time spent in the app

These internal events help measure user engagement without manual instrumentation.

## Best Practices

1. **Use descriptive event names**: `order_completed` instead of `click`
2. **Include relevant properties**: Add context that helps analyze the event
3. **Be consistent**: Use the same event names and property keys across your app
4. **Don't track sensitive data**: Avoid PII in event properties

```javascript
// Good: Descriptive with relevant properties
base44.analytics.track({
  eventName: "subscription_started",
  properties: {
    plan: "pro",
    billing_cycle: "annual"
  }
});

// Avoid: Vague event name, no context
base44.analytics.track({
  eventName: "click"
});
```

## Type Definitions

```typescript
/** Properties that can be attached to a tracked event. */
type TrackEventProperties = {
  [key: string]: string | number | boolean | null | undefined;
};

/** Parameters for the track() method. */
interface TrackEventParams {
  /** The name of the event to track. */
  eventName: string;
  /** Optional properties to attach to the event. */
  properties?: TrackEventProperties;
}

/** The analytics module interface. */
interface AnalyticsModule {
  /** Track a custom event with optional properties. */
  track(params: TrackEventParams): void;
}
```
