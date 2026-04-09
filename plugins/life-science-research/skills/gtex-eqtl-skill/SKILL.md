---
name: gtex-eqtl-skill
description: Fetch GTEx single-tissue eQTL associations from one variant input by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query for the GTEx v2 API. Use when a user wants eQTL associations returned as JSON.
---

# Operating rules

- Use Python `requests` for all network calls.
- Accept exactly one of `rsid`, `grch37`, `grch38`, or `variant`, and resolve to a GRCh38 `chrom-pos-ref-alt` query.
- Convert to GTEx `variantId` format: `chr{chrom}_{pos}_{ref}_{alt}_b38`.
- Always return one JSON object (no markdown) as final output.

# Input

Accept JSON on stdin as either:

- A string: `"10-112998590-C-T"` (treated as GRCh38)
- An object:

```json
{
  "grch38": "10-112998590-C-T",
  "max_results": 200
}
```

Other accepted object forms include:

```json
{
  "grch37": "10-114758349-C-T"
}
```

```json
{
  "rsid": "rs7903146",
  "max_results": 50
}
```

Allowed variant separators include `-`, `:`, `_`, `/`, or whitespace, for example:

- `10-112998590-C-T`
- `10:112998590-C-T`
- `10:112998590:C:T`
- `chr10 112998590 C T`

`max_results` is optional and truncates returned eQTL rows when provided.

# Output

Success shape:

```json
{
  "ok": true,
  "source": "gtex-v2",
  "input": {"type": "grch38", "value": "10-112998590-C-T"},
  "query_variant": {
    "chr": "10",
    "pos": 112998590,
    "ref": "C",
    "alt": "T",
    "canonical": "10:112998590-C-T",
    "variant_id": "chr10_112998590_C_T_b38"
  },
  "eqtl_count": 2,
  "eqtl_count_total": 2,
  "truncated": false,
  "eqtls": [],
  "paging_info": {},
  "warnings": []
}
```

Failure shape:

```json
{
  "ok": false,
  "error": {"code": "...", "message": "..."},
  "warnings": []
}
```

# Execution

Use:

- `scripts/gtex_eqtl.py`

The script reads JSON from stdin and prints JSON to stdout.

Example:

```bash
echo '{"grch38":"10-112998590-C-T","max_results":5}' | python scripts/gtex_eqtl.py
```
