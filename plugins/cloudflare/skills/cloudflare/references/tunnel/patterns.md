# Tunnel Deployment Decisions

Choose deployment ownership and availability requirements before adapting an example.

| Task | Documentation |
| --- | --- |
| Install a remotely-managed tunnel on a host or in Docker | [Setup](https://developers.cloudflare.com/tunnel/get-started/index.md) |
| Deploy cloudflared inside a cluster | [Kubernetes](https://developers.cloudflare.com/tunnel/guides/kubernetes/index.md) |
| Manage tunnel infrastructure declaratively | [Terraform](https://developers.cloudflare.com/tunnel/guides/terraform/index.md) |
| Deploy replicas and check current capacity | [Replicas and high availability](https://developers.cloudflare.com/tunnel/configuration/index.md#replicas-and-high-availability) |
| Choose redundancy or explicit traffic steering | [Routing](https://developers.cloudflare.com/tunnel/concepts/routing/index.md) |
| Plan upgrades for the existing installation method | [Update cloudflared](https://developers.cloudflare.com/tunnel/guides/update-cloudflared/index.md) |
| Add authentication or private connectivity | [Integrations](https://developers.cloudflare.com/tunnel/integrations/index.md) |

Establish which service each replica can reach and how configuration and credentials reach each host. Decide whether simple redundancy meets the requirement or whether health-based routing needs a load balancer. Verify replacement replicas before retiring existing ones, and include application-level checks in the rollout. See [api.md](./api.md) for programmatic operations.
