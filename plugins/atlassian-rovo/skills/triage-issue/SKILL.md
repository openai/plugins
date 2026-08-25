---
name: triage-issue
description: "Intelligently triage bug reports and error messages by searching for duplicates in Jira and offering to create new issues or add comments to existing ones. When an agent needs to: (1) Triage a bug report or error message, (2) Check if an issue is a duplicate, (3) Find similar past issues, (4) Create a new bug ticket with proper context, or (5) Add information to an existing ticket. Searches Jira for similar issues, identifies duplicates, checks fix history, and helps create well-structured bug reports."
---

# Triage Issue

## Keywords
triage bug, check duplicate, is this a duplicate, search for similar issues, create bug ticket, file a bug, report this error, triage this error, bug report, error message, similar issues, duplicate bug, who fixed this, has this been reported, search bugs, find similar bugs, create issue, file issue

## Overview

Automatically triage bug reports and error messages by searching Jira for duplicates, identifying similar past issues, and helping create well-structured bug tickets or add context to existing issues. This skill eliminates manual duplicate checking and ensures bugs are properly documented with relevant historical context.

**Use this skill when:** Users need to triage error messages, bug reports, or issues to determine if they're duplicates and take appropriate action.

---

## Workflow

Follow this 6-step process to effectively triage issues:

### Step 1: Extract Key Information

Analyze the bug report or error message to identify search terms.

#### Extract These Elements:

**Error signature:**
- Error type or exception name (e.g., "NullPointerException", "TimeoutError")
- Error code or status (e.g., "500", "404", "ERR_CONNECTION_REFUSED")
- Specific error message text (key phrases, not full stack trace)

**Context:**
- Component or system affected (e.g., "authentication", "payment gateway", "API")
- Environment (e.g., "production", "staging", "mobile app")
- User actions leading to error (e.g., "during login", "when uploading file")

**Symptoms:**
- Observable behavior (e.g., "page blank", "infinite loading", "data not saving")
- Impact (e.g., "users can't login", "payments failing")

#### Example Extractions:

**Input:** "Users getting 'Connection timeout' error when trying to login on mobile app"
**Extracted:**
- Error: "Connection timeout"
- Component: "login", "mobile app"
- Symptom: "can't login"

**Input:** "NullPointerException in PaymentProcessor.processRefund() line 245"
**Extracted:**
- Error: "NullPointerException"
- Component: "PaymentProcessor", "refund"
- Location: "processRefund line 245"

---

### Step 2: Search for Duplicates

Search Jira using extracted keywords to find similar or duplicate issues.

#### Search Strategy:

Execute **multiple targeted searches** to catch duplicates that may use different wording:

**Search 1: Error-focused**
```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql='project = "PROJ" AND (text ~ "error signature" OR summary ~ "error signature") AND type = Bug ORDER BY created DESC',
  fields=["summary", "description", "status", "resolution", "created", "updated", "assignee"],
  maxResults=20
)
```

**Search 2: Component-focused**
```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql='project = "PROJ" AND text ~ "component keywords" AND type = Bug ORDER BY updated DESC',
  fields=["summary", "description", "status", "resolution", "created", "updated", "assignee"],
  maxResults=20
)
```

**Search 3: Symptom-focused**
```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql='project = "PROJ" AND summary ~ "symptom keywords" AND type = Bug ORDER BY priority DESC, updated DESC',
  fields=["summary", "description", "status", "resolution", "created", "updated", "assignee"],
  maxResults=20
)
```

#### Search Tips:

**Use key terms only:**
- ✅ "timeout login mobile"
- ✅ "NullPointerException PaymentProcessor refund"
- ❌ "Users are getting a connection timeout error when..." (too verbose)

**Search recent first:**
- Order by `created DESC` or `updated DESC` to find recent similar issues
- Recent bugs are more likely to be relevant duplicates

**Don't over-filter:**
- Include resolved issues (might have been reopened or regression)
- Search across all bug statuses to find fix history

---

### Step 3: Analyze Search Results

Evaluate the search results to determine if this is a duplicate or a new issue.

#### Duplicate Detection:

**High confidence duplicate (>90%):**
- Exact same error message in summary or description
- Same component + same error type
- Recent issue (< 30 days) with identical symptoms
- **Action:** Strongly recommend adding comment to existing issue

**Likely duplicate (70-90%):**
- Similar error with slight variations
- Same component but different context
- Resolved issue with same root cause
- **Action:** Present as possible duplicate, let user decide

**Possibly related (40-70%):**
- Similar symptoms but different error
- Same component area but different specific error
- Old issue (> 6 months) that might be unrelated
- **Action:** Mention as potentially related

**Likely new issue (<40%):**
- No similar issues found
- Different error signature and component
- Unique symptom or context
- **Action:** Recommend creating new issue

#### Check Fix History:

If similar resolved issues are found:

**Extract relevant information:**
- Who fixed it? (assignee on resolved issues)
- How was it fixed? (resolution comment or linked PRs)
- When was it fixed? (resolution date)
- Has it regressed? (any reopened issues)

**Present this context** to help with triage decision.

---

### Step 4: Present Findings to User

**CRITICAL:** Always present findings and wait for user decision before taking any action.

#### Format for Likely Duplicate:

```
🔍 **Triage Results: Likely Duplicate**

I found a very similar issue already reported:

**PROJ-456** - Connection timeout during mobile login
Status: Open | Priority: High | Created: 3 days ago
Assignee: @john.doe
https://yoursite.atlassian.net/browse/PROJ-456

**Similarity:**
- Same error: "Connection timeout"
- Same component: Mobile app login
- Same symptoms: Users unable to login

**Difference:**
- Original report mentioned iOS specifically, this report doesn't specify platform

**Recommendation:** Add your details as a comment to PROJ-456

Would you like me to:
1. Add a comment to PROJ-456 with your error details
2. Create a new issue anyway (if you think this is different)
3. Show me more details about PROJ-456 first
```

#### Format for Possibly Related:

```
🔍 **Triage Results: Possibly Related Issues Found**

I found 2 potentially related issues:

**1. PROJ-789** - Mobile app authentication failures
Status: Resolved | Fixed: 2 weeks ago | Fixed by: @jane.smith
https://yoursite.atlassian.net/browse/PROJ-789

**2. PROJ-234** - Login timeout on slow connections
Status: Open | Priority: Medium | Created: 1 month ago
https://yoursite.atlassian.net/browse/PROJ-234

**Assessment:** Your error seems related but has unique aspects

**Recommendation:** Create a new issue, but reference these related tickets

Would you like me to create a new bug ticket?
```

#### Format for No Duplicates:

```
🔍 **Triage Results: No Duplicates Found**

I searched Jira for:
- "Connection timeout" errors
- Mobile login issues
- Authentication failures

No similar open or recent issues found.

**Recommendation:** Create a new bug ticket

**Note:** I found 1 old resolved issue (PROJ-123 from 8 months ago) about login timeouts, but it was for web, not mobile, and was resolved as "configuration error."

Would you like me to create a new bug ticket for this issue?
```

---

### Step 5: Execute User Decision

Based on user's choice, either add a comment or create a new issue.

#### Option A: Add Comment to Existing Issue

If user wants to add to existing issue:

**Fetch the full issue first** to understand context:
```
getJiraIssue(
  cloudId="...",
  issueIdOrKey="PROJ-456"
)
```

**Then add the comment:**
```
addCommentToJiraIssue(
  cloudId="...",
  issueIdOrKey="PROJ-456",
  commentBody="[formatted comment - see below]"
)
```

**Comment Structure:**
```markdown
## Additional Instance Reported

**Reporter:** [User's name or context]
**Date:** [Current date]

**Error Details:**
[Paste relevant error message or stack trace]

**Context:**
- Environment: [e.g., Production, iOS 16.5]
- User Impact: [e.g., 50+ users affected in last hour]
- Steps to Reproduce: [if provided]

**Additional Notes:**
[Any unique aspects of this instance]

---
*Added via triage automation*
```

#### Option B: Create New Issue

If user wants to create new issue:

**First, check available issue types:**
```
getJiraProjectIssueTypesMetadata(
  cloudId="...",
  projectIdOrKey="PROJ"
)
```

**Determine appropriate issue type:**
- For bugs/errors → Use "Bug" (if available)
- For issues without errors → Use "Task" or "Issue"
- Fallback → First available non-Epic, non-Subtask type

**Create the issue:**
```
createJiraIssue(
  cloudId="...",
  projectKey="PROJ",
  issueTypeName="Bug",
  summary="[Clear, specific summary - see below]",
  description="[Detailed description - see below]",
  additional_fields={
    "priority": {"name": "Medium"}  # Adjust based on user input severity assessment
  }
)
```

**Summary Format:**
Use the pattern: `[Component] [Error Type] - [Brief Symptom]`

**Examples:**
- ✅ "Mobile Login: Connection timeout during authentication"
- ✅ "Payment API: NullPointerException in refund processing"
- ✅ "Dashboard: Infinite loading on reports page"
- ❌ "Error in production" (too vague)
- ❌ "Users experiencing issues" (not specific)

**Description Structure:**
```markdown
## Issue Description
[1-2 sentence summary of the problem]

## Error Details
```
[Error message or stack trace]
```

## Environment
- **Platform:** [e.g., Mobile iOS, Web, API]
- **Version:** [if known]
- **Environment:** [Production/Staging/etc]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## User Impact
- **Frequency:** [e.g., Every time, Intermittent]
- **Affected Users:** [e.g., All users, Mobile users only]
- **Severity:** [e.g., Users cannot complete checkout]

## Additional Context
[Any other relevant information]

## Related Issues
[If applicable, reference similar issues found during triage]
- See also: PROJ-123 (similar but resolved)

---
*Created via automated triage*
```

---

### Step 6: Provide Summary

After taking action, confirm what was done.

#### If Comment Added:

```
✅ **Comment Added Successfully**

Added details to existing issue: **PROJ-456**
https://yoursite.atlassian.net/browse/PROJ-456

**What I included:**
- Your error details
- Environment context
- User impact information

**Next Steps:**
- The assignee (@john.doe) will be notified
- Monitor PROJ-456 for updates
- If this turns out to be different, we can still create a separate ticket
```

#### If New Issue Created:

```
✅ **New Issue Created**

**PROJ-890** - Mobile Login: Connection timeout during authentication
https://yoursite.atlassian.net/browse/PROJ-890

Type: Bug | Priority: Medium | Status: Open

**What's Included:**
- Complete error details and stack trace
- Environment and reproduction steps
- User impact assessment
- References to related issues (PROJ-123, PROJ-789)

**Next Steps:**
- Issue will be reviewed during next triage meeting
- Consider setting priority based on user impact
- Assign to appropriate team member
```

---

## Edge Cases & Troubleshooting

### Multiple Potential Duplicates

If you find 3+ very similar issues:

```
🔍 **Triage Results: Multiple Possible Duplicates**

I found 3 issues that might be related:

**Most Likely Duplicate:**
**PROJ-456** - [summary] (Open, 2 days ago)
Match: 95% - Same error and component

**Also Possibly Related:**
**PROJ-234** - [summary] (Open, 1 month ago)
Match: 70% - Similar symptoms, different error

**PROJ-123** - [summary] (Resolved, 8 months ago)
Match: 60% - Related component, but was fixed

**Recommendation:**
1. Add to PROJ-456 (most similar)
2. Reference PROJ-234 in your comment (might be related)
3. Note PROJ-123 was previously fixed (possible regression)

Which issue should I add your details to? (Or create new)
```

### Unclear Project Context

If user doesn't specify which project:

```
Which Jira project should I search for similar issues?

Available projects:
- BACKEND (Backend Services)
- MOBILE (Mobile Apps)
- WEB (Web Platform)
- INFRA (Infrastructure)

Or tell me the project key directly (e.g., BACKEND, MOBILE)
```

### Insufficient Information

If the bug report lacks critical details:

```
I need more information to effectively triage this issue:

**What I have:**
- Error: "Something went wrong"

**What would help:**
- Specific error message or code
- Which part of the system (login, payment, etc.)
- What the user was trying to do
- Which environment (production, staging, mobile, web)

Can you provide any of these details?
```

### Resolved Regression

If you find a resolved issue that matches:

```
🔍 **Triage Results: Possible Regression**

This looks like it might be a regression of a previously fixed issue:

**PROJ-567** - [Same issue description]
Status: Resolved (Fixed) | Fixed: 3 months ago | Fixed by: @jane.smith
Resolution: [Brief description of fix]
https://yoursite.atlassian.net/browse/PROJ-567

**This suggests:**
- The original fix may not have fully addressed the root cause
- OR there's been a regression in recent changes
- OR this is a different issue with similar symptoms

**Recommendation:** Create a new issue and link it to PROJ-567 as "may be related to" or "regression of"

Should I create a new issue with this context?
```

### Custom Required Fields

If creating an issue fails due to required fields:

1. **Check what fields are required:**
```
getJiraIssueTypeMetaWithFields(
  cloudId="...",
  projectIdOrKey="PROJ",
  issueTypeId="10001"
)
```

2. **Ask user for values:**
```
This project requires additional fields to create a Bug:
- Severity: [High/Medium/Low]
- Affected Version: [Version number]

Please provide these values so I can create the issue.
```

3. **Retry with additional fields:**
```
createJiraIssue(
  ...existing parameters...,
  additional_fields={
    "priority": {"name": "High"},
    "customfield_10001": {"value": "Production"}
  }
)
```

---

## Tips for Effective Triage

### For Search:

**Do:**
✅ Use multiple search queries with different angles
✅ Include both open and resolved issues in search
✅ Search for error signatures and symptoms separately
✅ Look at recent issues first (last 30-90 days)
✅ Check for patterns (multiple reports of same thing)

**Don't:**
❌ Search with entire error messages (too specific)
❌ Only search open issues (miss fix history)
❌ Ignore resolved issues (miss regressions)
❌ Use too many keywords (reduces matches)

### For Issue Creation:

**Do:**
✅ Write clear, specific summaries with component names
✅ Include complete error messages in code blocks
✅ Add environment and impact details
✅ Reference related issues found during search
✅ Use "Bug" issue type for actual bugs

**Don't:**
❌ Create vague summaries like "Error in production"
❌ Paste entire stack traces in summary (use description)
❌ Skip reproduction steps
❌ Forget to mention user impact
❌ Hard-code issue type without checking availability

### For Duplicate Assessment:

**High Confidence Duplicates:**
- Exact same error + same component + recent (< 30 days)
- Same root cause identified

**Likely Different Issues:**
- Different error signatures
- Different components/systems
- Significantly different contexts

**When Unsure:**
- Present both options to user
- Lean toward creating new issue (can be closed as duplicate later)
- Linking issues is better than hiding information

---

## Examples

### Example 1: Clear Duplicate Found

**User Input:**
```
Triage this error: "Connection timeout error when users try to login on iOS app"
```

**Process:**
1. Extract: "Connection timeout", "login", "iOS"
2. Search: Find PROJ-456 (open, 2 days ago) with exact same error
3. Analyze: 95% match - same error, component, symptom
4. Present: Show PROJ-456 as duplicate, recommend adding comment
5. Execute: User confirms, add comment with iOS-specific details
6. Confirm: Comment added to PROJ-456

**Output:**
```
✅ Comment added to PROJ-456

Your iOS-specific error details have been added to the existing issue.
The assignee will be notified.
```

### Example 2: New Issue with Related Context

**User Input:**
```
Error: NullPointerException in PaymentProcessor.processRefund() at line 245
Stack trace: [full stack trace]
```

**Process:**
1. Extract: "NullPointerException", "PaymentProcessor", "processRefund", "line 245"
2. Search: Find PROJ-789 (resolved, 3 weeks ago) about payment errors, but different line
3. Analyze: Related component but different specific error
4. Present: No duplicates, found related issue, recommend new ticket
5. Execute: User confirms, create new Bug with context
6. Confirm: PROJ-890 created

**Output:**
```
✅ New Issue Created

PROJ-890 - Payment API: NullPointerException in refund processing
https://yoursite.atlassian.net/browse/PROJ-890

References related issue PROJ-789 for context.
```

### Example 3: Possible Regression

**User Input:**
```
Users can't upload files larger than 5MB, getting "Upload failed" error
```

**Process:**
1. Extract: "Upload failed", "5MB", "file upload"
2. Search: Find PROJ-234 (resolved 2 months ago) - exact same issue
3. Analyze: Was fixed but now happening again
4. Present: Possible regression, recommend new issue linked to old one
5. Execute: Create new issue, link to PROJ-234 as "may be caused by"
6. Confirm: PROJ-891 created with regression context

**Output:**
```
✅ New Issue Created (Possible Regression)

PROJ-891 - File Upload: Upload failed for files >5MB (Regression?)
https://yoursite.atlassian.net/browse/PROJ-891

This may be a regression of PROJ-234, which was resolved 2 months ago.
Issue includes reference to original fix for investigation.
```

---

## When NOT to Use This Skill

This skill is for **triaging bugs and errors only**. Do NOT use for:

❌ Feature requests (use spec-to-backlog)
❌ General task creation (use capture-tasks-from-meeting-notes)
❌ Searching for information (use search-company-knowledge)
❌ Generating status reports (use generate-status-report)

**Use this skill specifically for:**
✅ "Is this a duplicate bug?"
✅ "Triage this error message"
✅ "Has this been reported before?"
✅ "Create a bug ticket for this"

---

## Quick Reference

**Primary workflow:** Extract → Search → Analyze → Present → Execute → Confirm

**Search tool:** `searchJiraIssuesUsingJql(cloudId, jql, fields, maxResults)`

**Action tools:**
- `addCommentToJiraIssue(cloudId, issueIdOrKey, commentBody)` - Add to existing
- `createJiraIssue(cloudId, projectKey, issueTypeName, summary, description)` - Create new

**Issue type:** Always prefer "Bug" for error reports, check with `getJiraProjectIssueTypesMetadata`

**Remember:**
- Multiple searches catch more duplicates
- Present findings before acting
- Include error details and context
- Reference related issues
- Use "Bug" issue type when available
