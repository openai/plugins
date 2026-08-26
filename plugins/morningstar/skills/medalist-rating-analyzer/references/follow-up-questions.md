# Standard Fund Follow-up Questions

Use this reference only after `data` for the same fund is already in session. For historical, dated, rating-change, current pillar-input, or raw-schema questions, use the more specific reference linked directly from `SKILL.md`.

## Contents

- [Formatter Routing](#formatter-routing)
- [Follow-up Question Examples](#follow-up-question-examples)

## Formatter Routing

Use the matching formatter method for a standard follow-up. When a formatter method is used, return its output in full and verbatim; do not summarize, reformat, or hand-copy it.

| User asks about | Action |
|----------------|--------|
| full analysis / overview | `fmt.full_report(data)` — include all narrative text |
| overall rating / rating breakdown | `fmt.overall_rating(data)` — includes the current Medalist Rating type and latest pillar scores with assignment types |
| price score / fees | `fmt.price_score(data)` |
| people pillar (current) | `fmt.people_pillar(data)` |
| process pillar (current) | `fmt.process_pillar(data)` |
| parent pillar (current) | `fmt.parent_pillar(data)` |
| product info / fund identity | `fmt.product_info(data)` |

## Follow-up Question Examples

**Show People pillar:**

```python
import sys, io
import glob, os
sys.path.insert(0, next((p for p in ['skills/medalist-rating-analyzer/scripts',
    *glob.glob('.remote-plugins/*/skills/medalist-rating-analyzer/scripts')] if os.path.isdir(p)),
    'skills/medalist-rating-analyzer/scripts'))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from formatter import Formatter
fmt = Formatter()
# data is already in context from the initial fund fetch
header = fmt.fund_header(data)
body   = fmt.people_pillar(data)
output = header + "\n\n" + body if header else body
print(output)
```
