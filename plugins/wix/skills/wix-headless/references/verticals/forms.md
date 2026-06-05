---
name: forms
description: "Forms — contact, lead capture, or newsletter signup with CRM integration."
triggers: ["contact form", "lead form", "signup form", "waitlist", "registration", "get in touch", "inquiry", "feedback"]

features:
  - name: "Contact form"
    description: "Dynamic form powered by @wix/forms with server-side schema discovery and client-side submission. Submissions create CRM contacts automatically."

apps:
  - name: "Wix Forms"
    appDefId: "225dd912-7dea-4738-8688-4b8c6955ffc2"

routes:
  - route: "/contact"

disabled: false
---

# Forms Pack

Loaded when the user's prompt mentions forms, contact pages, inquiries, or signups.

> **Discovery contract.** Phase 1 reads only the frontmatter above. Phase 2+ implementation (form creation, field selection per purpose, submission triggers, page composition) lives in an upstream skill plus this skill's own `templates/forms/` + `references/forms/INSTRUCTIONS.md`:
>
> - `@skills/wix-manage` ships the recipe — `references/forms/create-form.md`.