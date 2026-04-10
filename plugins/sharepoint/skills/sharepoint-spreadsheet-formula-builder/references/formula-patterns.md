# Formula Patterns

Use this file as an Excel syntax refresher for SharePoint-hosted workbooks, not as a full formulas manual.

These are Excel formula patterns, not SharePoint connector capabilities. The connector can fetch and overwrite workbook files, but formula support depends on the Excel environment that opens the workbook afterward.

Operationally, the SharePoint implementation prefers exact Graph item URLs from keyword search or explicit browse results for later `fetch` calls, and then uses root-relative paths or exact targets for writes. Use `get_site(...)`, `list_site_drives(...)`, and `search(query=None, ...)` for truthful site-scoped discovery instead of relying on user-recency.

## Formula Shape Heuristics

- Use a table formula when the target range is inside an Excel Table and the logic should auto-fill for each row.
- Use a copied row formula when the data is not in a table and the logic belongs to one row at a time.
- Use a spill formula when one anchor cell should populate a whole output region, but verify the spill range is empty first.
- If workbook compatibility is unknown, default to broadly compatible formulas first: `IF`, `IFERROR`, `SUMIFS`, `COUNTIFS`, `INDEX/MATCH`, and exact-match `VLOOKUP(FALSE)`.
- Prefer `XLOOKUP` for straightforward exact lookups when the workbook is expected to run in a modern Microsoft 365 Excel environment.
- If using `VLOOKUP`, explicitly pass `FALSE` for exact-match behavior.
- Use `FILTER` when the output should stay as the original rows or columns that satisfy conditions.
- Use `LET` when repeated subexpressions make the formula hard to read or maintain.
- Use `LAMBDA` or a named formula only when the same logic should be reused semantically, not just copied, and only when the workbook environment supports modern Excel functions.

## High-Value Syntax Reminders

### Structured References

- If the target data lives in an Excel Table, prefer structured references so formulas stay readable and resilient to row inserts.
- Row formulas commonly use `[@[Column Name]]` for the current row and `TableName[Column Name]` for full-column references.

Example:

```excel
=[@[Revenue]]-[@[Cost]]
```

### XLOOKUP

- Good default for exact lookups with a clean fallback.
- Keep the lookup array and return array aligned to the same shape.
- Not safe as a universal default for legacy Excel consumers.

Example:

```excel
=XLOOKUP([@[SKU]], Lookup[SKU], Lookup[Price], "")
```

### VLOOKUP

- The lookup key must be in the first column of the lookup range.
- Pass `FALSE` for exact-match behavior unless an approximate match is truly intended.

Example:

```excel
=IFERROR(VLOOKUP(A2, Lookup!A:D, 4, FALSE), "")
```

### INDEX / MATCH

- Safer than `XLOOKUP` when workbook compatibility is unclear but you still want a flexible left-or-right lookup pattern.
- Wrap with `IFERROR` when a blank or friendly fallback is better than a raw error.

Example:

```excel
=IFERROR(INDEX(Lookup!D:D, MATCH(A2, Lookup!A:A, 0)), "")
```

### SUMIFS / COUNTIFS

- Prefer these for conditional aggregations when you do not need dynamic-array output.
- Usually more compatible and easier to audit than building the same result from newer array functions.

Examples:

```excel
=SUMIFS(AmountRange, StatusRange, "Open")
```

```excel
=COUNTIFS(OwnerRange, A2, StatusRange, "Open")
```

### FILTER

- Useful when the output should be the original rows or columns that satisfy live conditions.
- Spill formulas fail if the spill range is blocked by existing content.
- Dynamic-array behavior depends on a modern Excel calculation engine.

Example:

```excel
=FILTER(Table1[[Name]:[Status]], Table1[Status]="Open", "")
```

### LET

- Use `LET` to name repeated intermediate values and make large formulas easier to maintain.
- Treat this as a modern Excel feature rather than a universally portable formula primitive.

Example:

```excel
=LET(score, [@[Score]], IF(score>=90, "On track", "At risk"))
```

### LAMBDA

- Best for reusable workbook logic, especially when the same transformation would otherwise be copied into many places.
- Prefer this only when the workbook environment already uses modern Excel functions or the user explicitly wants reusable workbook logic.

Example:

```excel
=LAMBDA(score, IF(score>=90, "On track", "At risk"))(A2)
```

## Practical Rollout Pattern

1. Draft the formula in a helper cell or scratch column in a local workbook copy.
2. Test representative rows, including blanks, missing lookups, and odd values.
3. Decide whether the final rollout should be a table formula, copied formula, spill-from-anchor formula, or named formula.
4. Verify the exact target cells and dependency ranges before upload.
5. After SharePoint upload, re-fetch the workbook metadata or content and confirm the intended formula landed in the right place.
