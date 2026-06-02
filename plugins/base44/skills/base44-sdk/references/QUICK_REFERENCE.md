# Base44 SDK Quick Reference

Compact method signatures for all SDK modules. **Verify against this before writing code.**

---

## Auth (`base44.auth.*`)

```
loginViaEmailPassword(email, password, turnstileToken?) → Promise<{access_token, user}>
loginWithProvider('google' | 'microsoft' | 'facebook', fromUrl?) → void
me() → Promise<User | null>
updateMe(data) → Promise<User>
isAuthenticated() → Promise<boolean>
logout(redirectUrl?) → void
redirectToLogin(nextUrl) → void              # ⚠️ Avoid - prefer custom login UI
register({email, password, turnstile_token?, referral_code?}) → Promise<any>
verifyOtp({email, otpCode}) → Promise<any>
resendOtp(email) → Promise<any>
inviteUser(userEmail, role) → Promise<any>
resetPasswordRequest(email) → Promise<any>
resetPassword({resetToken, newPassword}) → Promise<any>
changePassword({userId, currentPassword, newPassword}) → Promise<any>
setToken(token, saveToStorage?) → void
```

---

## Entities (`base44.entities.EntityName.*`)

```
create(data) → Promise<T>
bulkCreate(dataArray) → Promise<T[]>
list(sort?, limit?, skip?, fields?) → Promise<Pick<T, K>[]>
filter(query, sort?, limit?, skip?, fields?) → Promise<Pick<T, K>[]>
get(id) → Promise<T>
update(id, data) → Promise<T>
updateMany(query, mongoUpdateOp) → Promise<UpdateManyResult>   // e.g. { $set: { field: val } }
bulkUpdate(dataArray) → Promise<T[]>                           // each item must have id
delete(id) → Promise<DeleteResult>
deleteMany(query) → Promise<DeleteManyResult>
importEntities(file) → Promise<ImportResult<T>>                // frontend only
subscribe(callback) → () => void                               // returns unsubscribe fn
```

**Sort:** Use `SortField<T>`: `-fieldName` for descending (e.g., `-created_date`). Max 5,000 per request for list/filter.

---

## Functions (`base44.functions.*`)

```
invoke(functionName, data?) → Promise<any>
fetch(path, init?) → Promise<Response>   // low-level, for streaming/custom methods
```

**Backend:** Use `base44.asServiceRole.functions.invoke()` for admin access.

---

## Integrations (`base44.integrations.Core.*`)

```
InvokeLLM({prompt, add_context_from_internet?, response_json_schema?, file_urls?}) → Promise<string | object>
GenerateImage({prompt}) → Promise<{url}>
SendEmail({to, subject, body, from_name?}) → Promise<any>
UploadFile({file}) → Promise<{file_url}>
UploadPrivateFile({file}) → Promise<{file_uri}>
CreateFileSignedUrl({file_uri, expires_in?}) → Promise<{signed_url}>
ExtractDataFromUploadedFile({file_url, json_schema}) → Promise<object>
```

### Custom Integrations (`base44.integrations.custom.*`)

```
call(slug, operationId, {payload?, pathParams?, queryParams?}?) → Promise<{success, status_code, data}>
```

**operationId format:** `"method:/path"` (e.g., `"get:/contacts"`, `"post:/users/{id}"`)

---

## Analytics (`base44.analytics.*`)

```
track({eventName, properties?}) → void
```

---

## App Logs (`base44.appLogs.*`)

```
logUserInApp(pageName) → Promise<void>
fetchLogs(params?) → Promise<any>
getStats(params?) → Promise<any>
```

---

## Users (`base44.users.*`)

```
inviteUser(userEmail, role) → Promise<any>    // role: 'user' | 'admin'
```

---

## Service Role Connectors (`base44.asServiceRole.connectors.*`)

**Backend only, service role required.** App-scoped (shared account).

```
getConnection(integrationType) → Promise<{accessToken, connectionConfig}>   // recommended
getAccessToken(integrationType) → Promise<string>                           // deprecated
```

**Types:** Run `npx base44 connectors list-available` to see all available integration types.

---

## SSO (`base44.asServiceRole.sso.*`)

**Backend only, service role required.**

```
getAccessToken(userId) → Promise<{access_token}>
```

---

## Service Role Access

**Backend functions only.** Prefix any module with `asServiceRole` for admin access:

```javascript
base44.asServiceRole.entities.Task.list()
base44.asServiceRole.functions.invoke('name', data)
base44.asServiceRole.connectors.getConnection('slack')
base44.asServiceRole.sso.getAccessToken(userId)
```

---

## Backend Function Template

```javascript
import { createClientFromRequest } from "@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  const data = await req.json();
  
  // User context
  const user = await base44.auth.me();
  
  // Service role for admin operations
  const allRecords = await base44.asServiceRole.entities.Task.list();
  
  return Response.json({ success: true });
});
```

---

## Client Initialization (External Apps)

```javascript
import { createClient } from "@base44/sdk";

const base44 = createClient({ appId: "your-app-id" });  // MUST use 'appId'
```

---

## TypeScript type registries

For typed entities, function names, and agent names (autocomplete and type checking), the Base44 CLI generates types and wires them into your project. Use the **base44-cli** skill for how to generate types.
