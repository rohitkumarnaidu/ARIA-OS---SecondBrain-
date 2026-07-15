# Features Breakdown â€” Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-FEA-001 |
| Version | 4.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal â€” Product Reference |
| Total Modules | 15 |
| Total Epics | 15 |
| Total Features | 87 |
| Total Sub-Features | 215 |
| Related Docs | [Acceptance Criteria](./07_AcceptanceCriteria.md), [User Stories](./06_UserStories.md) |

---

## Feature Taxonomy & Inter-Dependencies

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#0A0B0F", "primaryColor": "#6366F1", "primaryTextColor": "#F1F5F9", "secondaryColor": "#13151A", "secondaryTextColor": "#94A3B8", "tertiaryColor": "#00FFA3", "tertiaryTextColor": "#0A0B0F", "lineColor": "#334155", "fontFamily": "DM Sans, sans-serif"}}}%%
flowchart LR
    subgraph CORE[Core Modules - P0]
        T[Tasks - 6 SF]
        C[Courses - 8 SF]
        G[Goals - 5 SF]
        P[Projects - 6 SF]
    end
    subgraph AI[AI Services - P1]
        B[Briefing Agent]
        R[Weekly Review]
        O[Opportunity Radar]
        M[Memory Agent]
    end
    subgraph DATA[Data Modules - P2]
        S[Sleep - 3 SF]
        I[Income - 5 SF]
        H[Habits - 7 SF]
        IDE[Ideas - 6 SF]
    end
    CORE --> AI
    AI --> DATA
    T -.-> B
    C -.-> R
```

## Module 1: Tasks (EPIC-01)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete (50 endpoints)

### Feature 1.1: Task CRUD (F-1.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /tasks |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.1.1 | Create task | Title, description, priority, category, due_date, estimated_minutes supported; saved to Supabase | âœ… |
| SF-1.1.2 | Read tasks | List with priority sort, filter by status/category | âœ… |
| SF-1.1.3 | Update task | All fields modifiable; optimistic UI update | âœ… |
| SF-1.1.4 | Delete task | Confirmation dialog; removes from DB | âœ… |
| SF-1.1.5 | Get task by ID | Single task view with all fields | âœ… |
| SF-1.1.6 | Mark complete | Updates status, sets completed_at timestamp | âœ… |

### Feature 1.2: Priority & Categorization (F-1.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-1.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.2.1 | Priority levels | Urgent, High, Medium, Low with visual badges | âœ… |
| SF-1.2.2 | Category assignment | Study, Project, Habit, Personal, Income | âœ… |
| SF-1.2.3 | Priority sort | Tasks auto-sorted by priority + due_date | âœ… |
| SF-1.2.4 | Filter by status | All, Pending, In Progress, Completed, Missed | âœ… |
| SF-1.2.5 | Filter by category | Category pill filters | âœ… |

### Feature 1.3: Task Dependencies (F-1.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-1.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.3.1 | Set dependency | Task A blocks Task B; B can't start before A done | âŒ |
| SF-1.3.2 | Dependency graph | Visual tree of blocked/blocking tasks | âŒ |
| SF-1.3.3 | Auto-block | Dependency chain auto-resolved on completion | âŒ |
| SF-1.3.4 | Circular dependency detection | Prevent user from creating cycles | âŒ |

### Feature 1.4: Recurring Tasks (F-1.4)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-1.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.4.1 | Set recurrence | Daily, weekly, monthly, custom interval | âŒ |
| SF-1.4.2 | Auto-generation | Next instance created on completion | âŒ |
| SF-1.4.3 | Skip instance | Skip one occurrence without breaking recurrence | âŒ |
| SF-1.4.4 | End condition | After N occurrences or on date | âŒ |

### Feature 1.5: Auto-Reschedule (F-1.5)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-1.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.5.1 | Missed task detection | Cron checks overdue tasks every 15 min | âœ… |
| SF-1.5.2 | Missed count tracking | Increments missed_count on each detection | âœ… |
| SF-1.5.3 | Auto-reschedule | Moves due_date to next available slot | âœ… |
| SF-1.5.4 | Escalation | Push at 3, Email at 5, SMS at 7 misses | âœ… |

### Feature 1.6: Pomodoro Timer (F-1.6)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-1.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.6.1 | Start timer | 25-min focus countdown linked to task | âœ… (in Time module) |
| SF-1.6.2 | Break timer | 5-min break after focus | âœ… |
| SF-1.6.3 | Session log | Logs completed Pomodoro to time_entries | âœ… |
| SF-1.6.4 | Daily Pomodoro count | Shows completed sessions | âœ… |

### Feature 1.7: Task Search & Pagination (F-1.7)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-1.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-1.7.1 | Full-text search | Search by title, description | âŒ |
| SF-1.7.2 | Pagination | 20 tasks per page with cursor/offset | âŒ |
| SF-1.7.3 | Infinite scroll | Load more on scroll | âŒ |

---

## Module 2: Courses (EPIC-02)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 2.1: Course CRUD (F-2.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /courses |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-2.1.1 | Create course | Title, platform, URL, total_videos, deadline, why_enrolled | âœ… |
| SF-2.1.2 | Read courses | List with progress bars, sorted by deadline | âœ… |
| SF-2.1.3 | Update course | All fields, progress %, completed_videos | âœ… |
| SF-2.1.4 | Delete course | Confirmation required | âœ… |

### Feature 2.2: Progress Tracking (F-2.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-2.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-2.2.1 | Video-based progress | completed_videos / total_videos | âœ… |
| SF-2.2.2 | Deadline calculation | Days remaining, required daily pace | âœ… |
| SF-2.2.3 | Status tracking | Not started, In Progress, Completed, Abandoned | âœ… |
| SF-2.2.4 | Behind-schedule detection | Compares required vs actual pace | âœ… |

### Feature 2.3: Study Task Generation (F-2.3)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-2.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-2.3.1 | Auto-create study task | 25-min study task created for behind course | âœ… |
| SF-2.3.2 | Daily target display | "Need X min/day" shown in UI | âœ… |
| SF-2.3.3 | Nudge notification | 6 PM push if course is behind | âœ… |

---

## Module 3: Goals (EPIC-03)

**Priority:** P0 | **Status:** Frontend Partial, Backend Complete

### Feature 3.1: Goal CRUD (F-3.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /goals |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-3.1.1 | Create goal | Title, description, roadmap_type, target_date, hours_per_day, intensity | âœ… |
| SF-3.1.2 | Read goals | List with progress %, sorted by status | âœ… |
| SF-3.1.3 | Update goal | All fields mutable | âœ… |
| SF-3.1.4 | Delete goal | Confirmation required | âœ… |

### Feature 3.2: Roadmap Builder (F-3.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-3.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-3.2.1 | Visual roadmap | React Flow editor with nodes and edges | âš ï¸ Shell only (no API) |
| SF-3.2.2 | Add milestone | Title, description, type, estimated_hours | âš ï¸ |
| SF-3.2.3 | Set dependencies | Drag edge between milestones | âš ï¸ |
| SF-3.2.4 | Auto-layout | Automatic node positioning | âŒ |
| SF-3.2.5 | Timeline projection | Visual timeline bar with milestones | âŒ |

### Feature 3.3: Scenario Planning (F-3.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-3.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-3.3.1 | What-if simulation | "What if I study 1h/day?" shows adjusted timeline | âŒ |
| SF-3.3.2 | Intensity slider | Adjustable low/medium/high intensity | âŒ |
| SF-3.3.3 | Hard-deadline mode | Work backwards from fixed date | âŒ |

### Feature 3.4: Weekly Relevance Check (F-3.4)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-3.1, AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-3.4.1 | Auto-check milestones | Sunday scan: are roadmap items still relevant? | âŒ |
| SF-3.4.2 | Change suggestion | "React 19 released â€” consider updating" | âŒ |
| SF-3.4.3 | Relevance score | 0-100 for each milestone | âŒ |

### Feature 3.5: Goal Analytics (F-3.5)

| Attribute | Value |
|---|---|
| Priority | P2 |
| Dependencies | F-3.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-3.5.1 | Progress velocity | % change per week | âŒ |
| SF-3.5.2 | Completion prediction | Predicted vs target date | âŒ |
| SF-3.5.3 | Goal completion rate | % of goals completed on time | âŒ |

---

## Module 4: Habits (EPIC-04)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 4.1: Habit CRUD (F-4.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /habits |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-4.1.1 | Create habit | Name, frequency, custom_days, time_target_minutes | âœ… |
| SF-4.1.2 | Read habits | List with streak, consistency % | âœ… |
| SF-4.1.3 | Update habit | All fields mutable | âœ… |
| SF-4.1.4 | Delete/archive habit | Soft delete (archive) | âœ… |

### Feature 4.2: Habit Tracking (F-4.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-4.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-4.2.1 | Daily check-in | Mark habit as done for today | âœ… |
| SF-4.2.2 | Streak tracking | Current streak, best streak, consistency % | âœ… |
| SF-4.2.3 | Weekly calendar | Visual calendar showing 30-day completion | âœ… |
| SF-4.2.4 | Goal-linked habits | Habits tied to a parent goal | âœ… |

### Feature 4.3: Habit Notifications (F-4.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-4.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-4.3.1 | Streak-at-risk alert | Push notification at 2 consecutive misses | âœ… |
| SF-4.3.2 | Daily check-in reminder | 8 PM push if habit not logged | âœ… |
| SF-4.3.3 | Consistency report | Weekly summary in review | âœ… |

---

## Module 5: Sleep (EPIC-05)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 5.1: Sleep Logging (F-5.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, DELETE /{id} |
| Frontend Route | /sleep |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-5.1.1 | Log sleep | Bedtime, wake_time, quality_rating | âœ… |
| SF-5.1.2 | Auto-calculate duration | Duration in hours from bedtime â†’ wake | âœ… |
| SF-5.1.3 | View history | Last 30 logs with scores | âœ… |

### Feature 5.2: Sleep Score (F-5.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-5.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-5.2.1 | Score calculation | Combination of duration + quality, max 100 | âœ… |
| SF-5.2.2 | Sleep debt | Rolling 7-day debt = (8h - actual_duration) | âœ… |
| SF-5.2.3 | Score display | Score card with color indicator | âœ… |

### Feature 5.3: Wind-Down Reminder (F-5.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-5.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-5.3.1 | 9:30 PM push | Wind-down notification with tomorrow's first task | âœ… |
| SF-5.3.2 | Bedtime goal | User-configurable target bedtime | âœ… |

### Feature 5.4: Morning Adjustment (F-5.4)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-5.1, Planner Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-5.4.1 | Score < 50 adjustment | Heavy tasks moved to afternoon | âŒ |
| SF-5.4.2 | Score < 30 adjustment | Total tasks reduced by 50% | âŒ |
| SF-5.4.3 | Plan notification | User notified of adjusted plan | âŒ |

---

## Module 6: Income (EPIC-06)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 6.1: Income Source Tracking (F-6.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /income |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-6.1.1 | Add income source | Platform, type, description | âœ… |
| SF-6.1.2 | Log income entry | Amount, date, hours_spent, source | âœ… |
| SF-6.1.3 | Hourly rate calc | Auto-calculated if hours_spent provided | âœ… |
| SF-6.1.4 | Effective rate | amount / hours_spent | âœ… |

### Feature 6.2: Income Analytics (F-6.2)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-6.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-6.2.1 | Monthly total | Income chart by month | âœ… |
| SF-6.2.2 | Source breakdown | Pie chart by source type | âœ… |
| SF-6.2.3 | Hourly rate trend | Rate over time chart | âœ… |
| SF-6.2.4 | Milestone tracking | "Earned $1K total" badges | âœ… |

### Feature 6.3: Skill-to-Income Mapping (F-6.3)

| Attribute | Value |
|---|---|
| Priority | P2 |
| Dependencies | F-6.1, Career Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-6.3.1 | Tag skills to income | Associate skill with each income entry | âŒ |
| SF-6.3.2 | Skill monetization chart | Which skills generate most income | âŒ |
| SF-6.3.3 | Recommend monetization | "Your Python skills could earn â‚¹X on Fiverr" | âŒ |

---

## Module 7: Projects (EPIC-07)

**Priority:** P1 | **Status:** Frontend Complete, Backend Complete

### Feature 7.1: Project CRUD (F-7.1)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /projects |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-7.1.1 | Create project | Title, description, phase, github_url, live_url, next_action | âœ… |
| SF-7.1.2 | Read projects | List with phase filter, sorted by last_updated | âœ… |
| SF-7.1.3 | Update project | All fields, phase changes, blocker tracking | âœ… |
| SF-7.1.4 | Delete project | Confirmation required | âœ… |

### Feature 7.2: Phase Management (F-7.2)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-7.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-7.2.1 | Phase tracking | Planning â†’ Building â†’ Testing â†’ Deployed â†’ Maintained | âœ… |
| SF-7.2.2 | Next action | Single next step displayed prominently | âœ… |
| SF-7.2.3 | Blocker tracking | Mark blocker, set type, link to resource | âœ… |

### Feature 7.3: GitHub Integration (F-7.3)

| Attribute | Value |
|---|---|
| Priority | P2 |
| Dependencies | F-7.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-7.3.1 | Link GitHub repo | URL + auto-fetch metadata | âš ï¸ URL store only |
| SF-7.3.2 | Commit activity | Show recent commits in project view | âŒ |
| SF-7.3.3 | PR count | Open/merged PR count | âŒ |

### Feature 7.4: LinkedIn Post Draft (F-7.4)

| Attribute | Value |
|---|---|
| Priority | P2 |
| Dependencies | F-7.1, AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-7.4.1 | Generate post | AI drafts LinkedIn post from project data | âŒ |
| SF-7.4.2 | Edit + approve | User can edit before posting | âŒ |
| SF-7.4.3 | Post history | Track which projects got posted | âŒ |

---

## Module 8: Ideas (EPIC-08)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 8.1: Idea CRUD (F-8.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /ideas |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-8.1.1 | Capture idea | Title, description, quick capture | âœ… |
| SF-8.1.2 | Update idea | Market research, competitors, status | âœ… |
| SF-8.1.3 | Delete idea | Confirmation | âœ… |

### Feature 8.2: Idea Pipeline (F-8.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-8.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-8.2.1 | Pipeline stages | Raw â†’ Validating â†’ Planned â†’ Building â†’ Launched | âœ… |
| SF-8.2.2 | Stage drag | Move ideas between stages | âœ… |
| SF-8.2.3 | Stage count | Count per stage in header | âœ… |

### Feature 8.3: AI Market Check (F-8.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-8.1, AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-8.3.1 | Market research | AI analyzes competitors for the idea | âŒ (UI has field) |
| SF-8.3.2 | Feasibility score | 0-100 AI-generated feasibility rating | âŒ |
| SF-8.3.3 | Similar ideas | AI finds similar projects/products | âŒ |

---

## Module 9: Resources (EPIC-09)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 9.1: Resource CRUD (F-9.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /resources |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-9.1.1 | Save resource | URL, title, type, tags, notes | âœ… |
| SF-9.1.2 | Update resource | All fields, archive toggle | âœ… |
| SF-9.1.3 | Delete resource | Confirmation | âœ… |

### Feature 9.2: Organization (F-9.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-9.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-9.2.1 | Auto-tagging | Tags extracted from URL/title | âœ… |
| SF-9.2.2 | Type filter | Article, Video, Book, Documentation, Tool, Course | âœ… |
| SF-9.2.3 | Natural language search | "React hooks tutorial" returns relevant resources | âœ… |

### Feature 9.3: AI Summarization (F-9.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-9.1, AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-9.3.1 | Auto-summary | AI generates 2-3 sentence summary of URL | âŒ |
| SF-9.3.2 | Key takeaways | Bullet-point key points | âŒ |
| SF-9.3.3 | Read-later queue | Resources marked for later reading | âŒ |

---

## Module 10: Opportunities (EPIC-10)

**Priority:** P0 | **Status:** Frontend Partial, Backend Complete

### Feature 10.1: Opportunity Display (F-10.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id} |
| Frontend Route | /opportunities |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-10.1.1 | List opportunities | Cards with title, company, match_score, deadline | âš ï¸ Uses mock data |
| SF-10.1.2 | Filter by type | Internship, Hackathon, Open Source, Fellowship, Freelance | âš ï¸ |
| SF-10.1.3 | Sort by match | Sort by match_score descending | âš ï¸ |
| SF-10.1.4 | Save/applied/reject | User action tracking on each opportunity | âš ï¸ |

### Feature 10.2: Auto-Scanning (F-10.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-10.2.1 | Daily scan | 6 AM cron scans 6 categories | âœ… (AI-powered now) |
| SF-10.2.2 | Match scoring | 0-100 based on skills + interests | âœ… |
| SF-10.2.3 | Filter low matches | < 40 match hidden | âœ… |

### Feature 10.3: Deadline Alerts (F-10.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-10.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-10.3.1 | 48h alert | Push notification for closing opportunities | âŒ |
| SF-10.3.2 | Daily countdown | Show upcoming deadlines in briefing | âŒ |
| SF-10.3.3 | Priority sorting | Sort by deadline + match | âŒ |

---

## Module 11: Academics (EPIC-11)

**Priority:** P1 | **Status:** Frontend Complete, Backend Complete (inline)

### Feature 11.1: CGPA Calculator (F-11.1)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | None |
| Frontend Route | /academics |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-11.1.1 | Add subject | Semester, subject name, credits | âœ… |
| SF-11.1.2 | Add marks | Internal, external, total | âœ… |
| SF-11.1.3 | Calculate CGPA | Weighted average across all semesters | âœ… |
| SF-11.1.4 | Semester view | Per-semester GPA breakdown | âœ… |

### Feature 11.2: Exam Countdown (F-11.2)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-11.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-11.2.1 | Add exam | Subject, date, type (midterm/final) | âœ… |
| SF-11.2.2 | Countdown timer | Days remaining with color urgency | âœ… |
| SF-11.2.3 | Exam calendar | Semester view of all exams | âœ… |

### Feature 11.3: Grade Prediction (F-11.3)

| Attribute | Value |
|---|---|
| Priority | P2 |
| Dependencies | F-11.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-11.3.1 | Target CGPA | "I want 8.5 CGPA" â†’ required marks per subject | âŒ |
| SF-11.3.2 | What-if scenario | "If I score X in finals, my CGPA will be Y" | âŒ |

---

## Module 12: YouTube (EPIC-12)

**Priority:** P0 | **Status:** Frontend Complete

### Feature 12.1: YouTube Save (F-12.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| Frontend Route | /youtube |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-12.1.1 | Save video | URL, title, channel, duration | âœ… |
| SF-12.1.2 | Auto-fetch metadata | Title, thumbnail from YouTube API | âœ… |
| SF-12.1.3 | Categorize | Topic, course, project tags | âœ… |

### Feature 12.2: Watch Scheduling (F-12.2)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-12.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-12.2.1 | Schedule for later | Assign date/time to watch | âœ… |
| SF-12.2.2 | Expiry system | Videos expire if not watched by scheduled date | âœ… |
| SF-12.2.3 | Watch queue | Sorted by scheduled date | âœ… |

### Feature 12.3: AI Summary (F-12.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-12.1, AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-12.3.1 | Auto-summary | AI generates summary from video title | âš ï¸ Basic |
| SF-12.3.2 | Topic extraction | Extracts technologies/topics mentioned | âŒ |
| SF-12.3.3 | Related resources | Suggests similar videos from library | âŒ |

---

## Module 13: Chat / ARIA (EPIC-13)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete (AI-wired)

### Feature 13.1: Chat Interface (F-13.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | POST / |
| Frontend Route | /chat |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-13.1.1 | Message input | Text input with send button | âœ… |
| SF-13.1.2 | Message history | Scrollable chat history | âœ… |
| SF-13.1.3 | Role indicators | User vs ARIA message styling | âœ… |
| SF-13.1.4 | Typing indicator | Shows when ARIA is generating | âœ… |

### Feature 13.2: Intent Recognition (F-13.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | AI Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-13.2.1 | Task intent | "Add task" creates a new task | âœ… |
| SF-13.2.2 | Query intent | "Show my tasks" lists tasks | âœ… |
| SF-13.2.3 | Goal intent | "Create goal" initiates goal flow | âœ… |
| SF-13.2.4 | Mixed intent | "Add task and show goals" handles both | âŒ |

### Feature 13.3: Action Execution (F-13.3)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-13.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-13.3.1 | Create from chat | "Add task to study DBMS" creates in DB | âœ… |
| SF-13.3.2 | Update from chat | "Mark task X as done" updates status | âœ… |
| SF-13.3.3 | Delete from chat | "Delete task X" requires confirmation | âŒ |
| SF-13.3.4 | Log from chat | "Log 2h study" creates time entry | âœ… |

### Feature 13.4: Context Awareness (F-13.4)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-13.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-13.4.1 | Day context | ARIA knows time of day, adjusts tone | âœ… |
| SF-13.4.2 | Pending count | ARIA knows how many tasks are pending | âœ… |
| SF-13.4.3 | Recent activity | ARIA knows what user did today | âœ… |

### Feature 13.5: Memory (F-13.5)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-13.1, Memory Agent |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-13.5.1 | Fact extraction | Remembers preferences from chat | âœ… |
| SF-13.5.2 | Fact recall | "Remember I prefer morning study" â†’ uses it | âœ… |
| SF-13.5.3 | Forget command | "Forget that" removes memory | âœ… |
| SF-13.5.4 | Pattern detection | Notices productivity patterns | âš ï¸ Basic |

---

## Module 14: Automation Dashboard (EPIC-14)

**Priority:** P1 | **Status:** Frontend Complete, Backend Complete

### Feature 14.1: Cron Status (F-14.1)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | Scheduler |
| Frontend Route | /automation |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-14.1.1 | Job list | All 15 cron jobs with schedule | âœ… |
| SF-14.1.2 | Status indicator | Last run, next run, green/red status | âœ… |
| SF-14.1.3 | Schedule display | Human-readable schedule times | âœ… |

### Feature 14.2: Manual Trigger (F-14.2)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-14.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-14.2.1 | Trigger briefing | POST /trigger/briefing | âœ… |
| SF-14.2.2 | Trigger radar | POST /trigger/radar | âœ… |
| SF-14.2.3 | Trigger weekly review | POST /trigger/weekly-review | âœ… |
| SF-14.2.4 | Result display | Shows output after trigger | âœ… |

---

## Module 15: Time Tracking (EPIC-15)

**Priority:** P0 | **Status:** Frontend Complete, Backend Complete

### Feature 15.1: Time Entry (F-15.1)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | None |
| API Endpoints | GET /, POST /, PUT /{id}, DELETE /{id}, POST /stop, GET /stats/daily |
| Frontend Route | /time |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-15.1.1 | Start timer | Begin tracking with task/category | âœ… |
| SF-15.1.2 | Stop timer | End tracking, auto-calculate duration | âœ… |
| SF-15.1.3 | Manual entry | Log past session manually | âœ… |
| SF-15.1.4 | Category assignment | Work, Study, Project, Break | âœ… |

### Feature 15.2: Daily Stats (F-15.2)

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | F-15.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-15.2.1 | Daily breakdown | Minutes per category | âœ… |
| SF-15.2.2 | Total focus time | Sum of all tracked time | âœ… |
| SF-15.2.3 | Category pie chart | Visual breakdown | âœ… |

### Feature 15.3: Pomodoro Mode (F-15.3)

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | F-15.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-15.3.1 | 25-min focus | Countdown timer | âœ… |
| SF-15.3.2 | 5-min break | Auto-transition | âœ… |
| SF-15.3.3 | Session counter | Completed sessions today | âœ… |

### Feature 15.4: Deep Work Detection (F-15.4)

| Attribute | Value |
|---|---|
| Priority | P2 |
| Dependencies | F-15.1 |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-15.4.1 | Long focus flag | Sessions > 90 min flagged as deep work | âœ… |
| SF-15.4.2 | Deep work count | Count per week | âœ… |
| SF-15.4.3 | Peak hours | Detect user's most productive hours | âŒ |

---

## Cross-Cutting Features

### CC-1: Daily Briefing

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | AI Agent, All Modules |
| Trigger | 7 AM daily (cron) |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-CC-1.1 | Top-3 tasks | Priority + deadline sorted | âœ… |
| SF-CC-1.2 | ARIA's pick | Single most important task with reason | âœ… |
| SF-CC-1.3 | Sleep-adjusted | Tone/volume adjusts based on sleep score | âœ… |
| SF-CC-1.4 | Course target | Daily study minutes needed | âœ… |
| SF-CC-1.5 | New opportunities | Overnight matches | âœ… |
| SF-CC-1.6 | Push delivery | Delivered at 7:00 AM Â± 2 min | âœ… |

### CC-2: Weekly Review

| Attribute | Value |
|---|---|
| Priority | P0 |
| Dependencies | AI Agent, All Modules |
| Trigger | Sunday 8 PM (cron) |

**Sub-Features:**

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-CC-2.1 | Pattern detection | One behavioral pattern user missed | âœ… |
| SF-CC-2.2 | Week-over-week | 6+ metric comparisons | âœ… |
| SF-CC-2.3 | Recommendations | 3 actionable suggestions | âœ… |
| SF-CC-2.4 | Email delivery | Resend API delivery | âœ… |
| SF-CC-2.5 | In-app save | Stored in weekly_reviews table | âœ… |

### CC-3: Data Export

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | All Modules |

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-CC-3.1 | JSON export | All user data as JSON | âŒ |
| SF-CC-3.2 | CSV export | Per-module CSV download | âŒ |
| SF-CC-3.3 | Scheduled backup | Monthly auto-export | âŒ |

### CC-4: PWA

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | None |

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-CC-4.1 | Manifest | Installable via browser prompt | âŒ |
| SF-CC-4.2 | Service worker | Offline CRUD caching | âŒ |
| SF-CC-4.3 | Push notifications | Browser push for reminders | âŒ |

### CC-5: Onboarding

| Attribute | Value |
|---|---|
| Priority | P1 |
| Dependencies | Frontend |

| ID | Sub-Feature | Acceptance Criteria | Status |
|---|---|---|---|
| SF-CC-5.1 | Step 1: Goals | "What do you want to achieve?" | âŒ |
| SF-CC-5.2 | Step 2: Skills | Current skills + target | âŒ |
| SF-CC-5.3 | Step 3: Courses | Courses you're taking | âŒ |
| SF-CC-5.4 | Step 4: Habits | Habits to track | âŒ |
| SF-CC-5.5 | Step 5: Schedule | Available hours, bedtime | âŒ |
| SF-CC-5.6 | First briefing | Generate after onboarding | âŒ |

---

## Feature Dependency Graph

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Auth/User   â”‚
                    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
           â”‚               â”‚               â”‚
     â”Œâ”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
     â”‚   Tasks    â”‚   â”‚  Time   â”‚   â”‚   Chat     â”‚
     â”‚ (P0, F-1) â”‚   â”‚(P0,F-15)â”‚   â”‚(P0, F-13)  â”‚
     â””â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”˜   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
        â”‚  â”‚  â”‚           â”‚               â”‚
        â”‚  â”‚  â”‚      â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”          â”‚
        â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”‚ Courses â”‚â—„â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
        â”‚  â”‚         â”‚ (P0,F-2)â”‚
        â”‚  â”‚         â””â”€â”€â”¬â”€â”€â”¬â”€â”€â”€â”˜
        â”‚  â”‚            â”‚  â”‚
   â”Œâ”€â”€â”€â”€â–¼â”€â”€â–¼â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â–¼â”€â”€â–¼â”€â”€â”€â”€â”
   â”‚   Goals    â”‚  â”‚  YouTube   â”‚
   â”‚ (P0, F-3) â”‚  â”‚ (P0, F-12) â”‚
   â””â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
      â”‚  â”‚  â”‚             â”‚
      â”‚  â”‚  â”‚        â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”
      â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”‚Resourcesâ”‚
      â”‚  â”‚           â”‚(P0, F-9)â”‚
      â”‚  â”‚           â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
 â”Œâ”€â”€â”€â”€â–¼â”€â”€â–¼â”€â”€â”€â”€â”           â”‚
 â”‚   Habits   â”‚      â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”
 â”‚ (P0, F-4)  â”‚      â”‚  Ideas  â”‚
 â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜      â”‚(P0, F-8)â”‚
        â”‚            â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”            â”‚
   â”‚  Sleep  â”‚       â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”
   â”‚ (P0,F-5)â”‚       â”‚Opportun.â”‚
   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜       â”‚(P0,F-10)â”‚
        â”‚            â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”
   â”‚  Income â”‚
   â”‚ (P0,F-6)â”‚
   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
        â”‚
   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”
   â”‚Projects â”‚
   â”‚ (P1,F-7)â”‚
   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
        â”‚
   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
   â”‚Academics â”‚
   â”‚ (P1,F-11)â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-04-01 | Product Team | Initial features breakdown |
| 2.0.0 | 2026-06-01 | Product Team | Updated for monorepo structure |
| 3.0.0 | 2026-06-11 | Product Team | Added status tracking, dependency graph, enterprise sub-features |
