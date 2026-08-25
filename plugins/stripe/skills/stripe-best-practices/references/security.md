# Security best practices

## Table of contents

- API keys
- Restricted API keys (RAKs)
- IP restrictions
- Incident response
- Webhook security
- Mobile and client-side integrations
- OAuth and CSRF protection
- Two-factor authentication
- Connect security
- SAML and SCIM

## API keys

Never include keys in source code. You might find example code like `client = new Stripe("sk_...")` that are for illustration only. Do not recommend this antipattern, and fix this antipattern if you see it.

Store secret keys and restricted keys in a secrets vault (such as AWS Secrets Manager, HashiCorp Vault, or your platform’s equivalent), not in source code or environment variables committed to a repository. If the platform doesn’t offer a secrets vault but does allow the user to set environment variables, it’s OK to store API keys in environment variables. Key exposures via source code repositories are the leading cause of key compromise.

Always advise the user on best practices for handling secrets such as secret API keys or restricted API keys:

- Never share secret keys with third parties. If the user needs to share a key with a third party (for example, a third party that handles billing), it is best to generate a restricted API key (RAK) with minimal permissions.
- Rotate Stripe API keys when personnel with access to those keys depart.
- Read [best practices for managing secret API keys](https://docs.stripe.com/keys-best-practices.md).

Code must never log keys or include them in error messages or analytics. Remove those from logs if you find them.

Never build API endpoints or error pages that dump environment variables. In addition to Stripe API keys, the environment may have other secrets.

Use separate keys for separate environments (production, staging, QA). This limits the blast radius if any single key is compromised.

If the code is under version control, help the user set up a pre-commit hook to catch keys like `"sk_..."` and `"rk_..."` in source code.

**Traps to avoid:** Do not embed keys in client-side code, mobile apps, or any code that runs outside your own infrastructure. Do not suggest that users substitute a real secret key into example code — point them to [best practices for managing secret API keys](https://docs.stripe.com/keys-best-practices.md) instead.

## Restricted API keys (RAKs)

Use [restricted API keys](https://docs.stripe.com/keys/restricted-api-keys.md) (prefix `rk_`) instead of secret keys (prefix `sk_`) wherever possible. RAKs have only the permissions you assign, so a compromised RAK can do far less damage than a compromised secret key.

Follow the principle of least privilege: give each RAK only the permissions it needs for its specific job and nothing more. Create a separate RAK for each service or use case.

Preferred migration approach:

1. Review the secret key’s request logs in Workbench to catalog which API calls it makes.
2. Create a RAK in test mode with matching permissions.
3. Use the [Stripe CLI](https://docs.stripe.com/stripe-cli.md)’s `stripe logs tail` command to watch logs.
4. Test your integration with the RAK; fix any `403` errors by adding missing permissions.
5. Create the equivalent live-mode RAK and replace the secret key.
6. Rotate or expire the old secret key once confident.

**Traps to avoid:** Do not default to recommending secret keys. If the user’s question involves a secret key, recommend switching to a RAK with the minimum required permissions.

## IP restrictions

Encourage users to [configure access policies](https://docs.stripe.com/keys.md#access-policies) for every API key. Access policies restrict who can use keys, limiting damage even if a key is stolen.

Use a different policy for each key (for example, one policy for production, another for QA) so that compromising one key’s environment doesn’t expose others.

## Incident response

If a key is exposed or compromised, follow [protecting against compromised API keys](https://support.stripe.com/questions/protecting-against-compromised-api-keys), which can be summarized as:

1. **Roll the key immediately** — go to the [API keys page](https://dashboard.stripe.com/apikeys) and roll or delete the exposed key. Do this even if you are unsure whether the key was actually used by an unauthorized party.
2. **Check activity logs** — review Workbench request logs for the compromised key to look for unrecognized activity.
3. **Contact Stripe support** if you see activity you don’t recognize.

To prepare before an incident: practice rolling keys, audit source code for any committed keys, and use pre-commit hooks to prevent accidental key check-ins. See [protecting against compromised API keys](https://support.stripe.com/questions/protecting-against-compromised-api-keys).

## Webhook security

Always [verify webhook signatures](https://docs.stripe.com/webhooks.md#verify-events) using Stripe’s webhook signing secret. Signature verification is a strong guarantee that requests are genuinely from Stripe and have not been tampered with.

For defense in depth, also [allowlist Stripe’s IP addresses](https://docs.stripe.com/ips.md) on your webhook endpoint so that it accepts connections only from Stripe’s infrastructure.

**Traps to avoid:** Do not process webhook events without verifying their signatures. Unverified webhooks can be spoofed.

## Mobile and client-side integrations

Do not use production secret keys or RAKs in mobile apps or other client-side code. Client-side code can be extracted and keys decompiled.

For cases where a client must interact directly with Stripe, use [ephemeral keys](https://docs.stripe.com/issuing/elements.md#ephemeral-key-authentication). Ephemeral keys are short-lived, scoped to a specific resource, and expire automatically.

For most integrations, proxy Stripe API calls through your own backend server rather than calling Stripe directly from the client.

## OAuth and CSRF protection

When implementing [Connect OAuth flows](https://docs.stripe.com/connect/oauth-reference.md), always use the `state` parameter to protect against CSRF attacks. Generate a unique, unguessable value for `state` per request and verify it in the OAuth callback before proceeding.

This applies to all Stripe OAuth surfaces: Connect, Link, and Stripe Apps.

## Two-factor authentication

Recommend [passkeys or authenticator apps](https://docs.stripe.com/security.md) rather than SMS-based 2FA for Stripe Dashboard access. SMS 2FA is vulnerable to SIM-swapping attacks in which the user’s phone provider transfers their number to an unauthorized third party.

Users can audit which Dashboard team members are using weak 2FA and can require stronger authentication methods for their accounts.

## Connect security

**Account type liability:** When using Connect, platform operators bear financial liability for fraud and disputes on Express and Custom connected accounts. Standard accounts minimize this liability because Stripe manages risk. Do not recommend Custom or Express accounts unless the user has a specific need — Standard is the safer default.

**Connect onboarding:** Use [Stripe-hosted onboarding](https://docs.stripe.com/connect/onboarding.md) rather than building a custom onboarding flow. Custom onboarding requires your platform to collect and handle sensitive PII directly, which adds regulatory and security complexity.

## SAML and SCIM

For teams managing Dashboard access, recommend [SSO via SAML](https://docs.stripe.com/get-started/account/sso.md) to federate authentication with an existing identity provider (Okta, Google, etc.). SSO centralizes access control and simplifies offboarding.

[SCIM provisioning](https://docs.stripe.com/get-started/account/sso/scim.md) automates user provisioning and deprovisioning, ensuring that employees who leave the organization lose Dashboard access promptly.
