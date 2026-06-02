---
name: moody-s-company-analysis
description: Use when the user asks for Moody's company profiles, ownership, ratings, credit opinions, financial statements, filings, peers, research, or credit-risk analysis for a company.
---

# Moody's Company Analysis

Use this skill for company-level Moody's workflows that go beyond a lightweight connectivity probe.

## Ground Rules

- Resolve the company through Moody's entity search before calling entity-specific tools.
- Read live tool schemas before calling them; tool names and parameters may differ by MCP version.
- Do not invent entity IDs, rating values, ownership percentages, financial metrics, or document titles.
- Include Moody's citations for each substantive section when the tool response provides citations.
- Highlight missing fields plainly instead of filling gaps from outside assumptions.
- This is research context, not investment advice.

## Company Profile and Ownership

1. Resolve the correct entity. Mention close alternatives if the match is ambiguous.
2. Summarize the profile: legal name, headquarters, country, business description, industry classifications, legal status/form, employees, and identifiers where available.
3. Summarize ownership: ultimate owners, beneficial owners, direct and total ownership percentages, subsidiaries, direct subsidiary count, corporate group size, and key subsidiaries where available.
4. Call out gaps such as no beneficial-owner data, missing ownership percentages, or missing subsidiary detail.
5. Finish with a plain-English structure takeaway: who owns the company, what it owns, and how complex the group appears.

## Ratings and Credit Opinion

1. Resolve the correct entity.
2. Retrieve current long-term rating, outlook, and relevant recent rating history.
3. Summarize rating drivers, credit strengths and challenges, outlook rationale, upgrade factors, downgrade factors, methodology or scorecard factors, and ESG considerations where available.
4. Call out missing fields or stale source material.
5. Finish with a plain-English credit takeaway.

## Financial Statements and Filings

1. Resolve the correct entity.
2. Retrieve the latest two fiscal years of year-end income statement, balance sheet, cash flow statement, and key indicators or ratios where available.
3. Search company filings for the latest annual filing and latest interim filing.
4. Summarize material financial metrics and filing commentary on revenue, earnings, debt, liquidity, cash flow, capex, risks, restructuring, and strategy.
5. Highlight differences between structured financial-statement data and filing commentary.
6. Finish with a plain-English credit-risk takeaway.
