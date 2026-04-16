# Bug Report Templates

High-quality bug report templates for different types of issues.

---

## Template 1: Backend Error

**Summary Format:**
```
[Service/Component]: [Error Type] in [Functionality]
```

**Examples:**
- Payment API: NullPointerException in refund processing
- Auth Service: TimeoutError during token validation
- Database: Connection pool exhausted in user queries

**Description Template:**
```markdown
## Issue Description
[Brief 1-2 sentence description]

## Error Details
```
[Error message or exception]
Stack trace:
[Stack trace if available]
```

## Environment
- **Service:** [e.g., Payment Service v2.3.4]
- **Environment:** [Production/Staging]
- **Server:** [e.g., us-east-1 pod-7]
- **Timestamp:** [When it occurred]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Impact
- **Frequency:** [e.g., Every time, 10% of requests]
- **Affected Requests:** [e.g., ~500 requests/hour]
- **User Impact:** [e.g., Refunds cannot be processed]

## Logs
```
[Relevant log excerpts]
```

## Related Issues
[Any similar past issues]

---
*Reported via automated triage*
```

---

## Template 2: Frontend/UI Issue

**Summary Format:**
```
[Platform] [Component]: [Symptom]
```

**Examples:**
- iOS App Login: Screen remains blank after successful auth
- Web Dashboard: Infinite loading spinner on reports
- Android App: Crash when uploading photos

**Description Template:**
```markdown
## Issue Description
[Brief description of the visible problem]

## Environment
- **Platform:** [iOS/Android/Web]
- **Version:** [App/Browser version]
- **OS:** [e.g., iOS 16.5, Windows 11, macOS 13]
- **Device:** [e.g., iPhone 14 Pro, Chrome on Desktop]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Visual Evidence
[Screenshots or screen recording if available]

## User Impact
- **Frequency:** [e.g., Every time, Intermittent]
- **Affected Users:** [e.g., All iOS users, Only Safari users]
- **Severity:** [e.g., Cannot complete checkout, Minor visual glitch]

## Console Errors
```
[Browser console errors if applicable]
```

## Additional Context
[Network conditions, user permissions, etc.]

## Related Issues
[Any similar past issues]

---
*Reported via automated triage*
```

---

## Template 3: Performance Issue

**Summary Format:**
```
[Component]: [Performance Problem] - [Context]
```

**Examples:**
- Dashboard: Slow page load (15+ seconds) on reports
- API: Response time degradation under load
- Database: Query timeout on user search

**Description Template:**
```markdown
## Issue Description
[Brief description of the performance problem]

## Performance Metrics
- **Current:** [e.g., 15 second load time]
- **Expected:** [e.g., < 2 seconds]
- **Baseline:** [e.g., Was 1.5s last week]

## Environment
- **Platform:** [Where observed]
- **Environment:** [Production/Staging]
- **Time Observed:** [When it was slow]
- **Load:** [Concurrent users, request rate]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. Observe slow response

## Performance Data
```
[Response times, profiling data, slow query logs]
```

## Impact
- **Affected Users:** [e.g., All users during peak hours]
- **Frequency:** [e.g., Consistently slow, Only during peak]
- **Business Impact:** [e.g., Increased bounce rate, User complaints]

## Suspected Cause
[If you have a hypothesis]

## Related Issues
[Any similar past performance issues]

---
*Reported via automated triage*
```

---

## Template 4: Data Issue

**Summary Format:**
```
[Component]: [Data Problem] - [Scope]
```

**Examples:**
- User Profile: Data not persisting after save
- Orders: Missing order items in history
- Reports: Incorrect calculations in revenue report

**Description Template:**
```markdown
## Issue Description
[Brief description of the data problem]

## Data Issue Details
- **What's Wrong:** [e.g., Orders missing from history]
- **Expected Data:** [What should be there]
- **Actual Data:** [What is actually there]
- **Data Loss/Corruption:** [Scope of issue]

## Environment
- **Environment:** [Production/Staging]
- **Affected Records:** [e.g., All orders from Dec 1-5]
- **First Observed:** [When issue started]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. Observe incorrect/missing data

## Examples
**Affected Record:** Order #12345
**Expected:** [Expected data state]
**Actual:** [Actual data state]

## Impact
- **Affected Users:** [e.g., ~500 customers]
- **Data Integrity:** [e.g., Historical data lost]
- **Business Impact:** [e.g., Cannot fulfill orders]

## Database Queries
```sql
[Queries showing the issue if applicable]
```

## Related Issues
[Any similar past data issues]

---
*Reported via automated triage*
```

---

## Template 5: Integration Issue

**Summary Format:**
```
[Integration]: [Error] - [External Service]
```

**Examples:**
- Stripe Integration: Payment processing fails
- Auth0: Token validation timeout
- Sendgrid: Email sending fails with 429 error

**Description Template:**
```markdown
## Issue Description
[Brief description of the integration problem]

## Integration Details
- **External Service:** [e.g., Stripe API]
- **Integration Point:** [e.g., Payment processing endpoint]
- **API Version:** [If known]

## Error Response
```
HTTP Status: [e.g., 429, 500]
Response Body:
[Error response from external service]
```

## Environment
- **Environment:** [Production/Staging]
- **Our Version:** [Our service version]
- **Time Observed:** [When it started failing]

## Steps to Reproduce
1. [Step that triggers integration]
2. [Expected external service response]
3. Observe failure

## Expected Behavior
[What should happen with external service]

## Actual Behavior
[What is actually happening]

## Impact
- **Frequency:** [e.g., 100% of payment attempts]
- **Affected Transactions:** [e.g., ~200 failed payments/hour]
- **User Impact:** [e.g., Cannot complete checkout]

## External Service Status
[Check if external service has known issues]

## Logs
```
[Our logs showing the integration failure]
```

## Related Issues
[Any past integration issues with this service]

---
*Reported via automated triage*
```

---

## Template 6: Regression (Previously Fixed)

**Summary Format:**
```
[Component]: [Issue] - Regression of PROJ-XXX
```

**Examples:**
- Login: Session timeout after 15min - Regression of PROJ-234
- Upload: File size limit error - Regression of PROJ-567

**Description Template:**
```markdown
## Issue Description
[Brief description - note this was previously fixed]

⚠️ **This appears to be a regression of [PROJ-XXX]**, which was resolved on [date].

## Original Issue
**Original Ticket:** [PROJ-XXX](link)
**Originally Fixed By:** @username
**Fix Date:** [date]
**Original Fix:** [Brief description of what was fixed]

## Current Issue
[Description of the current occurrence]

## Environment
- **Environment:** [Production/Staging]
- **Version:** [Current version]
- **First Observed:** [When regression appeared]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. Observe issue is back

## Expected Behavior
[Should remain fixed as per PROJ-XXX]

## Actual Behavior
[Issue has returned]

## Impact
[Current impact of regression]

## Possible Causes
[Speculation about what might have caused regression]
- Recent deployment on [date]?
- Configuration change?
- Dependency update?

## Investigation Needed
- Review changes since original fix
- Check if original fix was rolled back
- Verify fix is still in codebase

## Related Issues
- **Original Issue:** [PROJ-XXX](link)
[Any other related issues]

---
*Reported via automated triage - Possible Regression*
```

---

## Summary Writing Best Practices

### Good Summaries

✅ **Specific and actionable:**
- "Payment API: NullPointerException in refund processing"
- "iOS App: Crash when uploading photos >5MB"
- "Dashboard: 15s load time on revenue report"

✅ **Includes component:**
- Start with the affected component/system
- Makes it easy to filter and assign

✅ **Describes the problem:**
- Use clear, technical language
- Avoid vague terms

### Bad Summaries

❌ **Too vague:**
- "Error in production"
- "App crashes sometimes"
- "Something is slow"

❌ **Too long:**
- "Users are reporting that when they try to login on the mobile app using their email and password, the app shows a connection timeout error and they cannot proceed"

❌ **Missing component:**
- "NullPointerException in refund" (what component?)
- "Page won't load" (which page?)

---

## Description Writing Best Practices

### Good Practices

✅ **Use structured format** with headers
✅ **Include complete error messages** in code blocks
✅ **Provide context** (environment, version, time)
✅ **List concrete steps** to reproduce
✅ **Quantify impact** (affected users, frequency)
✅ **Add relevant logs** in code blocks
✅ **Reference related issues** with links

### What to Avoid

❌ Pasting entire stack traces without context
❌ Vague descriptions like "it doesn't work"
❌ Missing environment information
❌ No reproduction steps
❌ Formatting errors/code without code blocks
❌ Forgetting to mention user impact

---

## Field Guidelines

### Priority Selection

**Highest:** System down, data loss, security issue
**High:** Major functionality broken, large user impact
**Medium:** Feature partially broken, moderate impact
**Low:** Minor issue, cosmetic, workaround available

### Component Selection

Always specify the affected component if the project uses components:
- Makes routing to correct team easier
- Helps with duplicate detection
- Improves searchability

### Labels (If Available)

Consider adding labels:
- `regression` - Previously fixed issue
- `production` - Occurring in production
- `data-loss` - Involves data loss/corruption
- `performance` - Performance related
- `mobile-ios` / `mobile-android` - Platform specific
