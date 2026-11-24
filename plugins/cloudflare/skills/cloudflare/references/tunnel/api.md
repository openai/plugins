# Tunnel APIs and Commands

Fetch current operation schemas, permissions, and examples before automating tunnel changes.

| Task | Documentation |
| --- | --- |
| Create a tunnel, configure ingress, and create application DNS through the API | [Setup](https://developers.cloudflare.com/tunnel/get-started/index.md) |
| List existing tunnels and inspect response fields | [List Cloudflare Tunnels API](https://developers.cloudflare.com/api/resources/zero_trust/subresources/tunnels/subresources/cloudflared/methods/list/index.md) |
| Retrieve and rotate tunnel tokens | [Tunnel tokens](https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/index.md) |
| Manage local tunnels using the CLI | [Useful commands](https://developers.cloudflare.com/tunnel/features/locally-managed-tunnels/tunnel-useful-commands/index.md) |
| Configure public DNS and routing behavior | [Routing](https://developers.cloudflare.com/tunnel/concepts/routing/index.md) |
| Select private-network integration and its setup guide | [Integrations](https://developers.cloudflare.com/tunnel/integrations/index.md) |

Identify the account, tunnel ID, and management mode before a write. Review existing routes before replacing configuration; distinguish tunnel lifecycle operations from DNS changes. Use [patterns.md](./patterns.md) when infrastructure as code owns these resources.
