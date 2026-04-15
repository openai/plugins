# Search Patterns for Duplicate Detection

Effective JQL patterns for finding duplicate bugs and similar issues.

---

## Error-Based Search Patterns

### Exception Searches

**For Java/Backend exceptions:**
```jql
project = "PROJ" AND text ~ "NullPointerException" AND type = Bug ORDER BY created DESC
```

**For specific class/method:**
```jql
project = "PROJ" AND text ~ "PaymentProcessor processRefund" AND type = Bug ORDER BY created DESC
```

**For HTTP errors:**
```jql
project = "PROJ" AND (text ~ "500 error" OR summary ~ "500") AND type = Bug ORDER BY updated DESC
```

### Timeout Searches

**General timeout:**
```jql
project = "PROJ" AND (text ~ "timeout" OR summary ~ "timeout") AND type = Bug ORDER BY priority DESC
```

**Specific timeout type:**
```jql
project = "PROJ" AND text ~ "connection timeout" AND component = "API" ORDER BY created DESC
```

---

## Component-Based Search Patterns

### By System Component

**Authentication:**
```jql
project = "PROJ" AND text ~ "authentication login" AND type = Bug AND status != Done
```

**Payment:**
```jql
project = "PROJ" AND (component = "Payment" OR text ~ "payment checkout") AND type = Bug
```

**Mobile:**
```jql
project = "PROJ" AND (text ~ "mobile iOS" OR text ~ "mobile Android") AND type = Bug ORDER BY updated DESC
```

### By Functionality

**Upload/Download:**
```jql
project = "PROJ" AND (text ~ "upload" OR text ~ "download") AND type = Bug
```

**Database:**
```jql
project = "PROJ" AND text ~ "database query SQL" AND type = Bug ORDER BY created DESC
```

---

## Symptom-Based Search Patterns

### User-Facing Symptoms

**Page/Screen issues:**
```jql
project = "PROJ" AND (summary ~ "blank page" OR summary ~ "white screen") AND type = Bug
```

**Loading issues:**
```jql
project = "PROJ" AND (summary ~ "infinite loading" OR summary ~ "stuck loading") AND type = Bug
```

**Data issues:**
```jql
project = "PROJ" AND (summary ~ "data not saving" OR summary ~ "data lost") AND type = Bug
```

### Performance Symptoms

**Slow performance:**
```jql
project = "PROJ" AND (text ~ "slow" OR summary ~ "performance") AND type = Bug ORDER BY priority DESC
```

**Crashes:**
```jql
project = "PROJ" AND (summary ~ "crash" OR text ~ "application crash") AND type = Bug ORDER BY created DESC
```

---

## Time-Based Search Patterns

### Recent Issues (Last 30 Days)

```jql
project = "PROJ" AND text ~ "error keywords" AND type = Bug AND created >= -30d ORDER BY created DESC
```

### Recently Updated

```jql
project = "PROJ" AND text ~ "error keywords" AND type = Bug AND updated >= -7d ORDER BY updated DESC
```

### Recently Resolved

```jql
project = "PROJ" AND text ~ "error keywords" AND type = Bug AND status = Done AND resolved >= -90d ORDER BY resolved DESC
```

---

## Combined Search Patterns

### High-Priority Recent

```jql
project = "PROJ" AND text ~ "error" AND type = Bug AND priority IN ("Highest", "High") AND created >= -60d ORDER BY priority DESC, created DESC
```

### Component + Error Type

```jql
project = "PROJ" AND component = "API" AND text ~ "timeout" AND type = Bug ORDER BY updated DESC
```

### Environment-Specific

```jql
project = "PROJ" AND text ~ "production" AND text ~ "error keywords" AND type = Bug ORDER BY created DESC
```

---

## Advanced Patterns for Regression Detection

### Previously Resolved

```jql
project = "PROJ" AND text ~ "error keywords" AND type = Bug AND status = Done AND resolution = Fixed ORDER BY resolved DESC
```

### Reopened Issues

```jql
project = "PROJ" AND text ~ "error keywords" AND type = Bug AND status = Reopened ORDER BY updated DESC
```

### Similar Fix History

```jql
project = "PROJ" AND text ~ "error keywords" AND type = Bug AND (status = Resolved OR status = Closed) AND resolved >= -180d ORDER BY resolved DESC
```

---

## Multi-Angle Search Strategy

For thorough duplicate detection, run searches in this order:

**1. Exact error signature (narrow):**
```jql
project = "PROJ" AND summary ~ "exact error text" AND type = Bug ORDER BY created DESC
```

**2. Error type + component (medium):**
```jql
project = "PROJ" AND text ~ "error type" AND component = "ComponentName" AND type = Bug ORDER BY updated DESC
```

**3. Symptom-based (broad):**
```jql
project = "PROJ" AND summary ~ "user symptom" AND type = Bug ORDER BY priority DESC
```

**4. Historical (regression check):**
```jql
project = "PROJ" AND text ~ "keywords" AND type = Bug AND status = Done ORDER BY resolved DESC
```

---

## Field Selection for Triage

Always request these fields for effective analysis:

```
fields: ["summary", "description", "status", "resolution", "priority", "created", "updated", "resolved", "assignee", "reporter", "components"]
```

**Why each field matters:**
- `summary` - Quick identification of duplicate
- `description` - Detailed error matching
- `status` - Know if open/resolved
- `resolution` - How it was fixed (if resolved)
- `priority` - Severity assessment
- `created` - Age of issue
- `updated` - Recent activity
- `resolved` - When it was fixed
- `assignee` - Who fixed it or is working on it
- `reporter` - Original reporter
- `components` - Affected system parts

---

## Tips for Better Search Results

### Use Key Terms Only

✅ Good:
- "timeout login"
- "NullPointerException PaymentProcessor"
- "500 error API"

❌ Too Verbose:
- "users are experiencing a timeout when trying to login"
- "we got a NullPointerException in the PaymentProcessor class"

### Combine Searches

Don't rely on a single search. Run 2-3 searches with different angles:
1. Error-focused
2. Component-focused
3. Symptom-focused

### Order Strategically

- Recent first: `ORDER BY created DESC`
- Active first: `ORDER BY updated DESC`
- Important first: `ORDER BY priority DESC, updated DESC`

### Limit Results

- Use `maxResults=20` for initial searches
- Don't overwhelm with 100+ results
- Focus on top 10-15 most relevant

---

## Common Pitfalls to Avoid

❌ Searching with full stack traces (too specific, no matches)
❌ Using only exact text matching (miss paraphrased duplicates)
❌ Ignoring resolved issues (miss regressions)
❌ Not checking multiple projects (duplicate across teams)
❌ Only searching summaries (miss details in descriptions)
