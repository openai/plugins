---
name: ramp-vendor-analysis
description: Analyzes vendor spend data from Ramp and exports to connected systems. Use when user asks to "analyze vendor spend", "build vendor database", "update managed vendors", "top vendors report", "show vendors over X spend", "vendor spend analysis", "vendor renewals", "contract end dates", or asks about vendor spending patterns, vendor owners, purchase orders, or department-level vendor data.
metadata:
  author: Ramp
  version: 1.1.0
  mcp-server: ramp
---

# Ramp Vendor Spend Analysis

## Overview

This skill extracts comprehensive vendor data from Ramp, enriches it with owner/department information and contract data from purchase orders, and outputs structured results. Data can be displayed as text/tables or exported to connected integrations (Notion, Google Sheets, etc.).

## When to Use This Skill

- User asks to analyze vendor spend or build a vendor database
- User wants to see top vendors by spend (L365, L30, YTD, all-time)
- User asks about vendor owners or which departments own which vendors
- User asks about contract end dates, renewals, or purchase order status
- User wants vendor data exported to Notion, spreadsheets, or other systems
- User asks ad-hoc questions like "vendors with spend over $50k" or "upcoming renewals"

## Prerequisites

- Ramp MCP server must be connected
- For exports: Target integration (Notion, Google Sheets, etc.) should be connected

## Data Collection Workflow

### Step 1: Load Core Vendor Data

**Tool:** `ramp-demo:load_vendors`

This is the primary data source. Call with default parameters to load all vendors.

```
Parameters: {}
```

**Data extracted per vendor:**
- Vendor ID
- Vendor Name
- Vendor Owner ID
- Vendor Contacts (email, phone)
- Total spend L365 (last 365 days)
- Total spend L30 (last 30 days)
- Total spend YTD (year to date)
- Total spend all-time
- Billing frequency
- Tax information (W-9 status, tax ID)
- Active status

### Step 2: Load Users for Owner Details

**Tool:** `ramp-demo:load_users`

Required to resolve Vendor Owner IDs to names and get their department assignments.

```
Parameters: {}
```

**Data extracted per user:**
- User ID
- First name, Last name
- Email
- Department ID
- Location ID
- Manager ID

### Step 3: Load Departments

**Tool:** `ramp-demo:load_departments`

Required to map Department IDs to department names.

```
Parameters: {}
```

**Data extracted:**
- Department ID
- Department Name

### Step 4: Load Bills for Payment Method Analysis

**Tool:** `ramp-demo:load_spend_export`

Query bills to determine preferred payment methods per vendor.

```
Parameters:
  spend_export_type: "bills"
  from_date: [365 days ago, YYYY-MM-DD format]
  to_date: [today, YYYY-MM-DD format]
```

**Data extracted per bill:**
- Vendor ID (to join with vendor data)
- Payment method used
- Bill amount
- Bill date

### Step 5: Load Purchase Orders for Contract Data

**Tool:** `ramp-demo:load_purchase_orders`

Purchase orders contain contract/renewal information. The spend end date on a PO maps to the contract end date for that vendor relationship.

```
Parameters:
  from_date: [365 days ago, YYYY-MM-DD format]
  to_date: [today, YYYY-MM-DD format]
```

**Data extracted per purchase order:**
- PO ID
- PO Number
- Vendor ID (to join with vendor data)
- Spend end date → **maps to contract end date**
- Total amount
- Amount paid/billed
- Receipt status (FULLY_RECEIVED, PARTIALLY_RECEIVED, OVER_RECEIVED, NOT_RECEIVED)
- Three-way match enabled flag
- Created date

**Contract status logic:**
- If vendor has PO with spend_end_date → "Contract in place", use date as contract end
- If vendor has multiple POs → "Multiple contracts", use earliest upcoming end date
- If vendor has no POs → "No contract in place"
- If PO is nearing full billing (amount_paid approaching total_amount) → flag for renewal attention

### Step 6: Join and Enrich Data

After loading all data sources, perform the following joins using SQL queries:

**Tool:** `ramp-demo:execute_query`

```sql
-- Join vendors with owner names, departments, and contract info from POs
SELECT 
  v.vendor_name,
  v.total_spend_l365,
  v.total_spend_l30,
  v.total_spend_ytd,
  v.total_spend_all_time,
  v.billing_frequency,
  v.tax_status,
  u.first_name || ' ' || u.last_name AS vendor_owner_name,
  u.email AS vendor_owner_email,
  d.name AS owner_department,
  po.spend_end_date AS contract_end_date,
  po.total_amount AS po_total,
  po.amount_paid AS po_paid,
  po.receipt_status,
  CASE 
    WHEN po.id IS NULL THEN 'No contract in place'
    WHEN po_count.cnt > 1 THEN 'Multiple contracts'
    ELSE 'Contract'
  END AS contract_status
FROM vendors v
LEFT JOIN users u ON v.vendor_owner_id = u.id
LEFT JOIN departments d ON u.department_id = d.id
LEFT JOIN purchase_orders po ON v.id = po.vendor_id
LEFT JOIN (
  SELECT vendor_id, COUNT(*) as cnt 
  FROM purchase_orders 
  GROUP BY vendor_id
) po_count ON v.id = po_count.vendor_id
ORDER BY v.total_spend_l365 DESC;
```

**Note:** Actual column names may vary. After loading data, query the schema:
```sql
PRAGMA table_info(vendors);
PRAGMA table_info(users);
PRAGMA table_info(departments);
PRAGMA table_info(purchase_orders);
PRAGMA table_info(bills);
```

## Output Schema

The final enriched dataset should include these fields per vendor:

| Field | Source | Description |
|-------|--------|-------------|
| Vendor Name | vendors | Company/vendor name |
| Vendor Owner | users (joined) | Full name of owner |
| Owner Email | users (joined) | Email of vendor owner |
| Owner Department | departments (joined) | Department name |
| Spend L365 | vendors | Last 365 days spend |
| Spend L30 | vendors | Last 30 days spend |
| Spend YTD | vendors | Year-to-date spend |
| Spend All-Time | vendors | Total historical spend |
| Billing Frequency | vendors | Monthly, annual, etc. |
| Tax Status | vendors | W-9 on file, tax ID |
| Preferred Payment Method | bills (aggregated) | Most common payment method |
| Vendor Contacts | vendors | Contact email/phone |
| Contract Status | purchase_orders | Contract / No contract / Multiple contracts |
| Contract End Date | purchase_orders.spend_end_date | Date contract/PO expires |
| PO Total Amount | purchase_orders | Total value of purchase order |
| PO Amount Paid | purchase_orders | Amount billed against PO |
| PO Receipt Status | purchase_orders | Fulfillment status |

## Handling Ad-Hoc Queries

For filtered queries like "show vendors over $50k spend":

1. Load data using Steps 1-5 above
2. Apply filters in the SQL query:

```sql
SELECT * FROM vendors 
WHERE total_spend_l365 > 50000
ORDER BY total_spend_l365 DESC;
```

Common filter patterns:
- Spend thresholds: `WHERE total_spend_l365 > [amount]`
- Department filter: `WHERE owner_department = '[dept_name]'`
- Active only: `WHERE is_active = 1`
- Top N vendors: `LIMIT [n]`
- Upcoming renewals: `WHERE contract_end_date BETWEEN date('now') AND date('now', '+90 days')`
- Missing contracts: `WHERE contract_status = 'No contract in place' AND total_spend_l365 > 25000`
- POs nearing completion: `WHERE po_paid / po_total > 0.8`

## Output Options

After data collection, ask the user how they want to receive the results:

### Option 1: Text/Table Display (Default)

Display results as a formatted markdown table directly in the conversation.

### Option 2: Export to Connected Integration

Check for available integrations and offer export:

**For Notion:**
- Create or update a database with the output schema
- Map fields to Notion properties:
  - Vendor Name → Title
  - Spend fields → Number ($ format)
  - Contract Status → Select (Contract | No contract in place | Multiple contracts)
  - Contract End Date → Date
  - Tax Status → Select (Tax details verified by Ramp | Missing | N/A)
  - Payment Method → Select (Pay by card | Pay by Bill pay (ACH) | Mixed)

**For Google Sheets:**
- Create a new sheet or append to existing
- Include headers matching the output schema

**For other integrations:**
- Adapt the output schema to the target system's format

## Example Usage

**User:** "Build me a vendor database with our top vendors"

**Workflow:**
1. Call `load_vendors` → loads vendor table
2. Call `load_users` → loads users table  
3. Call `load_departments` → loads departments table
4. Call `load_spend_export` with type="bills" → loads bills table
5. Call `load_purchase_orders` → loads purchase orders table
6. Execute join query to create enriched dataset with contract info
7. Ask user: "I've compiled data on [X] vendors. Would you like me to display this as a table, or export to a connected system like Notion?"
8. Output based on user preference

**User:** "Show me vendors with contracts expiring in the next 90 days"

**Workflow:**
1. Load all data sources (Steps 1-5)
2. Execute filtered query:
```sql
SELECT vendor_name, vendor_owner_name, owner_department, 
       total_spend_l365, contract_end_date,
       julianday(contract_end_date) - julianday('now') AS days_until_expiry
FROM enriched_vendors
WHERE contract_end_date BETWEEN date('now') AND date('now', '+90 days')
ORDER BY contract_end_date ASC;
```
3. Display results as table

**User:** "Which high-spend vendors don't have contracts?"

**Workflow:**
1. Load all data sources (Steps 1-5)
2. Execute filtered query:
```sql
SELECT vendor_name, vendor_owner_name, total_spend_l365
FROM enriched_vendors
WHERE contract_status = 'No contract in place'
AND total_spend_l365 > 25000
ORDER BY total_spend_l365 DESC;
```
3. Display results with recommendation to establish contracts

**User:** "Show me purchase orders that are almost fully billed"

**Workflow:**
1. Load purchase orders data
2. Execute query:
```sql
SELECT vendor_name, po_number, po_total, po_paid,
       ROUND(po_paid * 100.0 / po_total, 1) AS percent_used,
       contract_end_date
FROM enriched_vendors
WHERE po_paid / po_total > 0.8
ORDER BY percent_used DESC;
```
3. Display results - these vendors may need renewal attention

## Error Handling

### MCP Connection Failed
- Verify Ramp MCP is connected in Settings > Extensions
- Check API credentials are valid
- Try reconnecting the integration

### No Vendors Returned
- Confirm the Ramp account has vendor data
- Check if filters are too restrictive
- Try loading without filters first

### No Purchase Orders Found
- Not all vendors will have purchase orders
- Mark these vendors as "No contract in place"
- This is expected for many card-based or self-serve SaaS vendors

### Join Failures
- Query table schemas first to verify column names
- Check for NULL values in join keys
- Use LEFT JOIN to preserve vendors without owners or POs

### Export Failures
- Verify target integration is connected
- Check permissions on target database/sheet
- Confirm field mapping is valid for target system