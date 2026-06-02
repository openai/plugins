# Users Module

Invite users to the app via `base44.users`.

## Contents
- [Methods](#methods)
- [Examples](#examples) (Invite User)
- [Roles](#roles)
- [Notes](#notes)

## Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `inviteUser(user_email, role)` | `Promise<any>` | Invite a user to the app |

## Examples

### Invite User

```javascript
// Invite a user with "user" role
await base44.users.inviteUser("newuser@example.com", "user");

// Invite an admin
await base44.users.inviteUser("admin@example.com", "admin");
```

### Invite Multiple Users

```javascript
const usersToInvite = [
  { email: "user1@example.com", role: "user" },
  { email: "user2@example.com", role: "user" },
  { email: "manager@example.com", role: "admin" }
];

for (const user of usersToInvite) {
  await base44.users.inviteUser(user.email, user.role);
  console.log(`Invited ${user.email} as ${user.role}`);
}
```

## Roles

The `role` parameter must be one of:

| Role | Description |
|------|-------------|
| `"user"` | Standard user with default permissions |
| `"admin"` | Administrator with elevated permissions |

**Note:** Only `"user"` and `"admin"` are valid role values. An error will be thrown if you pass any other value.

## Notes

- **Email invitation**: The invited user receives an email with a link to join the app
- **Duplicate handling**: Inviting an existing user will re-send the invitation
- **Also available in auth**: `base44.auth.inviteUser()` provides the same functionality
- **Role validation**: Only `"user"` or `"admin"` are accepted

```javascript
// These are equivalent:
await base44.users.inviteUser("newuser@example.com", "user");
await base44.auth.inviteUser("newuser@example.com", "user");
```

## Type Definitions

```typescript
/** Users module for inviting users to the app. */
interface UsersModule {
  /**
   * Invite a user to the application.
   * @param user_email - User's email address.
   * @param role - User's role ('user' or 'admin').
   * @returns Promise resolving when the invitation is sent.
   * @throws Error if role is not 'user' or 'admin'.
   */
  inviteUser(user_email: string, role: "user" | "admin"): Promise<any>;
}
```
