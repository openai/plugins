# Daloopa Plugin for Codex and ChatGPT Skills

Financial analysis skills powered by [Daloopa](https://daloopa.com) institutional-grade financial data. This repo packages the Daloopa analyst workflows for Codex plugin use and ChatGPT skill uploads.

## What This Includes

- 21 reusable financial analysis skills
- Daloopa MCP configuration for Codex in `.mcp.json`
- Codex plugin manifest in `.codex-plugin/plugin.json`
- OpenAI skill UI metadata in each skill's `agents/openai.yaml`
- ChatGPT packaging script that creates one uploadable skill zip per workflow

## Prerequisites

- Codex or ChatGPT with skills enabled
- A Daloopa account
- For Codex: access to the Daloopa MCP servers configured in `.mcp.json`
- For ChatGPT: Daloopa MCP connector or equivalent Daloopa tool access enabled in the target workspace

## Codex Usage

Validate the plugin locally:

```bash
python3 /Users/corymchattie/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/corymchattie/Projects/daloopa-plugin-codex
```

Validate all source skills:

```bash
find skills -mindepth 1 -maxdepth 1 -type d -exec python3 /Users/corymchattie/.codex/skills/.system/skill-creator/scripts/quick_validate.py {} \;
```

This repo is ready to be added to a Codex marketplace or installed through the local Codex plugin workflow. The public plugin name is `daloopa`.

Start with:

```text
Verify my Daloopa setup.
Create a tearsheet for AAPL.
Review MSFT earnings and guidance.
Build a DCF valuation for NVDA.
```

## ChatGPT Skill Packages

Build one uploadable zip per skill:

```bash
python3 scripts/package_chatgpt_skills.py
```

The generated packages are written to:

```text
dist/chatgpt-skills/
```

Each zip contains a self-contained skill folder with `SKILL.md`, `agents/openai.yaml`, and shared references copied into `references/`.

## Available Skills

| Skill | Description | Example prompt |
|---|---|---|
| `setup` | Verify Daloopa MCP connection and available workflows | Verify my Daloopa setup. |
| `tearsheet` | Quick one-page company overview | Create a tearsheet for MSFT. |
| `earnings-review` | Full earnings analysis with guidance tracking | Review AAPL earnings and guidance. |
| `earnings-prep` | Pre-earnings preparation report | Prepare me for NVDA earnings. |
| `earnings-flash` | Rapid first-read earnings flash | Draft an earnings flash for AAPL. |
| `guidance-tracker` | Track management guidance accuracy | Track NVDA guidance accuracy. |
| `bull-bear` | Bull/bear/base scenario framework | Create a bull-bear analysis for TSLA. |
| `industry` | Cross-company industry comparison | Compare AAPL, MSFT, GOOGL, and AMZN. |
| `inflection` | Detect metric accelerations and decelerations | Find AAPL's biggest inflections. |
| `capital-allocation` | Buybacks, dividends, shareholder yield | Analyze MSFT capital allocation. |
| `dcf` | DCF valuation with sensitivity analysis | Build a DCF for AAPL. |
| `comps` | Trading comparables and implied valuation | Run comps for AAPL. |
| `precedent-transactions` | Precedent M&A transaction analysis | Analyze precedent transactions for AAPL peers. |
| `supply-chain` | Supplier/customer dependency dashboard | Map AAPL's supply chain. |
| `research-note` | Professional research note | Generate a research note for AAPL. |
| `build-model` | Multi-tab Excel financial model | Build an Excel model for AAPL. |
| `comp-sheet` | Industry comp sheet Excel model | Build a comp sheet for AAPL. |
| `ib-deck` | Investment banking pitch deck | Create an IB deck for AAPL. |
| `initiate` | Coverage initiation report plus model | Initiate coverage on AAPL. |
| `unit-economics` | Bottoms-up unit economics decomposition | Analyze NFLX unit economics. |
| `working-capital` | Cash conversion and working-capital deep dive | Analyze AAPL working capital. |

## Data Sources

- **Daloopa MCP** - Institutional-grade financial data from SEC filings, including income statements, balance sheets, cash flow, KPIs, guidance, segment breakdowns, documents, and stock prices.
- **Market data** - Skills use Daloopa stock price data first, then other available tools or web search when needed.
- **Consensus estimates** - Included when available; skipped or clearly labeled when unavailable.

Every Daloopa-sourced financial figure should include a citation link back to the original source.

## Related Repos

- This repo is the Codex and ChatGPT skills distribution.
- The Claude distribution lives in the sibling [`daloopa-plugin-claude`](https://github.com/daloopa/daloopa-plugin-claude) repo.
- For enhanced infrastructure and application code, see [github.com/daloopa/investing](https://github.com/daloopa/investing).
