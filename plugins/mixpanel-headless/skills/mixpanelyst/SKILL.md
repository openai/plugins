---
name: mixpanelyst
description: This skill should be used when the user asks about Mixpanel product analytics, event data, funnel analysis, retention curves, cohort analysis, segmentation queries, user behavior, conversion rates, churn, DAU/MAU, ARPU, revenue metrics, feature adoption, A/B test results, user paths, flow analysis, or any request to query, explore, visualize, or analyze Mixpanel data using Python. Also use when the user asks to read, write, or manage Mixpanel "business context" — the markdown documentation that grounds AI assistants in an organization's structure and goals.
allowed-tools: Bash Read Write WebFetch
---

# mixpanel_headless API Reference

Analyze Mixpanel data by writing and executing Python code using the `mixpanel_headless` library and `pandas`.
Before running bundled helper scripts, set `SKILL_DIR` to the absolute path of this
`skills/mixpanelyst` directory.

```python
import mixpanel_headless as mp
ws = mp.Workspace()
result = ws.query("Login", last=30)
print(result.df.head())
```

## Query Engines

| Question | Method | Returns |
|----------|--------|---------|
| How much? How many? Trends? | `ws.query()` | `QueryResult` |
| Do users convert through a sequence? | `ws.query_funnel()` | `FunnelQueryResult` |
| Do users come back? | `ws.query_retention()` | `RetentionQueryResult` |
| What paths do users take? | `ws.query_flow()` | `FlowQueryResult` |
| Who are they? What do they look like? | `ws.query_user()` | `UserQueryResult` |

All result types have a `.df` property returning a pandas DataFrame and a `.params` dict containing the bookmark JSON.
`FlowQueryResult` also has `.graph` (NetworkX DiGraph) and `.anytree` (list of tree roots).

**Quick lookups** use `python3 -c "..."` one-liners. **Multi-step analysis** writes `.py` files.

## Discovery — ALWAYS Do Both Steps Before Querying

Guessing event names causes silent empty results. Guessing API parameters causes TypeErrors and invalid queries. **Discover both the data schema AND the API surface before writing any query.**

### Step 1: Discover the data schema

```python
import mixpanel_headless as mp
from mixpanel_headless import Filter, GroupBy, Metric
ws = mp.Workspace()

# 1. Find real event names
events = ws.events()
top = ws.top_events(limit=10)
print("Events:", events[:20])
print("Top:", [(e.event, e.count) for e in top])

# 2. Find real property names for the event you'll query
props = ws.properties("Login")  # use an actual event name from step 1
print("Properties:", props)

# 3. (Optional) Check property values to validate filter inputs
vals = ws.property_values("platform", event="Login")
print("Platforms:", vals)
```

### Step 2: Discover the API surface with `help.py`

**`help.py` is the source of truth for method signatures, parameter names, type constructors, and enum values.** The method signatures later in this document are summaries — always verify with `help.py` before using a method or type you haven't looked up.

**Never guess parameter names.** If you're unsure whether a parameter is called `property` or `math_property`, or what arguments `GroupBy()` accepts, run `help.py` first. Wrong parameter names cause TypeErrors that waste tool calls.

```bash
# Look up a query method BEFORE writing the query
python3 $SKILL_DIR/scripts/help.py Workspace.query
python3 $SKILL_DIR/scripts/help.py Workspace.query_funnel

# Look up types BEFORE constructing them
python3 $SKILL_DIR/scripts/help.py Filter          # → classmethods: .equals(), .less_than(), etc.
python3 $SKILL_DIR/scripts/help.py Metric          # → property=, NOT math_property=
python3 $SKILL_DIR/scripts/help.py GroupBy          # → property, property_type only
python3 $SKILL_DIR/scripts/help.py MathType         # → enum values

# Look up result types to know what columns .df returns
python3 $SKILL_DIR/scripts/help.py QueryResult
python3 $SKILL_DIR/scripts/help.py FlowQueryResult

# Search when you're not sure of the exact name
python3 $SKILL_DIR/scripts/help.py search cohort   # → CohortBreakdown, CohortMetric, CohortDefinition, ...
python3 $SKILL_DIR/scripts/help.py search retention # → query_retention, RetentionEvent, RetentionMathType, ...

# List everything
python3 $SKILL_DIR/scripts/help.py types            # all public types
python3 $SKILL_DIR/scripts/help.py exceptions        # all exceptions
```

For tutorials and guides: `WebFetch(url="https://mixpanel.github.io/mixpanel-headless/llms.txt")`

### Discovery method signatures

```python
def events(self) -> list[str]: ...
    # List all event names (cached).

def properties(self, event: str) -> list[str]: ...
    # List all property names for an event (cached).

def property_values(self, property_name: str, *, event: str | None = None, limit: int = 100) -> list[str]: ...
    # Get sample values for a property.

def top_events(self, *, type: Literal['general', 'average', 'unique'] = 'general', limit: int | None = None) -> list[TopEvent]: ...
    # Get today's most active events. TopEvent has .event (str), .count (int), .percent_change (float).

def funnels(self) -> list[FunnelInfo]: ...
    # List saved funnels.

def cohorts(self) -> list[SavedCohort]: ...
    # List saved cohorts.

def list_bookmarks(self, bookmark_type: BookmarkType | None = None) -> list[BookmarkInfo]: ...
    # List all saved reports (bookmarks).

def lexicon_schemas(self, *, entity_type: EntityType | None = None) -> list[LexiconSchema]: ...
    # List Lexicon schemas (event/property definitions).

def clear_discovery_cache(self) -> None: ...
    # Clear cached discovery results.
# User Guide: WebFetch(url="https://mixpanel.github.io/mixpanel-headless/guide/discovery/index.md")
```

## Exploratory Analysis Workflow

When exploring an unfamiliar dataset or asked to "find insights," follow this systematic approach. Do NOT skip to querying — explore first.

### Step 1: Orient — Map the Event Schema

```python
import mixpanel_headless as mp
ws = mp.Workspace()

events = ws.events()
top = ws.top_events(limit=15)
print("Events:", events)
print("Top events:", [(e.event, e.count) for e in top])

# Profile the top 3-5 events by volume
for event in [e.event for e in top[:5]]:
    props = ws.properties(event)
    print(f"\n{event} ({len(props)} properties):")
    for p in props[:15]:
        vals = ws.property_values(p, event=event, limit=10)
        print(f"  {p}: {vals}")
```

### Step 2: Classify Properties

Infer property types from sampled values to decide how to use each:

- **Boolean**: values are `['true', 'false']` — segment with `group_by`, often pre-computed behavioral flags
- **Low-cardinality categorical** (<10 values): `platform`, `tier`, `category` — use for `group_by`
- **Numeric**: values parse as int/float: `price`, `total`, `count` — use for `math='average'` or `math='sum'` with `math_property=`
- **High-cardinality** (>100 values): IDs, names — skip for `group_by`, may need custom property cleanup
- **Temporal**: ISO dates or epoch values — use for time-based analysis

Property naming patterns that signal analytical value:
- `is_*`, `has_*`, `was_*`, `post_*` → boolean flags, often pre-computed behavioral segments worth investigating
- `*_total`, `*_count`, `*_value`, `*_amount` → numeric, aggregate with avg/sum/median
- `*_name`, `*_type`, `*_category`, `*_tier` → categorical, use for breakdowns
- `*_id`, `*_uuid` → identifiers, skip for breakdowns

### Step 3: Scan for Significant Segments

For each boolean and low-cardinality categorical property on key events, run a quick breakdown against a numeric metric:

```python
# Example: scan all interesting properties on a purchase event
numeric_prop = 'order_total'  # or whatever the key metric is
interesting_props = [p for p in props if not p.endswith('_id')]

for prop in interesting_props:
    vals = ws.property_values(prop, event=event, limit=10)
    if len(set(vals)) <= 10:  # low cardinality — worth a breakdown
        result = ws.query(event, math='average', math_property=numeric_prop,
                           group_by=prop, last=90, mode='total')
        print(f"\n{numeric_prop} by {prop}:")
        print(result.df.to_string(index=False))
        # Flag segments where metric differs >15% from overall
```

### Step 4: Deep Dive on Significant Findings

When a breakdown reveals a notable difference (>15% between segments):
1. **Quantify**: calculate the exact ratio between segments
2. **Cross-reference**: does this segment differ on other metrics too?
3. **Investigate causally**: run funnels or retention filtered by the segment
4. **Control for confounds**: add a second `group_by` dimension to check if the effect holds

### Step 5: Analyze Messy String Properties

When string properties have complex/unreadable values (e.g., campaign names from tools like Braze):
1. Sample 15-20 values to identify the naming convention
2. Look for structural patterns: date codes, targeting prefixes, channel suffixes, audience tags
3. Design regex cleanup rules, one layer per structural element
4. Create a custom property with `ws.create_custom_property(CreateCustomPropertyParams(...))`
5. Verify by querying with the custom property as `group_by`

### Custom Property Formula Reference

Formulas use a SQL-like expression language. Variables (A, B, _A, etc.) map to properties via `composedProperties`.

**Variable binding:** `LET(name, expression, body)` — define intermediate results:
```
LET(raw, A, REGEX_REPLACE(raw, "pattern", "replacement"))
LET(x, A * B, IFS(x < 50, "low", x < 200, "mid", TRUE, "high"))
```

**Conditionals:** `IF(cond, then, else)`, `IFS(cond1, val1, cond2, val2, ..., TRUE, default)`

**String functions:** `UPPER(s)`, `LOWER(s)`, `LEN(s)`, `LEFT(s, n)`, `RIGHT(s, n)`, `MID(s, start, count)`, `SPLIT(s, delim, n)`, `HAS_PREFIX(s, p)`, `HAS_SUFFIX(s, p)`, `PARSE_URL(s, "domain")`

**Regex functions (PCRE2 engine):**
- `REGEX_MATCH(haystack, pattern)` — returns true/false
- `REGEX_EXTRACT(haystack, pattern, capture_group)` — returns match or capture group
- `REGEX_REPLACE(haystack, pattern, replacement)` — replaces all matches

**Regex engine quirks (Mixpanel-specific):**
- **Case-insensitive by default** — use `(?-i)` to switch to case-sensitive matching within a pattern
- **Backreferences work** — `$1`, `$2` capture groups and `$0` whole-match all work in `REGEX_REPLACE` replacements
- **`{n,m}` quantifiers conflict with formula syntax** — curly braces are parsed as formula constructs. Use repeated character classes instead (e.g., `[0-9][0-9][0-9][0-9]` instead of `[0-9]{4}`)
- **`\d`, `\w` shorthand classes don't work** — use `[0-9]`, `[A-Za-z0-9_]` explicitly
- **Escape backslashes carefully** — in formula strings, `\\\\` may be needed for a literal `\` depending on how the formula is constructed (Python string → JSON → regex engine)

**CamelCase splitting** — insert space between lowercase→uppercase boundaries:
```
REGEX_REPLACE(text, "(?-i)([a-z])([A-Z])", "$1 $2")
// ChickenSundaysApril → Chicken Sundays April
```

**Practical multi-step cleanup example** (campaign names from Braze):
```
LET(s1, REGEX_REPLACE(A, "^[0-9][0-9][0-9][0-9][0-9]*_", ""),
LET(s2, REGEX_REPLACE(s1, "^(NW|TARGETED|REGIONAL|NTL)_", ""),
LET(s3, REGEX_REPLACE(s2, "_(Push|Email|NotificationCenter|ModalInAppMessage)_.*$", ""),
LET(s4, REGEX_REPLACE(s3, "_", " "),
  REGEX_REPLACE(s4, " +", " ")
))))
```

**Type functions:** `STRING(x)`, `NUMBER(x)`, `BOOLEAN(x)`, `DEFINED(x)`

**Math:** `+`, `-`, `*`, `/`, `%`, `MIN(a,b)`, `MAX(a,b)`, `FLOOR(n)`, `CEIL(n)`, `ROUND(n)`

**Date:** `DATEDIF(start, end, unit)` — units: D, M, Y, MD, YM, YD. `TODAY()` for current date.

**List:** `SUM(list)`, `ANY(x, list, expr)`, `ALL(x, list, expr)`, `FILTER(x, list, expr)`, `MAP(x, list, expr)`

**Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=` (case-insensitive for strings), `IN` for list membership

**Logical:** `AND`, `OR`, `NOT(x)`

**Constants:** `TRUE`, `FALSE`, `UNDEFINED`

**Creating a custom property via the API:**
```python
from mixpanel_headless import CreateCustomPropertyParams, ComposedPropertyValue

params = CreateCustomPropertyParams(
    name="Clean Campaign Name",
    resource_type="events",
    display_formula='LET(raw, A, REGEX_REPLACE(REGEX_REPLACE(raw, "^[0-9]+_", ""), "_", " "))',
    composed_properties={
        "A": ComposedPropertyValue(
            resource_type="event", type="string", value="campaign_name",
            label="Campaign Name", property_default_type="string",
        )
    }
)
prop = ws.create_custom_property(params)
ref = CustomPropertyRef(prop.custom_property_id)
result = ws.query(event, group_by=GroupBy(ref), last=30, mode='total')
```

## Workspace

```python
class Workspace:
    """Unified entry point for Mixpanel data operations (042 redesign)."""

    def __init__(
        self,
        *,
        account: str | None = None,
        project: str | None = None,
        workspace: int | None = None,
        target: str | None = None,
        session: Session | None = None,
    ) -> None:
        """Create a new Workspace. Resolution per axis is independent
        (env > param > target > bridge > config); see
        ``mixpanel_headless.auth_types`` and the resolver.

        With ``session=`` supplied, all other axis kwargs are ignored
        (full bypass).
        """
        ...

    # --- Properties (read-only) ---
    account: Account            # Resolved Account (discriminated union)
    project: Project            # Resolved Project
    workspace: WorkspaceRef | None  # Resolved workspace, or None for lazy-resolve
    session: Session            # The (account, project, workspace) tuple
    api: MixpanelAPIClient      # Direct API client access (escape hatch)

    def use(
        self,
        *,
        account: str | None = None,
        project: str | None = None,
        workspace: int | None = None,
        target: str | None = None,
        persist: bool = False,
    ) -> Self:
        """Switch any axis in-session. Returns self for chaining.
        Preserves the underlying httpx.Client. With persist=True, also
        writes to ~/.mp/config.toml [active]. ``target=`` is mutex
        with the per-axis kwargs.
        """
        ...
```

Supports context manager: `with mp.Workspace() as ws: ...`

### Project & Workspace Management

```python
def me(self, *, force_refresh: bool = False) -> Any: ...
    # Get /me response for current credentials (cached 24h).

def projects(self) -> list[Project]: ...
    # List accessible projects (v3; returns Project records — id, name,
    # organization_id, timezone). Replaces deprecated discover_projects().

def workspaces(self, *, project_id: str | None = None) -> list[WorkspaceRef]: ...
    # List workspaces in a project (v3; returns WorkspaceRef records —
    # id, name, is_default). Replaces deprecated discover_workspaces().

def list_workspaces(self) -> list[PublicWorkspace]: ...
    # List all public workspaces for the current project (App API).

def resolve_workspace_id(self) -> int: ...
    # Auto-discover and resolve workspace ID (lazy-resolve helper).

def close(self) -> None: ...
    # Close all resources (HTTP client). Idempotent.
```

> **Removed (042 redesign — FR-038):** `Workspace.workspace_id` property,
> `set_workspace_id()`, `switch_project()`, `switch_workspace()`,
> `discover_projects()`, `discover_workspaces()`, `current_project`,
> `current_credential`, `test_credentials()`. Use `ws.session.workspace_id`,
> `ws.use(workspace=N)`, `ws.use(project=P)`, `ws.projects()`,
> `ws.workspaces()`, `ws.project`, `ws.account`, and `mp.accounts.test(NAME)`
> respectively.

### Insights Query

Run `python3 $SKILL_DIR/scripts/help.py Workspace.query` for the full signature.

```python
def query(
    self,
    events: str | Metric | CohortMetric | Formula | Sequence[...],
    *,
    from_date: str | None = None,        # YYYY-MM-DD, overrides last
    to_date: str | None = None,          # YYYY-MM-DD, requires from_date
    last: int = 30,                      # relative days (ignored if from_date set)
    unit: QueryTimeUnit = 'day',
    math: MathType = 'total',            # aggregation: total, unique, dau, average, sum, ...
    math_property: str | None = None,    # top-level shorthand; Metric() uses property= instead
    per_user: PerUserAggregation | None = None,
    percentile_value: int | float | None = None,
    group_by: str | GroupBy | CohortBreakdown | FrequencyBreakdown | list[...] | None = None,
    where: Filter | FrequencyFilter | list[...] | None = None,
    formula: str | None = None,          # e.g. "(B / A) * 100", requires 2+ events
    formula_label: str | None = None,
    rolling: int | None = None,
    cumulative: bool = False,
    mode: Literal['timeseries', 'total', 'table'] = 'timeseries',
    time_comparison: TimeComparison | None = None,
    data_group_id: int | None = None,
) -> QueryResult:
    # .df columns: timeseries → [date, event, count]
    #              total → [event, count]
    #              with group_by → adds segment column
    ...
```

### Funnel Query

Run `python3 $SKILL_DIR/scripts/help.py Workspace.query_funnel` for the full signature.

```python
def query_funnel(
    self,
    steps: list[str | FunnelStep],      # at least 2 steps required
    *,
    conversion_window: int = 14,
    conversion_window_unit: Literal['second', 'minute', 'hour', 'day', 'week', 'month', 'session'] = 'day',
    order: Literal['loose', 'any'] = 'loose',
    from_date: str | None = None, to_date: str | None = None, last: int = 30,
    unit: QueryTimeUnit = 'day',
    math: FunnelMathType = 'conversion_rate_unique',
    math_property: str | None = None,
    group_by: str | GroupBy | CohortBreakdown | list[...] | None = None,
    where: Filter | list[Filter] | None = None,
    exclusions: list[str | Exclusion] | None = None,
    holding_constant: str | HoldingConstant | list[...] | None = None,
    mode: Literal['steps', 'trends', 'table'] = 'steps',
    reentry_mode: FunnelReentryMode | None = None,
    time_comparison: TimeComparison | None = None,
    data_group_id: int | None = None,
) -> FunnelQueryResult:
    # .df columns: [step, event, count, step_conv_ratio, avg_time]
    # .overall_conversion_rate: float
    ...
```

### Retention Query

Run `python3 $SKILL_DIR/scripts/help.py Workspace.query_retention` for the full signature.

```python
def query_retention(
    self,
    born_event: str | RetentionEvent,
    return_event: str | RetentionEvent,
    *,
    retention_unit: TimeUnit = 'week',
    alignment: RetentionAlignment = 'birth',
    bucket_sizes: list[int] | None = None,
    from_date: str | None = None, to_date: str | None = None, last: int = 30,
    unit: QueryTimeUnit = 'day',
    math: RetentionMathType = 'retention_rate',
    group_by: str | GroupBy | CohortBreakdown | list[...] | None = None,
    where: Filter | list[Filter] | None = None,
    mode: RetentionMode = 'curve',
    unbounded_mode: RetentionUnboundedMode | None = None,
    retention_cumulative: bool = False,
    time_comparison: TimeComparison | None = None,
    data_group_id: int | None = None,
) -> RetentionQueryResult:
    # .df columns: [cohort_date, bucket, count, rate]  (+ segment with group_by)
    # .average: synthetic average across cohorts
    ...
```

### Flow Query

Run `python3 $SKILL_DIR/scripts/help.py Workspace.query_flow` for the full signature.

```python
def query_flow(
    self,
    event: str | FlowStep | Sequence[str | FlowStep],
    *,
    forward: int = 3, reverse: int = 0,
    from_date: str | None = None, to_date: str | None = None, last: int = 30,
    conversion_window: int = 7,
    conversion_window_unit: Literal['day', 'week', 'month', 'session'] = 'day',
    count_type: Literal['unique', 'total', 'session'] = 'unique',
    cardinality: int = 3,
    collapse_repeated: bool = False,
    hidden_events: list[str] | None = None,
    mode: Literal['sankey', 'paths', 'tree'] = 'sankey',
    where: Filter | list[Filter] | None = None,
    segments: str | GroupBy | CohortBreakdown | FrequencyBreakdown | list[...] | None = None,
    exclusions: list[str] | None = None,
    data_group_id: int | None = None,
) -> FlowQueryResult:
    # .df, .graph (NetworkX DiGraph), .anytree (tree mode)
    # .top_transitions(n), .drop_off_summary()
    ...
```

### User Profile Query

Run `python3 $SKILL_DIR/scripts/help.py Workspace.query_user` for the full signature.

```python
def query_user(
    self,
    *,
    where: Filter | list[Filter] | str | None = None,
    cohort: int | CohortDefinition | None = None,
    properties: list[str] | None = None,
    sort_by: str | None = None,
    sort_order: Literal['ascending', 'descending'] = 'descending',
    limit: int | None = 1,              # None = fetch all matching
    search: str | None = None,
    distinct_id: str | None = None,     # single user lookup
    distinct_ids: list[str] | None = None,  # batch lookup
    group_id: str | None = None,        # query group profiles
    as_of: str | int | None = None,     # point-in-time
    mode: Literal['profiles', 'aggregate'] = 'aggregate',
    aggregate: Literal['count', 'extremes', 'percentile', 'numeric_summary'] = 'count',
    aggregate_property: str | None = None,
    percentile: float | None = None,
    segment_by: list[int] | None = None,
    parallel: bool = False, workers: int = 5,
    include_all_users: bool = False,
) -> UserQueryResult:
    # .df, .total, .profiles
    ...
```

### Build Params (without executing)

Same parameters as the corresponding query methods, but return `dict[str, Any]` bookmark params without making an API call. Useful for creating saved reports (bookmarks).

```python
def build_params(self, events, **kwargs) -> dict[str, Any]: ...
def build_funnel_params(self, steps, **kwargs) -> dict[str, Any]: ...
def build_retention_params(self, born_event, return_event, **kwargs) -> dict[str, Any]: ...
def build_flow_params(self, event, **kwargs) -> dict[str, Any]: ...
def build_user_params(self, **kwargs) -> dict[str, Any]: ...
```

### Multi-Step Analysis Patterns

Every query engine has parameters that look like simple settings but are actually analytical choices with outsized influence on results. Before running any query, apply these principles:

- [ ] **Find the master dial.** Each engine has one parameter (or small set) that reshapes all downstream metrics. Changing it changes the story. Know which parameter it is and choose deliberately — don't accept defaults blindly.
- [ ] **Match parameters to the domain.** There are no universal "correct" values. A social app needs daily retention; a B2B SaaS needs monthly. A food-ordering funnel needs a 1-hour window; an onboarding funnel needs 14 days. The product's natural usage cadence dictates the setting.
- [ ] **Distrust averages.** Averages include outliers — one extreme value distorts the whole metric. Use medians (`math='median'`, `percentile=50`) to see what's typical. If the mean and median diverge, the distribution is skewed and the mean is misleading.
- [ ] **Counting methodology is a modeling choice.** "Unique users," "total events," and "sessions" aren't just modes — they answer fundamentally different questions. "How many people?" vs "How much activity?" vs "How many engagement moments?" Choose the counting method that matches the business question.
- [ ] **Know the silent defaults.** Parameters are sometimes silently ignored (e.g., `math_property` with `math='unique'`), silently constraining (e.g., no funnel re-entry by default), or silently inflating (e.g., `unbounded_mode='carry_forward'` in retention). If results look surprising, check whether a default is shaping them.
- [ ] **Sweep, don't guess.** When unsure which parameter value to use, try several and observe how metrics shift. Where the metric stabilizes or diverges reveals the true signal. The code examples below demonstrate this for each engine.

#### Comparing Segments Across Multiple Dimensions

When a single breakdown shows a difference, verify it holds across dimensions:

```python
# Step 1: Find the interesting segment
result = ws.query(event, math='average', math_property='order_total',
                   group_by='deal_sweet_spot', last=90, mode='total')
# Found: deal_sweet_spot=true has 37% higher AOV

# Step 2: Check if it holds across another dimension
result = ws.query(event, math='average', math_property='order_total',
                   group_by=['deal_sweet_spot', 'platform'], last=90, mode='total')
# Does the sweet spot hold for both iOS and Android?

# Step 3: Check segment rates across a third dimension
result = ws.query(event, math='unique',
                   group_by=['loyalty_tier', 'deal_sweet_spot'], last=90, mode='total')
# Which tier is most likely to achieve the sweet spot?
```

#### Insights Analysis: MathType, Per-User, and the Unit of Analysis

**MathType is the most critical Insights parameter.** It defines what you're counting — `total` (event volume), `unique` (user reach), `dau/wau/mau` (time-bounded engagement), `average/median/percentile` (property distributions), `sum` (revenue totals). Choosing the wrong MathType answers the wrong question silently. Match MathType to the business question: engagement → `dau` or `wau`; revenue → `sum` or `average` with `math_property`; adoption → `unique`; intensity → `total`.

**Per-user aggregation is a two-stage process** that fundamentally changes the unit of analysis. `per_user='average'` with `math='average'` first computes each user's average, then averages across users. This is NOT the same as a global average — a power user with 1000 events and a casual user with 2 events contribute equally. This is often the right choice (prevents power users from dominating) but it changes the story dramatically:

```python
# Sweep MathTypes to understand an event from multiple angles
event = 'Purchase'  # use a real event name
prop = 'order_total'  # use a real numeric property

for mt in ['total', 'unique', 'dau', 'average', 'median', 'sum']:
    kwargs = {'math': mt, 'last': 30, 'mode': 'total'}
    if mt in ('average', 'median', 'sum'):
        kwargs['math_property'] = prop
    result = ws.query(event, **kwargs)
    print(f"{mt:>10}: {result.df['count'].iloc[0]:>12,.2f}")
# total = event volume, unique = user reach, dau = daily engagement,
# average/median = typical transaction, sum = total revenue

# Per-user aggregation: compare global average vs per-user average
global_avg = ws.query(event, math='average', math_property=prop, last=30, mode='total')
per_user_avg = ws.query(event, math='average', math_property=prop,
                         per_user='average', last=30, mode='total')
print(f"Global avg: {global_avg.df['count'].iloc[0]:.2f}")
print(f"Per-user avg: {per_user_avg.df['count'].iloc[0]:.2f}")
# If these differ significantly, power users are skewing the global average
```

**Prefer medians over averages for property distributions** — same principle as funnel time-to-convert. Use `math='median'` instead of `math='average'`, or `math='percentile'` with `percentile_value=50`. Averages include outliers; medians reveal what's typical.

**Silent traps:** `math_property` is silently ignored with non-property MathType (e.g., `math='unique'` discards `math_property`). `rolling` reduces data point count without warning (a 30-day rolling window over 59 days produces ~29 points, not 59). `unit` is silently ignored in `mode='total'`.

#### Funnel Analysis: Windows, Modes, and Time

Funnel queries return time data in step metadata columns (`avg_time`, `avg_time_from_start`) alongside conversion rates.

**Conversion window is the most critical funnel parameter.** It defines the maximum time a user has to complete the funnel from their first step. It affects every other metric — conversion rate, time-to-convert, and segment comparisons all shift dramatically with window size.

**Choosing a window:** Match it to the user journey being measured. Short funnels (ordering food, adding to cart) need tight windows — hours, not days. Long funnels (onboarding, subscription purchase) need wider windows — days or weeks. When unsure, experiment:

```python
# Try progressively tighter windows to find where signal emerges
for window, unit in [(14, 'day'), (7, 'day'), (1, 'day'), (12, 'hour'), (6, 'hour')]:
    result = ws.query_funnel(steps, last=90,
        conversion_window=window, conversion_window_unit=unit)
    final = result.df[result.df['step'] == result.df['step'].max()].iloc[0]
    print(f"{window}{unit}: conv={final['overall_conv_ratio']:.3f} "
          f"time={final['avg_time_from_start']/3600:.1f}h")
# Look for: conversion stabilizing, time differences appearing at tighter windows
```

**Conversion counting modes** change what "conversion" means:
- `conversion_rate_unique` (default): unique users who completed. No re-entry — first attempt in the window or out.
- `conversion_rate_total`: total completions. One user can count multiple times.
- Combine with `reentry_mode='basic'` or `reentry_mode='optimized'` for multiple attempts. Optimized re-entry picks the best completion path.

**Time-to-convert: prefer medians over averages.** Average time includes outliers — one slow user inflates the average; one fast user pulls it down. Use median or percentiles for true speed trends:

```python
# Median time via funnel math
result = ws.query_funnel(steps, last=90, math='median')

# Compare segments with filtered funnels + tight window
ios = ws.query_funnel(steps, where=Filter.equals('platform', 'iOS'),
    last=90, conversion_window=6, conversion_window_unit='hour')
android = ws.query_funnel(steps, where=Filter.equals('platform', 'Android'),
    last=90, conversion_window=6, conversion_window_unit='hour')
# Compare avg_time_from_start on matching steps
```

**When comparing segments across funnels:** always try at least 2-3 conversion windows. A difference invisible at 14 days may be stark at 6 hours. This is especially true for speed comparisons — tighter windows filter out noise and reveal which segment completes faster.

**`order` changes what "conversion" means.** `'loose'` (default) requires steps in sequence but allows other events between them. `'any'` requires all steps in any order — a user who does C→B→A counts as converting. The difference is dramatic: loose funnels measure sequential workflows; any-order funnels measure feature adoption breadth. When unsure, run both and compare:

```python
# order='loose' vs 'any' — same steps, fundamentally different questions
for ord in ['loose', 'any']:
    result = ws.query_funnel(steps, last=90, order=ord)
    print(f"order={ord}: {result.overall_conversion_rate:.3f}")
# If 'any' >> 'loose', users are completing all steps but not in the expected order
# This often reveals UX issues — users accomplish the goal but not via the designed path
```

**`holding_constant` isolates cross-step consistency.** Hold a property like `'platform'` or `'device_id'` constant and users who change values between steps (e.g., sign up on iOS, purchase on Android) are excluded. This reveals single-device vs cross-device conversion and is essential for understanding journeys that span platforms. Maximum 3 properties.

**Exclusions disqualify tainted journeys.** `exclusions=["Logout"]` removes users who logged out between funnel steps — unlike flow `hidden_events`, exclusions completely remove users from the funnel. Use for support escalation events, churn signals, or any action that taints the conversion path. Control which steps the exclusion applies to with `Exclusion("Logout", from_step=0, to_step=2)` (0-indexed).

**Per-step filters narrow individual steps without affecting others.** `FunnelStep("Purchase", filters=[Filter.greater_than("amount", 50)])` restricts which Purchase events count, but doesn't filter Signup events. Global `where` filters ALL steps. This distinction is subtle but powerful: filter the population with `where`, filter the definition of a step with per-step filters.

**Session windows are a distinct paradigm.** `conversion_window_unit='session'` constrains the entire funnel to a single engagement session — no multi-session hops. This reveals true in-session conversion behavior, separate from users who spread a journey across days. The third counting mode, `math='conversion_rate_session'`, counts sessions rather than users or events (requires `conversion_window_unit='session'`).

#### Retention Analysis: The Cohort Bucketing Triple

**`retention_unit` + `alignment` + `bucket_sizes` define your entire retention model** — retention's equivalent of the funnel conversion window. `retention_unit` groups users into cohorts (day/week/month). `alignment` anchors cohorts (`birth` = each user's clock starts from their event; `interval_start` = snap to calendar boundaries). `bucket_sizes` sets measurement points. Changing any one reshapes all downstream metrics.

**Match `retention_unit` to your product's natural usage cadence.** Daily products (social, messaging) need `retention_unit='day'`. Weekly products (task management, fitness) need `'week'`. Monthly products (subscriptions, B2B SaaS) need `'month'`. When unsure, experiment:

```python
# Sweep retention_unit to find natural product cadence
born, ret = 'Signup', 'Login'  # use real event names
for ru in ['day', 'week', 'month']:
    result = ws.query_retention(born, ret, retention_unit=ru, last=90)
    avg = result.average
    if avg is not None and len(avg) > 1:
        bucket_1_rate = avg.iloc[1]['rate'] if 'rate' in avg.columns else None
        print(f"{ru:>6} retention: bucket 1 = {bucket_1_rate}")
# The unit where bucket-1 retention is highest reveals natural usage cadence

# Custom buckets for milestone-based retention (days 1, 3, 7, 14, 30)
result = ws.query_retention(born, ret, retention_unit='week',
    bucket_sizes=[1, 3, 7, 14, 30], unit='day', last=90)
print(result.df[result.df['cohort_date'] == '$overall'])
# Day 1 = activation, Day 7 = habit formation, Day 30 = long-term retention

# Compare alignment modes — can shift results dramatically
for align in ['birth', 'interval_start']:
    result = ws.query_retention(born, ret, retention_unit='week',
        alignment=align, last=90)
    print(f"\nalignment={align}:")
    print(result.average.head() if result.average is not None else "No data")
```

**Be wary of unbounded modes — they inflate retention.** `unbounded_mode='carry_forward'` credits future returns to past buckets — a user who returns only on day 30 gets counted as retained in all buckets from 30 onward. `carry_back` inflates early buckets instead. Useful for "did they ever engage?" analysis but distorts standard retention curves.

**`retention_cumulative=True` masks re-engagement gaps.** Cumulative retention creates monotonically increasing curves where each bucket includes all prior buckets. This hides whether users who returned in week 1 ALSO returned in week 2. Standard (non-cumulative) retention reveals re-engagement patterns and true habit formation.

**Counting methodology:** `math='retention_rate'` (% who returned — the default), `math='unique'` (count who returned), `math='total'` (how many times they returned — events, not users). `total` reveals engagement intensity; a user logging in 5 times in bucket 1 counts as 5, not 1. Like funnels, the counting choice changes the question.

#### Flow Analysis: Windows, Cardinality, and Signal-to-Noise

**Cardinality controls signal-to-noise** — the most important flow-specific parameter. Low cardinality (2-3) reveals dominant paths — the main story. High cardinality (10+) reveals edge cases and niche journeys. Start low to find the narrative, then increase to find exceptions.

**`conversion_window` matters for flows too** — identical concept to funnels. Session-based windows (`conversion_window_unit='session'`) reveal in-app behavior within a single engagement. Calendar windows reveal multi-day journeys. A tight window isolates intentional workflows; a wide window captures exploratory meandering:

```python
# Sweep cardinality to find signal-to-noise sweet spot
event = 'Login'  # use a real anchor event
for card in [2, 3, 5, 10]:
    result = ws.query_flow(event, forward=3, cardinality=card, last=30)
    transitions = result.top_transitions(5)
    print(f"\ncardinality={card}: {len(transitions)} top transitions")
    for src, dst, count in transitions[:3]:
        print(f"  {src} → {dst}: {count}")
# Low cardinality = clear narrative; high cardinality = exhaustive but noisy

# Compare count types (same principle as funnels)
for ct in ['unique', 'total', 'session']:
    result = ws.query_flow(event, forward=3, count_type=ct, last=30)
    dropoff = result.drop_off_summary()
    print(f"\n{ct}: step 0 dropoff = {dropoff}")
# unique = how many people; total = how much activity; session = how many sessions

# Compare collapse_repeated to separate intent from noise
for collapse in [False, True]:
    result = ws.query_flow(event, forward=3, collapse_repeated=collapse,
                            cardinality=5, last=30)
    print(f"\ncollapse_repeated={collapse}:")
    for src, dst, count in result.top_transitions(3):
        print(f"  {src} → {dst}: {count}")
```

**`collapse_repeated` changes what "a path" means.** With `False` (default), A→A→A→B is a distinct path from A→B — repetitive clicks look like distinct journeys. With `True`, consecutive duplicates merge, revealing intent over noise. Toggle this to see both the raw behavior and the simplified user intent.

**`hidden_events` vs `exclusions` — hiding vs disqualifying.** `hidden_events` removes events from display but they still affect path structure and counts. `exclusions` disqualifies users who performed those events entirely — a much stronger operation. Use `hidden_events` for decluttering (e.g., ubiquitous page views); use `exclusions` for removing tainted journeys (e.g., users who churned mid-flow).

**Three modes reveal different stories.** `sankey` shows aggregate flow structure and bottlenecks (where do most users go?). `paths` shows exact user journeys in sequence (what are the top 5 complete paths?). `tree` shows branching decision points (where do users diverge?). Use all three on the same data to build a complete picture.

#### User Profile Analysis: Modes, Aggregates, and Distribution Shape

**`mode` is the most critical user query parameter.** `'profiles'` returns individual user records (one row per user). `'aggregate'` returns a single statistic. These are fundamentally different operations — profiles is a data extraction, aggregate is a calculation. Aggregate is also dramatically faster (single API call vs paginated fetching).

**Sweep aggregate functions to understand distribution shape** before building expensive profile queries. `count` tells you "how many." `extremes` reveals range (min/max). `percentile` at 50 gives median. `numeric_summary` gives mean, variance, and sum-of-squares:

```python
# Sweep aggregate functions to understand a property's distribution
prop = 'lifetime_value'  # use a real numeric profile property
for agg in ['count', 'extremes', 'percentile', 'numeric_summary']:
    kwargs = {'mode': 'aggregate', 'aggregate': agg}
    if agg != 'count':
        kwargs['aggregate_property'] = prop
    if agg == 'percentile':
        kwargs['percentile'] = 50  # median
    result = ws.query_user(**kwargs)
    print(f"{agg:>16}: {result.aggregate_data}")
# count = population size, extremes = range, percentile@50 = median,
# numeric_summary = full distribution stats
# If mean (from numeric_summary) >> median (from percentile), distribution is right-skewed

# Point-in-time comparison with as_of
today_count = ws.query_user(mode='aggregate', aggregate='count',
    where=Filter.equals('plan', 'premium'))
past_count = ws.query_user(mode='aggregate', aggregate='count',
    where=Filter.equals('plan', 'premium'), as_of='2025-01-01')
print(f"Premium users: {past_count.value} (Jan 1) → {today_count.value} (today)")
```

**Prefer medians over averages** — same principle as funnels and Insights. `aggregate='percentile', percentile=50` gives median; `numeric_summary` gives mean. If they diverge significantly, the distribution is skewed and the mean is misleading.

**`as_of` enables temporal analysis** — query profiles as they existed at a past date. Compare population states over time: "how many premium users existed on Jan 1 vs today?" Without `as_of`, you always see current state, making growth and churn invisible.

**Inline `CohortDefinition` vs saved cohorts.** Inline cohorts (`cohort=CohortDefinition.all_of(...)`) let you define complex behavioral segments on-the-fly without roundtripping to save/delete in Mixpanel. Much faster iteration for exploratory analysis. Use saved cohorts for production dashboards and monitoring.

#### Analytical Building Blocks: Custom Properties, Cohorts, and Frequency

Raw data is rarely analysis-ready. These three tools transform raw events and properties into analytically useful dimensions, populations, and segments. Recognize when to reach for each — they compose with every query engine.

**Inline Custom Properties — transform data at query time.** When property values are messy, need bucketing, or you need to derive new dimensions, create an `InlineCustomProperty` rather than querying raw values. Key patterns:

- **Bucketing continuous values** for breakdowns (revenue → Low/Medium/High)
- **Cleaning messy strings** with IFS/REGEX_EXTRACT (campaign names, UTM parameters)
- **Deriving new dimensions** from arithmetic or date functions (profit margin, days since signup)
- **Fallback chains** across multiple properties (display_name → username → "unknown")

```python
from mixpanel_headless import InlineCustomProperty, PropertyInput, GroupBy, Filter, Metric

# Bucket revenue into tiers for breakdown
revenue_tier = InlineCustomProperty(
    formula='IFS(A < 50, "Low", A < 200, "Medium", TRUE, "High")',
    inputs={"A": PropertyInput("revenue", type="number")},
    property_type="string",
)
result = ws.query("Purchase", group_by=GroupBy(property=revenue_tier), last=30, mode='total')

# Derive profit margin for aggregation
margin = InlineCustomProperty.numeric("(A - B) / A * 100", A="revenue", B="cost")
result = ws.query(Metric("Purchase", math="average", property=margin), last=30)

# Clean messy strings for segmentation
domain = InlineCustomProperty(
    formula='REGEX_EXTRACT(A, "@(.+)$")',
    inputs={"A": PropertyInput("email", type="string")},
    property_type="string",
)
result = ws.query("Signup", group_by=GroupBy(property=domain), last=30, mode='total')
```

Use `InlineCustomProperty` for ad-hoc exploration. When a formula proves valuable, persist it with `ws.create_custom_property()` and reference it via `CustomPropertyRef(id)` across reports.

**Inline Cohorts — define complex populations on-the-fly.** Every analytical question starts with "among WHICH users?" Simple property filters (`where=Filter.equals(...)`) answer "users with attribute X." Inline cohorts answer harder questions: "users who did X at least N times in the last D days AND did NOT do Y AND have property Z." Compose criteria with AND/OR logic:

```python
from mixpanel_headless import CohortDefinition, CohortCriteria, CohortBreakdown, CohortMetric

# "Power users": purchased 5+ times in 30 days, never contacted support
power_users = CohortDefinition.all_of(
    CohortCriteria.did_event("Purchase", at_least=5, within_days=30),
    CohortCriteria.did_not_do_event("Support Ticket", within_days=90),
)

# Use inline cohort as a breakdown — no need to save first
result = ws.query("Login", group_by=CohortBreakdown(power_users, "Power Users"), last=30)

# Use inline cohort as a filter in user queries
result = ws.query_user(cohort=power_users, mode='aggregate', aggregate='count')

# Track saved cohort size over time alongside event metrics
result = ws.query(
    [Metric("Login", math="unique"), CohortMetric(saved_cohort_id, "Power Users")],
    formula="(B / A) * 100", formula_label="% Power Users Active", last=90,
)
```

**Frequency Breakdown/Filter — segment by behavioral intensity.** `FrequencyBreakdown` answers "how do users who did X once differ from users who did X ten times?" `FrequencyFilter` restricts queries to users meeting a frequency threshold. These bridge "what users did" with "who users are":

```python
from mixpanel_headless import FrequencyBreakdown, FrequencyFilter

# Break down login behavior by purchase frequency
result = ws.query("Login", math='unique',
    group_by=FrequencyBreakdown("Purchase", bucket_size=3, bucket_min=0, bucket_max=15),
    last=30, mode='total')
# Reveals: do frequent purchasers also log in more?

# Filter to users who purchased 3+ times in 30 days, then analyze their flow
result = ws.query_flow("Login", forward=3,
    where=FrequencyFilter("Purchase", value=3, date_range_value=30, date_range_unit="day"),
    last=30)
# Reveals: what do repeat purchasers do after logging in?
```

**When to reach for each:**
- Property values are messy or need derivation → **Custom Property**
- Population requires behavioral criteria (did X, didn't do Y, frequency thresholds) → **Inline Cohort**
- You need to segment by event frequency (how often, not just whether) → **FrequencyBreakdown/Filter**
- You need to compare in-cohort vs out-of-cohort behavior → **CohortBreakdown** with `include_negated=True`
- You need to track a segment's size as a time series → **CohortMetric** (saved cohorts only)

### Legacy Queries & Counts

These use older APIs. Prefer the typed query methods above when possible.

```python
def segmentation(self, event: str, *, from_date: str, to_date: str, on: str | None = None, unit: Literal['day', 'week', 'month'] = 'day', where: str | None = None) -> SegmentationResult: ...
def funnel(self, funnel_id: int, *, from_date: str, to_date: str, unit: str | None = None, on: str | None = None) -> FunnelResult: ...
def retention(self, *, born_event: str, return_event: str, from_date: str, to_date: str, born_where: str | None = None, return_where: str | None = None, interval: int = 1, interval_count: int = 10, unit: Literal['day', 'week', 'month'] = 'day') -> RetentionResult: ...
def event_counts(self, events: list[str], *, from_date: str, to_date: str, type: Literal['general', 'unique', 'average'] = 'general', unit: Literal['day', 'week', 'month'] = 'day') -> EventCountsResult: ...
def property_counts(self, event: str, property_name: str, *, from_date: str, to_date: str, type: Literal['general', 'unique', 'average'] = 'general', unit: Literal['day', 'week', 'month'] = 'day', values: list[str] | None = None, limit: int | None = None) -> PropertyCountsResult: ...
def frequency(self, *, from_date: str, to_date: str, unit: Literal['day', 'week', 'month'] = 'day', addiction_unit: Literal['hour', 'day'] = 'hour', event: str | None = None, where: str | None = None) -> FrequencyResult: ...
def activity_feed(self, distinct_ids: list[str], *, from_date: str | None = None, to_date: str | None = None) -> ActivityFeedResult: ...
def query_saved_report(self, bookmark_id: int, *, bookmark_type: Literal['insights', 'funnels', 'retention', 'flows'] = 'insights', from_date: str | None = None, to_date: str | None = None) -> SavedReportResult: ...
def query_saved_flows(self, bookmark_id: int) -> FlowsResult: ...
def segmentation_numeric(self, event: str, *, from_date: str, to_date: str, on: str, unit: Literal['hour', 'day'] = 'day', where: str | None = None, type: Literal['general', 'unique', 'average'] = 'general') -> NumericBucketResult: ...
def segmentation_sum(self, event: str, *, from_date: str, to_date: str, on: str, unit: Literal['hour', 'day'] = 'day', where: str | None = None) -> NumericSumResult: ...
def segmentation_average(self, event: str, *, from_date: str, to_date: str, on: str, unit: Literal['hour', 'day'] = 'day', where: str | None = None) -> NumericAverageResult: ...
```

### Entity CRUD (App API)

All entity methods require a workspace ID. Use `python3 $SKILL_DIR/scripts/help.py Workspace.<method>` for full signatures and parameter types.
User Guide: `WebFetch(url="https://mixpanel.github.io/mixpanel-headless/guide/entity-management/index.md")`

#### Dashboard (→ `Dashboard`)

`list_dashboards`, `create_dashboard`, `get_dashboard`, `update_dashboard`, `delete_dashboard`, `bulk_delete_dashboards`, `favorite_dashboard`, `unfavorite_dashboard`, `pin_dashboard`, `unpin_dashboard`, `add_report_to_dashboard`, `remove_report_from_dashboard`, `update_text_card`, `update_report_link`

**Blueprints:** `list_blueprint_templates` → `list[BlueprintTemplate]`, `create_blueprint`, `get_blueprint_config`, `update_blueprint_cohorts`, `finalize_blueprint`, `create_rca_dashboard`

**Helpers:** `get_bookmark_dashboard_ids` → `list[int]`, `get_dashboard_erf` → `dict`

#### Bookmark / Report (→ `Bookmark`)

`list_bookmarks_v2`, `create_bookmark`, `get_bookmark`, `update_bookmark`, `delete_bookmark`, `bulk_delete_bookmarks`, `bulk_update_bookmarks`, `bookmark_linked_dashboard_ids` → `list[int]`, `get_bookmark_history` → `BookmarkHistoryResponse`

#### Cohort (→ `Cohort`)

`list_cohorts_full`, `get_cohort`, `create_cohort`, `update_cohort`, `delete_cohort`, `bulk_delete_cohorts`, `bulk_update_cohorts`

#### Feature Flag (→ `FeatureFlag`)

`list_feature_flags`, `create_feature_flag`, `get_feature_flag`, `update_feature_flag`, `delete_feature_flag`, `archive_feature_flag`, `restore_feature_flag`, `duplicate_feature_flag`, `set_flag_test_users`, `get_flag_history` → `FlagHistoryResponse`, `get_flag_limits` → `FlagLimitsResponse`

#### Experiment (→ `Experiment`)

`list_experiments`, `create_experiment`, `get_experiment`, `update_experiment`, `delete_experiment`, `launch_experiment`, `conclude_experiment`, `decide_experiment`, `archive_experiment`, `restore_experiment`, `duplicate_experiment`, `list_erf_experiments` → `list[dict]`

#### Alert (→ `CustomAlert`)

`list_alerts`, `create_alert`, `get_alert`, `update_alert`, `delete_alert`, `bulk_delete_alerts`, `get_alert_count` → `AlertCount`, `get_alert_history` → `AlertHistoryResponse`, `test_alert`, `get_alert_screenshot_url`, `validate_alerts_for_bookmark`

#### Annotation (→ `Annotation`)

`list_annotations`, `create_annotation`, `get_annotation`, `update_annotation`, `delete_annotation`, `list_annotation_tags` → `list[AnnotationTag]`, `create_annotation_tag`

#### Webhook (→ `ProjectWebhook`)

`list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `test_webhook`

#### Lexicon & Data Governance

**Event/Property Definitions:** `get_event_definitions`, `update_event_definition`, `delete_event_definition`, `bulk_update_event_definitions`, `get_property_definitions`, `update_property_definition`, `bulk_update_property_definitions`, `export_lexicon`, `get_event_history`, `get_property_history`

**Tags:** `list_lexicon_tags`, `create_lexicon_tag`, `update_lexicon_tag`, `delete_lexicon_tag`

**Drop Filters:** `list_drop_filters`, `create_drop_filter`, `update_drop_filter`, `delete_drop_filter`, `get_drop_filter_limits`

**Custom Properties:** `list_custom_properties`, `create_custom_property`, `get_custom_property`, `update_custom_property`, `delete_custom_property`, `validate_custom_property`

**Custom Events:** `list_custom_events`, `update_custom_event`, `delete_custom_event`

**Lookup Tables:** `list_lookup_tables`, `upload_lookup_table`, `download_lookup_table`, `update_lookup_table`, `delete_lookup_tables`

**Schema Registry:** `list_schema_registry`, `create_schema`, `update_schema`, `create_schemas_bulk`, `update_schemas_bulk`, `delete_schemas`

**Schema Enforcement:** `get_schema_enforcement`, `init_schema_enforcement`, `update_schema_enforcement`, `replace_schema_enforcement`, `delete_schema_enforcement`

**Audit & Monitoring:** `run_audit`, `run_audit_events_only`, `list_data_volume_anomalies`, `update_anomaly`, `bulk_update_anomalies`

**Data Deletion:** `list_deletion_requests`, `create_deletion_request`, `cancel_deletion_request`, `preview_deletion_filters`

**Other:** `get_tracking_metadata`

### Business Context

Read and write the markdown documentation that grounds AI assistants in your organization's structure and goals, exposed as a typed Python API.

Two scopes — `level="organization"` (shared across the whole org) and `level="project"` (per-project). 50,000-character cap enforced **client-side before any HTTP call** so oversize input fails fast. Org-level operations auto-resolve `organization_id` from the cached `/me` response; pass `organization_id=N` to override.

Run `python3 $SKILL_DIR/scripts/help.py search business_context` to see all four methods, two types, and one exception.

```python
from mixpanel_headless import BUSINESS_CONTEXT_MAX_CHARS  # 50_000

# Read
project_ctx = ws.get_business_context(level="project")
org_ctx = ws.get_business_context(level="organization")  # auto-resolves org_id
explicit = ws.get_business_context(level="organization", organization_id=42)

# Read both at once (single round-trip via /business-context/chain)
chain = ws.get_business_context_chain()
print(chain.organization.content)
print(chain.project.content)

# Write (full-replace; pass "" to clear, or use clear_business_context())
ws.set_business_context("# About Acme\n…", level="project")
ws.set_business_context("# Org-wide standards", level="organization")
ws.clear_business_context(level="project")

# All return BusinessContext with: level, content, organization_id, project_id
# Plus convenience .is_empty and .character_count properties (Python only)
print(f"{project_ctx.character_count}/{BUSINESS_CONTEXT_MAX_CHARS} chars; "
      f"empty={project_ctx.is_empty}")
```

**When to reach for this:**

- User asks "what's the business context for this project/org?" → `get_business_context_chain()`
- User wants to version-control project context as a `.md` file → `ws.set_business_context(Path("ctx.md").read_text(), level="project")` in CI
- User asks to "audit which projects have AI context configured" → iterate `ws.projects()` + `ws.use(project=...)` + `ws.get_business_context(level="project")` and check `.is_empty`
- User asks to seed a new project from the org default → `chain = ws.get_business_context_chain(); ws.set_business_context(chain.organization.content, level="project")`

**Permissions:** project-scope reads need any project access; project-scope writes need `edit_project_info` on the project. Org-scope writes need `edit_project_info` at the org level (typically OAuth, not service account). The `BusinessContextValidationError` exception is raised client-side BEFORE any HTTP call when content exceeds 50,000 chars, so use it to detect oversize input without burning a round-trip.

User Guide: `WebFetch(url="https://mixpanel.github.io/mixpanel-headless/guide/business-context/index.md")`

## Key Types

Run `python3 $SKILL_DIR/scripts/help.py types` for the full list of all types. Use `help.py <TypeName>` for fields, constructors, and enum values.
Full reference: `WebFetch(url="https://mixpanel.github.io/mixpanel-headless/api/types/index.md")`

| Type | Purpose |
|------|---------|
| `Filter` | Property filter conditions (`.equals()`, `.contains()`, `.in_cohort()`, etc.) |
| `GroupBy` | Property breakdown with optional bucketing |
| `Formula` | Calculated metric expression referencing events by position (A, B, C...) |
| `Metric` | Event with per-event math/aggregation settings |
| `CohortMetric` | Track cohort size over time as an event metric |
| `FunnelStep` | Funnel step with per-step filters, labels, ordering |
| `Exclusion` | Event to exclude between funnel steps |
| `HoldingConstant` | Property to hold constant across funnel steps |
| `RetentionEvent` | Retention event with per-event filters |
| `FlowStep` | Flow anchor event with per-step forward/reverse configuration |
| `TimeComparison` | Period-over-period comparison (`.relative("month")`, `.absolute_start(...)`) |
| `FrequencyBreakdown` | Break down by how often users performed an event |
| `FrequencyFilter` | Filter by how often users performed an event |
| `CohortBreakdown` | Break down results by cohort membership |
| `CohortDefinition` | Inline cohort definition for user queries |
| `CohortCriteria` | Atomic condition for cohort membership |
| `CustomPropertyRef` | Reference to a persisted custom property by ID |
| `InlineCustomProperty` | Ephemeral computed property defined by formula |

**Aggregation enums** (use `help.py <EnumName>` to see all values):

| Enum | Used by | Common values |
|------|---------|---------------|
| `MathType` | `query()` | total, unique, dau, average, sum, min, max, percentile, sessions |
| `FunnelMathType` | `query_funnel()` | conversion_rate_unique, conversion_rate_total, average, median |
| `RetentionMathType` | `query_retention()` | retention_rate, retention_count |

## Statistical Analysis — numpy, scipy

All query results produce pandas DataFrames, which integrate directly with numpy and scipy:

```python
import numpy as np
from scipy import stats

# Compare two segments
a = result.df[result.df["platform"] == "iOS"]["count"]
b = result.df[result.df["platform"] == "Android"]["count"]
t_stat, p_value = stats.ttest_ind(a, b)
cohens_d = (a.mean() - b.mean()) / np.sqrt((a.std()**2 + b.std()**2) / 2)

# Useful scipy.stats tests: ttest_ind, mannwhitneyu, chi2_contingency, pearsonr, spearmanr
# Useful numpy: np.percentile, np.corrcoef, np.polyfit (trend lines)
```

## Visualization — matplotlib, seaborn

Save charts to files for the user. Always use a non-interactive backend:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots(figsize=(10, 5))
result.df.plot(x="date", y="count", ax=ax)
ax.set_title("Daily Logins")
fig.savefig("chart.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# seaborn: sns.lineplot, sns.barplot, sns.heatmap (for retention matrices)
# Multi-panel: fig, axes = plt.subplots(2, 2) for dashboard-style layouts
```

## Exceptions

Full reference: `WebFetch(url="https://mixpanel.github.io/mixpanel-headless/api/exceptions/index.md")`

| Exception | When |
|-----------|------|
| `MixpanelHeadlessError` | Base for all errors |
| `ConfigError` | No credentials resolved |
| `AccountNotFoundError` | Named account doesn't exist |
| `AuthenticationError` | Invalid credentials (401) |
| `QueryError` | Invalid query parameters (400) |
| `BookmarkValidationError` | Params failed validation |
| `RateLimitError` | Rate limit exceeded (429) |
| `ServerError` | Mixpanel server error (5xx) |
| `WorkspaceScopeError` | Workspace resolution error (also raised when org_id can't be auto-resolved for `level="organization"` business-context calls) |
| `DateRangeTooLargeError` | Date range exceeds API maximum |
| `OAuthError` | OAuth flow error |
| `BusinessContextValidationError` | Business context content exceeds 50,000 chars (client-side, before HTTP) |
