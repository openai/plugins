# Functions Module

Invoke custom backend functions via `base44.functions`.

## Contents
- [Method](#method)
- [Invoking Functions](#invoking-functions) (Frontend, File Upload, Service Role, REST API)
- [Writing Backend Functions](#writing-backend-functions) (Basic, Service Role, Secrets, Errors)
- [Setup Requirements](#setup-requirements)
- [Authentication Modes](#authentication-modes)

## Methods

### `invoke`

```javascript
base44.functions.invoke(functionName, data?): Promise<any>
```

- `functionName`: Name of the backend function
- `data`: Optional object of parameters (sent as JSON, or multipart if contains File objects)
- Returns: Whatever the function returns

### `fetch`

```javascript
base44.functions.fetch(path, init?): Promise<Response>
```

Low-level method that performs a direct HTTP request to a backend function path and returns the native `Response` object. Use when you need streaming responses, custom HTTP methods, or raw response access.

- `path`: Function path (e.g., `/streaming_demo` or `/my-function/endpoint`)
- `init`: Optional native fetch options (`RequestInit`)
- Returns: Native `Response` object

## Invoking Functions

### From Frontend

```javascript
const result = await base44.functions.invoke("processOrder", {
  orderId: "order-123",
  action: "ship"
});

console.log(result);
```

### Streaming Response (using fetch)

```javascript
// Use fetch() for streaming responses (SSE, chunked text, etc.)
const response = await base44.functions.fetch("/stream-data", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: "Tell me a story" })
});

// Read as a stream
const reader = response.body.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value));
}
```

### Custom HTTP Methods (using fetch)

```javascript
// PUT, PATCH, DELETE, or other methods
const response = await base44.functions.fetch("/my-resource/123", {
  method: "DELETE"
});
console.log(response.status); // 204
```

### With File Upload

```javascript
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];

// Automatically uses multipart/form-data when File objects present
const result = await base44.functions.invoke("uploadDocument", {
  file: file,
  category: "invoices"
});
```

### With Service Role (Backend)

```javascript
// Inside another backend function
const result = await base44.asServiceRole.functions.invoke("adminTask", {
  userId: "user-123"
});
```

### Via REST API (curl)

Functions can be called via HTTP POST to your app domain:

```bash
curl -X POST "https://<app-domain>/functions/<function-name>" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## Writing Backend Functions

Backend functions run on Deno. Must export using `Deno.serve()`.

### Required Directory Structure

Each function must be in its own subdirectory under `base44/functions/` with a configuration file:

```
base44/
  functions/
    process-order/          # kebab-case directory name
      function.jsonc        # required configuration
      index.ts              # entry point
```

**function.jsonc:**
```jsonc
{
  "name": "process-order",
  "entry": "index.ts"
}
```

For complete setup and deployment instructions, see [functions-create.md](../../base44-cli/references/functions-create.md) in base44-cli.

### Basic Structure

```javascript
// base44/functions/process-order/index.ts
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

### With Service Role Access

```javascript
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

### Using Secrets

```javascript
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

### Error Handling

```javascript
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  try {
    const base44 = createClientFromRequest(req);
    const { orderId } = await req.json();
    
    const order = await base44.entities.Orders.get(orderId);
    if (!order) {
      return Response.json(
        { error: "Order not found" },
        { status: 404 }
      );
    }
    
    return Response.json({ order });
    
  } catch (error) {
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
});
```

## Setup Requirements

1. Enable Backend Functions in app settings (requires appropriate plan)
2. Create function files in `/functions` folder
3. Configure secrets via app dashboard for API keys

## Authentication Modes

| Mode | Context | Permissions |
|------|---------|-------------|
| User | `base44.functions.invoke()` | Runs under calling user's permissions |
| Service Role | `base44.asServiceRole.functions.invoke()` | Admin-level access |

Inside the function, use `createClientFromRequest(req)` to get a client that inherits the caller's auth context.

## Type Definitions

**How to get typed function names:** The Base44 CLI can generate an augmentation of `FunctionNameRegistry` from your project. For how to run it, use the **base44-cli** skill.

```typescript
/**
 * Registry of function names.
 * Augment this interface to enable autocomplete for function names.
 * Typically populated by the Base44 CLI type generator.
 */
interface FunctionNameRegistry {}

/**
 * Function name type - uses registry keys if augmented, otherwise string.
 */
type FunctionName = keyof FunctionNameRegistry extends never ? string : keyof FunctionNameRegistry;

/**
 * Options for functions.fetch(). Uses native fetch options directly.
 */
type FunctionsFetchInit = RequestInit;

/** Functions module for invoking custom backend functions. */
interface FunctionsModule {
  /**
   * Invokes a custom backend function by name.
   *
   * If any parameter is a File object, the request will automatically be
   * sent as multipart/form-data. Otherwise, it will be sent as JSON.
   *
   * @param functionName - The name of the function to invoke.
   * @param data - Optional object containing named parameters for the function.
   * @returns Promise resolving to the function's response.
   */
  invoke(functionName: FunctionName, data?: Record<string, any>): Promise<any>;

  /**
   * Performs a direct HTTP request to a backend function path and returns the native Response.
   *
   * Use for streaming responses (SSE, chunked text), custom HTTP methods,
   * or when you need raw access to the response.
   *
   * @param path - Function path, e.g. `/streaming_demo` or `/my-function/endpoint`
   * @param init - Optional native fetch options.
   * @returns Promise resolving to a native fetch Response.
   */
  fetch(path: string, init?: FunctionsFetchInit): Promise<Response>;
}
```
