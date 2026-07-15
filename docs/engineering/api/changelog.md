# API Changelog â€” Second Brain OS API

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-CHG-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |

---

## Format

This changelog follows the [Keep a Changelog](https://keepachangelog.com/) format. Each entry documents:

- **Date** (ISO 8601)
- **Version** of the API specification
- **Change Type**: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
- **Endpoint(s)**: The affected route(s)
- **Description**: What changed and why

---

## Migration Guides

### Between API Versions

When breaking changes are introduced under `/api/v2/`, a migration guide will appear here with:
1. A summary of what changed
2. Before/after code examples
3. Automated migration script (if available)

### Current Migration Path

There are currently no active migrations. All endpoints are under `/api/v1/`.

---

## Sunset Policy

When an endpoint is deprecated:

1. **Deprecation announced:** `Deprecation: true` header added to responses
2. **Sunset header added:** `Sunset: <RFC1123 date>` with minimum 6 months notice
3. **Migration guide published:** At least 3 months before sunset date
4. **Endpoint removed:** After sunset date

### Currently Deprecated Endpoints

None at this time.

---

## Version History

### [Unreleased]

### [1.0.0] â€” 2026-07-10

Initial API specification. The Second Brain OS API is now generally available with 31 routers under `/api/v1/`.

#### Added

- **Tasks** (`/api/v1/tasks/`): Full CRUD + complete action. Schemas: `TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskListResponse`
- **Courses** (`/api/v1/courses/`): Full CRUD with progress tracking. Schemas: `CourseCreate`, `CourseUpdate`, `CourseResponse`
- **Goals** (`/api/v1/goals/`): Full CRUD with progress. Schemas: `GoalCreate`, `GoalUpdate`, `GoalResponse`
- **Ideas** (`/api/v1/ideas/`): Full CRUD with stage pipeline. Schemas: `IdeaCreate`, `IdeaUpdate`, `IdeaResponse`
- **Chat** (`/api/v1/chat/`): AI chat with ARIA. Streaming support via SSE. Rate limited to 30 req/min. Schemas: `ChatRequest`, `ChatResponse`
- **Projects** (`/api/v1/projects/`): Full CRUD. Schemas: `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`
- **Resources** (`/api/v1/resources/`): Full CRUD with tags. Schemas: `ResourceCreate`, `ResourceUpdate`, `ResourceResponse`
- **Opportunities** (`/api/v1/opportunities/`): Full CRUD + AI matching. Schemas: `OpportunityCreate`, `OpportunityUpdate`, `OpportunityResponse`, `MatchRequest`
- **Income** (`/api/v1/income/`): Full CRUD with auto-calculated hourly rate. Schemas: `IncomeCreate`, `IncomeUpdate`, `IncomeResponse`
- **Habits** (`/api/v1/habits/`): Full CRUD with streak tracking. Schemas: `HabitCreate`, `HabitUpdate`, `HabitResponse`
- **Sleep** (`/api/v1/sleep/`): Full CRUD + wind-down recommendations. Schemas: `SleepCreate`, `SleepUpdate`, `SleepResponse`
- **Time** (`/api/v1/time/`): Full CRUD + timer stop + daily stats. Schemas: `TimeEntryCreate`, `TimeEntryUpdate`, `TimeEntryResponse`
- **Automation** (`/api/v1/automation/`): 6 AI trigger endpoints + plan/execute + data retention cleanup
- **Briefings** (`/api/v1/briefings/`): List, get today, get by ID, mark read. Schema: `BriefingRead`
- **Reviews** (`/api/v1/reviews/`): List, get latest, get by ID. Schema: `WeeklyReviewRead`
- **Memory** (`/api/v1/memory/`): Full CRUD + AI consolidation + search. Schemas: `MemoryCreate`, `MemoryUpdate`, `MemoryResponse`, `MemorySearchRequest`
- **Roadmap** (`/api/v1/roadmap/`): Full CRUD for milestones. Schemas: `RoadmapMilestoneCreate`, `RoadmapMilestoneUpdate`, `RoadmapMilestoneResponse`
- **Academics** (`/api/v1/academics/`): Subjects CRUD, marks CRUD, learning progress stats/timeline
- **Videos** (`/api/v1/videos/`): Full CRUD for video library. Schemas: `VideoCreate`, `VideoUpdate`, `VideoResponse`
- **Analytics** (`/api/v1/analytics/`): Daily summary, weekly trends, aggregated stats, AI pattern detection
- **Predictions** (`/api/v1/predictions/`): Task completion, habit streak risk, sleep insights, optimal productivity slots. All algorithmic (no AI dependency)
- **Notifications** (`/api/v1/notifications/`): List, mark read, mark all read, AI nudges, deadline alerts
- **NLP** (`/api/v1/nlp/`): Natural language parse + execute. Supports task creation and navigation
- **Prompts** (`/api/v1/prompts/`): List, get, render, history for all prompt files
- **Feedback** (`/api/v1/feedback/`): Submit feedback with rating, get summary with positive rate
- **Monitoring** (`/api/v1/monitoring/`): Token usage recording, cost tracking, agent activity, AI cache management, RED metrics dashboard
- **Data Export** (`/api/v1/data/export`): GDPR-compliant export across 18 data tables
- **Feature Flags** (`/api/v1/feature-flags/`): Full CRUD + per-user evaluation with rollout percentages
- **Auth** (`/api/v1/auth/`): API key rotation, JWT token refresh
- **Skills** (`/api/v1/skills/`): ~50+ endpoints for skills taxonomy, user skills, evidence, market data, certifications, learning paths, recommendations, events, audit log, analytics, forecasts, and materialized views
- **Learning** (`/api/v1/learning/insights`): AI-powered learning insights and pattern detection
- **System Endpoints**: `GET /`, `GET /health`, `GET /health/live`, `GET /health/ready`

#### Added (Infrastructure)

- Rate limiting middleware (sliding window, 100 req/min default)
- Per-endpoint rate limiter (chat: 30 req/min)
- `X-Request-ID` tracing on all requests
- `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
- CORS middleware (configurable origins)
- GZip compression middleware (min 1000 bytes)
- CSRF protection middleware
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`)
- Sentry error tracking integration
- Structured JSON logging with Logtail
- Background event outbox and webhook delivery services
- AI circuit breaker with 5-failure threshold

---

## Template for New Entries

When adding new API changes, use the following template:

```markdown
### [X.Y.Z] â€” YYYY-MM-DD

#### Added
- **Endpoint** (`/path/`): Description of what was added

#### Changed
- **Endpoint** (`/path/`): Description of what changed and why

#### Deprecated
- **Endpoint** (`/path/`): Reason for deprecation. Sunset date: YYYY-MM-DD. Migration to: `/new-path/`

#### Removed
- **Endpoint** (`/path/`): Reason for removal. Migration: `/new-path/`

#### Fixed
- **Endpoint** (`/path/`): Bug fix description

#### Security
- **Endpoint** (`/path/`): Security improvement description
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial changelog documenting all 31 routers and ~120 endpoints |
