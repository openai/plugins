# Public Equity Investing Source Category Runtime

Use `skills/user-context/plugin-author-config/source-category-config.json` from the plugin root as the static catalog of Public Equity Investing source categories, labels, and preference hints. The catalog is a routing aid, not proof that a plugin, app, connector, or manual source is usable for the current user.

## Ownership

- `.app.json` declares app and connector dependencies the plugin can request. It does not prove installation, authorization, preference, or readability.
- `skills/user-context/plugin-author-config/source-category-config.json` owns static category ids, labels, and preferred plugins or apps.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/user-context.md` owns durable user-approved source preferences, source-of-truth pointers, and "do not use" rules.
- `$CODEX_HOME/state/plugins/{marketplace_id}/{plugin_id}/onboarding-state.json` owns operational setup confirmations under `connector_confirmation`.
- Do not create, read, or migrate `category-state.json`.

## Explicit Inspection

The inspection helper is a reader for explicit saved-context, setup-status, or onboarding turns. Its `source_category_plan` returns static routing hints, saved setup confirmations, and unresolved setup gaps. It must not inspect apps, connectors, plugins, or `.app.json`; choose a plugin, app, connector, or manual route; claim readiness; perform proof reads; or write state.

## Explicit Setup

Source route selection belongs in the user-approved Source Setup onboarding step or an explicit source-setup turn. Do not inspect setup surfaces before the user opts in, and do not run broad setup merely because an ordinary workflow needs evidence.

During one setup pass:

1. Start from unresolved categories in the inspection helper's `source_category_plan`.
2. Read the session's available skills, apps, connectors, and installable plugin list when those surfaces are exposed. Load `.app.json` only to map preferred app names to declared connector ids and semantic categories.
3. Prefer a related installed plugin with visible plugin-owned skill or tool surface, then an installable related plugin, then an exposed app or connector, then manual or exported context.
4. Ask before installing or authorizing anything. Ask the user to choose only when multiple plausible routes tie, an installable plugin needs approval, no suitable source is exposed, or IT/admin help may be required.
5. Write the selected operational route under `onboarding-state.json` `connector_confirmation`. Do not write source setup state to `user-context.md`.

A candidate is related when its `name` or `display_name` matches a preferred plugin or app, its `id` clearly names the preferred plugin or app, its `app_connector_ids` intersects the `.app.json` ids for a category preferred app, or its `description` clearly names the same provider or category and no better preferred match exists.

If setup finds an installed app or connector and also finds a related plugin candidate, prefer the plugin because plugin-owned skills and tools can add workflow support. Keep the app or connector route as fallback if the user defers plugin installation or install visibility is pending.

Use `status: active` only when the selected plugin, app, or connector surface is exposed clearly enough to attempt later. This is setup-only evidence, not a readiness claim. Use `needs_confirmation`, `missing`, `deferred`, `skipped`, or `unavailable` when the route is not active. Include `source_kind` and compact plugin, app, connector, or manual route details when known. Do not guess connector ids or infer active status from `.app.json`.

Do not mark a newly installed plugin route as active until its plugin-owned skill or tool surface is visible. If installation succeeds but skills or tools are not visible until the next turn or session refresh, write `needs_confirmation` or `deferred`, not `active`, and ask the user to continue after refresh.

Do not perform connector reads merely to prove setup. Install or connect confirmed candidates one at a time using the current install/connect UI available in the session, such as `request_plugin_install` when it is exposed with a concrete installable plugin id. Do not guess plugin ids, connector ids, tool ids, or active status, and do not call install/connect tools in parallel with other setup actions.

## Workflow Use

Attempt actual connector reads only when the active workflow needs the source. Before telling the user that a source is ready, use the smallest safe native read-only probe for that source. A successful read is evidence for that run only, not durable connector-readiness state. When a source is unavailable, continue from pasted, uploaded, or exported context when the workflow can still produce a useful limited answer.
