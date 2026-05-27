# shopify

## 1.2.2

### Patch Changes

- 716d22b: `shopify-app-store-review` skill now points the agent at the canonical shopify.dev requirements page (https://shopify.dev/docs/apps/launch/app-store-review/app-store-ai-self-review-requirements) instead of carrying a hand-maintained inline copy, and adds 5.x category-specific requirements. Output format and status taxonomy are unchanged. (Retroactive changeset for #722, which merged without one.)
- f8d1abd: Disclose default-on telemetry more clearly in mirrored plugin install surfaces and generated skill privacy notices, including the opt-out environment variable. Clarify that validation and search scripts report specific request data to `shopify.dev/mcp/usage`.
- 716d22b: Skill validate scripts (`validate_graphql`, `validate_components`, `validate_functions`, `validate_theme`) now emit the same markdown summary the MCP `validate_*_codeblocks` tools return, including artifact ID and revision lines. The id is auto-minted when not supplied and echoed back to the agent, matching the MCP behavior so retries can chain across revisions on either surface.

## 1.2.1

### Patch Changes

- aab0a72: `shopify-app-store-review` skill now points the agent at the canonical shopify.dev requirements page (https://shopify.dev/docs/apps/launch/app-store-review/app-store-ai-self-review-requirements) instead of carrying a hand-maintained inline copy, and adds 5.x category-specific requirements. Output format and status taxonomy are unchanged. (Retroactive changeset for #722, which merged without one.)

## 1.2.0

### Minor Changes

- d7608c7: Changeset to force a new release
