---
name: search-company-knowledge
description: "Search across company knowledge bases (Confluence, Jira, internal docs) to find and explain internal concepts, processes, and technical details. When an agent needs to: (1) Find or search for information about systems, terminology, processes, deployment, authentication, infrastructure, architecture, or technical concepts, (2) Search internal documentation, knowledge base, company docs, or our docs, (3) Explain what something is, how it works, or look up information, or (4) Synthesize information from multiple sources. Searches in parallel and provides cited answers."
---

# Search Company Knowledge

## Keywords
find information, search company knowledge, look up, what is, explain, company docs, internal documentation, Confluence search, Jira search, our documentation, internal knowledge, knowledge base, search for, tell me about, get information about, company systems, terminology, find everything about, what do we know about, deployment, authentication, infrastructure, processes, procedures, how to, how does, our systems, our processes, internal systems, company processes, technical documentation, engineering docs, architecture, configuration, search our docs, search internal docs, find in our docs

## Overview

Search across siloed company knowledge systems (Confluence, Jira, internal documentation) to find comprehensive answers to questions about internal concepts, systems, and terminology. This skill performs parallel searches across multiple sources and synthesizes results with proper citations.

**Use this skill when:** Users ask about internal company knowledge that might be documented in Confluence pages, Jira tickets, or internal documentation.

---

## Workflow

Follow this 5-step process to provide comprehensive, well-cited answers:

### Step 1: Identify Search Query

Extract the core search terms from the user's question.

**Examples:**
- User: "Find everything about Stratus minions" → Search: "Stratus minions"
- User: "What do we know about the billing system?" → Search: "billing system"
- User: "Explain our deployment process" → Search: "deployment process"

**Consider:**
- Main topic or concept
- Any specific system/component names
- Technical terms or jargon

---

### Step 2: Execute Parallel Search

Search across all available knowledge sources simultaneously for comprehensive coverage.

#### Option A: Cross-System Search (Recommended First)

Use the **`search`** tool (Rovo Search) to search across Confluence and Jira at once:

```
search(
  cloudId="...",
  query="[extracted search terms]"
)
```

**When to use:** 
- Default approach for most queries
- When you don't know which system has the information
- Fastest way to get results from multiple sources

**Example:**
```
search(
  cloudId="...",
  query="Stratus minions"
)
```

This returns results from both Confluence pages and Jira issues.

#### Option B: Targeted Confluence Search

Use **`searchConfluenceUsingCql`** when specifically searching Confluence:

```
searchConfluenceUsingCql(
  cloudId="...",
  cql="text ~ 'search terms' OR title ~ 'search terms'"
)
```

**When to use:**
- User specifically mentions "in Confluence" or "in our docs"
- Cross-system search returns too many Jira results
- Looking for documentation rather than tickets

**Example CQL patterns:**
```
text ~ "Stratus minions"
text ~ "authentication" AND type = page
title ~ "deployment guide"
```

#### Option C: Targeted Jira Search

Use **`searchJiraIssuesUsingJql`** when specifically searching Jira:

```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql="text ~ 'search terms' OR summary ~ 'search terms'"
)
```

**When to use:**
- User mentions "tickets", "issues", or "bugs"
- Looking for historical problems or implementation details
- Cross-system search returns mostly documentation

**Example JQL patterns:**
```
text ~ "Stratus minions"
summary ~ "authentication" AND type = Bug
text ~ "deployment" AND created >= -90d
```

#### Search Strategy

**For most queries, use this sequence:**

1. Start with `search` (cross-system) - **always try this first**
2. If results are unclear, follow up with targeted searches
3. If results mention specific pages/tickets, fetch them for details

---

### Step 3: Fetch Detailed Content

After identifying relevant sources, fetch full content for comprehensive answers.

#### For Confluence Pages

When search results reference Confluence pages:

```
getConfluencePage(
  cloudId="...",
  pageId="[page ID from search results]",
  contentFormat="markdown"
)
```

**Returns:** Full page content in Markdown format

**When to fetch:**
- Search result snippet is too brief
- Need complete context
- Page seems to be the primary documentation

#### For Jira Issues

When search results reference Jira issues:

```
getJiraIssue(
  cloudId="...",
  issueIdOrKey="PROJ-123"
)
```

**Returns:** Full issue details including description, comments, status

**When to fetch:**
- Need to understand a reported bug or issue
- Search result doesn't show full context
- Issue contains important implementation notes

#### Prioritization

**Fetch in this order:**
1. **Official documentation pages** (Confluence pages with "guide", "documentation", "overview" in title)
2. **Recent/relevant issues** (Jira tickets that are relevant and recent)
3. **Additional context** (related pages mentioned in initial results)

**Don't fetch everything** - be selective based on relevance to user's question.

---

### Step 4: Synthesize Results

Combine information from multiple sources into a coherent answer.

#### Synthesis Guidelines

**Structure your answer:**

1. **Direct Answer First**
   - Start with a clear, concise answer to the question
   - "Stratus minions are..."

2. **Detailed Explanation**
   - Provide comprehensive details from all sources
   - Organize by topic, not by source

3. **Source Attribution**
   - Note where each piece of information comes from
   - Format: "According to [source], ..."

4. **Highlight Discrepancies**
   - If sources conflict, note it explicitly
   - Example: "The Confluence documentation states X, however Jira ticket PROJ-123 indicates that due to bug Y, the behavior is actually Z"

5. **Provide Context**
   - Mention if information is outdated
   - Note if a feature is deprecated or in development

#### Synthesis Patterns

**Pattern 1: Multiple sources agree**
```
Stratus minions are background worker processes that handle async tasks.

According to the Confluence documentation, they process jobs from the queue and 
can be scaled horizontally. This is confirmed by several Jira tickets (PROJ-145, 
PROJ-203) which discuss minion configuration and scaling strategies.
```

**Pattern 2: Sources provide different aspects**
```
The billing system has two main components:

**Payment Processing** (from Confluence "Billing Architecture" page)
- Handles credit card transactions
- Integrates with Stripe API
- Runs nightly reconciliation

**Invoice Generation** (from Jira PROJ-189)
- Creates monthly invoices
- Note: Currently has a bug where tax calculation fails for EU customers
- Fix planned for Q1 2024
```

**Pattern 3: Conflicting information**
```
There is conflicting information about the authentication timeout:

- **Official Documentation** (Confluence) states: 30-minute session timeout
- **Implementation Reality** (Jira PROJ-456, filed Oct 2023): Actual timeout is 
  15 minutes due to load balancer configuration
- **Status:** Engineering team aware, fix planned but no timeline yet

Current behavior: Expect 15-minute timeout despite docs saying 30 minutes.
```

**Pattern 4: Incomplete information**
```
Based on available documentation:

[What we know about deployment process from Confluence and Jira]

However, I couldn't find information about:
- Rollback procedures
- Database migration handling

You may want to check with the DevOps team or search for additional documentation.
```

---

### Step 5: Provide Citations

Always include links to source materials so users can explore further.

#### Citation Format

**For Confluence pages:**
```
**Source:** [Page Title](https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/123456)
```

**For Jira issues:**
```
**Related Tickets:**
- [PROJ-123](https://yoursite.atlassian.net/browse/PROJ-123) - Brief description
- [PROJ-456](https://yoursite.atlassian.net/browse/PROJ-456) - Brief description
```

**Complete citation section:**
```
## Sources

**Confluence Documentation:**
- [Stratus Architecture Guide](https://yoursite.atlassian.net/wiki/spaces/DOCS/pages/12345)
- [Minion Configuration](https://yoursite.atlassian.net/wiki/spaces/DEVOPS/pages/67890)

**Jira Issues:**
- [PROJ-145](https://yoursite.atlassian.net/browse/PROJ-145) - Minion scaling implementation
- [PROJ-203](https://yoursite.atlassian.net/browse/PROJ-203) - Performance optimization

**Additional Resources:**
- [Internal architecture doc link if found]
```

---

## Search Best Practices

### Effective Search Terms

**Do:**
- ✅ Use specific technical terms: "OAuth authentication flow"
- ✅ Include system names: "Stratus minions"
- ✅ Use acronyms if they're common: "API rate limiting"
- ✅ Try variations if first search fails: "deploy process" → "deployment pipeline"

**Don't:**
- ❌ Be too generic: "how things work"
- ❌ Use full sentences: Use key terms instead
- ❌ Include filler words: "the", "our", "about"

### Search Result Quality

**Good results:**
- Recent documentation (< 1 year old)
- Official/canonical pages (titled "Guide", "Documentation", "Overview")
- Multiple sources confirming same information
- Detailed implementation notes

**Questionable results:**
- Very old tickets (> 2 years, may be outdated)
- Duplicate or conflicting information
- Draft pages or work-in-progress docs
- Personal pages (may not be official)

**When results are poor:**
- Try different search terms
- Expand search to include related concepts
- Search for specific error messages or codes
- Ask user for more context

---

## Handling Common Scenarios

### Scenario 1: No Results Found

If searches return no results:

```
I searched across Confluence and Jira but couldn't find information about "[topic]".

This could mean:
- The concept hasn't been documented yet
- It might be called something else (can you provide alternative names?)
- Documentation might be in a different system I don't have access to

Would you like me to:
1. Try searching with different terms?
2. Search for related concepts?
3. Look for mentions in recent Jira tickets?
```

### Scenario 2: Too Many Results

If search returns 50+ results:

- Focus on most recent and most relevant (top 10-15)
- Prioritize official documentation over random tickets
- Group similar results: "I found 15 tickets related to authentication bugs..."
- Offer to narrow search: "Would you like me to focus on [specific aspect]?"

### Scenario 3: Ambiguous Query

If the user's question is vague:

```
I found information about several topics related to "[term]":
1. [Topic A] - from Confluence page X
2. [Topic B] - from Jira tickets Y, Z
3. [Topic C] - from documentation W

Which aspect are you most interested in?
```

### Scenario 4: Outdated Information

If you find information is old:

```
I found documentation about [topic], but note that it's from [date] and may be outdated.

[Provide the information anyway]

You may want to verify this is still current, especially if it's from more than 
a year ago.
```

### Scenario 5: Restricted/Private Content

If search returns inaccessible content:

```
Search results mention [topic] in the following locations, but I don't have 
access to view the full content:
- Confluence page: [title] (Space: [SPACE])
- Jira issue: PROJ-123

You may need to access these directly or check your permissions.
```

---

## Examples

### Example 1: Clear Documentation Available

**User:** "What are Stratus minions?"

**Process:**
1. Search: `search(cloudId="...", query="Stratus minions")`
2. Find: Confluence page "Stratus Architecture" + 3 Jira tickets
3. Fetch: Get full Confluence page content
4. Synthesize: Combine architectural overview with implementation details from tickets
5. Cite: Provide links to all sources

**Answer:**
```
Stratus minions are background worker processes that handle asynchronous task 
processing in the Stratus system.

**Key Characteristics:**
- Run independently from web servers
- Process jobs from a Redis queue
- Can be scaled horizontally for increased throughput
- Handle tasks like email sending, report generation, and data processing

**Architecture:**
According to the Stratus Architecture documentation, minions follow a 
worker-queue pattern where:
1. Web application enqueues tasks
2. Minions poll the queue for work
3. Tasks are processed asynchronously
4. Results are stored in the database

**Implementation Notes:**
From Jira ticket PROJ-203, the current deployment runs 5 minion instances, 
with plans to scale to 10 for handling increased load.

## Sources
- [Stratus Architecture Guide](link)
- [PROJ-203](link) - Minion scaling implementation
```

### Example 2: Conflicting Information

**User:** "How long is our session timeout?"

**Process:**
1. Search across Confluence and Jira
2. Find: Docs say 30 min, but ticket reports actual timeout is 15 min
3. Fetch both sources for complete context
4. Clearly note the discrepancy

**Answer:**
```
There is a discrepancy between documented and actual behavior:

**Official Documentation** (Security Guidelines):
Session timeout is configured for 30 minutes of inactivity.

**Actual Behavior** (PROJ-456, reported Oct 2023):
Users are being logged out after 15 minutes due to a load balancer configuration 
that overrides the application setting.

**Current Status:**
The engineering team is aware of this issue. The load balancer timeout needs to 
be adjusted to match the application setting. No fix timeline has been set.

**Recommendation:** Plan for 15-minute timeout until this is resolved.

## Sources
- [Security Guidelines](link) - Official documentation
- [PROJ-456](link) - Timeout discrepancy bug report
```

### Example 3: Partial Information

**User:** "Explain our deployment process"

**Process:**
1. Search finds some information but not complete
2. Synthesize what is available
3. Note gaps in documentation

**Answer:**
```
Based on available documentation, here's what I found about the deployment process:

**Build Phase** (from Confluence "CI/CD Guide"):
1. Code pushed to main branch triggers GitHub Actions
2. Automated tests run (unit, integration)
3. Docker image built and pushed to registry

**Deployment Phase** (from Jira PROJ-789):
4. Staging deployment happens automatically
5. Manual approval required for production
6. Blue-green deployment strategy used

**Gaps in Documentation:**
I couldn't find documented information about:
- Rollback procedures
- Database migration handling
- Post-deployment verification steps

These details may exist in tribal knowledge or need to be documented.

## Sources
- [CI/CD Guide](link)
- [PROJ-789](link) - Deployment pipeline implementation

Would you like me to search for more specific aspects of deployment?
```

---

## Tips for High-Quality Answers

### Do:
✅ Always search before answering (don't rely on general knowledge)
✅ Cite all sources with links
✅ Note discrepancies explicitly
✅ Mention when information is old
✅ Provide context and examples
✅ Structure answers clearly with headers
✅ Link to related documentation

### Don't:
❌ Assume general knowledge applies to this company
❌ Make up information if search returns nothing
❌ Ignore conflicting information
❌ Quote entire documents (summarize instead)
❌ Overwhelm with too many sources (curate top 5-10)
❌ Forget to fetch details when snippets are insufficient

---

## When NOT to Use This Skill

This skill is for **internal company knowledge only**. Do NOT use for:

❌ General technology questions (use your training knowledge)
❌ External documentation (use web_search)
❌ Company-agnostic questions
❌ Questions about other companies
❌ Current events or news

**Examples of what NOT to use this skill for:**
- "What is machine learning?" (general knowledge)
- "How does React work?" (external documentation)
- "What's the weather?" (not knowledge search)
- "Find a restaurant" (not work-related)

---

## Quick Reference

**Primary tool:** `search(cloudId, query)` - Use this first, always

**Follow-up tools:**
- `getConfluencePage(cloudId, pageId, contentFormat)` - Get full page content
- `getJiraIssue(cloudId, issueIdOrKey)` - Get full issue details
- `searchConfluenceUsingCql(cloudId, cql)` - Targeted Confluence search
- `searchJiraIssuesUsingJql(cloudId, jql)` - Targeted Jira search

**Answer structure:**
1. Direct answer
2. Detailed explanation
3. Source attribution
4. Discrepancies (if any)
5. Citations with links

**Remember:**
- Parallel search > Sequential search
- Synthesize, don't just list
- Always cite sources
- Note conflicts explicitly
- Be clear about gaps in documentation
