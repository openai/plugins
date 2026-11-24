# Hyperdrive troubleshooting

Start with the actual error and the affected configuration. Fetch [Troubleshoot and debug](https://developers.cloudflare.com/hyperdrive/observability/troubleshooting/index.md) for current error codes and diagnosis rather than guessing from a generic connection failure.

| Symptom | What to inspect and where to read |
|---------|----------------------------------|
| Connection refused or authentication failure | Check origin reachability and credentials using [troubleshooting](https://developers.cloudflare.com/hyperdrive/observability/troubleshooting/index.md) and [firewall/networking configuration](https://developers.cloudflare.com/hyperdrive/configuration/firewall-and-networking-configuration/index.md). |
| Private database or TLS failure | Follow the selected [Workers VPC](https://developers.cloudflare.com/hyperdrive/configuration/connect-to-private-database-vpc/index.md) or [Tunnel/Access](https://developers.cloudflare.com/hyperdrive/configuration/connect-to-private-database/index.md) path and its certificate prerequisites; see [SSL/TLS configuration](https://developers.cloudflare.com/hyperdrive/configuration/tls-ssl-certificates-for-hyperdrive/index.md). |
| Pool exhaustion or too many connections | Distinguish client connection lifetime from origin pool capacity. Read [connection lifecycle](https://developers.cloudflare.com/hyperdrive/concepts/connection-lifecycle/index.md), [pool tuning](https://developers.cloudflare.com/hyperdrive/configuration/tune-connection-pool/index.md), and [limits](https://developers.cloudflare.com/hyperdrive/platform/limits/index.md). |
| Query timeout | Check the current [limits](https://developers.cloudflare.com/hyperdrive/platform/limits/index.md) and [metrics](https://developers.cloudflare.com/hyperdrive/observability/metrics/index.md) before changing query or transaction design. |
| Stale reads or unexpectedly uncached queries | Inspect the binding's cache configuration and query eligibility in [query caching](https://developers.cloudflare.com/hyperdrive/concepts/query-caching/index.md). Writes do not purge cached reads; do not treat prepared-statement settings as cache controls. |
| Slow multi-query requests | Inspect [metrics](https://developers.cloudflare.com/hyperdrive/observability/metrics/index.md) and check whether Worker placement matches the regional database. Follow [placement setup](./configuration.md#place-compute-near-the-database); a Hyperdrive binding alone does not place compute near the origin. |
| Local connection failure, ignored environment variable, or absent cache behavior | Check binding names, local connection overrides, precedence, and remote testing in [local development](https://developers.cloudflare.com/hyperdrive/configuration/local-development/index.md). |
| Unsupported driver or SQL feature | Check [supported databases and features](https://developers.cloudflare.com/hyperdrive/reference/supported-databases-and-features/index.md) and the selected [driver guide](./api.md). |

## Capacity and changes

Retrieve [limits](https://developers.cloudflare.com/hyperdrive/platform/limits/index.md) and [pricing](https://developers.cloudflare.com/hyperdrive/platform/pricing/index.md) for current plan allowances, connection and query bounds, and limit-increase guidance. Check [release notes](https://developers.cloudflare.com/hyperdrive/platform/release-notes/index.md) when behavior changes after an upgrade.

See [configuration.md](./configuration.md) to change a configuration and [patterns.md](./patterns.md) to revisit freshness or connection decisions.
