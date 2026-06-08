# Creating Functions

Base44 functions are serverless backend functions that run on Deno. They are defined locally in your project and deployed to the Base44 backend.

## Function Directory

All function definitions must be placed in the `base44/functions/` folder in your project. Each function lives in its own subdirectory with a configuration file and entry point.

Example structure:
```
my-app/
  base44/
    functions/
      process-order/
        function.jsonc
        index.ts
      send-notification/
        function.jsonc
        index.ts
```

## How to Create a Function

1. Create a new directory in `base44/functions/` with your function name (use kebab-case)
2. Create a `function.jsonc` configuration file in the directory
3. Create the entry point file (e.g., `index.ts`)
4. Deploy the function using the CLI

## Function Configuration

Each function requires a `function.jsonc` configuration file:

```jsonc
{
  "name": "my-function",
  "entry": "index.ts",
  // Optionally add automations
  "automations": [
    {
      "name": "Daily run",
      "type": "scheduled",
      "schedule_mode": "recurring",
      "schedule_type": "cron",
      "cron_expression": "0 9 * * *"
    }
  ]
}
```

### Configuration Properties

| Property | Description | Required |
|----------|-------------|----------|
| `name` | Function name (must match `/^[^.]+$/` - no dots allowed) | Yes |
| `entry` | Entry point file path relative to the function directory (min 1 char) | Yes |
| `automations` | Array of triggers (CRON, simple schedule, one-time, entity hooks); deployed with the function | No |

## Automations

Functions can define automations (triggers) so they run on a schedule or when entity data changes. Add an optional `automations` array to `function.jsonc`. Supported types: **scheduled** (one-time, CRON, or simple interval) and **entity hooks** (on entity create/update/delete). Automations are deployed with the function via `npx base44 functions deploy`. For full schemas and examples, see [automations.md](automations.md).

## Entry Point File

Functions run on Deno and must export using `Deno.serve()`. Use `npm:` prefix for npm packages.

```typescript
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  // Get authenticated client from request
  const base44 = createClientFromRequest(req);
  
  // Parse input
  const { orderId, action } = await req.json();
  
  // Your logic here
  const order = await base44.entities.Orders.get(orderId);
  
  // Return response
  return Response.json({
    success: true,
    order: order
  });
});
```

### Request Object

The function receives a standard Deno `Request` object:
- `req.json()` - Parse JSON body
- `req.text()` - Get raw text body
- `req.headers` - Access request headers
- `req.method` - HTTP method

### Response Object

Return using `Response.json()` for JSON responses:

```typescript
// Success response
return Response.json({ data: result });

// Error response with status code
return Response.json({ error: "Something went wrong" }, { status: 400 });

// Not found
return Response.json({ error: "Order not found" }, { status: 404 });
```

## Complete Example

### Directory Structure
```
base44/
  functions/
    process-order/
      function.jsonc
      index.ts
```

### function.jsonc
```jsonc
{
  "name": "process-order",
  "entry": "index.ts"
}
```

### index.ts
```typescript
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  try {
    const base44 = createClientFromRequest(req);
    const { orderId } = await req.json();
    
    // Validate input
    if (!orderId) {
      return Response.json(
        { error: "Order ID is required" },
        { status: 400 }
      );
    }
    
    // Fetch and process the order
    const order = await base44.entities.Orders.get(orderId);
    if (!order) {
      return Response.json(
        { error: "Order not found" },
        { status: 404 }
      );
    }
    
    return Response.json({
      success: true,
      orderId: order.id,
      processedAt: new Date().toISOString()
    });
    
  } catch (error) {
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
});
```

## Using Service Role Access

For admin-level operations, use `asServiceRole`:

```typescript
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  
  // Check user is authenticated
  const user = await base44.auth.me();
  if (!user) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  
  // Use service role for admin operations
  const allOrders = await base44.asServiceRole.entities.Orders.list();
  
  return Response.json({ orders: allOrders });
});
```

## Using Secrets

Access environment variables configured in the app dashboard:

```typescript
Deno.serve(async (req) => {
  // Access environment variables (configured in app settings)
  const apiKey = Deno.env.get("STRIPE_API_KEY");
  
  const response = await fetch("https://api.stripe.com/v1/charges", {
    headers: {
      "Authorization": `Bearer ${apiKey}`
    }
  });
  
  return Response.json(await response.json());
});
```

## Naming Conventions

- **Directory name**: Use kebab-case (e.g., `process-order`, `send-notification`)
- **Function name**: Match the directory name, must match pattern `/^[^.]+$/` (no dots allowed)
  - Valid: `process-order`, `send_notification`, `myFunction`
  - Invalid: `process.order`, `send.notification.v2`
- **Entry file**: Typically `index.ts` or `index.js`

## Deploying Functions

After creating your function, deploy it to Base44:

```bash
npx base44 functions deploy
```

For more details on deploying, see [functions-deploy.md](functions-deploy.md).

## Notes

- Functions run on Deno runtime, not Node.js
- Use `npm:` prefix for npm packages (e.g., `npm:@base44/sdk`)
- Use `createClientFromRequest(req)` to get a client that inherits the caller's auth context
- Configure secrets via app dashboard for API keys
- Make sure to handle errors gracefully and return appropriate HTTP status codes

## Common Mistakes

| Wrong | Correct | Why |
|-------|---------|-----|
| `functions/myFunction.js` (single file) | `functions/my-function/index.ts` + `function.jsonc` | Functions require subdirectory with config |
| `import { ... } from "@base44/sdk"` | `import { ... } from "npm:@base44/sdk"` | Deno requires `npm:` prefix for npm packages |
| `MyFunction` or `myFunction` directory | `my-function` directory | Use kebab-case for directory names |
