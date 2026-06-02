---
name: forms-implementer
description: "Implements contact, lead, and signup forms via @wix/forms. Scopes: seed, components, pages. Extends references/shared/IMPLEMENTER.md."
---

# Forms Implementer

Extends `references/shared/IMPLEMENTER.md`. Read that file first for phase routing, REST auth + doc lookups, prompt-inlined inputs (no site.json reads), return contract, style conventions, and common failure modes.

## Scope routing

| Scope | Phase | Reference |
|-------|-------|-----------|
| `seed` | Seed (Forms app install + form creation + postSubmissionTriggers PATCH) | `../astro/forms/CONTACT_FORM.md` (§ Form Setup) |
| `components` | Components (ContactForm.tsx React island) | `../astro/forms/CONTACT_FORM.md` (§ React island) |
| `pages` | Pages (contact.astro wire with formId from seeded data) | `../astro/forms/CONTACT_FORM.md` (§ Page wiring) |

## Files this vertical creates / contributes

See `<SKILL_ROOT>/references/verticals/forms.md` frontmatter.

## Form purpose variants

The `seed` scope adapts field selection based on business purpose from the functional plan:

| Purpose | Fields | Layout |
|---------|--------|--------|
| Waitlist / newsletter | EMAIL + SUBMIT | Single column |
| Lead capture | FIRST_NAME + EMAIL + SUBMIT | Single column |
| Contact (full) | FIRST_NAME + LAST_NAME + EMAIL + PHONE + MESSAGE + SUBMIT | First+last side-by-side, rest stacked |
| Registration | FIRST_NAME + LAST_NAME + EMAIL + custom | Single column |

## Forms-specific failure modes

| Wrong | Right |
|---|---|
| Skip `postSubmissionTriggers` PATCH after form creation | Always PATCH — the POST silently drops triggers; without them, submissions are silently lost (no CRM Contact created) |
| Include triggers in POST body and assume it worked | POST drops `postSubmissionTriggers`; always follow up with PATCH |
| Fall back to hardcoded fields on `UNSUPPORTED_FORM_NAMESPACE` | Wait 10s and retry up to 3 times — namespace propagation delay after Forms app install |
| Skip `auth.elevate` when listing forms | `listForms` requires elevated permissions |
| Submit forms from server-side code | Form submission must be client-side (React island with `client:load`) |
| Detect textarea by `componentType === "TEXT_AREA"` | Check `identifier === "TEXT_AREA"` or `target === "message"` |
| Hardcode form field IDs or form ID | Use `forms.listForms("wix.form_app.form")` with `auth.elevate` for runtime discovery |