# Task Breakdown

> **Document ID:OPS-TSK-001 SB-OPS-TASK-005  
> **Version:** 2.0.0  
> **Status:** Active  
> **Last Updated:** 2026-06-11  
> **Classification:** Internal â€” Development Process  
> **Owner:** Lead Developer  

---

## Table of Contents

1. [Task Decomposition Methodology](#1-task-decomposition-methodology)
2. [Task Size Guidelines](#2-task-size-guidelines)
3. [Task Template](#3-task-template)
4. [Task Types and Subtask Breakdown Patterns](#4-task-types-and-subtask-breakdown-patterns)
5. [Estimation Techniques](#5-estimation-techniques)
6. [Task Dependencies Management](#6-task-dependencies-management)
7. [Task Prioritization Framework](#7-task-prioritization-framework)
8. [Sprint Capacity Planning](#8-sprint-capacity-planning)
9. [Tracking Tools](#9-tracking-tools)
10. [Task Lifecycle States](#10-task-lifecycle-states)
11. [Definition of Ready Per Task](#11-definition-of-ready-per-task)
12. [Appendices](#12-appendices)

---

## 1. Task Decomposition Methodology

### 1.1 Decomposition Hierarchy

```
Epic (Multi-sprint initiative)
    â”‚
    â–¼
User Story (User-valuable feature â€” fits in 1 sprint)
    â”‚
    â–¼
Feature (Logical unit of work â€” 1-3 days)
    â”‚
    â–¼
Task (Individual work item â€” 2-8 hours)
    â”‚
    â–¼
Subtask (Granular action â€” < 2 hours, optional)
```

### 1.2 Decomposition Rules

| Level | Duration | Story Points | Responsible | Completeness Check |
|---|---|---|---|---|
| Epic | 2-6 sprints | 40-100+ | Product Owner | Milestone achieved |
| User Story | 1-3 days | 5-13 | Product Owner | Acceptance criteria met |
| Feature | 1-2 days | 3-8 | Tech Lead | Feature complete |
| Task | 2-8 hours | 1-3 | Developer | DoD checklist |
| Subtask | < 2 hours | Not estimated | Developer | Subtask completed |

### 1.3 Decomposition Process

```mermaid
graph TD
    A[Epic / Initiative] --> B{Break down into<br>User Stories}
    B --> C[Story 1: User login]
    B --> D[Story 2: Dashboard]
    B --> E[Story 3: Task management]
    
    C --> F{Break story into<br>Features}
    F --> G[Auth UI]
    F --> H[Session management]
    F --> I[OAuth integration]
    
    G --> J{Break feature into<br>Tasks}
    J --> K[Create login page]
    J --> L[Add form validation]
    J --> M[Connect to auth API]
    J --> N[Write tests]
```

**Step-by-step decomposition workflow:**

1. **Start with the epic** â€” What is the high-level goal?
2. **Identify user stories** â€” What value does each user get?
3. **Break stories into features** â€” What technical capabilities are needed?
4. **Split features into tasks** â€” What are the individual work items?
5. **Optionally create subtasks** â€” What are the exact steps for each task?

### 1.4 Decomposition Heuristics

| If a story/feature is... | Then... |
|---|---|
| > 13 story points | Split into multiple stories |
| > 3 days of work | Split into multiple features |
| > 8 hours for one task | Break into smaller tasks |
| Understood by only 1 person | Need knowledge sharing first |
| Dependent on 3+ other items | Escalate dependency resolution |
| Not testable in isolation | Restructure to make testable |

### 1.5 INVEST Principle for User Stories

| Letter | Meaning | Question |
|---|---|---|
| **I** | Independent | Can it be developed independently? |
| **N** | Negotiable | Is there room for discussion? |
| **V** | Valuable | Does it deliver value to users? |
| **E** | Estimable | Can the team estimate it? |
| **S** | Small | Is it small enough to fit in a sprint? |
| **T** | Testable | Can we verify it's done? |

---

## 2. Task Size Guidelines

### 2.1 Size Limits

| Metric | Optimal | Maximum | Action if Exceeded |
|---|---|---|---|
| Duration | < 4 hours (half day) | 3 days | Split into 2+ tasks |
| Story points | 1-3 points | 8 points | Split into 2+ tasks |
| Lines of code | < 100 lines | 400 lines (per PR) | Split into stacked PRs |
| Files changed | 1-5 files | 15 files | Split by concern |
| Dependencies | 0-2 | 5 | Resolve dependencies first |

### 2.2 Breaking Down Large Tasks

**Task > 3 days: Break by concern**

```
âŒ BAD: Large task
"Build task management feature" (5 days, 8 points)

âœ… GOOD: Broken down
1. "Create task API endpoints"          (2 days, 3 points)
2. "Build task list UI component"       (1 day, 2 points)
3. "Add task creation form"             (1 day, 2 points)
4. "Implement task filtering & search"  (1 day, 2 points)
```

**Task > 3 days: Break by layer**

```
1. "Backend: task CRUD API"             (1 day, 2 points)
2. "Frontend: task data fetching layer" (1 day, 2 points)
3. "Frontend: task UI components"       (1 day, 2 points)
4. "Testing: integration + E2E tests"   (0.5 day, 1 point)
```

### 2.3 Task Granularity Examples

| Granularity | Duration | Example |
|---|---|---|
| Too coarse | 1 week | "Build the entire dashboard" |
| Good | 1-2 days | "Create daily briefing API endpoint" |
| Good | 4-8 hours | "Add form validation to login page" |
| Too fine | 15 minutes | "Rename variable 'x' to 'userCount'" |

### 2.4 Time Boxing for Unknown Tasks

When a task involves unknowns (spike/research), timebox it:

```markdown
## Timeboxed Task Template

**Task:** Research vector database options
**Timebox:** 4 hours (no more)
**Goal:** Recommend primary and secondary vector DB choices

**Research questions:**
1. What vector DBs work with Supabase?
2. What is the pricing model?
3. What is the setup complexity?
4. What is the query performance?

**Output:** 1-page comparison doc with recommendation

**Decision point:** After 4 hours, present findings; decide to continue or pivot
```

---

## 3. Task Template

### 3.1 Standard Task Template

```markdown
---
title: "[Module] Brief task description"
labels: [type/feature, module/<module>]
assignees: [username]
milestone: SB-YY.SN
---

## Description

[Clear description of what needs to be done. Include context and motivation.]

## Acceptance Criteria

- [ ] [Criterion 1 â€” specific, measurable, testable]
- [ ] [Criterion 2 â€” specific, measurable, testable]
- [ ] [Criterion 3 â€” specific, measurable, testable]

## Technical Notes

- [Implementation approach or design decisions]
- [Relevant files or modules that need to be modified]
- [Any known constraints or gotchas]

## Files to Modify

- `apps/api/app/api/<module>.py` â€” [what changes]
- `apps/web/app/<module>/page.tsx` â€” [what changes]
- `packages/ai/agents/<agent>.py` â€” [what changes]

## Dependencies

### Blocked By
- #[issue-number] â€” [description of dependency]
- #[issue-number] â€” [description of dependency]

### Blocks
- #[issue-number] â€” [description of what this blocks]

## Effort

- Story Points: [1|2|3|5|8]
- T-shirt Size: [XS|S|M|L]
- Estimated Hours: [hours]

## Definition of Ready Checklist

- [ ] Acceptance criteria are clear and testable
- [ ] Dependencies are identified
- [ ] Technical approach is defined
- [ ] Design is approved (if UI change)
- [ ] Task is estimated
- [ ] Task is sized correctly (< 3 days)

## Testing Notes

- [What to test, edge cases to consider]
- [Unit tests needed? Integration tests? E2E?]
```

### 3.2 Bug Fix Task Template

```markdown
---
title: "fix([module]): [brief description of bug]"
labels: [type/bug, severity/<severity>]
assignees: [username]
---

## Bug Description

[Clear description of the bug, including what happens vs what should happen]

## Steps to Reproduce

1. Go to [page]
2. Click on [element]
3. Scroll to [position]
4. See error: [actual behavior]

## Expected Behavior

[What should happen instead]

## Environment

- Browser: [Chrome/Firefox/Safari/Edge] [version]
- OS: [Windows/macOS/Linux]
- Device: [Desktop/Tablet/Mobile]
- App Version: [version or commit]

## Screenshots / Logs

[Attach screenshots, console logs, or error messages]

## Root Cause Analysis

[To be filled during investigation]

## Technical Notes

- [Relevant files, modules, or functions]
- [Suspected cause]

## Checklist

- [ ] Bug reproduced in dev environment
- [ ] Root cause identified
- [ ] Unit test added (that fails without fix)
- [ ] Fix implemented
- [ ] Regression tests pass
- [ ] PR created
- [ ] Deployed (if critical)
```

### 3.3 Tech Debt Task Template

```markdown
---
title: "refactor([module]): [description]"
labels: [type/tech-debt]
assignees: [username]
---

## Current State

[Description of the current code or architecture problem]

## Problem

- [Issue 1: e.g., slow performance]
- [Issue 2: e.g., hard to test]
- [Issue 3: e.g., duplicate code]

## Target State

[Description of the desired state after refactoring]

## Migration Plan

1. [Step 1: e.g., Extract function]
2. [Step 2: e.g., Move to new module]
3. [Step 3: e.g., Update references]
4. [Step 4: e.g., Remove old code]

## Risk Assessment

- Risk level: [Low/Medium/High]
- Behavior change: [None/Minimal/Some]
- Rollback plan: [How to revert]

## Verification

- [ ] Existing tests pass with no changes
- [ ] Performance benchmarks within 5% of baseline
- [ ] Manual smoke test of affected features
```

---

## 4. Task Types and Subtask Breakdown Patterns

### 4.1 Frontend Feature Breakdown

```
Story: "As a user, I want to view my tasks with priority sorting"

Feature: Task list with priority sorting

Tasks:
â”œâ”€â”€ 1. API Layer (2 points)
â”‚   â”œâ”€â”€ Create API endpoint: GET /api/tasks?sort=priority
â”‚   â”œâ”€â”€ Add TypeScript types for priority sort params
â”‚   â””â”€â”€ Write API integration tests
â”‚
â”œâ”€â”€ 2. Data Fetching (1 point)
â”‚   â”œâ”€â”€ Create useTasks hook with sort parameter
â”‚   â”œâ”€â”€ Add loading and error states
â”‚   â””â”€â”€ Implement optimistic updates
â”‚
â”œâ”€â”€ 3. UI Components (3 points)
â”‚   â”œâ”€â”€ Build TaskList component with sort dropdown
â”‚   â”œâ”€â”€ Create PriorityBadge component
â”‚   â”œâ”€â”€ Implement drag-to-reorder (priority-based)
â”‚   â””â”€â”€ Add empty state and error state
â”‚
â”œâ”€â”€ 4. State Management (1 point)
â”‚   â”œâ”€â”€ Add sort preference to Zustand store
â”‚   â”œâ”€â”€ Persist sort preference to localStorage
â”‚   â””â”€â”€ Handle edge case: no tasks to sort
â”‚
â”œâ”€â”€ 5. Styling (1 point)
â”‚   â”œâ”€â”€ CSS for priority indicators
â”‚   â”œâ”€â”€ Responsive layout adjustments
â”‚   â””â”€â”€ Dark mode compliance
â”‚
â””â”€â”€ 6. Tests (2 points)
    â”œâ”€â”€ Unit tests for sorting logic
    â”œâ”€â”€ Component tests for TaskList
    â”œâ”€â”€ Integration tests for API + fetch
    â””â”€â”€ E2E test for full flow
```

### 4.2 Backend Endpoint Breakdown

```
Task: Create task CRUD API endpoint

Subtasks:
â”œâ”€â”€ 1. Data Model (1 hour)
â”‚   â”œâ”€â”€ Define Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse)
â”‚   â”œâ”€â”€ Validate fields (title length, priority enum, due_date format)
â”‚   â””â”€â”€ Add OpenAPI examples
â”‚
â”œâ”€â”€ 2. Database (1 hour)
â”‚   â”œâ”€â”€ Write Supabase migration (if table doesn't exist)
â”‚   â”œâ”€â”€ Add RLS policy for user isolation
â”‚   â””â”€â”€ Add indexes on commonly queried fields
â”‚
â”œâ”€â”€ 3. Route Handler (2 hours)
â”‚   â”œâ”€â”€ Create CRUD functions (create, read, update, delete, list)
â”‚   â”œâ”€â”€ Add error handling (404, 400, 500)
â”‚   â”œâ”€â”€ Add pagination for list endpoint
â”‚   â””â”€â”€ Implement query parameters (filter, sort, search)
â”‚
â”œâ”€â”€ 4. Validation (1 hour)
â”‚   â”œâ”€â”€ Input sanitization
â”‚   â”œâ”€â”€ Business rule validation (due_date not in past)
â”‚   â””â”€â”€ Permission validation (user_id matches auth)
â”‚
â”œâ”€â”€ 5. Tests (2 hours)
â”‚   â”œâ”€â”€ Unit tests for validation logic
â”‚   â”œâ”€â”€ Integration tests for each CRUD operation
â”‚   â”œâ”€â”€ Test error cases (invalid input, missing record)
â”‚   â””â”€â”€ Test RLS policy enforcement
â”‚
â””â”€â”€ 6. Documentation (30 min)
    â”œâ”€â”€ Update OpenAPI schema
    â”œâ”€â”€ Add examples to API docs
    â””â”€â”€ Update endpoint inventory
```

### 4.3 Agent Module Breakdown

```
Story: "ARIA should generate daily briefings with AI"

Feature: Daily Briefing Agent (A09)

Tasks:
â”œâ”€â”€ 1. Prompt Engineering (3 points)
â”‚   â”œâ”€â”€ Create prompts/agents/briefing_agent.md with YAML frontmatter
â”‚   â”œâ”€â”€ Define output JSON schema (tasks_summary, courses_progress, etc.)
â”‚   â”œâ”€â”€ Write 5+ few-shot examples
â”‚   â”œâ”€â”€ Document edge cases and anti-patterns
â”‚   â””â”€â”€ Run validate_prompts.py â€” pass with zero errors
â”‚
â”œâ”€â”€ 2. Agent Module (3 points)
â”‚   â”œâ”€â”€ Create packages/ai/agents/briefing_agent.py
â”‚   â”œâ”€â”€ Import from PromptLoader: prompts.get_agent("briefing_agent")
â”‚   â”œâ”€â”€ Implement generate_briefing(user_id) async function
â”‚   â”œâ”€â”€ Add fallback prompt (hardcoded inline string)
â”‚   â”œâ”€â”€ Parse LLM response as JSON with validation
â”‚   â””â”€â”€ Handle LLM failure gracefully (return default briefing)
â”‚
â”œâ”€â”€ 3. Database Integration (2 points)
â”‚   â”œâ”€â”€ Create daily_briefings table in Supabase
â”‚   â”œâ”€â”€ Add RLS policy
â”‚   â”œâ”€â”€ Create Pydantic schemas
â”‚   â””â”€â”€ Create API endpoint: GET /api/briefings/latest
â”‚
â”œâ”€â”€ 4. Scheduler Integration (2 points)
â”‚   â”œâ”€â”€ Add cron job in services/scheduler/main.py
â”‚   â”œâ”€â”€ Configure trigger at 7:00 AM daily
â”‚   â”œâ”€â”€ Add error handling and retry logic
â”‚   â””â”€â”€ Add logging for monitoring
â”‚
â”œâ”€â”€ 5. Frontend UI (2 points)
â”‚   â”œâ”€â”€ Create dashboard briefing card component
â”‚   â”œâ”€â”€ Format LLM output for display
â”‚   â”œâ”€â”€ Add loading skeleton
â”‚   â”œâ”€â”€ Add refresh button
â”‚   â””â”€â”€ Handle case: no briefing available yet
â”‚
â””â”€â”€ 6. Testing (2 points)
    â”œâ”€â”€ Prompt content tests (tests/test_agent_prompts.py)
    â”œâ”€â”€ Agent unit tests (mock LLM, verify parsing)
    â”œâ”€â”€ Integration test (scheduler â†’ agent â†’ database)
    â””â”€â”€ Manual testing with real LLM
```

### 4.4 Bug Fix Breakdown

```
Task: Fix login redirect loop when token expires

Subtasks:
â”œâ”€â”€ 1. Reproduce (30 min)
â”‚   â”œâ”€â”€ Set up test scenario: expired token
â”‚   â”œâ”€â”€ Document exact reproduction steps
â”‚   â””â”€â”€ Capture error logs
â”‚
â”œâ”€â”€ 2. Locate Root Cause (1 hour)
â”‚   â”œâ”€â”€ Trace auth middleware flow
â”‚   â”œâ”€â”€ Identify where redirect is triggered
â”‚   â””â”€â”€ Determine why refresh isn't happening first
â”‚
â”œâ”€â”€ 3. Fix Implementation (2 hours)
â”‚   â”œâ”€â”€ Move token expiry check after refresh attempt
â”‚   â”œâ”€â”€ Add max redirect counter (3) to prevent infinite loops
â”‚   â”œâ”€â”€ Add toast notification on token refresh failure
â”‚   â””â”€â”€ Minimize diff (only touch affected lines)
â”‚
â”œâ”€â”€ 4. Tests (1 hour)
â”‚   â”œâ”€â”€ Add unit test for token refresh flow
â”‚   â”œâ”€â”€ Add integration test for expired token handling
â”‚   â””â”€â”€ Verify no regression in other auth flows
â”‚
â””â”€â”€ 5. Deploy (30 min)
    â”œâ”€â”€ Create PR with bug fix
    â”œâ”€â”€ Deploy to production
    â””â”€â”€ Verify fix with smoke test
```

### 4.5 Refactoring Breakdown

```
Task: Refactor PromptLoader for better error handling

Subtasks:
â”œâ”€â”€ 1. Map Current State (1 hour)
â”‚   â”œâ”€â”€ Document current PromptLoader architecture
â”‚   â”œâ”€â”€ Identify pain points (error handling, caching)
â”‚   â””â”€â”€ Read all current consumers
â”‚
â”œâ”€â”€ 2. Plan Migration (1 hour)
â”‚   â”œâ”€â”€ Design new error handling approach
â”‚   â”œâ”€â”€ Define new public API
â”‚   â””â”€â”€ Write migration plan
â”‚
â”œâ”€â”€ 3. Execute Refactoring (4 hours)
â”‚   â”œâ”€â”€ Add error handling for YAML parse failures
â”‚   â”œâ”€â”€ Add caching layer with TTL
â”‚   â”œâ”€â”€ Add logging for debug
â”‚   â””â”€â”€ Update type hints
â”‚
â”œâ”€â”€ 4. Verify (1 hour)
â”‚   â”œâ”€â”€ Run existing tests â€” all pass unchanged
â”‚   â”œâ”€â”€ Add new tests for error scenarios
â”‚   â””â”€â”€ Manual test with malformed prompt files
â”‚
â””â”€â”€ 5. Clean Up (30 min)
    â”œâ”€â”€ Remove deprecated methods
    â”œâ”€â”€ Update documentation
    â””â”€â”€ Mark migration task as complete
```

### 4.6 Task Breakdown by Module (Second Brain OS)

| Module | Typical Tasks | Avg Points |
|---|---|---|
| Tasks API | CRUD endpoint, filtering, sorting, prioritization | 2-3 |
| Tasks UI | List view, create form, drag-drop, search | 3-5 |
| Courses | Progress tracking, enrollment, deadlines | 2-5 |
| Habits | Streak calculation, logging, calendar view | 3-5 |
| Sleep | Logging, score calculation, wind-down | 2-3 |
| Income | Entry logging, hourly rate, reporting | 2-3 |
| Projects | Phase management, blocker tracking | 3-5 |
| Ideas | Pipeline management, voting, evaluation | 2-3 |
| Resources | CRUD, tagging, search | 2-3 |
| Opportunities | Matching algorithm, scoring, notifications | 3-5 |
| Time | Pomodoro timer, deep work tracking, stats | 3-5 |
| AI Agents | Prompt engineering, agent module, fallback | 3-8 |
| Prompt System | New prompt, validation, testing | 2-5 |
| Scheduler | Cron job, error handling, monitoring | 2-3 |
| Infrastructure | CI/CD, deployment, monitoring | 3-5 |
| Documentation | API docs, README, runbooks | 1-2 |

---

## 5. Estimation Techniques

### 5.1 T-Shirt Sizing â†’ Fibonacci

| T-Shirt | Points | Time Range | Certainty |
|---|---|---|---|
| XS | 1 | < 2 hours | Very high |
| S | 2 | 2-4 hours | High |
| M | 3 | 4-8 hours (1 day) | High |
| L | 5 | 1-2 days | Moderate |
| XL | 8 | 2-3 days | Moderate |
| XXL | 13 | 3-5 days | Low â€” must split |

### 5.2 Affinity Estimation

For estimating many items quickly:

```
1. Place all stories on a table/board
2. Team silently sorts stories into groups by size
3. Groups are labeled: XS, S, M, L, XL, XXL
4. Review and adjust as a team
5. Convert T-shirt sizes to Fibonacci points
```

**Best for:** Backlog refinement with 10+ unestimated items
**Time:** 15-30 minutes for 20 items
**Accuracy:** Â±30% (acceptable for backlog prioritization)

### 5.3 Reference Stories

Fixed reference stories that the team calibrates against:

```markdown
## Reference Stories (1 point)
- Fix a typo in a UI label
- Update a CSS variable in tailwind.config.js
- Add a comment to a function

## Reference Stories (2 points)
- Add form validation to an existing form
- Create a simple CRUD endpoint (following existing pattern)
- Update API documentation for one endpoint

## Reference Stories (3 points)
- Create a new page component with data fetching
- Add a new database table with RLS policies
- Implement a small LLM agent with fallback

## Reference Stories (5 points)
- Build a new module from scratch (backend + frontend)
- Implement a real-time feature with Supabase subscriptions
- Create a dashboard with multiple data sources

## Reference Stories (8 points)
- Implement a complex AI agent with prompt engineering
- Build an E2E feature across all layers
- Major refactoring of a core module

## Reference Stories (13 points)
- Epic-level feature spanning multiple sprints
- Architecture-level change (data model migration)
- Integrating a new external service
```

### 5.4 Estimation Guidelines

| Principle | Description |
|---|---|
| **Relative sizing** | Compare to reference stories, not absolute time |
| **Collective ownership** | Whole team estimates, not just implementer |
| **No anchoring** | Don't reveal your estimate first (use planning poker) |
| **Timebox estimation** | Max 5 minutes per story |
| **Trust the process** | Velocity will calibrate over 3-5 sprints |
| **Don't revise** | Once a story is pointed, points don't change (split instead) |

### 5.5 Common Estimation Anti-Patterns

| Anti-Pattern | Problem | Solution |
|---|---|---|
| "This is like the last one" | False comparison | Break down and re-estimate |
| "It's simple, just 2 points" | Underselling complexity | Add buffer for unknowns |
| "We need to pad for risk" | Over-estimation | Add separate risk/uncertainty task |
| "It's 13 points, but we'll squeeze" | Overcommitment | Split into multiple stories > 13 |
| "Bob can do it in 1 day" | Single-person perspective | Team estimates, not individual |
| "We did this before, same points" | Scope creep ignored | If scope changed, points change |

---

## 6. Task Dependencies Management

### 6.1 Dependency Types

| Type | Description | Example | Resolution |
|---|---|---|---|
| **Technical** | Code depends on other code | Frontend waiting for API | API-first development |
| **External** | Third-party service or team | Waiting for Supabase feature | Escalate, find alternative |
| **Knowledge** | Need expertise from someone | LLM prompt expertise | Pair programming |
| **Data** | Need data to test | Need seed data | Create seed scripts |
| **Decision** | Waiting for decision | Design approval | Set decision deadline |
| **Process** | Blocked by process | Code review pending | SLA enforcement |

### 6.2 Dependency Tracking

**In GitHub Issues, use the linked issues feature:**

```markdown
## Dependencies

### Blocked By (must complete first)
- [ ] #142 â€” Task API endpoints (Alice) â€” Due: S7.D3
- [ ] #143 â€” Database migrations (Bob) â€” Due: S7.D2

### Blocks (must complete before these can start)
- [ ] #145 â€” Task list UI (Carol) â€” Needs API endpoints
- [ ] #146 â€” Task filtering (Dave) â€” Needs API endpoints
```

**Dependency status labels:**

| Label | Meaning |
|---|---|
| `status/blocked` | Cannot proceed, waiting on dependency |
| `status/needs-dependency` | Dependency identified, not yet resolved |
| `status/dependency-resolved` | Blocking item complete, ready to proceed |

### 6.3 Dependency Graph

```mermaid
graph LR
    A[DB Migration] --> B[API Endpoint]
    B --> C[Frontend UI]
    B --> D[Agent Integration]
    C --> E[E2E Tests]
    D --> F[Prompt Validation]
    E --> G[Sprint Review Ready]
    F --> G
    
    style A fill:#f9f,stroke:#333
    style G fill:#9f9,stroke:#333
```

### 6.4 Critical Path Analysis

For complex features, identify the critical path (longest dependent chain):

```
Task: Daily Briefing Agent feature

Chain A (Frontend): 
  API endpoint â†’ Frontend card â†’ Dashboard integration â†’ Tests = 5 days

Chain B (Backend): 
  DB migration â†’ Agent module â†’ Prompt â†’ Scheduler â†’ Tests = 8 days â¬… CRITICAL

Chain C (Integration):
  Agent + Scheduler â†’ E2E tests â†’ Documentation = 3 days

Critical path = Chain B (8 days)
Schedule buffer = 2 days (for risk)
Total timeline = 10 days = 1 sprint
```

### 6.5 Dependency Resolution SLA

| Dependency Type | Max Wait Time | Escalation |
|---|---|---|
| Code review | 12 hours | Ping reviewer after 12h |
| Design approval | 24 hours | Escalate to Design Lead |
| External team | 48 hours | Escalate to Engineering Manager |
| Decision (PM) | 24 hours | Escalate to Product Owner |
| Technical spike | 4 hours (timebox) | Decide: continue or pivot |

---

## 7. Task Prioritization Framework

### 7.1 RICE Scoring

**Formula:** RICE Score = `(Reach Ã— Impact Ã— Confidence) / Effort`

| Factor | Description | Scale | Weight |
|---|---|---|---|
| **Reach** | How many users per time period? | 0.25 (0.25Ã—) |
| **Impact** | How much impact per user? | 0.35 (0.35Ã—) |
| **Confidence** | How confident are we? | 0.15 (multiplier) |
| **Effort** | How many person-months? | - (divisor) |

**Scoring Guide:**

| Score | Reach (users/quarter) | Impact | Confidence |
|---|---|---|---|
| 5 | All users (1000+) | Massive (core workflow) | Very high (solid data) |
| 4 | Most users (500-1000) | High (major improvement) | High (good data) |
| 3 | Some users (100-500) | Medium (noticeable) | Medium (reasonable) |
| 2 | Few users (10-100) | Low (minor) | Low (educated guess) |
| 1 | Very few (<10) | Minimal (cosmetic) | Very low (wild guess) |

**Effort (person-months):**
- 0.5 = < 1 week
- 1.0 = 1-2 weeks
- 2.0 = 1 month
- 3.0 = 2 months
- 5.0 = 3+ months

**Example RICE Calculation:**

```
Feature: Daily Briefing Agent
Reach: 5 (all users get it daily)
Impact: 4 (significantly improves morning routine)
Confidence: 4 (well-understood, existing patterns)
Effort: 1.0 (2 weeks)

RICE = (5 Ã— 4 Ã— 4) / 1.0 = 80

Feature: Dark mode toggle
Reach: 3 (some users prefer dark mode)
Impact: 2 (nice to have, not critical)
Confidence: 3 (straightforward CSS)
Effort: 0.5 (3 days)

RICE = (3 Ã— 2 Ã— 3) / 0.5 = 36
```

### 7.2 Priority Matrix

```
                    High Impact
                        â”‚
                   â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”
                   â”‚         â”‚
    Low Effort â”€â”€â”€â”€â”¤ DO NOW  â”‚ SCHEDULE â”œâ”€â”€â”€â”€ High Effort
                   â”‚ (P0)    â”‚ (P1)     â”‚
                   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
                        â”‚
                   â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”
                   â”‚         â”‚
                   â”‚ DO NEXT â”‚ MAYBE    â”‚
                   â”‚ (P2)    â”‚ (P3/P4)  â”‚
                   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                        â”‚
                    Low Impact
```

### 7.3 Sprint Prioritization Rules

| Rule | Description |
|---|---|
| 60/20/10/10 split | 60% features, 20% tech debt, 10% bugs, 10% docs |
| P0 always first | Critical items go to top of sprint backlog |
| Max 1 P0 per developer | Prevents context switching on critical items |
| Stretch goals | 20% buffer for ambitious items |
| Cut scope, not quality | Remove features before cutting testing |

---

## 8. Sprint Capacity Planning

### 8.1 Per-Developer Capacity

| Role | Daily Hours | Focus Factor | Sprint Hours | Story Points (avg) |
|---|---|---|---|---|
| Full-stack Developer | 6 | 0.75 | 45 | 12-15 |
| Frontend Developer | 6 | 0.75 | 45 | 12-15 |
| Backend Developer | 6 | 0.80 | 48 | 13-16 |
| QA Engineer | 6 | 0.80 | 48 | Not applicable |
| Tech Lead | 5 | 0.50 | 25 | 5-8 |

### 8.2 Capacity Allocation Template

```markdown
## Sprint Capacity Plan â€” SB-26.S7

### Team Availability

| Name | Role | Days Avail | Hours/Day | Focus | Eff. Hours | Notes |
|---|---|---|---|---|---|---|
| Alice | Dev | 10 | 6 | 0.80 | 48 | Full sprint |
| Bob | Dev | 8 | 6 | 0.75 | 36 | Conference Mon-Tue |
| Carol | Dev | 10 | 6 | 0.80 | 48 | Full sprint |
| Dave | Dev | 10 | 6 | 0.75 | 45 | On-call week 1 |
| Eve | QA | 10 | 6 | 0.80 | 48 | Full sprint |
| **Total** | | **48** | | | **225** | |

### Sprint Goals
1. Feature: Daily Briefing Agent (A09)
2. Feature: Weekly Review Agent (A10)
3. Tech Debt: PromptLoader error handling
4. Bug Fixes: Auth redirect loop

### Capacity Allocation

| Developer | Assignment | Estimated Points |
|---|---|---|
| Alice | A09: Backend + Prompt | 8 |
| Bob | A09: Frontend + Scheduler | 5 |
| Alice | Tech debt: PromptLoader | 3 |
| Carol | A10: Agent + Prompt | 8 |
| Dave | A10: Frontend + Scheduler | 5 |
| Dave | Bug fixes | 3 |
| **Total Committed** | | **32** |
| **Team Velocity (avg)** | | **35** |
| **Forecast Confidence** | | **High (91%)** |
```

### 8.3 Velocity-Based Capacity

```markdown
## Velocity-Based Planning

| Sprint | Velocity |
|---|---|
| SB-26.S4 | 30 |
| SB-26.S5 | 33 |
| SB-26.S6 | 35 |
| **Average** | **32.7** |
| **Std Dev** | **2.5** |

### Forecast Ranges

| Scenario | Calculation | Points |
|---|---|---|
| Conservative | Avg - Ïƒ | 30 |
| Expected | Avg | 33 |
| Optimistic | Avg + Ïƒ | 35 |

### Recommended Commitment: 30-33 points
```

---

## 9. Tracking Tools

### 9.1 GitHub Issues Configuration

```yaml
# Issue fields configuration
fields:
  - name: Story Points
    type: number
    required: true
    range: [1, 2, 3, 5, 8, 13]

  - name: Priority
    type: single_select
    options: [P0, P1, P2, P3, P4]
    required: true

  - name: Module
    type: single_select
    options: [tasks, courses, habits, goals, sleep, income, projects,
              ideas, resources, opportunities, time, chat, automation,
              agents, prompts, api, web, db, ci, deps, infra, auth]
    required: true

  - name: Sprint
    type: iteration
    required: true

  - name: Status
    type: single_select
    options: [backlog, ready, in-progress, in-review, in-qa, done, deployed]
    required: true
```

### 9.2 Labels

```yaml
# Type
type/feature:     "New functionality"
type/bug:         "Defect fix"
type/tech-debt:   "Refactoring, optimization"
type/docs:        "Documentation"
type/spike:       "Research, investigation"
type/hotfix:      "Emergency production fix"

# Priority
priority/p0:      "Drop everything â€” critical"
priority/p1:      "High priority"
priority/p2:      "Medium priority"
priority/p3:      "Low priority"
priority/p4:      "Icebox"

# Module
module/tasks:     module/tasks
module/courses:   module/courses
module/habits:    module/habits
module/agents:    module/agents
module/prompts:   module/prompts
module/api:       module/api
module/web:       module/web
module/infra:     module/infra

# Size
size/xs:          "< 2 hours"
size/s:           "2-4 hours"
size/m:           "4-8 hours"
size/l:           "1-2 days"
size/xl:          "2-3 days"

# Status
status/blocked:   "Blocked by dependency"
status/needs-review: "PR submitted"
status/in-qa:     "Awaiting QA verification"
status/needs-dependency: "Dependency not yet resolved"
```

### 9.3 Milestones

```yaml
# Release milestones
milestones:
  - title: v1.0
    description: "Initial production release"
    due_on: 2026-08-16
    
  - title: v1.1
    description: "Feature release"
    due_on: 2026-10-01

# Sprint milestones
  - title: SB-26.S7
    description: "Sprint 7 â€” AI Agent Integration"
    due_on: 2026-04-12
    
  - title: SB-26.S8
    description: "Sprint 8 â€” AI Agent Integration"
    due_on: 2026-04-26
```

### 9.4 GitHub Projects Views

```yaml
# Sprint Board View
view: Sprint Board
layout: board
group_by: Status
columns:
  - Backlog
  - Ready
  - In Progress
  - In Review
  - In QA
  - Done
  - Deployed

# Developer View
view: Developer View
layout: table
group_by: Assignee
sort_by: Priority (ascending)

# Dependency View
view: Dependency View
layout: table
filter: "label:status/blocked"
group_by: "Blocked By (linked issues)"

# Velocity View
view: Velocity View
layout: chart
type: bar
x_axis: Milestone
y_axis: Story Points
```

### 9.5 Reporting

| Report | Tool | Frequency | Audience |
|---|---|---|---|
| Sprint Burndown | GitHub Insights | Daily | Team |
| Velocity Chart | GitHub Insights | Per sprint | Team + PM |
| Cycle Time | GitHub Insights | Weekly | Team |
| Blocked Items | Board filter | Daily | Scrum Master |
| PR Review Time | GitHub Pulse | Weekly | Tech Lead |
| Developer Throughput | Custom dashboard | Per sprint | Engineering Manager |

---

## 10. Task Lifecycle States

### 10.1 State Flow

```
                   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                   â”‚                                      â”‚
                   â–¼                                      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚Backlog â”‚ â†’ â”‚ Ready  â”‚ â†’ â”‚ In Progressâ”‚ â†’ â”‚In Review â”‚  â”‚  â”‚   Done   â”‚ â†’ â”‚  Deployed  â”‚
â”‚        â”‚   â”‚(DoR met)â”‚   â”‚ (Active)   â”‚   â”‚(PR sent)  â”‚  â”‚  â”‚(DoD met) â”‚   â”‚(In prod)   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                               â”‚               â”‚         â”‚       â–²
                               â–¼               â–¼         â”‚       â”‚
                          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚       â”‚
                          â”‚  Blocked   â”‚   â”‚  In QA   â”‚â”€â”€â”˜       â”‚
                          â”‚(Dependency)â”‚   â”‚(QA check)â”‚          â”‚
                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                     (QA failed â†’ back to In Progress)
```

### 10.2 State Definitions

| State | Definition | Responsible | Max Duration | Exit Criteria |
|---|---|---|---|---|
| **Backlog** | Refined but not committed | Product Owner | Indefinite | Sprint planning |
| **Ready** | DoR met, ready for sprint | Scrum Master | 2 weeks | Developer picks up |
| **In Progress** | Active development | Developer | Sprint duration | PR submitted |
| **Blocked** | Waiting on dependency | Developer + SM | 48h before escalation | Dependency resolved |
| **In Review** | PR submitted for review | Reviewer | 24h SLA | At least 1 approval |
| **In QA** | Passed review, in QA testing | QA Engineer | 24h | QA verified |
| **Done** | DoD met, ready for deploy | Developer | 24h | Deployed to production |
| **Deployed** | Live in production | CI/CD | Permanent | Monitoring confirms |

### 10.3 State Transition Rules

| From | To | Condition |
|---|---|---|
| Backlog | Ready | All DoR criteria met |
| Ready | In Progress | Developer self-assigns |
| In Progress | In Review | PR submitted with CI green |
| In Progress | Blocked | Dependency not available â€” add `status/blocked` label |
| Blocked | In Progress | Dependency resolved â€” remove label |
| In Review | In QA | 1+ approval received, PR ready for QA |
| In Review | In Progress | Changes requested â€” address feedback |
| In QA | Done | QA verified, all checks pass |
| In QA | In Progress | QA failed â€” fix issues |
| Done | Deployed | Merge to main, CD deploys |

---

## 11. Definition of Ready Per Task

### 11.1 Ready Checklist

Every task in the sprint backlog must meet:

```markdown
## Definition of Ready for Tasks

### Clarity
- [ ] Task description is clear and unambiguous
- [ ] Technical approach is defined (how will we build this?)
- [ ] Acceptance criteria are specific and testable
- [ ] All team members understand the task

### Dependencies
- [ ] All blocking dependencies are identified
- [ ] No unresolved external blockers
- [ ] Dependent tasks are visible in the board

### Estimation
- [ ] Task is estimated (points and/or hours)
- [ ] Task duration is < 3 days (if more, split)
- [ ] Task has a size label (XS, S, M, L, XL)

### Completeness
- [ ] Design mockups are approved (if UI change)
- [ ] API contract is defined (if API change)
- [ ] Database changes are reviewed (if DB change)
- [ ] Associated tests are identified

### Environment
- [ ] Required services are available
- [ ] Test data is available (or can be created)
- [ ] Feature flag is configured (if needed)
```

### 11.2 Ready Gate Questions

| Question | Who Answers | Gate |
|---|---|---|
| Is the task clear enough to start? | Developer | Yes/No |
| Are all dependencies resolved? | Scrum Master | Yes/No |
| Is the design approved? | Design Lead (if UI) | Yes/No |
| Is the estimate valid? | Team | Â±25% |
| Is test data available? | QA Lead | Yes/No |

---

## 12. Appendices

### Appendix A: Task Breakdown Cheatsheet

```
Legend: Pts = Story Points, Dur = Duration

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           TASK BREAKDOWN â€” QUICK REFERENCE                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                             â”‚
â”‚  USER STORY â†’ FEATURES â†’ TASKS â†’ SUBTASKS                   â”‚
â”‚                                                             â”‚
â”‚  Size limits:                                               â”‚
â”‚    Story:   â‰¤ 13 pts, â‰¤ 3 days         [If >, split]        â”‚
â”‚    Feature: â‰¤ 8 pts,  â‰¤ 2 days         [If >, split]        â”‚
â”‚    Task:    â‰¤ 3 pts,  â‰¤ 8 hours        [If >, split]        â”‚
â”‚    Subtask: Not estimated, < 2 hours   [Optional]           â”‚
â”‚                                                             â”‚
â”‚  Typical breakdown:                                         â”‚
â”‚    Frontend:  API â†’ Data â†’ UI â†’ State â†’ Style â†’ Tests       â”‚
â”‚    Backend:   Model â†’ Schema â†’ Route â†’ Val â†’ Tests â†’ Docs   â”‚
â”‚    Agent:     Prompt â†’ Module â†’ Tests â†’ Integration         â”‚
â”‚    Bug:       Reproduce â†’ Find â†’ Fix â†’ Test â†’ Deploy        â”‚
â”‚    Refactor:  Map â†’ Plan â†’ Execute â†’ Verify â†’ Cleanup       â”‚
â”‚                                                             â”‚
â”‚  Estimation:                                                â”‚
â”‚    XS = 1 pt (< 2h)    S = 2 pt (2-4h)                     â”‚
â”‚    M = 3 pt (4-8h)     L = 5 pt (1-2d)                     â”‚
â”‚    XL = 8 pt (2-3d)    XXL = 13 pt (split!)                â”‚
â”‚                                                             â”‚
â”‚  Dependencies:                                              â”‚
â”‚    Blocked By: #[issue] â€” dependency must complete first     â”‚
â”‚    Blocks: #[issue] â€” other work depends on this task        â”‚
â”‚                                                             â”‚
â”‚  Task states: Backlog â†’ Ready â†’ In Progress â†’ In Review      â”‚
â”‚               â†’ In QA â†’ Done â†’ Deployed                      â”‚
â”‚                                                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Appendix B: Common Task Templates by Type

| Task Type | Template File |
|---|---|
| API endpoint | `.github/ISSUE_TEMPLATE/api-endpoint.md` |
| Frontend page | `.github/ISSUE_TEMPLATE/frontend-page.md` |
| Agent module | `.github/ISSUE_TEMPLATE/agent-module.md` |
| Prompt creation | `.github/ISSUE_TEMPLATE/prompt-creation.md` |
| Bug fix | `.github/ISSUE_TEMPLATE/bug-fix.md` |
| Refactoring | `.github/ISSUE_TEMPLATE/refactoring.md` |

### Appendix C: Task Splitting Strategies

| Strategy | When to Use | Example |
|---|---|---|
| **By layer** | Full-stack features | API â†’ Frontend â†’ Tests |
| **By use case** | Multiple user workflows | Create task â†’ Edit task â†’ Complete task |
| **By data type** | Multiple entity types | Task CRUD â†’ Goal CRUD â†’ Habit CRUD |
| **By operation** | CRUD features | Create â†’ Read â†’ Update â†’ Delete |
| **By complexity** | Varying difficulty | Simple case â†’ Edge cases â†’ Advanced features |
| **By scenario** | Multiple paths | Happy path â†’ Error path â†’ Empty state |

### Appendix D: Estimation Poker Cards

```
â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”
â”‚  0  â”‚  â”‚  1  â”‚  â”‚  2  â”‚  â”‚  3  â”‚  â”‚  5  â”‚  â”‚  8  â”‚
â”‚  ?  â”‚  â”‚ XS  â”‚  â”‚  S  â”‚  â”‚  M  â”‚  â”‚  L  â”‚  â”‚ XL  â”‚
â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜

â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”
â”‚ 13  â”‚  â”‚ 21  â”‚  â”‚ âˆž   â”‚  â”‚ â˜•  â”‚  â”‚ ?   â”‚
â”‚ XXL â”‚  â”‚SPLITâ”‚  â”‚UNKNWâ”‚  â”‚BREAKâ”‚  â”‚UNCLRâ”‚
â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”˜

Card Meanings:
0    = Already done / trivial (no effort)
?    = Don't understand, need clarification
âˆž    = Too large, must split
â˜•   = Need a break / can't estimate right now
21   = Epic, must split into smaller stories
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-01 | Lead Developer | Initial task breakdown document |
| 2.0.0 | 2026-06-11 | Lead Developer | Added 6 task breakdown patterns, estimation techniques, dependency management, RICE prioritization, capacity planning, lifecycle states, DoR per task |
