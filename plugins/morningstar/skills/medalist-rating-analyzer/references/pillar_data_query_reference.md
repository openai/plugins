# pillar_data_query.py Reference

## get_pillar_data_id

Query pillar rating input data and return matching data point IDs.

### Usage

```python
import sys
import glob, os
sys.path.insert(0, next((p for p in ['skills/medalist-rating-analyzer/scripts',
    *glob.glob('.remote-plugins/*/skills/medalist-rating-analyzer/scripts')] if os.path.isdir(p)),
    'skills/medalist-rating-analyzer/scripts'))

from pillar_data_query import get_pillar_data_id

# Get Process pillar IDs for Active management type
active_process_ids = get_pillar_data_id("process", "active")
# Returns: ['ZS71V', 'ODA4H', 'MVD74', 'USMSQ', 'IRTWI', ...]

# Get People pillar IDs for Active management type
active_people_ids = get_pillar_data_id("people", "active")
# Returns: ['A9SD3', 'E89P9', 'I4JKP', 'LGFDO', 'MYVT1', ...]

# Get Parent pillar IDs for Passive management type
# Note: Parent only has Passive/Active entries, which are returned for passive queries
passive_parent_ids = get_pillar_data_id("parent", "passive")
# Returns: ['CW7G7', 'DX37P', 'EO0U8', 'HXDS7', 'J25I9', ...]
```

### Parameters

- **pillar**: `Literal["parent", "people", "process"]`
  - The pillar type to query (case-insensitive)

- **manage_type**: `Literal["active", "passive"]`
  - The management type to filter by (case-insensitive)

### Returns

- `List[str]`: List of matching data point IDs

### Data Distribution

See `pillar_rating_input_data.md` (same folder) for the authoritative list of pillar/management-type
datapoint counts — it is not duplicated here so the two can't drift out of sync.

### Notes

- The tool automatically handles "Passive/Active" entries in the data, including them when querying for passive management type
- All IDs are cleaned (tabs and whitespace removed)
- Input parameters are case-insensitive
