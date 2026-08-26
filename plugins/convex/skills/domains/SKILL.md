---
name: domains
description: "Wire a domain the user ALREADY OWNS (GoDaddy/Namecheap/Cloudflare/…) to their Convex app: exact DNS records, custom-domain attachment, auth-origin rebind. TRIGGER when the user owns a domain and wants it pointing at their app ('point my domain at this', 'use my own domain', 'set up example.com'). Never asks for registrar credentials."
license: Apache-2.0
---

# Custom domain with your own provider ($domains)

Point a domain the user already owns at their Convex app. No purchase, no
registrar credentials — you give the user the exact records to create themselves.

## Procedure

1. **Identify the target:** the published site host (for static hosting) or the
   deployment's HTTP actions URL (`npx convex env get CONVEX_SITE_URL` or the
   dashboard).
2. **Give the exact DNS records** to create at THEIR registrar: the CNAME (or
   A/ALIAS at the apex) plus the TXT verification record — concrete host/value
   strings, not placeholders.
3. **Attach the custom domain** on Convex (dashboard → deployment → Custom
   Domains, or the CLI) and wait for verification. DNS propagation can take
   minutes to hours — tell the user, don't poll forever.
4. **If the app uses auth** (passkeys/OAuth), rebind the auth origin
   (`SITE_URL` / `RP_ID` / `ORIGIN` env vars) to the new domain and re-deploy —
   otherwise sign-in breaks on the new domain.
5. **Verify:** the domain serves the app over HTTPS, including the apex → www
   redirect if configured.

## Rules

- Never ask for registrar credentials — the user creates the records.
- Always include the TXT verification record, not just the CNAME.
- Rebinding the domain changes the auth origin — re-deploy after, or sign-in breaks.
