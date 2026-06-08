# Client Setup

How to create and configure the Base44 client.

## Contents
- [In Base44-Generated Apps](#in-base44-generated-apps)
- [In External Apps](#in-external-apps)
- [In Backend Functions](#in-backend-functions)
- [Authentication Modes](#authentication-modes) (Anonymous, User, Service Role)
- [Available Modules](#available-modules)
- [Client Methods](#client-methods)
- [Client Configuration Options](#client-configuration-options)

## In Base44-Generated Apps

Inside a Base44 app, the client is automatically created and configured. Import it from `@/api/base44Client` and use it as `base44`:

```javascript
const tasks = await base44.entities.Task.list();
```

## In External Apps

When using Base44 as a backend from an external app, install the SDK and create a client by calling `createClient()` directly:

```bash
npm install @base44/sdk
```

```javascript
import { createClient } from "@base44/sdk";

// IMPORTANT: The parameter name is 'appId' (NOT 'clientId', NOT 'id')
// IMPORTANT: onError must be nested inside 'options' object
const base44 = createClient({
  appId: "your-app-id",          // Required: Use 'appId' parameter
  token: "optional-user-token",  // Optional: for pre-authenticated requests
  options: {                      // Optional: configuration options
    onError: (error) => {         // Optional: error handler (must be in options)
      console.error("Base44 error:", error);
    }
  }
});
```

**Common Mistakes:**
- ❌ `createClient({ clientId: "..." })` - WRONG parameter name
- ❌ `createClient({ id: "..." })` - WRONG parameter name
- ❌ `createClient({ appId: "...", onError: ... })` - WRONG: onError must be in options
- ✅ `createClient({ appId: "..." })` - CORRECT parameter name
- ✅ `createClient({ appId: "...", options: { onError: ... } })` - CORRECT: onError in options

## In Backend Functions

`createClientFromRequest()` is designed for Base44-hosted backend functions. It extracts auth from request headers that Base44 injects and returns a client that includes service role access (`base44.asServiceRole`). For frontends and external backends, use `createClient()` instead.

```javascript
import { createClientFromRequest } from "@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  
  // Client inherits authentication from the request
  const user = await base44.auth.me();
  
  return Response.json({ user });
});
```

## Authentication Modes

| Mode | How to Get | Permissions |
|------|-----------|-------------|
| **Anonymous** | `createClient({ appId })` without token | Public data only |
| **User** | After `loginViaEmailPassword()` or via `createClientFromRequest` | User's own data |
| **Service Role** | `base44.asServiceRole.*` in backend | Full admin access |

## Anonymous Mode

No authentication. Can only access public resources.

```javascript
const base44 = createClient({ appId: "your-app-id" });

// Only works if Task entity allows anonymous read
const publicTasks = await base44.entities.Task.list();
```

## User Mode

After user logs in, the client automatically includes their token.

```javascript
const base44 = createClient({ appId: "your-app-id" });

// Login sets the token
await base44.auth.loginViaEmailPassword("user@example.com", "password");

// Subsequent requests are authenticated
const user = await base44.auth.me();
const myTasks = await base44.entities.Task.list();  // filtered by permissions
```

## Service Role Mode

Admin-level access. **Backend only.**

```javascript
// Inside a backend function
Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  
  // User mode - respects permissions
  const myTasks = await base44.entities.Task.list();
  
  // Service role - bypasses permissions
  const allTasks = await base44.asServiceRole.entities.Task.list();
  const allUsers = await base44.asServiceRole.entities.User.list();
  const oauthToken = await base44.asServiceRole.connectors.getAccessToken("slack");
  
  return Response.json({ myTasks, allTasks });
});
```

## Available Modules

The client exposes these modules:

```javascript
base44.agents        // AI conversations
base44.analytics     // Event tracking
base44.appLogs       // App usage logging
base44.auth          // Authentication
base44.connectors    // Per-user OAuth flows (UserConnectorsModule)
base44.entities      // CRUD operations
base44.functions     // Backend function invocation
base44.integrations  // Third-party services
base44.users         // User invitations

// Service role only (backend)
base44.asServiceRole.agents
base44.asServiceRole.appLogs
base44.asServiceRole.connectors  // App-scoped OAuth tokens (ConnectorsModule)
base44.asServiceRole.entities
base44.asServiceRole.functions
base44.asServiceRole.integrations
base44.asServiceRole.sso         // SSO token generation
```

## Client Methods

The client provides these methods:

```javascript
// Set authentication token for all subsequent requests
base44.setToken(newToken);

// Cleanup WebSocket connections (call when done with client)
base44.cleanup();
```

### setToken

Updates the authentication token for all subsequent API requests and WebSocket connections.

```javascript
// After receiving a token (e.g., from external auth)
base44.setToken("new-jwt-token");
```

### cleanup

Disconnects WebSocket connections. Call when you're done with the client or when the component unmounts.

```javascript
// Cleanup on component unmount (React example)
useEffect(() => {
  return () => base44.cleanup();
}, []);
```

## Client Configuration Options

```javascript
createClient({
  appId: "your-app-id",      // Required: MUST use 'appId' (not 'clientId' or 'id')
  token: "jwt-token",        // Optional: pre-set auth token
  options: {                 // Optional: configuration options
    onError: (error) => {}   // Optional: global error handler (must be in options)
  }
});
```

**⚠️ Critical:**
- The parameter name is `appId`, not `clientId` or `id`. Using the wrong parameter name will cause errors.
- The `onError` handler must be nested inside the `options` object, not at the top level.

## Type Definitions

### CreateClientConfig

```typescript
/** Configuration for creating a Base44 client. */
interface CreateClientConfig {
  /** The Base44 app ID (required). */
  appId: string;
  /** User authentication token. Used to authenticate as a specific user. */
  token?: string;
  /** @internal Service role token; only set automatically in Base44-hosted backend functions. */
  serviceToken?: string;
  /** Additional client options. */
  options?: CreateClientOptions;
}

/** Options for creating a Base44 client. */
interface CreateClientOptions {
  /** Optional error handler called whenever an API error occurs. */
  onError?: (error: Error) => void;
}
```

### Base44Client

```typescript
/** The Base44 client instance. */
interface Base44Client {
  /** Agents module for managing AI agent conversations. */
  agents: AgentsModule;
  /** Analytics module for tracking custom events. */
  analytics: AnalyticsModule;
  /** App logs module for tracking app usage. */
  appLogs: AppLogsModule;
  /** Auth module for user authentication and management. */
  auth: AuthModule;
  /** Entities module for CRUD operations on your data models. */
  entities: EntitiesModule;
  /** Functions module for invoking custom backend functions. */
  functions: FunctionsModule;
  /** Integrations module for calling pre-built integration methods. */
  integrations: IntegrationsModule;

  /** Cleanup function to disconnect WebSocket connections. */
  cleanup(): void;

  /** Sets a new authentication token for all subsequent requests. */
  setToken(newToken: string): void;

  /** Per-user OAuth flows. Each end user has their own connection. */
  connectors: UserConnectorsModule;

  /** Provides access to modules with elevated service role permissions (backend only). */
  readonly asServiceRole: {
    agents: AgentsModule;
    appLogs: AppLogsModule;
    /** App-scoped OAuth tokens. All users share the same connected account. */
    connectors: ConnectorsModule;
    entities: EntitiesModule;
    functions: FunctionsModule;
    integrations: IntegrationsModule;
    /** SSO token generation for users. */
    sso: SsoModule;
    cleanup(): void;
  };
}
```
