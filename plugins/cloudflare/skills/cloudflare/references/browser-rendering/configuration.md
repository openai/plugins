# Browser Run Configuration

Check the project's runtime, installed client and Wrangler versions, and compatibility date before adapting setup instructions. Cloudflare's packages for Workers and standard clients connecting over CDP have different setup requirements.

| Task | Documentation |
|------|---------------|
| Start a project or configure REST authentication | [Get started](https://developers.cloudflare.com/browser-run/get-started/index.md) — Quick Actions and browser session setup |
| Configure a Worker or choose a development mode | [Wrangler reference](https://developers.cloudflare.com/browser-run/reference/wrangler/index.md) — browser bindings, compatibility requirements, and local/remote development |
| Install or update a Workers browser client | [Puppeteer](https://developers.cloudflare.com/browser-run/puppeteer/index.md) or [Playwright](https://developers.cloudflare.com/browser-run/playwright/index.md) — package-specific setup and supported versions |
| Connect from a script, server, or CI outside Workers | [CDP](https://developers.cloudflare.com/browser-run/cdp/index.md) — authentication and client integration guides |

Development support depends on the selected interface. Follow its current guidance rather than applying one remote-mode requirement to all Browser Run workflows.
