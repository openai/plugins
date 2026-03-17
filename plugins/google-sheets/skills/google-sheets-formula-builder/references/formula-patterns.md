# Formula Patterns

Use this file as a syntax refresher, not a full formulas manual.

## Formula Shape Heuristics

- Use a row formula when the logic is evaluated row-by-row and should be copied down.
- Use a spill formula when one anchor cell should populate the whole output region.
- Prefer `XLOOKUP` for straightforward exact lookups when available.
- If using `VLOOKUP`, explicitly pass `FALSE` for exact match behavior.
- Use `FILTER` when the output should be the original rows or columns that satisfy conditions.
- Use a named function when the same formula pattern should be reused semantically, not just copied.
- Use `MAP` with `LAMBDA` when you need per-item transformation logic that would be awkward as a plain spill formula.

## High-Value Syntax Reminders

### ARRAYFORMULA

- Official doc: https://support.google.com/docs/answer/3093275?hl=en
- Google notes that many array formulas automatically expand into neighboring cells, so explicit `ARRAYFORMULA` is not always required.
- Good when one anchor formula should fill an output column.

Example:

```gs
=ARRAYFORMULA(IF(A2:A="", "", IF(E2:E>=90, "On track", "At risk")))
```

### FILTER

- Official doc: https://support.google.com/docs/answer/3093197?hl=en
- Conditions must match the length of the filtered range.
- Google notes that you cannot mix row conditions and column conditions in the same `FILTER`.
- If no values satisfy the conditions, Google returns `#N/A`.

Example:

```gs
=FILTER(A2:D, D2:D="Open", A2:A<>"")
```

### XLOOKUP

- Official doc: https://support.google.com/docs/answer/12405947?hl=en
- `lookup_range` must be a single row or column.
- `result_range` should have the same row or column size as the lookup range.
- Use `missing_value` when you want a cleaner fallback than raw `#N/A`.

Example:

```gs
=XLOOKUP(A2, Lookup!A:A, Lookup!D:D, "")
```

### VLOOKUP

- Official doc: https://support.google.com/docs/answer/3093318?hl=en
- Google strongly recommends using `FALSE` for `is_sorted` for more predictable exact-match behavior.
- The search key must be in the first column of the lookup range.
- If you need a friendlier fallback, wrap with `IFNA` or `IFERROR`.

Example:

```gs
=IFNA(VLOOKUP(A2, Lookup!A:D, 4, FALSE), "")
```

### MAP

- Official doc: https://support.google.com/docs/answer/12568985?hl=en
- The `LAMBDA` must accept exactly as many names as the number of input arrays.
- Each mapped value must resolve to a single value, not another array.
- Useful for per-item transformations that are more expressive than a plain copied formula.

Example:

```gs
=MAP(A2:A, LAMBDA(item, JOIN("-", SPLIT(item, ","))))
```

### Named Functions

- Official doc: https://support.google.com/docs/answer/12504534?hl=en
- Named functions are appropriate when the formula pattern should be reused conceptually across a sheet or across files.
- Google requires placeholder names rather than A1-style references for function arguments.

## Practical Rollout Pattern

1. Draft in one helper cell or scratch column.
2. Test on representative rows, including blanks, missing lookups, and unusual values.
3. Decide whether the final rollout should be copy-down, spill-from-anchor, or named-function-based.
4. Only then replace the target formula region.

## Official References

- Google Sheets function list: https://support.google.com/docs/table/25273?hl=en
- ARRAYFORMULA: https://support.google.com/docs/answer/3093275?hl=en
- FILTER: https://support.google.com/docs/answer/3093197?hl=en
- XLOOKUP: https://support.google.com/docs/answer/12405947?hl=en
- VLOOKUP: https://support.google.com/docs/answer/3093318?hl=en
- MAP: https://support.google.com/docs/answer/12568985?hl=en
- Named functions: https://support.google.com/docs/answer/12504534?hl=en
