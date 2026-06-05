---
name: cms
description: "Content pages — Home, About, FAQ managed via Wix CMS. Always loaded."
triggers: []   # not trigger-based — always loaded (every site needs About/FAQ)

features:
  - name: "About (CMS-based)"
    description: "Tell your brand story with images and rich text. Editable from the Wix dashboard's Content Manager."
  - name: "FAQ (CMS-based)"
    description: "Common questions and answers about your products. Managed from the dashboard's Content Manager."

apps: []   # CMS is built-in, no app install

routes:
  - route: "/"
  - route: "/about"
  - route: "/faq"

disabled: false
---

# CMS Pack

Always loaded. Provides Home + About + FAQ content pages editable from the Wix dashboard's Content Manager.

> **Discovery contract.** Phase 1 reads only the frontmatter above. Phase 2+ implementation (collection schemas, item seeding, page composition) lives in an upstream skill plus this skill's own `templates/cms/` + `references/cms/INSTRUCTIONS.md`:
>
> - `@skills/wix-manage` ships the recipes — `references/cms/cms-schema-management.md`, `cms-data-items-crud.md`, `cms-references-and-relationships.md`.
>
> Collection names like `about-content` / `faq` are an implementation detail the seeder picks at run time — they are not pre-approved by the user in the discovery plan.