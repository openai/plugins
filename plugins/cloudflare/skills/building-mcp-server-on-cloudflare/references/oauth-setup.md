# Securing MCP Servers

MCP servers require authentication to ensure only trusted users can access them. The MCP specification uses OAuth 2.1 for authentication between clients and servers.

Cloudflare's `workers-oauth-provider` handles token management, client registration, and access token validation automatically.

## Basic Setup

```typescript
import { OAuthProvider } from "@cloudflare/workers-oauth-provider";
import { createMcpHandler } from "agents/mcp";

const apiHandler = {
  async fetch(request: Request, env: unknown, ctx: ExecutionContext) {
    return createMcpHandler(server)(request, env, ctx);
  }
};

export default new OAuthProvider({
  authorizeEndpoint: "/authorize",
  tokenEndpoint: "/oauth/token",
  clientRegistrationEndpoint: "/oauth/register",
  apiRoute: "/mcp",
  apiHandler: apiHandler,
  defaultHandler: AuthHandler
});
```

## Proxy Server Pattern

MCP servers often act as OAuth clients too. Your server sits between Claude Desktop and a third-party API like GitHub. To Claude, you're a server. To GitHub, you're a client. This lets users authenticate with their GitHub credentials.

Building a secure proxy server requires careful attention to several security concerns.

---

## Security Requirements

### Redirect URI Validation

The `workers-oauth-provider` validates that `redirect_uri` in authorization requests matches registered URIs. This prevents attackers from redirecting authorization codes to malicious endpoints.

### Consent Dialog

When proxying to third-party providers, implement your own consent dialog before forwarding users upstream. This prevents the "confused deputy" problem where attackers exploit cached consent.

Your consent dialog should:
- Identify the requesting MCP client by name
- Display the specific scopes being requested

---

## CSRF Protection

Prevent attackers from tricking users into approving malicious OAuth clients. Use a random token stored in a secure cookie.

```typescript
// Generate token when showing consent form
function generateCSRFProtection(): { token: string; setCookie: string } {
  const token = crypto.randomUUID();
  const setCookie = `__Host-CSRF_TOKEN=${token}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=600`;
  return { token, setCookie };
}

// Validate token when user approves
function validateCSRFToken(formData: FormData, request: Request): { clearCookie: string } {
  const tokenFromForm = formData.get("csrf_token");
  const cookieHeader = request.headers.get("Cookie") || "";
  const tokenFromCookie = cookieHeader
    .split(";")
    .find((c) => c.trim().startsWith("__Host-CSRF_TOKEN="))
    ?.split("=")[1];

  if (!tokenFromForm || !tokenFromCookie || tokenFromForm !== tokenFromCookie) {
    throw new Error("CSRF token mismatch");
  }

  return {
    clearCookie: `__Host-CSRF_TOKEN=; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=0`
  };
}
```

Include the token as a hidden form field:

```html
<input type="hidden" name="csrf_token" value="${csrfToken}" />
```

---

## Input Sanitization

Client-controlled content (names, logos, URIs) can execute malicious scripts if not sanitized. Treat all client metadata as untrusted.

```typescript
function sanitizeText(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function sanitizeUrl(url: string): string {
  if (!url) return "";
  try {
    const parsed = new URL(url);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      return "";
    }
    return url;
  } catch {
    return "";
  }
}
```

**Required protections:**
- Client names/descriptions: HTML-escape before rendering
- Logo URLs: Allow only `http:` and `https:` schemes
- Client URIs: Same as logo URLs
- Scopes: Treat as text, HTML-escape

---

## Content Security Policy

CSP headers block dangerous content and provide defense in depth.

```typescript
function buildSecurityHeaders(setCookie: string, nonce?: string): HeadersInit {
  const cspDirectives = [
    "default-src 'none'",
    "script-src 'self'" + (nonce ? ` 'nonce-${nonce}'` : ""),
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' https:",
    "font-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "connect-src 'self'"
  ].join("; ");

  return {
    "Content-Security-Policy": cspDirectives,
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Content-Type": "text/html; charset=utf-8",
    "Set-Cookie": setCookie
  };
}
```

---

## State Management

Ensure the same user that hits authorize reaches the callback. Use a random state token stored in KV with short expiration.

```typescript
// Create state before redirecting to upstream provider
async function createOAuthState(
  oauthReqInfo: AuthRequest,
  kv: KVNamespace
): Promise<{ stateToken: string }> {
  const stateToken = crypto.randomUUID();
  await kv.put(`oauth:state:${stateToken}`, JSON.stringify(oauthReqInfo), {
    expirationTtl: 600
  });
  return { stateToken };
}

// Bind state to browser session via hashed cookie
async function bindStateToSession(stateToken: string): Promise<{ setCookie: string }> {
  const encoder = new TextEncoder();
  const data = encoder.encode(stateToken);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

  return {
    setCookie: `__Host-CONSENTED_STATE=${hashHex}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=600`
  };
}

// Validate in callback - check both KV and session cookie
async function validateOAuthState(
  request: Request,
  kv: KVNamespace
): Promise<{ oauthReqInfo: AuthRequest; clearCookie: string }> {
  const url = new URL(request.url);
  const stateFromQuery = url.searchParams.get("state");

  if (!stateFromQuery) {
    throw new Error("Missing state parameter");
  }

  // Check KV
  const storedDataJson = await kv.get(`oauth:state:${stateFromQuery}`);
  if (!storedDataJson) {
    throw new Error("Invalid or expired state");
  }

  // Check session cookie matches
  const cookieHeader = request.headers.get("Cookie") || "";
  const consentedStateHash = cookieHeader
    .split(";")
    .find((c) => c.trim().startsWith("__Host-CONSENTED_STATE="))
    ?.split("=")[1];

  if (!consentedStateHash) {
    throw new Error("Missing session binding cookie");
  }

  // Hash state and compare
  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(stateFromQuery));
  const stateHash = Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  if (stateHash !== consentedStateHash) {
    throw new Error("State token does not match session");
  }

  await kv.delete(`oauth:state:${stateFromQuery}`);

  return {
    oauthReqInfo: JSON.parse(storedDataJson),
    clearCookie: `__Host-CONSENTED_STATE=; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=0`
  };
}
```

---

## Approved Clients Registry

Maintain a registry of approved client IDs per user. Store in a cryptographically signed cookie with HMAC-SHA256.

```typescript
export async function addApprovedClient(
  request: Request,
  clientId: string,
  cookieSecret: string
): Promise<string> {
  const existingClients = await getApprovedClientsFromCookie(request, cookieSecret) || [];
  const updatedClients = Array.from(new Set([...existingClients, clientId]));

  const payload = JSON.stringify(updatedClients);
  const signature = await signData(payload, cookieSecret);
  const cookieValue = `${signature}.${btoa(payload)}`;

  return `__Host-APPROVED_CLIENTS=${cookieValue}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=2592000`;
}
```

When reading the cookie, verify the signature before trusting data. If client isn't approved, show consent dialog.

---

## Cookie Security

### Why `__Host-` prefix?

The `__Host-` prefix prevents subdomain attacks on `*.workers.dev` domains. Requirements:
- Must have `Secure` flag (HTTPS only)
- Must have `Path=/`
- Must not have `Domain` attribute

Without this prefix, an attacker on `evil.workers.dev` could set cookies for your `mcp-server.workers.dev` domain.

### Multiple OAuth Providers

If running multiple OAuth flows on the same domain, namespace your cookies:
- `__Host-CSRF_TOKEN_GITHUB` vs `__Host-CSRF_TOKEN_GOOGLE`
- `__Host-APPROVED_CLIENTS_GITHUB` vs `__Host-APPROVED_CLIENTS_GOOGLE`

---

## Inline JavaScript

If your consent dialog needs inline JavaScript, use data attributes and nonces:

```typescript
const nonce = crypto.randomUUID();

const html = `
  <script nonce="${nonce}" data-redirect-url="${sanitizeUrl(redirectUrl)}">
    setTimeout(() => {
      const script = document.querySelector('script[data-redirect-url]');
      window.location.href = script.dataset.redirectUrl;
    }, 2000);
  </script>
`;

return new Response(html, {
  headers: buildSecurityHeaders(setCookie, nonce)
});
```

Data attributes store user-controlled data separately from executable code. Nonces with CSP allow your specific script while blocking injected scripts.

---

## Provider-Specific Setup

### GitHub

1. Create OAuth App at github.com/settings/developers
2. Set callback URL: `https://[worker].workers.dev/callback`
3. Store secrets:
   ```bash
   wrangler secret put GITHUB_CLIENT_ID
   wrangler secret put GITHUB_CLIENT_SECRET
   ```

### Google

1. Create OAuth Client at console.cloud.google.com/apis/credentials
2. Set authorized redirect URI
3. Scopes: `openid email profile`

### Auth0

1. Create Regular Web Application in Auth0 Dashboard
2. Set allowed callback URLs
3. Endpoints: `https://${AUTH0_DOMAIN}/authorize`, `/oauth/token`, `/userinfo`

---

## References

- [MCP Authorization Spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [RFC 9700 - OAuth Security](https://www.rfc-editor.org/rfc/rfc9700)
