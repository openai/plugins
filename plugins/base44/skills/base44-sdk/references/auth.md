# Auth Module

User authentication, registration, and session management via `base44.auth`.

## Contents
- [TypeScript Types](#typescript-types)
- [Methods](#methods)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Auth Providers](#auth-providers)
- [Environment Availability](#environment-availability)
- [App Visibility](#app-visibility)
- [Limitations](#limitations)

---

## TypeScript Types

### User Interface
```typescript
interface User {
  id: string;
  created_date: string;
  updated_date: string;
  email: string;
  full_name: string | null;
  disabled: boolean | null;
  is_verified: boolean;
  app_id: string;
  is_service: boolean;
  role: string;
  [key: string]: any; // Custom schema fields
}
```

### LoginResponse Interface
```typescript
interface LoginResponse {
  access_token: string;  // JWT token
  user: User;           // Complete user object
}
```

### Parameter Interfaces

#### RegisterParams
```typescript
interface RegisterParams {
  email: string;                    // Required
  password: string;                 // Required
  turnstile_token?: string | null;  // Optional: Cloudflare Turnstile for bot protection
  referral_code?: string | null;    // Optional: Referral code
}
```

#### VerifyOtpParams
```typescript
interface VerifyOtpParams {
  email: string;     // User's email
  otpCode: string;   // OTP code from email
}
```

#### ResetPasswordParams
```typescript
interface ResetPasswordParams {
  resetToken: string;   // Token from password reset email
  newPassword: string;  // New password to set
}
```

#### ChangePasswordParams
```typescript
interface ChangePasswordParams {
  userId: string;          // User ID
  currentPassword: string; // Current password for verification
  newPassword: string;     // New password to set
}
```

### Provider Type
```typescript
type Provider = 'google' | 'microsoft' | 'facebook';
```

---

## Methods

### Module Interface
```typescript
interface AuthModule {
  // User Info
  me(): Promise<User>;
  updateMe(data: Partial<Omit<User, 'id' | 'created_date' | 'updated_date' | 'app_id' | 'is_service'>>): Promise<User>;
  isAuthenticated(): Promise<boolean>;

  // Login/Logout
  loginViaEmailPassword(email: string, password: string, turnstileToken?: string): Promise<LoginResponse>;
  loginWithProvider(provider: Provider, fromUrl?: string): void;
  logout(redirectUrl?: string): void;
  redirectToLogin(nextUrl: string): void;

  // Token Management
  setToken(token: string, saveToStorage?: boolean): void;

  // Registration
  register(params: RegisterParams): Promise<any>;
  verifyOtp(params: VerifyOtpParams): Promise<any>;
  resendOtp(email: string): Promise<any>;

  // User Management
  inviteUser(userEmail: string, role: string): Promise<any>;

  // Password Management
  resetPasswordRequest(email: string): Promise<any>;
  resetPassword(params: ResetPasswordParams): Promise<any>;
  changePassword(params: ChangePasswordParams): Promise<any>;
}
```

### Method Reference Table

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `register()` | `params: RegisterParams` | `Promise<any>` | Create new user account |
| `loginViaEmailPassword()` | `email: string, password: string, turnstileToken?: string` | `Promise<LoginResponse>` | Authenticate with email/password |
| `loginWithProvider()` | `provider: Provider, fromUrl?: string` | `void` | Initiate OAuth login flow. Providers: `'google'` (default), `'microsoft'`, `'facebook'` (enable in app settings) |
| `me()` | None | `Promise<User>` | Get current authenticated user |
| `updateMe()` | `data: Partial<User>` | `Promise<User>` | Update current user's profile |
| `logout()` | `redirectUrl?: string` | `void` | Redirect to server-side logout (clears HTTP-only cookies and session), then to redirectUrl or current URL |
| `redirectToLogin()` | `nextUrl: string` | `void` | ⚠️ **Avoid** - Prefer custom login UI with `loginViaEmailPassword()` or `loginWithProvider()` |
| `isAuthenticated()` | None | `Promise<boolean>` | Check if user is logged in |
| `setToken()` | `token: string, saveToStorage?: boolean` | `void` | Manually set auth token |
| `inviteUser()` | `userEmail: string, role: string` | `Promise<any>` | Send invitation email |
| `verifyOtp()` | `params: VerifyOtpParams` | `Promise<any>` | Verify OTP code |
| `resendOtp()` | `email: string` | `Promise<any>` | Resend OTP code |
| `resetPasswordRequest()` | `email: string` | `Promise<any>` | Request password reset |
| `resetPassword()` | `params: ResetPasswordParams` | `Promise<any>` | Reset password with token |
| `changePassword()` | `params: ChangePasswordParams` | `Promise<any>` | Change user password |

---

## Examples

### Register New User (Complete Flow)

Registration requires email verification before login. Complete flow:

1. **Register** - Create the user account
2. **Verification email sent** - User receives an OTP code
3. **Verify OTP** - User enters code to verify email
4. **Login** - User can now log in

```javascript
try {
  // Step 1: Register the user
  await base44.auth.register({
    email: "user@example.com",
    password: "securePassword123",
    referral_code: "OPTIONAL_CODE",    // optional
    turnstile_token: "CAPTCHA_TOKEN"   // optional, for bot protection
  });
  console.log('Registration successful. Check email for OTP code.');

  // Step 2: User receives email with OTP code (e.g., "123456")

  // Step 3: Verify the OTP code
  await base44.auth.verifyOtp({
    email: "user@example.com",
    otpCode: "123456"  // code from verification email
  });
  console.log('Email verified successfully.');

  // Step 4: Now the user can log in
  const loginResponse = await base44.auth.loginViaEmailPassword(
    "user@example.com",
    "securePassword123"
  );
  console.log('Login successful:', loginResponse.user);

} catch (error) {
  console.error('Registration flow failed:', error.message);
  // Handle specific errors (see Error Handling section)
}
```

> **Important**: Users cannot log in until they complete OTP verification. Attempting to call `loginViaEmailPassword` before verification will fail.

### Login with Email/Password

```javascript
try {
  const response = await base44.auth.loginViaEmailPassword(
    "user@example.com",
    "password123",
    turnstileToken  // optional: for bot protection
  );

  console.log('Login successful');
  console.log('User:', response.user);
  console.log('Token:', response.access_token);

  // JWT is automatically stored for subsequent requests

} catch (error) {
  console.error('Login failed:', error.message);
  if (error.status === 401) {
    console.error('Invalid credentials');
  } else if (error.status === 403) {
    console.error('Email not verified. Please check your email for OTP.');
  }
}
```

### Login with OAuth Provider

Supported providers: `'google'` (enabled by default), `'microsoft'`, and `'facebook'`. Enable Microsoft or Facebook in your app's authentication settings before using them.

```javascript
// Redirect to Google OAuth
base44.auth.loginWithProvider('google');

// Redirect to Google OAuth and return to current page after
base44.auth.loginWithProvider('google', window.location.href);

// Microsoft or Facebook (enable in app settings first)
base44.auth.loginWithProvider('microsoft');
base44.auth.loginWithProvider('facebook', '/dashboard');
```

### Get Current User

```javascript
try {
  const user = await base44.auth.me();

  if (user) {
    console.log('User ID:', user.id);
    console.log('Email:', user.email);
    console.log('Name:', user.full_name);
    console.log('Role:', user.role);
    console.log('Verified:', user.is_verified);
  } else {
    console.log('User not authenticated');
  }

} catch (error) {
  console.error('Failed to fetch user:', error.message);
  if (error.status === 401) {
    // Token expired or invalid - navigate to your custom login page
    navigate('/login');
  }
}
```

### Update User Profile

```javascript
try {
  const updatedUser = await base44.auth.updateMe({
    full_name: "John Doe",
    // Custom schema fields can be updated here
    phone: "+1234567890",
    preferences: { theme: "dark" }
  });

  console.log('Profile updated:', updatedUser);

} catch (error) {
  console.error('Profile update failed:', error.message);
  if (error.status === 400) {
    console.error('Invalid data provided');
  } else if (error.status === 401) {
    console.error('Authentication required');
    navigate('/login');
  }
}
```

### Check Authentication Status

```javascript
try {
  const isLoggedIn = await base44.auth.isAuthenticated();

  if (isLoggedIn) {
    // Show authenticated UI
    console.log('User is authenticated');
  } else {
    // Show login button
    console.log('User is not authenticated');
  }

} catch (error) {
  console.error('Failed to check authentication:', error.message);
  // On error, treat as not authenticated
}
```

### Logout

Logout redirects the user to the server-side logout endpoint (`/api/apps/auth/logout`) to clear HTTP-only cookies and the session, then redirects to the given URL (or the current page if omitted). Requires a browser environment.

```javascript
// Logout: clears session via server, then redirects to current page
base44.auth.logout();

// Logout and redirect to goodbye page after
base44.auth.logout("/goodbye");

// Logout and redirect to homepage
base44.auth.logout("/");
```

### Protected Route Pattern

```javascript
// Using a navigation function (e.g., React Router's useNavigate, Next.js router)
async function requireAuth(navigate) {
  try {
    const user = await base44.auth.me();

    if (!user) {
      // Navigate to your custom login page
      navigate('/login', { state: { returnTo: window.location.pathname } });
      return null;
    }

    return user;

  } catch (error) {
    console.error('Authentication check failed:', error.message);
    navigate('/login', { state: { returnTo: window.location.pathname } });
    return null;
  }
}

// Usage in your app
async function loadProtectedPage(navigate) {
  const user = await requireAuth(navigate);
  if (!user) {
    // Will navigate to login
    return;
  }

  // Continue with authenticated logic
  console.log('Welcome,', user.full_name);
}
```

### Set Authentication Token

```javascript
// SECURITY WARNING: Never hardcode tokens or expose them in client code
// Tokens should only be received from secure authentication flows

// Set token and save to localStorage (default)
base44.auth.setToken(receivedToken);

// Set token without saving to localStorage (temporary session)
base44.auth.setToken(receivedToken, false);

// Verify token was set
try {
  const isAuthenticated = await base44.auth.isAuthenticated();
  if (!isAuthenticated) {
    console.error('Token validation failed');
  }
} catch (error) {
  console.error('Failed to set token:', error.message);
}
```

### Invite User to Application

```javascript
try {
  // Note: Typically requires admin privileges
  const response = await base44.auth.inviteUser(
    "newuser@example.com",
    "user"  // or "admin"
  );

  console.log('Invitation sent successfully');

} catch (error) {
  console.error('Failed to invite user:', error.message);
  if (error.status === 403) {
    console.error('Insufficient permissions to invite users');
  } else if (error.status === 400) {
    console.error('Invalid email or role');
  }
}
```

### OTP Verification

```javascript
try {
  // Verify OTP code sent to user's email
  await base44.auth.verifyOtp({
    email: "user@example.com",
    otpCode: "123456"
  });

  console.log('OTP verified successfully');

} catch (error) {
  console.error('OTP verification failed:', error.message);
  if (error.status === 400) {
    console.error('Invalid or expired OTP code');
  } else if (error.status === 429) {
    console.error('Too many attempts. Please try again later.');
  }
}

// Resend OTP if needed
try {
  await base44.auth.resendOtp("user@example.com");
  console.log('OTP resent successfully');

} catch (error) {
  console.error('Failed to resend OTP:', error.message);
  if (error.status === 429) {
    console.error('Too many requests. Please wait before trying again.');
  }
}
```

### Password Reset Flow

```javascript
// Step 1: Request password reset
try {
  await base44.auth.resetPasswordRequest("user@example.com");
  console.log('Password reset email sent. Check your inbox.');

} catch (error) {
  console.error('Password reset request failed:', error.message);
  if (error.status === 429) {
    console.error('Too many requests. Please try again later.');
  }
  // Note: For security, don't reveal if email exists
}

// Step 2: Reset password with token from email
try {
  await base44.auth.resetPassword({
    resetToken: "token-from-email",
    newPassword: "newSecurePassword123"
  });

  console.log('Password reset successfully. You can now log in.');

} catch (error) {
  console.error('Password reset failed:', error.message);
  if (error.status === 400) {
    console.error('Invalid or expired reset token');
  } else if (error.status === 422) {
    console.error('Password does not meet requirements');
  }
}
```

### Change Password

```javascript
try {
  const currentUser = await base44.auth.me();

  if (!currentUser) {
    throw new Error('User must be authenticated to change password');
  }

  await base44.auth.changePassword({
    userId: currentUser.id,
    currentPassword: "oldPassword123",
    newPassword: "newSecurePassword456"
  });

  console.log('Password changed successfully');

} catch (error) {
  console.error('Password change failed:', error.message);
  if (error.status === 401) {
    console.error('Current password is incorrect');
  } else if (error.status === 422) {
    console.error('New password does not meet requirements');
  } else if (error.status === 403) {
    console.error('Not authorized to change this password');
  }
}
```

---

## Error Handling

### Common Error Scenarios

The auth module can throw various errors. Here are common scenarios and how to handle them:

#### Authentication Errors (401/403)
```javascript
try {
  const user = await base44.auth.me();
} catch (error) {
  if (error.status === 401) {
    // Token expired or invalid - navigate to your custom login page
    navigate('/login');
  } else if (error.status === 403) {
    // Email not verified or insufficient permissions
    console.error('Access denied:', error.message);
  }
}
```

#### Validation Errors (400/422)
```javascript
try {
  await base44.auth.register({
    email: "invalid-email",
    password: "weak"
  });
} catch (error) {
  if (error.status === 400) {
    console.error('Invalid input:', error.message);
    // Handle validation errors
  } else if (error.status === 422) {
    console.error('Data validation failed:', error.details);
  }
}
```

#### Rate Limiting (429)
```javascript
try {
  await base44.auth.resendOtp("user@example.com");
} catch (error) {
  if (error.status === 429) {
    console.error('Too many requests. Please wait before trying again.');
    // Show countdown or disable button temporarily
  }
}
```

#### Generic Error Handler
```javascript
function handleAuthError(error) {
  switch (error.status) {
    case 400:
      return 'Invalid input. Please check your data.';
    case 401:
      return 'Authentication required. Redirecting to login...';
    case 403:
      return 'Access denied. You may need to verify your email.';
    case 404:
      return 'Resource not found.';
    case 422:
      return 'Validation failed. Please check your input.';
    case 429:
      return 'Too many requests. Please try again later.';
    case 500:
      return 'Server error. Please try again.';
    default:
      return 'An unexpected error occurred.';
  }
}

// Usage
try {
  await base44.auth.loginViaEmailPassword(email, password);
} catch (error) {
  console.error(handleAuthError(error));
}
```

---

## Auth Providers

Configure authentication providers in your app dashboard:

### Available Providers

**Built-in (All Plans):**
- **Email/Password** - Default, always enabled
- **Google** - OAuth authentication
- **Microsoft** - OAuth authentication
- **Facebook** - OAuth authentication

**SSO Providers (Elite Plan):**
- **Okta**
- **Azure AD**
- **GitHub**

### Using OAuth Providers

- **Google** – enabled by default.
- **Microsoft** – enable in your app's authentication settings before use.
- **Facebook** – enable in your app's authentication settings before use.

```javascript
// Initiate OAuth login flow
base44.auth.loginWithProvider('google');

// Return to specific page after authentication
base44.auth.loginWithProvider('microsoft', '/dashboard');

// Supported values: 'google', 'microsoft', 'facebook'
```

---

## Environment Availability

| Environment | Availability | Notes |
|------------|--------------|-------|
| **Frontend** | ✅ Yes | All methods available |
| **Backend Functions** | ✅ Yes | Use `createClientFromRequest(req)` for authenticated client |
| **Service Role** | ❌ No | Auth methods not available in service role context |

### Frontend Usage
```javascript
// Standard browser usage
const user = await base44.auth.me();
```

### Backend Functions Usage
```javascript
import { createClientFromRequest } from "@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);

  // Get user from request context
  const user = await base44.auth.me();

  // User operations here...
  return Response.json({ user });
});
```

---

## App Visibility

Control who can access your app in the app settings:

### Public Apps
- No login required for basic access
- Users can view public content without authentication
- Authenticated users get additional features/data

### Private Apps
- Login required to access any content
- Unauthenticated users are automatically redirected to login
- All content is protected by default

---

## Limitations

### Authentication UI Options
- **Recommended:** Build custom login/signup UI using `loginViaEmailPassword()` and `loginWithProvider()` for full control over user experience and branding
- **Alternative:** `redirectToLogin()` uses Base44's hosted authentication pages with limited customization

### Hosted Login (via redirectToLogin)
- `redirectToLogin()` shows both login and signup options on the same page
- No separate `redirectToSignup()` method
- Users can switch between login/signup on the hosted page
- ⚠️ **Note:** Prefer building custom login UI for better user experience

### Password Requirements
- Minimum length and complexity requirements enforced
- Requirements not exposed via API
- Validation errors returned when requirements not met

### Rate Limiting
- OTP requests are rate-limited to prevent abuse
- Password reset requests are rate-limited
- Login attempts may be rate-limited with Turnstile protection

### Token Management
- JWTs are automatically stored in localStorage by default
- Token expiration and refresh not exposed in API
- Call `me()` or `isAuthenticated()` to verify token validity

---

## Best Practices

### 1. Always Handle Errors
```javascript
try {
  await base44.auth.loginViaEmailPassword(email, password);
} catch (error) {
  // Always handle authentication errors
  console.error('Login failed:', error.message);
}
```

### 2. Verify Authentication Before Protected Actions
```javascript
const user = await requireAuth();
if (!user) return; // Will redirect to login
// Proceed with authenticated action
```

### 3. Use Type Safety with TypeScript
```typescript
import type { User, LoginResponse } from '@base44/sdk';

const user: User = await base44.auth.me();
const response: LoginResponse = await base44.auth.loginViaEmailPassword(email, password);
```

### 4. Don't Hardcode Credentials
```javascript
// ❌ BAD
base44.auth.setToken("hardcoded-token-here");

// ✅ GOOD
const token = await secureAuthFlow();
base44.auth.setToken(token);
```

### 5. Provide User Feedback
```javascript
try {
  await base44.auth.register(params);
  showSuccessMessage('Registration successful! Check your email for verification code.');
} catch (error) {
  showErrorMessage('Registration failed: ' + error.message);
}
```

### 6. Handle Token Expiration Gracefully
```javascript
try {
  const user = await base44.auth.me();
} catch (error) {
  if (error.status === 401) {
    // Clear local state and navigate to login
    localStorage.clear();
    navigate('/login');
  }
}
```

### 7. Build Custom Login UI (Recommended)
```javascript
// ✅ RECOMMENDED - Custom login form with direct methods
const handleLogin = async (email, password) => {
  try {
    const { user } = await base44.auth.loginViaEmailPassword(email, password);
    navigate('/dashboard');
  } catch (error) {
    setError(error.message);
  }
};

const handleGoogleLogin = () => {
  base44.auth.loginWithProvider('google', '/dashboard');
};

// ❌ AVOID - Redirecting to hosted login page
// base44.auth.redirectToLogin(window.location.href);
```
