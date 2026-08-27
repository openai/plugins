# Worked Examples (Templates filled with placeholders)

## Table of contents
1. [Example plan.json](#example-planjson)
2. [Example normalized rows](#example-normalized-rows)
3. [Example tear sheet](#example-tear-sheet)
4. [Example changelog + diff](#example-changelog--diff)

---

## Example plan.json
```json
{
  "event": {
    "ticker": "MISSING",
    "company_name": "MISSING",
    "fiscal_period": "FY2026Q2",
    "event_date": "MISSING",
    "timezone": "America/New_York",
    "base_currency": "USD",
    "base_scale": "m"
  },
  "inputs": {
    "artifact_index_csv": "output/audit/ArtifactIndex.csv",
    "artifacts": {
      "press_release": "01_Raw/earnings_pr.pdf",
      "sec_filing_10q_or_10k": "01_Raw/10q.pdf",
      "sec_filing_8k": "01_Raw/8k.pdf",
      "deck": "01_Raw/deck.pdf",
      "transcript": "01_Raw/transcript.txt"
    },
    "normalized": {
      "metrics_csv": "normalized/metrics.csv",
      "estimates_csv": "normalized/estimates.csv",
      "guidance_csv": "normalized/guidance.csv",
      "quotes_csv": "normalized/quotes.csv",
      "driver_updates_csv": "normalized/driver_updates.csv"
    },
    "model": {
      "prior_model_xlsx": "02_Model/PriorModel.xlsx",
      "driver_registry_csv": "02_Model/driver_registry.csv",
      "output_registry_csv": "02_Model/output_registry.csv"
    }
  },
  "outputs": {
    "output_dir": "output",
    "render": {
      "executive_overview": true,
      "tear_sheet": true,
      "deep_dive": true
    },
    "model_update": {
      "enabled": true,
      "mode": "apply",
      "write_diff": true
    }
  },
  "controls": {
    "allow_call_only_guidance": true,
    "require_gaap_for_non_gaap": true,
    "require_source_tags": true,
    "dry_run": false
  }
}
```

## Example normalized rows

### metrics.csv
```csv
MetricName,Period,Value,Units,GAAP_Flag,Segment,IsTearSheet,DisplayOrder,SourceTag,ComparableGAAPMetricName,ReconciliationSourceTag,Notes
Revenue,FY2026Q2,MISSING,USDm,GAAP,Total,Y,1,"10-Q | p.MISSING, Consolidated Statements of Operations | Revenue",,,
GAAP EPS (Diluted),FY2026Q2,MISSING,USD,GAAP,Total,Y,2,"10-Q | p.MISSING, Consolidated Statements of Operations | EPS",,,
Adjusted EBITDA,FY2026Q2,MISSING,USDm,Non-GAAP,Total,Y,3,"Earnings PR (Exhibit 99.1) | p.MISSING, Table MISSING | Adj EBITDA","Operating income","Earnings PR (Exhibit 99.1) | p.MISSING, Non-GAAP reconciliation | Adj EBITDA",MISSING
```

### quotes.csv
```csv
Section,Speaker,Questioner,TopicTag,QuoteText,SourceTag
Q&A,CFO,"Analyst (Firm)",Guidance,"MISSING",MISSING
```

## Example tear sheet
See template: `assets/templates/tear_sheet.md`.

## Example changelog + diff
See templates:
- `assets/templates/changelog.csv`
- `assets/templates/what_changed_diff.csv`
