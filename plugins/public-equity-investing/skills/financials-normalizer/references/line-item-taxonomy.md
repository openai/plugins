# Line-item taxonomy

Use this starter taxonomy to map source labels into normalized financials while preserving the exact source label.

## Mapping principles

- Keep `line_item_original` exactly as found in the source.
- Map to `line_item_standard` only when the mapping is clear or reasonably supported.
- If uncertain, set confidence `low` and add a QA flag rather than forcing the mapping.
- Preserve company-defined non-GAAP metrics separately from reconstructed metrics.
- Do not collapse operating, non-operating, discontinued operations, minority interest, preferred dividends, or noncontrolling interest unless explicitly requested.

## Income statement starter map

| line_item_id | line_item_standard | Common labels |
|---|---|---|
| revenue | Revenue | revenue, net sales, sales, net revenue, total revenues, operating revenue |
| cogs | Cost of revenue | cost of revenue, cost of sales, cogs, cost of services |
| gross_profit | Gross profit | gross profit |
| sales_marketing | Sales and marketing | sales and marketing, selling expense, marketing |
| research_development | Research and development | r&d, research and development, product development |
| general_admin | General and administrative | g&a, general and administrative, administrative expense |
| opex_total | Total operating expenses | operating expenses, total opex |
| operating_income | Operating income | operating income, income from operations, operating profit |
| depreciation_amortization | Depreciation and amortization | d&a, depreciation, amortization |
| ebitda_company_defined | EBITDA, company-defined | ebitda, adjusted ebitda, company adjusted ebitda |
| stock_based_comp | Stock-based compensation | sbc, share-based compensation |
| interest_expense | Interest expense | interest expense, finance costs |
| interest_income | Interest income | interest income, investment income |
| other_income_expense | Other income / expense | other income, other expense, non-operating income |
| pretax_income | Income before taxes | pretax income, income before income taxes |
| tax_expense | Income tax expense | provision for income taxes, income tax expense |
| net_income | Net income | net income, net earnings, profit attributable to shareholders |
| eps_basic | EPS basic | basic EPS, basic earnings per share |
| eps_diluted | EPS diluted | diluted EPS, diluted earnings per share |
| shares_basic | Weighted average shares basic | basic weighted average shares |
| shares_diluted | Weighted average shares diluted | diluted weighted average shares |

## Balance sheet starter map

| line_item_id | line_item_standard | Common labels |
|---|---|---|
| cash_equivalents | Cash and equivalents | cash, cash equivalents, cash and cash equivalents |
| short_term_investments | Short-term investments | marketable securities, short-term investments |
| accounts_receivable | Accounts receivable | trade receivables, accounts receivable, ar |
| inventory | Inventory | inventory, inventories |
| prepaid_other_current_assets | Prepaids and other current assets | prepaid expenses, other current assets |
| total_current_assets | Total current assets | current assets, total current assets |
| ppne_net | Net PP&E | property and equipment, pp&e, fixed assets |
| goodwill | Goodwill | goodwill |
| intangibles_net | Intangible assets | intangible assets, acquired intangibles |
| total_assets | Total assets | total assets |
| accounts_payable | Accounts payable | trade payables, accounts payable, ap |
| accrued_expenses | Accrued expenses | accrued liabilities, accrued expenses |
| deferred_revenue_current | Current deferred revenue | current deferred revenue, current contract liabilities |
| short_term_debt | Short-term debt | current debt, current maturities, short-term borrowings |
| total_current_liabilities | Total current liabilities | current liabilities, total current liabilities |
| long_term_debt | Long-term debt | long-term debt, borrowings, notes payable |
| lease_liabilities | Lease liabilities | operating lease liabilities, finance lease liabilities |
| deferred_revenue_noncurrent | Noncurrent deferred revenue | long-term deferred revenue, noncurrent contract liabilities |
| total_liabilities | Total liabilities | liabilities, total liabilities |
| noncontrolling_interest | Noncontrolling interest | minority interest, nci |
| total_equity | Total equity | shareholders' equity, stockholders' equity, net assets |
| liabilities_equity | Total liabilities and equity | liabilities and equity, liabilities and shareholders' equity |

## Cash flow starter map

| line_item_id | line_item_standard | Common labels |
|---|---|---|
| net_income_cf | Net income in cash flow | net income, net earnings |
| depreciation_amortization_cf | D&A in cash flow | depreciation and amortization |
| stock_based_comp_cf | Stock-based compensation in cash flow | stock-based compensation, share-based compensation |
| deferred_taxes | Deferred taxes | deferred income taxes |
| accounts_receivable_change | Change in accounts receivable | accounts receivable change, receivables |
| inventory_change | Change in inventory | inventory change |
| accounts_payable_change | Change in accounts payable | accounts payable change |
| other_working_capital_change | Other working capital change | other operating assets and liabilities |
| cfo | Cash flow from operations | net cash provided by operating activities, cfo |
| capex | Capital expenditures | purchases of property and equipment, capex |
| acquisitions | Acquisitions | business acquisitions, acquisition of subsidiaries |
| cfi | Cash flow from investing | net cash used in investing activities |
| debt_issuance_repayment | Debt issuance / repayment | proceeds from debt, repayment of debt |
| equity_issuance | Equity issuance | issuance of common stock, proceeds from shares |
| dividends | Dividends | dividends paid |
| share_repurchases | Share repurchases | repurchases of stock, buybacks |
| cff | Cash flow from financing | net cash provided by financing activities |
| fx_cash_effect | FX effect on cash | effect of exchange rates on cash |
| net_change_cash | Net change in cash | net increase/decrease in cash |
| beginning_cash | Beginning cash | cash at beginning of period |
| ending_cash | Ending cash | cash at end of period |
| free_cash_flow | Free cash flow | fcf, cfo less capex |

## KPI handling

Treat sector KPIs as definition-sensitive. Store company definition or data-provider definition when available.

Common KPI categories:
- SaaS/software: ARR, NRR, GRR, churn, billings, bookings, RPO, customers, ACV, ARPU, CAC, LTV, payback.
- Banking/financials: net interest income, NIM, deposits, loans, CET1, provisions, charge-offs, efficiency ratio.
- Insurance: premiums, loss ratio, combined ratio, reserves, investment income.
- Real estate/REITs: NOI, same-store NOI, occupancy, rent PSF, AFFO, FFO, cap rate.
- Energy: production, reserves, realized price, lifting cost, DD&A, capex by basin.
- Marketplaces: GMV, take rate, active users, transactions, contribution profit.
- Healthcare/biotech: patients, procedures, trial milestones, R&D by program, cash runway.


## Equity-risk debt and liquidity context

Use only for common-equity read-through: net debt, cash, restricted cash, maturity wall summary, interest expense, revolver availability, refinancing date, rating or CDS/spread signal, and liquidity runway. Route covenant models, recovery waterfalls, bond/loan/CDS pricing, spread/yield relative value, and debt-security selection to Credit Markets.
