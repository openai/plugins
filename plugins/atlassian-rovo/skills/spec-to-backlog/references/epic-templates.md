# Epic Description Templates

Effective Epic descriptions provide context, goals, and success criteria. Use these templates based on the type of work.

## Template 1: New Feature Epic

```markdown
## Overview
[1-2 sentence description of what this Epic delivers]

## Source Specification
[Link to Confluence page or design doc]

## Business Value
[Why we're building this - user impact, business goals]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

## Technical Scope
- **Frontend**: [High-level frontend work]
- **Backend**: [High-level backend work]
- **Infrastructure**: [Any infrastructure needs]
- **Third-party**: [External integrations]

## Out of Scope
- [Explicitly list what's NOT included to prevent scope creep]

## Dependencies
- [List any blocking or related work]

## Launch Plan
- **Target completion**: [Date or sprint]
- **Rollout strategy**: [All at once, gradual, A/B test, etc.]
```

### Example: User Notifications System

```markdown
## Overview
Add comprehensive notification system supporting email and in-app notifications for user activity (comments, mentions, updates).

## Source Specification
https://company.atlassian.net/wiki/spaces/PRODUCT/pages/123456/Notifications-Spec

## Business Value
Users currently miss important updates, leading to delayed responses and reduced engagement. Notifications will increase daily active usage by an estimated 20% and improve user satisfaction scores.

## Success Criteria
- [ ] Users receive email notifications within 5 minutes of trigger event
- [ ] In-app notifications appear in real-time (< 2 second delay)
- [ ] 80% of users enable at least one notification type
- [ ] Email delivery rate > 95%
- [ ] System handles 10,000 notifications/minute at peak

## Technical Scope
- **Frontend**: Notification bell UI, preferences page, notification cards
- **Backend**: Notification service, email dispatcher, real-time delivery
- **Infrastructure**: Email service integration (SendGrid), websocket server
- **Third-party**: SendGrid for email delivery

## Out of Scope
- Push notifications (mobile) - planned for Q2
- SMS notifications - not in current roadmap
- Notification history beyond 30 days

## Dependencies
- None - self-contained feature

## Launch Plan
- **Target completion**: Sprint 24 (March 15)
- **Rollout strategy**: Gradual rollout, 10% → 50% → 100% over 1 week
```

---

## Template 2: Bug Fix Epic

```markdown
## Problem Statement
[Clear description of the bug and its impact]

## Source Documentation
[Link to Confluence investigation, incident report, or bug analysis]

## Current Impact
- **Severity**: [Critical/High/Medium/Low]
- **Users affected**: [Percentage or number]
- **Frequency**: [How often it occurs]
- **Business impact**: [Revenue, reputation, etc.]

## Root Cause
[Technical explanation of what's causing the issue]

## Solution Approach
[High-level approach to fixing the issue]

## Success Criteria
- [ ] [Bug no longer reproducible]
- [ ] [Related edge cases handled]
- [ ] [Monitoring in place to detect recurrence]

## Verification Plan
[How we'll confirm the fix works]
```

### Example: Payment Processing Failures

```markdown
## Problem Statement
Users experiencing intermittent payment failures during checkout, resulting in abandoned transactions and support tickets. Error rate spiked to 8% on Nov 15, up from baseline 0.5%.

## Source Documentation
https://company.atlassian.net/wiki/spaces/ENG/pages/789012/Payment-Failure-Investigation

## Current Impact
- **Severity**: Critical
- **Users affected**: ~800 customers per day
- **Frequency**: 8% of all payment attempts
- **Business impact**: $45K/day in lost revenue, customer trust erosion

## Root Cause
Payment gateway timeouts due to insufficient timeout settings (5s) and no retry logic. During high load, 3rd party payment API occasionally takes 6-8s to respond, causing failures.

## Solution Approach
1. Increase timeout to 15s with exponential backoff retry
2. Implement circuit breaker to prevent cascade failures
3. Add payment reconciliation job to handle stuck transactions
4. Improve error messaging for users

## Success Criteria
- [ ] Payment failure rate below 1%
- [ ] Zero timeout-related failures
- [ ] 100% of stuck payments reconciled within 15 minutes
- [ ] User-facing error messages are clear and actionable

## Verification Plan
- Load testing with simulated gateway delays
- Monitor production metrics for 1 week post-deployment
- Review support tickets for payment-related issues
```

---

## Template 3: Infrastructure/Technical Epic

```markdown
## Objective
[What infrastructure change or technical improvement we're making]

## Source Documentation
[Link to technical design doc or RFC]

## Current State
[Description of existing system/approach]

## Target State
[Description of desired system/approach after completion]

## Motivation
[Why we need to make this change - performance, cost, maintainability, etc.]

## Success Criteria
- [ ] [Technical metric 1]
- [ ] [Technical metric 2]
- [ ] [Zero downtime or minimal disruption]

## Risk Mitigation
- **Rollback plan**: [How to revert if issues occur]
- **Monitoring**: [What metrics we'll watch]
- **Testing strategy**: [Dry runs, canary deployments, etc.]

## Timeline Constraints
[Any time-sensitive factors like deprecations, costs]
```

### Example: PostgreSQL Migration

```markdown
## Objective
Migrate primary database from PostgreSQL 12 to PostgreSQL 15 to leverage performance improvements and new features before PostgreSQL 12 EOL.

## Source Documentation
https://company.atlassian.net/wiki/spaces/ENG/pages/345678/PG15-Migration-RFC

## Current State
Running PostgreSQL 12.8 on AWS RDS with 2TB data, 50K queries/minute at peak. Some queries use deprecated features.

## Target State
PostgreSQL 15.2 with optimized queries, improved query planner, and better connection pooling. Estimated 15-20% performance improvement on read-heavy queries.

## Motivation
- PostgreSQL 12 reaches EOL in November 2024
- PG15 query planner improvements will reduce latency on dashboard queries
- New features enable better monitoring and troubleshooting
- Cost savings: ~$800/month from improved efficiency

## Success Criteria
- [ ] Zero data loss during migration
- [ ] < 5 minutes of downtime during cutover
- [ ] All application queries working correctly
- [ ] Query performance same or better than PG12
- [ ] Monitoring confirms system health for 2 weeks

## Risk Mitigation
- **Rollback plan**: Keep PG12 instance available for 2 weeks; can revert in < 15 minutes
- **Monitoring**: Track query latency, error rates, connection pool health
- **Testing strategy**: Full migration dry-run in staging, 24-hour soak test

## Timeline Constraints
Must complete by October 2024 (1 month before PG12 EOL). Testing requires 3 weeks.
```

---

## Template 4: API Development Epic

```markdown
## Overview
[What API or integration we're building]

## Source Specification
[Link to API design doc or requirements]

## Use Cases
[Primary scenarios this API will enable]

## API Design
- **Authentication**: [Method - API keys, OAuth, etc.]
- **Rate limiting**: [Limits and quotas]
- **Versioning**: [Strategy]
- **Base URL**: [Endpoint structure]

## Endpoints Summary
[High-level list of main endpoint categories]

## Success Criteria
- [ ] [API stability metric]
- [ ] [Performance target]
- [ ] [Documentation completeness]
- [ ] [Developer adoption metric]

## Documentation Deliverables
- [ ] OpenAPI/Swagger spec
- [ ] Getting started guide
- [ ] Code examples (Python, JavaScript)
- [ ] Interactive API explorer

## Timeline
- **Beta release**: [Date]
- **GA release**: [Date]
```

### Example: Public REST API

```markdown
## Overview
Launch v1 of public REST API enabling third-party developers to integrate with our platform for user management and resource access.

## Source Specification
https://company.atlassian.net/wiki/spaces/API/pages/456789/Public-API-v1-Spec

## Use Cases
- SaaS companies integrating our user management into their products
- Data analytics tools pulling resource data
- Automation platforms connecting workflows
- Mobile app developers building custom clients

## API Design
- **Authentication**: OAuth 2.0 + API keys
- **Rate limiting**: 1,000 requests/hour per API key (higher tiers available)
- **Versioning**: URI-based (/v1/, /v2/)
- **Base URL**: https://api.company.com/v1

## Endpoints Summary
- User management (CRUD operations)
- Resource access (read-only initially)
- Webhooks for event notifications
- Account administration

## Success Criteria
- [ ] 99.9% uptime
- [ ] p95 latency < 200ms
- [ ] Complete OpenAPI documentation
- [ ] 50+ developers signed up for beta
- [ ] Zero security vulnerabilities in initial audit

## Documentation Deliverables
- [x] OpenAPI/Swagger spec
- [ ] Getting started guide
- [ ] Code examples (Python, JavaScript, Ruby)
- [ ] Interactive API explorer (Swagger UI)
- [ ] Authentication tutorial
- [ ] Best practices guide

## Timeline
- **Beta release**: February 15 (invite-only, 10 partners)
- **GA release**: March 30 (public availability)
```

---

## Template 5: Redesign/Modernization Epic

```markdown
## Overview
[What's being redesigned and why]

## Source Documentation
[Link to design specs, mockups, or requirements]

## Current Pain Points
- [Problem 1 with existing implementation]
- [Problem 2 with existing implementation]
- [Problem 3 with existing implementation]

## New Design Goals
- [Goal 1]
- [Goal 2]
- [Goal 3]

## Success Criteria
- [ ] [User experience metric]
- [ ] [Performance improvement]
- [ ] [Feature parity or improvements]
- [ ] [Accessibility standards met]

## Migration Strategy
[How users transition from old to new]

## Rollout Plan
[Phased rollout, A/B testing, feature flags]
```

### Example: Dashboard Modernization

```markdown
## Overview
Redesign main analytics dashboard with modern UI framework, improved performance, and better mobile support while maintaining all existing functionality.

## Source Documentation
https://company.atlassian.net/wiki/spaces/DESIGN/pages/567890/Dashboard-Redesign

## Current Pain Points
- Slow initial load time (4-6 seconds)
- Poor mobile experience (not responsive)
- Outdated UI feels "legacy"
- Difficult to customize widget layout
- Accessibility issues (WCAG 2.1 violations)

## New Design Goals
- Modern, clean visual design aligned with brand refresh
- < 2 second initial load time
- Fully responsive (desktop, tablet, mobile)
- Customizable dashboard layouts
- WCAG 2.1 AA compliant
- Improved data visualization clarity

## Success Criteria
- [ ] Initial load time < 2s (50% improvement)
- [ ] Perfect Lighthouse score (90+)
- [ ] Zero WCAG 2.1 AA violations
- [ ] 80% user approval rating in beta test
- [ ] Feature parity with legacy dashboard
- [ ] Mobile usage increases by 30%

## Migration Strategy
- Side-by-side availability during transition
- Users can switch between old/new with toggle
- Preferences automatically migrated
- 30-day sunset period for legacy dashboard

## Rollout Plan
1. Week 1: Internal beta (engineering team)
2. Week 2-3: Customer beta (10% of users via feature flag)
3. Week 4: Expand to 50% of users
4. Week 5: 100% rollout, legacy available via toggle
5. Week 9: Remove legacy dashboard
```

---

## Key Elements in Every Epic

Regardless of template, ensure every Epic includes:

1. **Clear objective** - Anyone should understand what's being built/fixed
2. **Source link** - Always link to the Confluence spec or design doc
3. **Success criteria** - Measurable outcomes that define "done"
4. **Scope clarity** - What IS and ISN'T included
5. **Context** - Enough background for someone new to understand why this matters

## Common Mistakes to Avoid

❌ **Too brief**: "Build notifications" - lacks context  
❌ **Too detailed**: Including implementation details that belong in tickets  
❌ **No success criteria**: How do we know when it's done?  
❌ **Missing source link**: Hard to trace back to requirements  
❌ **Vague scope**: Leads to scope creep and confusion
