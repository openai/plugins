# Linear

The maintained release source for Linear's existing app-backed plugin. Version
`5.0.1` contains the app connector, hosted MCP configuration, metadata, and icon,
with no bundled skills.

## Migration baseline

This package uses the verified public `5.0.0` payload recorded in the
[alpha inventory](../../../oai-maintained-plugins-alpha/no-skills-variants.json)
for release `pluginrel_a301e34c49108191869e88fecd431741`, via the already
skill-free [Linear alpha](../../../oai-maintained-plugins-alpha/plugins/linear/).
The alpha's app manifest, MCP configuration, and text SVG icon are preserved
byte-for-byte. Its remaining manifest metadata is unchanged except for the
stable version and repository URL.

The registered `openai/plugins` source was still `0.0.3` at
`11c74d6ba24d3a6d48f54a194cd00ef3beea18f9`; copying that source would regress
the recorded public metadata. The catalog retains that source's `AVAILABLE`
installation policy, `ON_INSTALL` authentication, and `Productivity` category.

## Release identity

- Plugin: `plugin_asdk_app_69a089a326dc8191b32a3f2553f5be2c`
- Canonical app: `asdk_app_69a089a326dc8191b32a3f2553f5be2c`
- Source: `openai/openai/chatgpt/oai-maintained-plugins/linear`

The registry moves the source mapping without creating a new plugin or app.
The other repository and experimental alpha remain unchanged. Before a human
publishes this version, re-read the production record and verify its current
version and destination policies against this snapshot, following the
[maintainer guide](../../docs/maintainer-guide.md#publish-one-plugin).
This source migration does not publish a release or change live rollout policy.
