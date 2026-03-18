# Task Breakdown Examples

This reference provides examples of effective task breakdowns for different types of specifications.

## Principles of Good Breakdowns

**DO:**
- Create tasks that are independently testable
- Group related frontend/backend work logically
- Include explicit testing and documentation tasks
- Use specific, actionable language
- Size tasks for 1-3 days of work typically

**DON'T:**
- Create overly granular tasks (e.g., "Write one function")
- Make tasks too large (e.g., "Build entire feature")
- Duplicate work across multiple tickets
- Use vague descriptions (e.g., "Do backend stuff")

## Example 1: New Feature - User Notifications System

### Spec Summary
Add email and in-app notifications for user actions (comments, mentions, updates).

### Good Breakdown (8 tasks)

**Epic:** User Notifications System

1. **Design notification data model and database schema**
   - Define notification types and attributes
   - Create database tables and indexes
   - Document schema in API docs

2. **Implement notification service backend**
   - Create notification creation/retrieval APIs
   - Add notification storage logic
   - Implement marking notifications as read

3. **Build email notification dispatcher**
   - Set up email template system
   - Implement async email sending queue
   - Add email preferences handling

4. **Create notification preferences API**
   - User settings for notification types
   - Email vs in-app preferences
   - Frequency controls (immediate, digest)

5. **Build notification UI components**
   - Notification bell icon with unread count
   - Notification dropdown panel
   - Individual notification cards

6. **Implement notification settings page**
   - Frontend for user preferences
   - Connect to preferences API
   - Add toggle controls for notification types

7. **Add notification triggers to existing features**
   - Hook into comment system
   - Hook into mention system
   - Hook into update/edit events

8. **Write tests and documentation**
   - Unit tests for notification service
   - Integration tests for email delivery
   - Update user documentation

### Why This Works
- Each task is independently completable
- Clear separation between backend, frontend, and integration
- Testing is explicit
- Tasks are sized appropriately (1-3 days each)

---

## Example 2: Bug Fix - Payment Processing Errors

### Spec Summary
Users report intermittent payment failures. Investigation shows timeout issues with payment gateway and inadequate error handling.

### Good Breakdown (5 tasks)

**Epic:** Fix Payment Processing Reliability

1. **Investigate and document payment failure patterns**
   - Analyze error logs and failure rates
   - Document specific error scenarios
   - Create reproduction steps

2. **Implement payment gateway timeout handling**
   - Add configurable timeout settings
   - Implement retry logic with exponential backoff
   - Add circuit breaker pattern

3. **Improve payment error messaging**
   - Enhance error categorization
   - Add user-friendly error messages
   - Log detailed errors for debugging

4. **Add payment status reconciliation job**
   - Create background job to verify payment status
   - Handle stuck/pending payments
   - Send notifications for payment issues

5. **Add monitoring and alerting**
   - Set up payment failure rate alerts
   - Add dashboard for payment health metrics
   - Document troubleshooting procedures

### Why This Works
- Starts with investigation (important for bugs)
- Addresses root cause and symptoms
- Includes monitoring to prevent recurrence
- Each task delivers incremental value

---

## Example 3: Infrastructure - Migration to New Database

### Spec Summary
Migrate from PostgreSQL 12 to PostgreSQL 15, update queries to use new features, ensure zero downtime.

### Good Breakdown (7 tasks)

**Epic:** PostgreSQL 15 Migration

1. **Set up PostgreSQL 15 staging environment**
   - Provision new database instances
   - Configure replication from production
   - Verify data consistency

2. **Audit and update database queries**
   - Identify queries using deprecated features
   - Update to PostgreSQL 15 syntax
   - Optimize queries for new planner

3. **Update application connection pooling**
   - Upgrade database drivers
   - Adjust connection pool settings
   - Test connection handling under load

4. **Create migration runbook**
   - Document step-by-step migration process
   - Define rollback procedures
   - List success criteria and validation steps

5. **Perform dry-run migration in staging**
   - Execute full migration process
   - Validate data integrity
   - Measure downtime duration
   - Test rollback procedure

6. **Execute production migration**
   - Follow migration runbook
   - Monitor system health during migration
   - Validate all services post-migration

7. **Post-migration cleanup and monitoring**
   - Remove old database instances after verification period
   - Update monitoring dashboards
   - Document lessons learned

### Why This Works
- Emphasizes planning and validation
- Includes explicit dry-run
- Risk mitigation with rollback planning
- Clear separation between prep, execution, and cleanup

---

## Example 4: API Development - Public REST API

### Spec Summary
Create public REST API for third-party integrations. Include authentication, rate limiting, and documentation.

### Good Breakdown (9 tasks)

**Epic:** Public REST API v1

1. **Design API specification**
   - Define endpoints and request/response schemas
   - Create OpenAPI/Swagger specification
   - Review with stakeholders

2. **Implement API authentication system**
   - Add API key generation and management
   - Implement OAuth2 flow
   - Create authentication middleware

3. **Build rate limiting infrastructure**
   - Implement token bucket algorithm
   - Add per-key rate limit tracking
   - Create rate limit headers and responses

4. **Implement core API endpoints - Users**
   - GET /users endpoints
   - POST /users endpoints
   - PUT/DELETE /users endpoints

5. **Implement core API endpoints - Resources**
   - GET /resources endpoints
   - POST /resources endpoints
   - PUT/DELETE /resources endpoints

6. **Add API versioning support**
   - Implement version routing
   - Add deprecation headers
   - Document versioning strategy

7. **Create developer portal and documentation**
   - Set up documentation site
   - Add interactive API explorer
   - Write getting started guide and examples

8. **Build API monitoring and analytics**
   - Track API usage metrics
   - Add error rate monitoring
   - Create usage dashboards for customers

9. **Write integration tests and SDK examples**
   - Create comprehensive API test suite
   - Write example code in Python/JavaScript
   - Document common integration patterns

### Why This Works
- Separates authentication and rate limiting (critical infrastructure)
- Groups endpoints by resource type
- Documentation is a first-class task
- Monitoring and developer experience are explicit

---

## Example 5: Frontend Redesign - Dashboard Modernization

### Spec Summary
Redesign main dashboard with modern UI framework, improve performance, maintain feature parity.

### Good Breakdown (8 tasks)

**Epic:** Dashboard UI Modernization

1. **Create new component library foundation**
   - Set up new UI framework (e.g., React + Tailwind)
   - Build reusable component primitives
   - Establish design system tokens

2. **Build dashboard layout and navigation**
   - Implement responsive grid layout
   - Create new navigation sidebar
   - Add breadcrumb and header components

3. **Rebuild analytics widgets**
   - Port existing chart components
   - Implement new data visualization library
   - Add loading and error states

4. **Rebuild data table components**
   - Create sortable/filterable table
   - Add pagination and search
   - Implement column customization

5. **Implement user settings panel**
   - Dashboard customization options
   - Widget arrangement and visibility
   - Preferences persistence

6. **Optimize performance and lazy loading**
   - Implement code splitting
   - Add lazy loading for heavy widgets
   - Optimize bundle size

7. **Add responsive mobile views**
   - Create mobile-optimized layouts
   - Test on various screen sizes
   - Implement touch gestures

8. **Migration and A/B testing setup**
   - Create feature flag for new dashboard
   - Set up A/B test framework
   - Plan gradual rollout strategy

### Why This Works
- Foundation first (component library)
- Groups by feature area (analytics, tables)
- Performance and mobile are explicit tasks
- Includes rollout strategy

---

## Anti-Patterns to Avoid

### Too Granular
❌ **Bad:**
- "Create User model"
- "Create User controller"  
- "Create User view"
- "Write User tests"
- "Update User documentation"

✅ **Better:**
- "Implement User management feature (model, controller, views, tests)"

### Too Vague
❌ **Bad:**
- "Do backend work"
- "Fix frontend issues"
- "Update database"

✅ **Better:**
- "Implement user authentication API endpoints"
- "Resolve navigation menu rendering bugs"
- "Add indexes to orders table for query performance"

### Missing Testing
❌ **Bad:**
- Only feature implementation tasks, no testing mentioned

✅ **Better:**
- Include explicit testing tasks or ensure testing is part of each feature task

### No Clear Ownership
❌ **Bad:**
- Tasks that require both frontend and backend work without clear boundaries

✅ **Better:**
- Split into "Backend API for X" and "Frontend UI for X" when different people work on each
