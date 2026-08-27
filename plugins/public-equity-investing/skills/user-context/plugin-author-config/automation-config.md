# Public Equity Investing Default Automations

## Weekday Watchlist Brief

- ID: `weekday-watchlist-brief`
- Name: `Weekday Public Equity Watchlist Brief`
- Frequency: Weekdays at 8:00 AM local time.
- Launcher: `Set up a weekday Public Equity Investing watchlist brief in this conversation.`

### Canonical Automation Prompt

Pass this prompt to the automation tool substantially verbatim:

```text
Run a read-only weekday Public Equity Investing source check. Invoke the Public Equity Investing router and apply its user-context preflight before substantive work. Review only saved watchlist pointers that are already present. Do not perform broad research.

Report only: Upcoming Catalysts, Stale Sources, and Missing Inputs. Include the ticker or watchlist pointer, the dated item or gap, the source pointer, and the as-of date when known.

If no saved watchlist pointer is available, ask for one ticker or watchlist pointer. Do not invent a portfolio or watchlist. If context exists but there is nothing to surface, return: No upcoming catalysts, stale sources, or missing inputs identified today. Then state the source coverage and freshness limitations.

Do not draft investment analysis or modify anything. Do not trade, send messages, edit source systems, or save new durable preferences without an explicit user request.
```
