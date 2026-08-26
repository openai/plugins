# Ticket Writing Guide

Guidelines for creating clear, actionable Jira tickets with effective summaries and descriptions.

## Summary Guidelines

The ticket summary should be a clear, concise action statement that immediately tells someone what needs to be done.

### Formula

**[Action Verb] + [Component/Feature] + [Optional: Context]**

### Good Examples

✅ "Implement user registration API endpoint"  
✅ "Fix pagination bug in search results"  
✅ "Add email validation to signup form"  
✅ "Optimize database query for dashboard load time"  
✅ "Create documentation for payment webhook"  
✅ "Design user preferences data schema"

### Bad Examples

❌ "Users" - Not actionable  
❌ "Do backend work" - Too vague  
❌ "Fix bug" - Lacks specificity  
❌ "API" - Not a task  
❌ "There's an issue with the login page that needs to be addressed" - Too wordy

### Action Verbs by Task Type

**Development:**
- Implement, Build, Create, Add, Develop

**Bug Fixes:**
- Fix, Resolve, Correct, Debug

**Design/Planning:**
- Design, Plan, Research, Investigate, Define

**Infrastructure:**
- Set up, Configure, Deploy, Migrate, Upgrade

**Documentation:**
- Write, Document, Update, Create

**Improvement:**
- Optimize, Refactor, Improve, Enhance

**Testing:**
- Test, Verify, Validate

---

## Description Structure

A good ticket description provides context, requirements, and guidance without being overwhelming.

### Recommended Template

```markdown
## Context
[1-2 sentences: Why we're doing this, what problem it solves]

## Requirements
- [Specific requirement 1]
- [Specific requirement 2]
- [Specific requirement 3]

## Technical Notes
[Any technical constraints, preferred approaches, or implementation hints]

## Acceptance Criteria
- [ ] [Testable outcome 1]
- [ ] [Testable outcome 2]
- [ ] [Testable outcome 3]

## Resources
- [Link to design mockup if applicable]
- [Link to API documentation]
- [Link to related tickets]
```

### Example 1: Feature Implementation

**Summary:** Implement user registration API endpoint

**Description:**
```markdown
## Context
Users need to create accounts through our REST API. This endpoint will be used by our web app and future mobile apps.

## Requirements
- Accept email, password, and name via POST request
- Validate email format and uniqueness
- Hash password using bcrypt
- Return JWT token for immediate authentication
- Send welcome email asynchronously

## Technical Notes
- Use existing email service for welcome emails
- Follow authentication patterns from login endpoint
- Rate limit: 5 registration attempts per IP per hour

## Acceptance Criteria
- [ ] Endpoint accepts valid registration data and returns 201 with JWT
- [ ] Duplicate email returns 409 error
- [ ] Invalid email format returns 400 error
- [ ] Password must be 8+ characters
- [ ] Welcome email sent within 1 minute
- [ ] Unit tests cover happy path and error cases

## Resources
- API Spec: https://company.atlassian.net/wiki/API-Design
- Related: AUTH-123 (Login endpoint)
```

### Example 2: Bug Fix

**Summary:** Fix pagination bug in search results

**Description:**
```markdown
## Context
Users report that clicking "Next Page" in search results sometimes shows duplicate items from the previous page. This happens intermittently when search results are sorted by date.

## Problem
The pagination offset calculation doesn't account for items with identical timestamps, causing cursor position drift when using timestamp-based pagination.

## Requirements
- Ensure each search result appears exactly once
- Maintain current sort order (date descending)
- Fix applies to all search endpoints

## Technical Notes
- Current implementation uses timestamp as cursor: `?cursor=2024-01-15T10:30:00Z`
- Suggested fix: Composite cursor using timestamp + ID
- Consider adding unique index on (timestamp, id) for better query performance

## Acceptance Criteria
- [ ] No duplicate items appear across paginated results
- [ ] Pagination works correctly with items having identical timestamps
- [ ] All existing search API tests still pass
- [ ] Added test case reproducing the original bug
- [ ] Performance impact < 5ms per query

## Resources
- Bug Report: https://company.atlassian.net/wiki/BUG-456
- Related: SEARCH-789 (Original search implementation)
```

### Example 3: Infrastructure Task

**Summary:** Set up PostgreSQL 15 staging environment

**Description:**
```markdown
## Context
First step in database migration from PG12 to PG15. Need staging environment to validate migration process and test query compatibility.

## Requirements
- Provision PG15 instance matching production specs
- Set up replication from production to staging
- Configure backup retention (7 days)
- Enable query logging for testing

## Technical Notes
- Use AWS RDS PostgreSQL 15.2
- Instance type: db.r6g.2xlarge (same as prod)
- Enable logical replication for zero-downtime testing
- VPC: staging-vpc-us-east-1

## Acceptance Criteria
- [ ] PG15 instance running and accessible from staging apps
- [ ] Replication lag < 30 seconds from production
- [ ] Can connect using standard credentials
- [ ] Query logs enabled and viewable
- [ ] Monitoring dashboards created
- [ ] Backup configured and tested (restore test)

## Resources
- Migration RFC: https://company.atlassian.net/wiki/PG15-Migration
- Infrastructure docs: https://wiki/Database-Setup
- Parent Epic: INFRA-100
```

### Example 4: Frontend Task

**Summary:** Create notification bell UI component

**Description:**
```markdown
## Context
Part of notification system. Need UI component showing unread notification count and opening notification panel.

## Requirements
- Bell icon in top navigation bar
- Display unread count badge (e.g., "5")
- Click opens notification dropdown panel
- Real-time updates via WebSocket
- Badge turns red for urgent notifications

## Technical Notes
- Use existing Icon component library
- WebSocket events: 'notification:new', 'notification:read'
- State management: Context API or Zustand
- Position: Right side of nav, left of user avatar

## Acceptance Criteria
- [ ] Bell icon displays in navigation bar
- [ ] Unread count badge shows accurate count
- [ ] Badge updates in real-time when new notification arrives
- [ ] Click opens/closes notification panel
- [ ] No badge shown when count is 0
- [ ] Component is accessible (keyboard navigation, screen reader)
- [ ] Responsive design (mobile, tablet, desktop)

## Resources
- Design mockup: [Figma link]
- WebSocket docs: https://wiki/Notifications-API
- Related: NOTIF-123 (Notification panel component)
```

---

## Descriptions by Task Type

### Backend Development

Focus on:
- API contract (request/response format)
- Data validation rules
- Error handling requirements
- Performance expectations
- Security considerations

### Frontend Development

Focus on:
- Visual design reference
- User interactions
- State management approach
- Responsive behavior
- Accessibility requirements

### Bug Fixes

Focus on:
- Reproduction steps
- Expected vs actual behavior
- Root cause (if known)
- Affected users/scenarios
- Verification approach

### Testing

Focus on:
- What needs testing (features, edge cases)
- Test coverage targets
- Types of tests (unit, integration, e2e)
- Performance benchmarks
- Test data requirements

### Documentation

Focus on:
- Target audience
- Required sections/topics
- Examples to include
- Existing docs to update
- Review/approval process

---

## Acceptance Criteria Best Practices

Acceptance criteria should be:

1. **Testable** - Can verify by testing or observation
2. **Specific** - No ambiguity about what "done" means
3. **Complete** - Covers all requirements in description
4. **User-focused** - When possible, frame from user perspective

### Good Acceptance Criteria

✅ "User can submit form and receive confirmation email within 30 seconds"  
✅ "API returns 400 error when email field is empty"  
✅ "Dashboard loads in under 2 seconds on 3G connection"  
✅ "All text meets WCAG 2.1 AA contrast ratios"

### Bad Acceptance Criteria

❌ "Feature works well" - Not specific  
❌ "Code is clean" - Subjective, not testable  
❌ "Fast performance" - Not measurable  
❌ "No bugs" - Too broad

---

## Technical Notes Guidelines

Use "Technical Notes" section for:

- **Architectural decisions**: "Use Redis for session caching"
- **Implementation hints**: "Follow pattern from UserService class"
- **Performance constraints**: "Query must complete in < 100ms"
- **Security requirements**: "Use parameterized queries to prevent SQL injection"
- **Dependencies**: "Requires AUTH-456 to be deployed first"
- **Gotchas**: "Watch out for timezone handling in date comparisons"

Keep it concise - detailed technical specs belong in Confluence or code comments.

---

## Common Mistakes to Avoid

### 1. Information Overload
❌ Pages of requirements copied from spec doc  
✅ Summary with link to full spec

### 2. Assuming Context
❌ "Fix the bug we discussed"  
✅ Clear description of the bug with reproduction steps

### 3. Implementation as Requirement
❌ "Use React hooks for state management"  
✅ "Component updates in real-time" (let developer choose approach unless there's a specific reason)

### 4. Vague Acceptance Criteria
❌ "Everything works correctly"  
✅ Specific, testable outcomes

### 5. Missing Links
❌ No reference to designs, specs, or related work  
✅ Links to all relevant documentation

---

## Length Guidelines

**Summary:** 
- Target: 3-8 words
- Max: 12 words

**Description:**
- Target: 100-300 words
- Min: Include at minimum context and acceptance criteria
- Max: 500 words (link to docs for more detail)

**Acceptance Criteria:**
- Target: 3-7 items
- Each item: 1 sentence

Remember: Ticket descriptions are not documentation. They're instructions for completing a specific task.
