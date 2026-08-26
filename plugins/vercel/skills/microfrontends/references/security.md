# Managing Microfrontends Security

> Source: [Vercel Docs — Managing microfrontends security](https://vercel.com/docs/microfrontends/managing-microfrontends/security)

How [Deployment Protection](https://vercel.com/docs/deployment-protection) and [Vercel Firewall](https://vercel.com/docs/vercel-firewall) apply to each microfrontend application.

## Deployment Protection and microfrontends

Each URL is protected by the [Deployment Protection](https://vercel.com/docs/security/deployment-protection) settings of the project it belongs to, so protection for the microfrontend experience as a whole is determined by the **default application**:

- Requests to a **microfrontend host** (a domain of the default application) are verified **only** by the **default application's** Deployment Protection.
- Requests **directly to a child application** (a child domain) are verified **only** by that **child application's** Deployment Protection.

This applies to all [protection methods](https://vercel.com/docs/security/deployment-protection/methods-to-protect-deployments) and [bypass methods](https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection), including [Vercel Authentication](https://vercel.com/docs/security/deployment-protection/methods-to-protect-deployments/vercel-authentication), [Password Protection](https://vercel.com/docs/security/deployment-protection/methods-to-protect-deployments/password-protection), [Trusted IPs](https://vercel.com/docs/security/deployment-protection/methods-to-protect-deployments/trusted-ips), [Shareable Links](https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection/sharable-links), [Protection Bypass for Automation](https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation), [Deployment Protection Exceptions](https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection/deployment-protection-exceptions), and [OPTIONS Allowlist](https://vercel.com/docs/security/deployment-protection/methods-to-bypass-deployment-protection/options-allowlist).

### Recommended configuration

- **Default app**: use [Standard Protection](https://vercel.com/docs/security/deployment-protection) so end users can reach the microfrontend through the default app's URL.
- **Child apps**: enable protection for **all deployments** so they aren't directly accessible. Child content is served through the default app's URL.

This works because Vercel routes to child apps within a single request at the network layer (see [Path Routing](https://vercel.com/docs/microfrontends/path-routing)) — not a rewrite that issues a separate request to the child's URL. Deployment protection on a child app therefore applies only when the child's URL is accessed directly.

## Vercel Firewall and microfrontends

- The [platform-wide firewall](https://vercel.com/docs/vercel-firewall#platform-wide-firewall) is applied to all requests.
- The customizable [Web Application Firewall (WAF)](https://vercel.com/docs/vercel-firewall/vercel-waf) of both the default application and the relevant child application is applied to a request:
  - Requests to a **microfrontend host** are verified by the **default application's** WAF; requests to child paths are **additionally** verified by the **child application's** WAF.
  - Requests **directly to a child application** are verified **only** by the **child application's** WAF.

This covers the entire [Vercel WAF](https://vercel.com/docs/vercel-firewall/vercel-waf), including [Custom Rules](https://vercel.com/docs/vercel-firewall/vercel-waf/custom-rules), [IP Blocking](https://vercel.com/docs/vercel-firewall/vercel-waf/ip-blocking), [WAF Managed Rulesets](https://vercel.com/docs/vercel-firewall/vercel-waf/managed-rulesets), and [Attack Challenge Mode](https://vercel.com/docs/vercel-firewall/attack-challenge-mode).

### Managing the WAF

- A rule that applies to **all** requests to a microfrontend → use the **default application's** WAF.
- A rule that applies **only** to a child application's paths → use the **child project's** WAF.
