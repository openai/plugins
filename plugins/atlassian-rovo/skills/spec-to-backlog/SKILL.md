---
name: spec-to-backlog
description: "Automatically convert Confluence specification documents into structured Jira backlogs with Epics and implementation tickets. When an agent needs to: (1) Create Jira tickets from a Confluence page, (2) Generate a backlog from a specification, (3) Break down a spec into implementation tasks, or (4) Convert requirements into Jira issues. Handles reading Confluence pages, analyzing specifications, creating Epics with proper structure, and generating detailed implementation tickets linked to the Epic."
---

# Spec to Backlog

## Overview

Transform Confluence specification documents into structured Jira backlogs automatically. This skill reads requirement documents from Confluence, intelligently breaks them down into logical implementation tasks, **creates an Epic first** to organize the work, then generates individual Jira tickets linked to that Epic—eliminating tedious manual copy-pasting.

## Core Workflow

**CRITICAL: Always follow this exact sequence:**

1. **Fetch Confluence Page** → Get the specification content
2. **Ask for Project Key** → Identify target Jira project
3. **Analyze Specification** → Break down into logical tasks (internally, don't create yet)
4. **Present Breakdown** → Show user the planned Epic and tickets
5. **Create Epic FIRST** → Establish parent Epic and capture its key
6. **Create Child Tickets** → Generate tickets linked to the Epic
7. **Provide Summary** → Present all created items with links

**Why Epic must be created first:** Child tickets need the Epic key to link properly during creation. Creating tickets first will result in orphaned tickets.

---

## Step 1: Fetch Confluence Page

When triggered, obtain the Confluence page content:

### If user provides a Confluence URL:

Extract the cloud ID and page ID from the URL pattern:
- Standard format: `https://[site].atlassian.net/wiki/spaces/[SPACE]/pages/[PAGE_ID]/[title]`
- The cloud ID can be extracted from `[site].atlassian.net` or by calling `getAccessibleAtlassianResources`
- The page ID is the numeric value in the URL path

### If user provides only a page title or description:

Use the `search` tool to find the page:
```
search(
  cloudId="...",
  query="type=page AND title~'[search terms]'"
)
```

If multiple pages match, ask the user to clarify which one to use.

### Fetch the page:

Call `getConfluencePage` with the cloudId and pageId:
```
getConfluencePage(
  cloudId="...",
  pageId="123456",
  contentFormat="markdown"
)
```

This returns the page content in Markdown format, which you'll analyze in Step 3.

---

## Step 2: Ask for Project Key

**Before analyzing the spec**, determine the target Jira project:

### Ask the user:
"Which Jira project should I create these tickets in? Please provide the project key (e.g., PROJ, ENG, PRODUCT)."

### If user is unsure:
Call `getVisibleJiraProjects` to show available projects:
```
getVisibleJiraProjects(
  cloudId="...",
  action="create"
)
```

Present the list: "I found these projects you can create issues in: PROJ (Project Alpha), ENG (Engineering), PRODUCT (Product Team)."

### Once you have the project key:
Call `getJiraProjectIssueTypesMetadata` to understand what issue types are available:
```
getJiraProjectIssueTypesMetadata(
  cloudId="...",
  projectIdOrKey="PROJ"
)
```

**Identify available issue types:**
- Which issue type is "Epic" (or similar parent type like "Initiative")
- What child issue types are available: "Story", "Task", "Bug", "Sub-task", etc.

**Select appropriate issue types for child tickets:**

The skill should intelligently choose issue types based on the specification content:

**Use "Bug" when the spec describes:**
- Fixing existing problems or defects
- Resolving errors or incorrect behavior
- Addressing performance issues
- Correcting data inconsistencies
- Keywords: "fix", "resolve", "bug", "issue", "problem", "error", "broken"

**Use "Story" when the spec describes:**
- New user-facing features or functionality
- User experience improvements
- Customer-requested capabilities
- Product enhancements
- Keywords: "feature", "user can", "add ability to", "new", "enable users"

**Use "Task" when the spec describes:**
- Technical work without direct user impact
- Infrastructure or DevOps work
- Refactoring or optimization
- Documentation or tooling
- Configuration or setup
- Keywords: "implement", "setup", "configure", "optimize", "refactor", "infrastructure"

**Fallback logic:**
1. If "Story" is available and content suggests new features → use "Story"
2. If "Bug" is available and content suggests fixes → use "Bug"
3. If "Task" is available → use "Task" for technical work
4. If none of the above are available → use the first available non-Epic, non-Subtask issue type

**Store the selected issue types for use in Step 6:**
- Epic issue type name (e.g., "Epic")
- Default child issue type (e.g., "Story" or "Task")
- Bug issue type name if available (e.g., "Bug")

---

## Step 3: Analyze Specification

Read the Confluence page content and **internally** decompose it into:

### Epic-Level Goal
What is the overall objective or feature being implemented? This becomes your Epic.

**Example Epic summaries:**
- "User Authentication System"
- "Payment Gateway Integration"  
- "Dashboard Performance Optimization"
- "Mobile App Notifications Feature"

### Implementation Tasks
Break the work into logical, independently implementable tasks.

**Breakdown principles:**
- **Size:** 3-10 tasks per spec typically (avoid over-granularity)
- **Clarity:** Each task should be specific and actionable
- **Independence:** Tasks can be worked on separately when possible
- **Completeness:** Include backend, frontend, testing, documentation, infrastructure as needed
- **Grouping:** Related functionality stays in the same ticket

**Consider these dimensions:**
- Technical layers: Backend API, Frontend UI, Database, Infrastructure
- Work types: Implementation, Testing, Documentation, Deployment
- Features: Break complex features into sub-features
- Dependencies: Identify prerequisite work

**Common task patterns:**
- "Design [component] database schema"
- "Implement [feature] API endpoints"
- "Build [component] UI components"
- "Add [integration] to existing [system]"
- "Write tests for [feature]"
- "Update documentation for [feature]"

**Use action verbs:**
- Implement, Create, Build, Add, Design, Integrate, Update, Fix, Optimize, Configure, Deploy, Test, Document

---

## Step 4: Present Breakdown to User

**Before creating anything**, show the user your planned breakdown:

**Format:**
```
I've analyzed the spec and here's the backlog I'll create:

**Epic:** [Epic Summary]
[Brief description of epic scope]

**Implementation Tickets (7):**
1. [Story] [Task 1 Summary]
2. [Task] [Task 2 Summary]  
3. [Story] [Task 3 Summary]
4. [Bug] [Task 4 Summary]
5. [Task] [Task 5 Summary]
6. [Story] [Task 6 Summary]
7. [Task] [Task 7 Summary]

Shall I create these tickets in [PROJECT KEY]?
```

**The issue type labels show what type each ticket will be created as:**
- [Story] - New user-facing feature
- [Task] - Technical implementation work
- [Bug] - Fix or resolve an issue

**Wait for user confirmation** before proceeding. This allows them to:
- Request changes to the breakdown
- Confirm the scope is correct
- Adjust the number or focus of tickets

If user requests changes, adjust the breakdown and re-present.

---

## Step 5: Create Epic FIRST

**CRITICAL:** The Epic must be created before any child tickets.

### Create the Epic:

Call `createJiraIssue` with:

```
createJiraIssue(
  cloudId="...",
  projectKey="PROJ",
  issueTypeName="Epic",
  summary="[Epic Summary from Step 3]",
  description="[Epic Description - see below]"
)
```

### Epic Description Structure:

```markdown
## Overview
[1-2 sentence summary of what this epic delivers]

## Source
Confluence Spec: [Link to Confluence page]

## Objectives
- [Key objective 1]
- [Key objective 2]
- [Key objective 3]

## Scope
[Brief description of what's included and what's not]

## Success Criteria
- [Measurable criterion 1]
- [Measurable criterion 2]
- [Measurable criterion 3]

## Technical Notes
[Any important technical context from the spec]
```

### Capture the Epic Key:

The response will include the Epic's key (e.g., "PROJ-123"). **Save this key**—you'll need it for every child ticket.

**Example response:**
```json
{
  "key": "PROJ-123",
  "id": "10001",
  "self": "https://yoursite.atlassian.net/rest/api/3/issue/10001"
}
```

**Confirm Epic creation to user:**
"✅ Created Epic: PROJ-123 - User Authentication System"

---

## Step 6: Create Child Tickets

Now create each implementation task as a child ticket linked to the Epic.

### For each task:

**Determine the appropriate issue type for this specific task:**
- If the task involves fixing/resolving an issue → use "Bug" (if available)
- If the task involves new user-facing features → use "Story" (if available)
- If the task involves technical/infrastructure work → use "Task" (if available)
- Otherwise → use the default child issue type from Step 2

Call `createJiraIssue` with:

```
createJiraIssue(
  cloudId="...",
  projectKey="PROJ",
  issueTypeName="[Story/Task/Bug based on task content]",
  summary="[Task Summary]",
  description="[Task Description - see below]",
  parent="PROJ-123"  # The Epic key from Step 5
)
```

**Example issue type selection:**
- "Fix authentication timeout bug" → Use "Bug"
- "Build user dashboard UI" → Use "Story"
- "Configure CI/CD pipeline" → Use "Task"
- "Implement password reset API" → Use "Story" (new user feature)

### Task Summary Format:

Use action verbs and be specific:
- ✅ "Implement user registration API endpoint"
- ✅ "Design authentication database schema"
- ✅ "Build login form UI components"
- ❌ "Do backend work" (too vague)
- ❌ "Frontend" (not actionable)

### Task Description Structure:

```markdown
## Context
[Brief context for this task from the Confluence spec]

## Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Technical Details
[Specific technical information relevant to this task]
- Technologies: [e.g., Node.js, React, PostgreSQL]
- Components: [e.g., API routes, database tables, UI components]
- Dependencies: [e.g., requires PROJ-124 to be completed first]

## Acceptance Criteria
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]

## Related
- Confluence Spec: [Link to relevant section if possible]
- Epic: PROJ-123
```

### Acceptance Criteria Best Practices:

Make them **testable** and **specific**:
- ✅ "API returns 201 status on successful user creation"
- ✅ "Password must be at least 8 characters and hashed with bcrypt"
- ✅ "Login form validates email format before submission"
- ❌ "User can log in" (too vague)
- ❌ "It works correctly" (not testable)

### Create all tickets sequentially:

Track each created ticket key for the summary.

---

## Step 7: Provide Summary

After all tickets are created, present a comprehensive summary:

```
✅ Backlog created successfully!

**Epic:** PROJ-123 - User Authentication System
https://yoursite.atlassian.net/browse/PROJ-123

**Implementation Tickets (7):**

1. PROJ-124 - Design authentication database schema
   https://yoursite.atlassian.net/browse/PROJ-124

2. PROJ-125 - Implement user registration API endpoint
   https://yoursite.atlassian.net/browse/PROJ-125

3. PROJ-126 - Implement user login API endpoint
   https://yoursite.atlassian.net/browse/PROJ-126

4. PROJ-127 - Build login form UI components
   https://yoursite.atlassian.net/browse/PROJ-127

5. PROJ-128 - Build registration form UI components
   https://yoursite.atlassian.net/browse/PROJ-128

6. PROJ-129 - Add authentication integration to existing features
   https://yoursite.atlassian.net/browse/PROJ-129

7. PROJ-130 - Write authentication tests and documentation
   https://yoursite.atlassian.net/browse/PROJ-130

**Source:** https://yoursite.atlassian.net/wiki/spaces/SPECS/pages/123456

**Next Steps:**
- Review tickets in Jira for accuracy and completeness
- Assign tickets to team members
- Estimate story points if your team uses them
- Add any additional labels or custom field values
- Schedule work for the upcoming sprint
```

---

## Edge Cases & Troubleshooting

### Multiple Specs or Pages

**If user references multiple Confluence pages:**
- Process each separately, or ask which to prioritize
- Consider creating separate Epics for distinct features
- "I see you've provided 3 spec pages. Should I create separate Epics for each, or would you like me to focus on one first?"

### Existing Epic

**If user wants to add tickets to an existing Epic:**
- Skip Epic creation (Step 5)
- Ask for the existing Epic key: "What's the Epic key you'd like to add tickets to? (e.g., PROJ-100)"
- Proceed with Step 6 using the provided Epic key

### Custom Required Fields

**If ticket creation fails due to required fields:**
1. Use `getJiraIssueTypeMetaWithFields` to identify what fields are required:
   ```
   getJiraIssueTypeMetaWithFields(
     cloudId="...",
     projectIdOrKey="PROJ",
     issueTypeId="10001"
   )
   ```

2. Ask user for values: "This project requires a 'Priority' field. What priority should I use? (e.g., High, Medium, Low)"

3. Include in `additional_fields` when creating:
   ```
   additional_fields={
     "priority": {"name": "High"}
   }
   ```

### Large Specifications

**For specs that would generate 15+ tickets:**
- Present the full breakdown to user
- Ask: "This spec would create 18 tickets. Should I create all of them, or would you like to adjust the scope?"
- Offer to create a subset first: "I can create the first 10 tickets now and wait for your feedback before creating the rest."

### Subtasks vs Tasks

**Some projects use "Subtask" issue types:**
- If metadata shows "Subtask" is available, you can use it for more granular work
- Subtasks link to parent tasks (not Epics directly)
- Structure: Epic → Task → Subtasks

### Ambiguous Specifications

**If the Confluence page lacks detail:**
- Create fewer, broader tickets
- Note in ticket descriptions: "Detailed requirements need to be defined during refinement"
- Ask user: "The spec is light on implementation details. Should I create high-level tickets that can be refined later?"

### Failed API Calls

**If `createJiraIssue` fails:**
1. Check the error message for specific issues (permissions, required fields, invalid values)
2. Use `getJiraProjectIssueTypesMetadata` to verify issue type availability
3. Inform user: "I encountered an error creating tickets: [error message]. This might be due to project permissions or required fields."

---

## Tips for High-Quality Breakdowns

### Be Specific
- ❌ "Do frontend work"
- ✅ "Create login form UI with email/password inputs and validation"

### Include Technical Context
- Mention specific technologies when clear from spec
- Reference components, services, or modules
- Note integration points

### Logical Grouping
- Related work stays in the same ticket
- Don't split artificially: "Build user profile page" includes both UI and API integration
- Do split when different specialties: Separate backend API task from frontend UI task if worked on by different people

### Avoid Duplication
- Don't create redundant tickets for the same functionality
- If multiple features need the same infrastructure, create one infrastructure ticket they all depend on

### Explicit Testing
- Include testing as part of feature tasks ("Implement X with unit tests")
- OR create separate testing tasks for complex features ("Write integration tests for authentication flow")

### Documentation Tasks
- For user-facing features: Include "Update user documentation" or "Create help articles"
- For developer tools: Include "Update API documentation" or "Write integration guide"

### Dependencies
- Note prerequisites in ticket descriptions
- Use "Depends on" or "Blocks" relationships in Jira if available
- Sequence tickets logically (infrastructure → implementation → testing)

---

## Examples of Good Breakdowns

### Example 1: New Feature - Search Functionality

**Epic:** Product Search and Filtering

**Tickets:**
1. [Task] Design search index schema and data structure
2. [Task] Implement backend search API with Elasticsearch
3. [Story] Build search input and results UI components
4. [Story] Add advanced filtering (price, category, ratings)
5. [Story] Implement search suggestions and autocomplete
6. [Task] Optimize search performance and add caching
7. [Task] Write search integration tests and documentation

### Example 2: Bug Fix - Performance Issue

**Epic:** Resolve Dashboard Load Time Issues

**Tickets:**
1. [Task] Profile and identify performance bottlenecks
2. [Bug] Optimize database queries with indexes and caching
3. [Bug] Implement lazy loading for dashboard widgets
4. [Bug] Add pagination to large data tables
5. [Task] Set up performance monitoring and alerts

### Example 3: Infrastructure - CI/CD Pipeline

**Epic:** Automated Deployment Pipeline

**Tickets:**
1. [Task] Set up GitHub Actions workflow configuration
2. [Task] Implement automated testing in CI pipeline
3. [Task] Configure staging environment deployment
4. [Task] Implement blue-green production deployment
5. [Task] Add deployment rollback mechanism
6. [Task] Create deployment runbook and documentation

