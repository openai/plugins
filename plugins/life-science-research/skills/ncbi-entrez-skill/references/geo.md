# GEO Within Entrez

Use GEO through Entrez rather than a separate GEO skill.

## Database choices
- Use `db=gds` for GEO DataSets and series-level metadata.
- Use `db=geoprofiles` for profile-level records.

## Common workflow
1. Run `esearch` to find candidate UIDs.
2. Run `esummary` or `efetch` for targeted metadata.
3. Run `elink` when the user wants linked PubMed articles or related Entrez records.

## Query patterns
- Series searches often use `GSE[ETYP]`.
- Sample searches often use `GSM[ETYP]`.
- Combine accession filters with disease or organism terms when narrowing results.

## Examples
- `{"endpoint":"esearch","params":{"db":"gds","term":"GSE[ETYP] AND breast cancer","retmax":10},"max_items":10}`
- `{"endpoint":"esummary","params":{"db":"gds","id":"200000001","retmode":"json"},"max_items":10}`
- `{"endpoint":"elink","params":{"dbfrom":"gds","db":"pubmed","id":"200000001","retmode":"json"},"max_items":10}`
