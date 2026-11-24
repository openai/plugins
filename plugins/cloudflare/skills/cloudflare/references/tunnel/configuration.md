# Tunnel Configuration

Read the documentation for the existing management mode before changing routes or credentials.

| Task | Documentation |
| --- | --- |
| Configure remotely-managed tunnels | [Setup](https://developers.cloudflare.com/tunnel/get-started/index.md) |
| Edit local ingress rules, service mappings, and validate matching | [Configuration file](https://developers.cloudflare.com/tunnel/features/locally-managed-tunnels/configuration-file/index.md) |
| Configure origin TLS, HTTP, and connection behavior | [Origin parameters](https://developers.cloudflare.com/tunnel/reference/origin-parameters/index.md) |
| Configure runtime flags and service arguments | [Run parameters](https://developers.cloudflare.com/tunnel/reference/run-parameters/index.md) |
| Manage remote tunnel tokens and rotation | [Tunnel tokens](https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/index.md) |
| Choose service protocols and DNS routing | [Routing](https://developers.cloudflare.com/tunnel/concepts/routing/index.md) |

Confirm which configuration source the running process uses, then review the routes affected by the change. Match origin settings to the actual service and certificate rather than copying settings from a different deployment. See [networking.md](./networking.md) for connectivity and [patterns.md](./patterns.md) for rollout decisions.
