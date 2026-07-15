# Use Cases â€” Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-UC-001 |
| Version | 1.0.0 |
| Status | Draft |
| Date | 2026-06-11 |
| Author | Product Team |
| Classification | Internal |

---

## 1. Introduction

This document catalogs 36 real-world use cases across all 12 modules of Second Brain OS. Each use case specifies the trigger, preconditions, step-by-step flow, expected outcome, frequency, priority, edge cases, and error recovery. Cross-module use cases show how multiple modules collaborate.

**Use Case ID Format:** `UC-{MODULE}-{NN}` where MODULE = DASH (Dashboard), TASK (Tasks), CRS (Courses), HAB (Habits), SLP (Sleep), INC (Income), PRJ (Projects), IDEA (Ideas), RES (Resources), OPP (Opportunities), TIME (Time), CHAT (Chat), AUTO (Automation)

---

### Use Case Execution Flow

```mermaid
%%
init: {
  'theme': 'base',
  'themeVariables': {
    'background': '#0A0B0F',
    'primaryColor': '#13151A',
    'primaryBorderColor': '#6366F1',
    'primaryTextColor': '#F1F5F9',
    'lineColor': '#818CF8',
    'secondaryColor': '#1A1D24',
    'tertiaryColor': '#00FFA3',
    'fontFamily': 'DM Sans',
    'fontSize': '14px'
  }
}
%%
flowchart TD
  Start([User Action Trigger]) --> Auth{Authenticated?}

  Auth -->|No| Login[Redirect to Login]
  Login --> Auth

  Auth -->|Yes| ModuleRouter{Module Selection}

  ModuleRouter -->|Dashboard| DASH[Fetch Daily Briefing]
  ModuleRouter -->|Tasks| TASK[Load Task List]
  ModuleRouter -->|Courses| CRS[Load Course Progress]
  ModuleRouter -->|Habits| HAB[Load Habit Streaks]
  ModuleRouter -->|Sleep| SLP[Load Sleep Data]
  ModuleRouter -->|Income| INC[Load Income Entries]
  ModuleRouter -->|Projects| PRJ[Load Project Phases]
  ModuleRouter -->|Ideas| IDEA[Load Idea Pipeline]
  ModuleRouter -->|Resources| RES[Load Resources]
  ModuleRouter -->|Opportunities| OPP[Load Opportunity Radar]
  ModuleRouter -->|Time| TIME[Load Time Entries]
  ModuleRouter -->|Chat| CHAT[ARIA Assistant]
  ModuleRouter -->|Automation| AUTO[Trigger Automation]

  DASH --> BriefingExists{Briefing<br/>Generated?}
  BriefingExists -->|Yes| RenderBriefing[Show Daily Briefing<br/>with Score + Insights]
  BriefingExists -->|No| TriggerGen[Trigger On-Demand<br/>Briefing Generation]
  TriggerGen --> GenSuccess{AI Available?}

  GenSuccess -->|Yes| AgentCall[Call BriefingAgent<br/>via LLM Client]
  GenSuccess -->|No| AlgoFallback[Algorithmic Fallback<br/>Top Tasks by Priority]

  AgentCall --> ValidJSON{Valid JSON<br/>Response?}
  ValidJSON -->|Yes| StoreBriefing[Save to daily_briefings]
  ValidJSON -->|No| AlgoFallback

  AlgoFallback --> StoreBriefing
  StoreBriefing --> RenderBriefing

  TASK --> TaskAction{Create / Read /<br/>Update / Delete?}
  TaskAction -->|Read| ListTasks[Query tasks table<br/>filter by user_id]
  TaskAction -->|Create| CreateTask[Validate schema â†’<br/>Insert to tasks table]
  TaskAction -->|Update| UpdateTask[Update task fields<br/>+ status change]
  TaskAction -->|Delete| DeleteTask[Soft/Hard delete<br/>cascade dependents]

  CHAT --> AriaAvailable{ARIA Agent<br/>Available?}
  AriaAvailable -->|Yes| LLMResponse[Process via ARIA<br/>Orchestrator â†’ Sub-Agents]
  AriaAvailable -->|No| RuleResponse[Rule-Based Fallback<br/>Keyword Matching]

  RenderBriefing --> End([Render View])
  ListTasks --> End
  CreateTask --> End
  UpdateTask --> End
  DeleteTask --> End
  LLMResponse --> End
  RuleResponse --> End

  style Start fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style End fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style Login fill:#13151A,stroke:#EF4444,color:#F1F5F9
  style AlgoFallback fill:#13151A,stroke:#F59E0B,color:#F1F5F9
  style AgentCall fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style LLMResponse fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style RuleResponse fill:#13151A,stroke:#F59E0B,color:#F1F5F9
```

---

## 2. Dashboard & Briefing Module (DASH)

### UC-DASH-01: View Daily Morning Briefing

| Field | Value |
|---|---|
| **Title** | View Daily Morning Briefing |
| **Description** | User opens dashboard at any time to see their AI-generated daily briefing |
| **Trigger** | User navigates to /dashboard after 6:00 AM |
| **Preconditions** | User is authenticated, briefing was generated at 7:00 AM or triggered on-demand |
| **Frequency** | Daily, 1-3 times per user |
| **Priority** | Critical |

**Steps:**
1. User opens web app â†’ redirected to /dashboard
2. Frontend fetches today's briefing from GET /api/briefing/today
3. Query supabase `daily_briefings` for user_id + today's date
4. If found: render briefing card with top 3 tasks, score gauge, insights, quote
5. If not found: trigger on-demand briefing generation (see UC-AUTO-01)
6. Briefing is displayed with animated entry (framer-motion stagger)
7. User can check off tasks, dismiss insights, or click through to modules

**Outcome:** User sees prioritized day plan in under 3 seconds

**Edge Cases:**
- Briefing not yet generated (before 7 AM): Show "Good morning! Your briefing is being prepared..."
- User opens app at 4 AM: Show yesterday's briefing with note "Yesterday's summary"
- No tasks exist: Show "You have no tasks today. Capture something?"
- Sleep score missing: Omit sleep insight section, don't show empty state
- Opportunity radar returned nothing: Omit opportunity section
- LLM generated bad data: Validate JSON schema, fallback to algorithmic data

**Error Recovery:**
- Supabase query fails â†’ Show cached briefing from last successful fetch
- AI generation fails â†’ Fallback to algorithmic briefing (top 3 tasks by priority + due date)
- All data sources return empty â†’ Show motivational fallback with quick capture prompt

---

### UC-DASH-02: View Productivity Score

| Field | Value |
|---|---|
| **Title** | View Real-Time Productivity Score |
| **Description** | User sees their current productivity score updated in real-time |
| **Trigger** | Any dashboard view, or user clicks the score gauge |
| **Preconditions** | User has at least 3 days of activity data |
| **Frequency** | 3-10x daily |
| **Priority** | High |

**Steps:**
1. Frontend calls GET /api/analytics/productivity-score
2. Backend calculates score from weighted formula:
   - Task completion rate (30%) â€” completed / created (7-day rolling)
   - Habit consistency (20%) â€” habits logged / habits defined
   - Sleep score (15%) â€” average sleep over last 7 days
   - Focus time (20%) â€” total deep work hours / target
   - Course progress (15%) â€” active courses maintaining pace
3. Score is returned as 0-100 integer with breakdown components
4. Frontend renders animated gauge with color coding:
   - 0-39: Red (danger)
   - 40-59: Amber (warning)
   - 60-79: Green (good)
   - 80-100: Neon green with glow (excellent)

**Outcome:** Instant feedback on current productivity trend

---

## 3. Task Manager Module (TASK)

### UC-TASK-01: Create Task via Natural Language

| Field | Value |
|---|---|
| **Title** | Create Task via Natural Language |
| **Description** | User types a task description in plain English and AI parses it into structured fields |
| **Trigger** | User uses Quick Capture (Cmd+K) or clicks "+" on tasks page |
| **Preconditions** | User is authenticated |
| **Frequency** | 3-7x daily |
| **Priority** | Critical |

**Steps:**
1. User activates Quick Capture from any screen via keyboard shortcut or FAB
2. Text input appears with placeholder: "What do you need to do?"
3. User types e.g., "finish dbms assignment by tomorrow high priority"
4. After 500ms debounce, frontend sends partial text to AI parsing endpoint
5. AI returns parsed fields: title, priority, due_date, category, linked_to
6. Frontend shows live preview of parsed fields below input
7. User can edit any field before saving
8. User presses Enter to save
9. POST /api/tasks/ with parsed data
10. Supabase inserts task row, frontend updates store, toast confirms

**Outcome:** Task created in < 10 seconds without manual field entry

**Input â†’ Output Examples:**

| Input | Parsed Title | Priority | Due Date | Category | Confidence |
|---|---|---|---|---|---|
| "buy groceries tomorrow" | Buy groceries | Low | Tomorrow | Personal | 0.95 |
| "leetcode daily challenge" | LeetCode Daily Challenge | Medium | Today 11:59 PM | Coding | 0.92 |
| "urgent: prepare for google interview friday" | Prepare for Google interview | Urgent | Friday 9 AM | Career | 0.94 |
| "read clean code chapters 4-6" | Read Clean Code chapters 4-6 | Medium | â€” | Learning | 0.87 |
| "fix login bug in project" | Fix login bug in project | High | â€” | Projects | 0.88 |

**Edge Cases:**
- Very short input (< 3 words): "todo" â†’ Prompt user for more detail
- No time reference: Assume ASAP, set due date to today
- Multi-sentence input: Only process first actionable sentence, prompt about rest
- Existing task with same title + active status: Show duplicate warning, offer to merge
- Special characters or emoji: Strip emoji, keep alphanumeric

**Error Recovery:**
- AI parsing fails: Show manual field form as fallback
- Save fails (network): Queue in IndexedDB, save when online
- Duplicate detected: Show "Similar task exists" with merge option

---

### UC-TASK-02: Complete a Task

| Field | Value |
|---|---|
| **Title** | Complete a Task |
| **Description** | User marks a task as completed |
| **Trigger** | User clicks checkbox or uses mark-complete gesture |
| **Preconditions** | Task exists and is not already completed |
| **Frequency** | 2-5x daily |
| **Priority** | Critical |

**Steps:**
1. User checks task checkbox in any view (dashboard, tasks page, briefing)
2. Optimistic UI update: task crosses out with animation
3. POST /api/tasks/{id}/complete
4. Backend sets `completed_at = NOW()`, `status = "completed"`
5. If task has dependent tasks â†’ unblock them, notify user
6. If task was in today's top 3 â†’ check if all 3 done â†’ celebratory animation
7. Update productivity score (recalculate)
8. If task was linked to course â†’ update course progress
9. If task was part of project â†’ update project milestone tracking

**Outcome:** Task marked complete, dependent tasks unblocked, score updated

---

### UC-TASK-03: Auto-Reschedule Overdue Tasks

| Field | Value |
|---|---|
| **Title** | Auto-Reschedule Overdue Tasks |
| **Description** | System automatically reschedules overdue tasks every 15-minute cycle |
| **Trigger** | Cron job runs every 15 minutes |
| **Preconditions** | Task exists with `due_date < NOW()` and `status = "active"` |
| **Frequency** | Every 15 minutes, affects 0-20 tasks per cycle |
| **Priority** | Critical |

**Steps:**
1. Cron job queries all tasks where `due_date < NOW()` AND `status = "active"`
2. Group by user_id
3. For each user with overdue tasks:
   a. Check total count of overdue tasks
   b. If > 5 overdue â†’ ARIA marks this as "task overload" pattern
   c. Reschedule each task: set new due_date = NOW() + (original duration estimate)
   d. Priority unchanged (unless user has low sleep â†’ auto-demote non-critical)
   e. Log reschedule action in task history
4. If a task has been overdue and auto-rescheduled > 3 times â†’ escalate to user
5. Push notification: "You have N overdue tasks. Need help reprioritizing?"

**Outcome:** No task silently expires. All tasks remain actionable.

**Edge Cases:**
- Task overdue > 7 days and rescheduled > 5 times: Flag as "stale", prompt user to drop or break down
- User on vacation/break: Detect via calendar integration or manual vacation mode â†’ pause auto-reschedule
- Dependency chain with overdue tasks: Reschedule dependents proportionally

---

### UC-TASK-04: AI Task Breakdown

| Field | Value |
|---|---|
| **Title** | AI Task Breakdown |
| **Description** | User asks ARIA to break a complex task into subtasks |
| **Trigger** | User selects "Break Down" on any task, or asks ARIA via chat |
| **Preconditions** | Task exists and has no subtasks yet |
| **Frequency** | 1-3x weekly |
| **Priority** | Medium |

**Steps:**
1. User clicks "Break Down" on task card
2. Frontend sends task to AI for decomposition
3. AI returns 3-7 subtasks with estimated durations and logical order
4. Frontend shows preview: "ARIA suggests breaking this into N subtasks"
5. User can edit, add, remove subtasks before confirming
6. On confirm: POST subtasks as child tasks with parent_id linking
7. Original task becomes a "project" container with progress bar

**Example Breakdown:**

```
Input: "Build portfolio website"
Output:
  â–¡ Research portfolio examples (30 min)
  â–¡ Choose tech stack (15 min)
  â–¡ Set up project scaffolding (20 min)
  â–¡ Build hero section (1 hour)
  â–¡ Build projects section (2 hours)
  â–¡ Build about/contact section (1 hour)
  â–¡ Deploy to Vercel (15 min)
  â–¡ Custom domain setup (15 min)
  â–¡ Write case studies for 3 projects (2 hours)
```

---

## 4. Course Tracker Module (CRS)

### UC-CRS-01: Register a New Course

| Field | Value |
|---|---|
| **Title** | Register a New Course |
| **Description** | User adds a course they've enrolled in with tracking parameters |
| **Trigger** | User navigates to /courses and clicks "Add Course" |
| **Preconditions** | User is authenticated |
| **Frequency** | 1-3x monthly |
| **Priority** | Critical |

**Steps:**
1. User opens /courses â†’ sees list of active courses + "Add Course" button
2. Clicks Add â†’ modal with form fields
3. Fills: Course name, Platform (Udemy/Coursera/NPTEL/College/YouTube/Other)
4. Optional: URL, Total hours, Hours/week, Deadline, "Why I'm taking this"
5. If total hours + hours/week provided â†’ auto-calculate suggested deadline
6. Saves â†’ POST /api/courses/
7. ==>[Background] Generate study task schedule for course duration
8. ==>[Background] Check if URL already registered â†’ duplicate alert
9. Course appears in active list with progress bar at 0%

**Outcome:** Course registered with progress tracking and auto-generated study schedule

**Edge Cases:**
- No deadline set: Course marked as "self-paced," no deadline warnings
- Duplicate course (same URL + same user): Warning shown, option to update existing
- Platform not in dropdown: "Other" option with custom text field
- Total hours unknown: Default to 40 hours, user can update later

---

### UC-CRS-02: Log Study Progress

| Field | Value |
|---|---|
| **Title** | Log Study Hours for a Course |
| **Description** | User logs time spent studying a course |
| **Trigger** | Timer completion in time tracker, or manual entry |
| **Preconditions** | Course exists and is active |
| **Frequency** | 3-7x weekly |
| **Priority** | High |

**Steps:**
1. User studies a course while time tracker is running with course tag
2. On timer stop â†’ study hours auto-logged to course progress
3. OR: User manually enters hours on course detail page
4. Backend updates `courses.hours_completed`, recalculates `completion_pct`
5. Check if course completion_pct >= 100% â†’ prompt to mark as complete
6. Recalculate deadline status: on track / at risk / behind

---

### UC-CRS-03: Receive Deadline Warning

| Field | Value |
|---|---|
| **Title** | Receive Course Deadline Warning |
| **Description** | System warns user when course is at risk of missing its deadline |
| **Trigger** | Daily cron job (6:00 AM) |
| **Preconditions** | Course has deadline set and progress < 80% of expected |
| **Frequency** | Per-course, up to 7 days before deadline |
| **Priority** | High |

**Steps:**
1. Daily cron queries courses where deadline < 14 days away
2. Calculate: `hours_remaining / days_remaining` vs `avg_hours_per_day`
3. If pace_needed > pace_actual * 1.5 â†’ "at risk" status
4. Create warning if days_remaining < 3:
   - Push notification: "URGENT: [Course] deadline in N days"
   - Create high-priority catch-up study task
   - ARIA message on next dashboard open
5. If days_remaining 3-14:
   - Dashboard warning badge on course
   - Create medium-priority catch-up task
   - Weekly review includes status

**Outcome:** User is warned with enough time to adjust pace

---

## 5. Habits Module (HAB)

### UC-HAB-01: Log Daily Habits

| Field | Value |
|---|---|
| **Title** | Log Daily Habits |
| **Description** | User marks habits as completed/not completed for the day |
| **Trigger** | Push notification at 8:00 PM, or user opens /habits |
| **Preconditions** | User has at least 1 active habit defined |
| **Frequency** | Daily |
| **Priority** | High |

**Steps:**
1. User opens /habits or receives notification
2. List of today's habits displayed with toggle switches
3. Each habit shows: name, current streak, goal description, completion status
4. User toggles each habit: Done / Not Done / Skip for cause
5. POST /api/habit_logs/ with batch of statuses
6. Backend updates streaks:
   - If all completed â†’ increment streak_current
   - If streak_current > streak_best â†’ update best
   - If missed 3+ consecutive days â†’ reset streak_current to 0
7. Show today's summary: "3/5 habits done. You're on a 7-day streak!"
8. If streak milestone reached (7, 30, 60, 90) â†’ celebration animation

**Edge Cases:**
- Midnight logging (12:05 AM): Log to previous day if habit uses "previous day" setting
- Multiple logs same day: Update existing record, don't duplicate
- Skip for cause: Count as neither log nor miss for streak purposes
- User on vacation: Pause streak tracking

---

### UC-HAB-02: Define New Habit

| Field | Value |
|---|---|
| **Title** | Define New Habit |
| **Description** | User creates a new habit to track |
| **Trigger** | User clicks "Add Habit" on /habits page |
| **Preconditions** | None |
| **Frequency** | 1-2x monthly |
| **Priority** | Medium |

**Steps:**
1. User clicks "Add Habit"
2. Form: Name, Goal description, Frequency (daily/weekly), Reminder time
3. Optional: Target count (e.g., "Drink 8 glasses of water")
4. User saves â†’ POST /api/habits/
5. New habit appears in daily habit list
6. ==>[Background] ARIA suggests optimal reminder time based on user's schedule

---

## 6. Sleep Module (SLP)

### UC-SLP-01: Log Sleep Data

| Field | Value |
|---|---|
| **Title** | Log Sleep Data |
| **Description** | User logs previous night's sleep |
| **Trigger** | Morning notification at 7:30 AM, or manual entry |
| **Preconditions** | None |
| **Frequency** | Daily |
| **Priority** | Medium |

**Steps:**
1. User receives notification: "How did you sleep?"
2. Quick log interface: Sleep time, Wake time, Quality rating (1-5)
3. OR: User logs manually from /sleep page
4. POST /api/sleep/
5. Backend calculates: duration, sleep score, sleep debt delta
6. Update sleep debt running total
7. If sleep < 6 hours â†’ briefing adjusts task load
8. If sleep < 5 hours for 3+ consecutive nights â†’ ARIA sends sleep hygiene suggestions

---

### UC-SLP-02: Receive Wind-Down Reminder

| Field | Value |
|---|---|
| **Title** | Receive Wind-Down Reminder |
| **Description** | ARIA sends a personalized wind-down message at 9:30 PM |
| **Trigger** | Cron job at 9:30 PM user timezone |
| **Preconditions** | User has sleep tracking enabled |
| **Frequency** | Daily |
| **Priority** | Medium |

**Steps:**
1. At 9:30 PM, system triggers sleep agent
2. Collects context: today's task completion, sleep debt, tomorrow's schedule
3. Calls PromptLoader.get_agent("sleep_agent")
4. LLM generates personalized wind-down message
5. Push notification: "Time to wind down, Arjun. You have a 7 AM class tomorrow."
6. ==>[Background] If user has a habit scheduled before bed â†’ remind of that habit

---

## 7. Income Module (INC)

### UC-INC-01: Log Income Entry

| Field | Value |
|---|---|
| **Title** | Log Income Entry |
| **Description** | User logs an income transaction |
| **Trigger** | User receives payment and opens /income |
| **Preconditions** | None |
| **Frequency** | 2-8x monthly |
| **Priority** | High |

**Steps:**
1. User opens /income â†’ sees monthly summary, timeline, hourly rate trends
2. Clicks "Add Income Entry"
3. Form: Amount (Rs.), Source (Freelance/Internship/Scholarship/Other)
4. Optional: Description, Hours worked, Date (defaults to today), Linked project
5. If hours worked > 0 â†’ auto-calculate hourly rate
6. Saves â†’ POST /api/income/
7. Dashboard income summary updates
8. ==>[Background] Update monthly total, recalculate average hourly rate

---

### UC-INC-02: View Income Analytics

| Field | Value |
|---|---|
| **Title** | View Income Analytics |
| **Description** | User views income trends, hourly rate history, and projections |
| **Trigger** | User opens /income |
| **Preconditions** | At least 3 income entries exist |
| **Frequency** | 2-4x monthly |
| **Priority** | Medium |

**Steps:**
1. Load income data for last 12 months
2. Render: Monthly bar chart, hourly rate line chart, source breakdown pie chart
3. Show metrics: month total, average, hourly rate trend
4. Show year-to-date total and projection to year end
5. ARIA insight: "Your freelance rate has increased 40% this year"

---

## 8. Projects Module (PRJ)

### UC-PRJ-01: Create a Project

| Field | Value |
|---|---|
| **Title** | Create a Project |
| **Description** | User creates a project from scratch or from an idea |
| **Trigger** | User clicks "New Project" or promotes an idea to project status |
| **Preconditions** | None |
| **Frequency** | 1-3x monthly |
| **Priority** | High |

**Steps:**
1. User opens /projects â†’ sees project list with status indicators
2. Clicks "New Project" â†’ form: Name, Description, Tech Stack, Timeline
3. Optional: GitHub URL, Deployment URL, Milestones
4. Can import from idea vault: select idea â†’ auto-fills project details
5. Saves â†’ POST /api/projects/
6. ==>[Background] ARIA suggests initial task list based on tech stack + project type
7. Project appears in list with Milestone 1 highlighted

---

### UC-PRJ-02: Update Project Milestone

| Field | Value |
|---|---|
| **Title** | Update Project Milestone |
| **Description** | User marks a project milestone as completed |
| **Trigger** | User clicks milestone checkbox or updates progress |
| **Preconditions** | Project exists, milestone is defined |
| **Frequency** | 1-4x monthly |
| **Priority** | Medium |

**Steps:**
1. User opens project detail page
2. Views milestones with completion status
3. Marks milestone as complete
4. PUT /api/projects/{id} with updated milestone
5. ==>[Background] ARIA may trigger: if "MVP Complete" milestone â†’ suggest deployment + sharing
6. If all milestones complete â†’ prompt: "Mark project as shipped?"

---

## 9. Ideas Module (IDEA)

### UC-IDEA-01: Capture an Idea

| Field | Value |
|---|---|
| **Title** | Capture an Idea |
| **Description** | User captures an idea quickly with minimal friction |
| **Trigger** | User uses Quick Capture or opens /ideas |
| **Preconditions** | None |
| **Frequency** | 2-5x weekly |
| **Priority** | High |

**Steps:**
1. User captures: "An app that helps students find study groups near them"
2. POST /api/ideas/ with raw text
3. ==>[Background] ARIA checks if idea already exists online
4. ==>[Background] AI generates: category tags, feasibility score, market notes
5. Idea appears in vault with status "Raw"

---

### UC-IDEA-02: Promote Idea to Project

| Field | Value |
|---|---|
| **Title** | Promote Idea to Project |
| **Description** | User moves a validated idea into active project development |
| **Trigger** | User clicks "Build This" on idea card |
| **Preconditions** | Idea exists in status "Validating" or "Building" |
| **Frequency** | 1-2x monthly |
| **Priority** | Medium |

**Steps:**
1. User selects idea from vault
2. Clicks "Build This"
3. System creates project from idea template
4. Original idea status changes to "Building"
5. Project page opens with idea context pre-filled
6. ARIA generates initial milestones and task breakdown

---

## 10. Resources Module (RES)

### UC-RES-01: Save a Resource

| Field | Value |
|---|---|
| **Title** | Save a Resource |
| **Description** | User saves an article, book, repo, tool, or other resource |
| **Trigger** | User clicks browser extension or uses quick capture |
| **Preconditions** | None |
| **Frequency** | 3-10x weekly |
| **Priority** | Medium |

**Steps:**
1. User captures URL or pastes content
2. System fetches metadata: title, description, OG image, site name
3. AI auto-tags: [react, tutorial, frontend, beginner]
4. User can add notes, change tags, set priority
5. POST /api/resources/
6. ==>[Background] Check if URL already exists â†’ show existing or update

---

### UC-RES-02: Get Reading Queue

| Field | Value |
|---|---|
| **Title** | Get Personalized Reading Queue |
| **Description** | ARIA prioritizes saved resources based on active goals |
| **Trigger** | User opens /resources and clicks "Reading Queue" |
| **Preconditions** | At least 5 resources exist |
| **Frequency** | 1-2x weekly |
| **Priority** | Low |

**Steps:**
1. System analyzes active goals, courses, and projects
2. Matches resource tags to active contexts
3. Reorders resources: highest relevance first
4. Shows: "Your reading queue based on [project name]"
5. User can work through queue, marking as "Read" or "Archived"

---

## 11. Opportunities Module (OPP)

### UC-OPP-01: Discover Opportunities

| Field | Value |
|---|---|
| **Title** | Discover New Opportunities |
| **Description** | System finds and matches opportunities to the user |
| **Trigger** | Daily cron at 6:00 AM |
| **Preconditions** | User has profile with skills and interests |
| **Frequency** | Daily |
| **Priority** | Critical |

**Steps:**
1. Cron triggers opportunity radar scan
2. Query sources: Internshala, LinkedIn, Devfolio, Devpost, GitHub, ScholarshipsIndia
3. Collect and deduplicate opportunities
4. Run AI matching: score each 0-100 based on skill overlap, location, deadline urgency
5. Filter: score > 70 â†’ save, score < 70 â†’ archive
6. If match found with deadline < 5 days â†’ immediate push notification
7. Otherwise â†’ include in morning briefing
8. Log scan completion with match count

---

### UC-OPP-02: Apply to Opportunity

| Field | Value |
|---|---|
| **Title** | Apply to Opportunity |
| **Description** | User applies to an opportunity from the list |
| **Trigger** | User clicks "Apply" on opportunity card |
| **Preconditions** | Opportunity exists, user wants to apply |
| **Frequency** | 1-4x monthly |
| **Priority** | High |

**Steps:**
1. User views opportunity details
2. Clicks "Track Application"
3. Modal: Application date, Notes, Status (Applied/Interviewing/Offer/Rejected)
4. Optional: Link to resume or portfolio
5. Saves â†’ auto-creates follow-up task in 7 days
6. Add opportunity to income tracking if paid position
7. If multiple applications â†’ weekly review shows application funnel

---

## 12. Time Tracking Module (TIME)

### UC-TIME-01: Start Focus Session

| Field | Value |
|---|---|
| **Title** | Start a Focus Session |
| **Description** | User starts a time tracking session for a task or project |
| **Trigger** | User clicks "Start Focus" on task or from timer widget |
| **Preconditions** | A task or project is selected |
| **Frequency** | 2-5x daily |
| **Priority** | Medium |

**Steps:**
1. User selects task and clicks "Start Focus"
2. Timer begins with Pomodoro option (25/5 or custom intervals)
3. Ambient focus mode: minimal UI, current task visible
4. Distraction blocker: optional, blocks specified sites
5. On timer complete: log time entry, ask for focus rating
6. POST /api/time/ with session data
7. Update task progress, daily focus total

---

### UC-TIME-02: View Time Analytics

| Field | Value |
|---|---|
| **Title** | View Time Analytics |
| **Description** | User reviews their time usage patterns |
| **Trigger** | User opens /time and views Stats tab |
| **Preconditions** | At least 5 time entries exist |
| **Frequency** | 1-2x weekly |
| **Priority** | Low |

**Steps:**
1. Load time entries for selected period (day/week/month)
2. Render: daily focus hours bar chart, category breakdown
3. Show metrics: total focus hours, deep work ratio, most productive time
4. ARIA insight: "You're most productive between 10 AM-12 PM. Your focus score is 72."

---

## 13. Chat Module (CHAT)

### UC-CHAT-01: Chat with ARIA

| Field | Value |
|---|---|
| **Title** | Chat with ARIA |
| **Description** | User sends a message to ARIA and receives an AI response |
| **Trigger** | User opens /chat and types a message |
| **Preconditions** | User is authenticated |
| **Frequency** | 3-10x daily |
| **Priority** | Critical |

**Steps:**
1. User opens /chat â†’ full conversation history loads
2. ARIA greeting based on context (time of day, pending tasks, etc.)
3. User types message
4. POST /api/chat/ with message + context
5. Backend classifies intent, routes to appropriate handler
6. LLM generates response (streamed via SSE)
7. Frontend renders streaming response
8. ==>[Background] Memory agent logs key information from conversation
9. User can thumbs up/down response for quality feedback

**Intent Categories:**
- Task: "add task buy groceries" â†’ direct action
- Query: "what's my productivity score?" â†’ database query
- Advice: "how should I prepare for interviews?" â†’ AI generation
- Memory: "what was that article I saved last week?" â†’ memory recall
- Command: "brief me" â†’ trigger briefing
- Casual: "good morning" â†’ friendly response

---

### UC-CHAT-02: Ask ARIA for Insights

| Field | Value |
|---|---|
| **Title** | Ask ARIA for Personalized Insights |
| **Description** | User asks ARIA to analyze their data and provide insights |
| **Trigger** | User sends an analysis query |
| **Preconditions** | Sufficient data exists for analysis |
| **Frequency** | 1-3x weekly |
| **Priority** | High |

**Examples:**
- "What's my most productive day of the week?"
- "Show me my income trend this year"
- "What should I focus on this week?"
- "Am I on track for my placement prep?"
- "Compare my productivity when I sleep well vs poorly"

---

## 14. Automation Module (AUTO)

### UC-AUTO-01: Trigger On-Demand Briefing

| Field | Value |
|---|---|
| **Title** | Trigger On-Demand Briefing |
| **Description** | User or system generates a briefing outside the scheduled time |
| **Trigger** | User types "brief me" in chat, or system detects no briefing for today |
| **Preconditions** | None |
| **Frequency** | As needed |
| **Priority** | Medium |

**Steps:**
1. POST /api/automation/trigger/briefing
2. Backend runs same flow as morning briefing
3. But uses user's current context (time of day, tasks completed so far)
4. Briefing generated and saved
5. User sees generated briefing in dashboard

---

### UC-AUTO-02: Trigger Opportunity Radar Scan

| Field | Value |
|---|---|
| **Title** | Trigger On-Demand Radar Scan |
| **Description** | User manually triggers opportunity scan |
| **Trigger** | User clicks "Scan Now" on opportunities page |
| **Preconditions** | Last scan was > 1 hour ago |
| **Frequency** | 1-3x weekly |
| **Priority** | Low |

**Steps:**
1. User clicks "Scan Now" on /opportunities
2. System runs full scan (same as daily cron)
3. Results shown inline with loading animation
4. New matches highlighted

---

## 15. Cross-Module Use Cases

### UC-CROSS-01: Morning Routine Unlock

| Field | Value |
|---|---|
| **Modules** | DASH, TASK, SLP, HAB, OPP |
| **Title** | Complete Morning Routine |
| **Description** | User wakes up, checks briefing, logs sleep, reviews tasks |
| **Trigger** | User wakes up and opens app |
| **Frequency** | Daily |
| **Priority** | Critical |

**Steps:**
1. Open app â†’ briefing ready (UC-DASH-01)
2. Log last night's sleep (UC-SLP-01)
3. Quick scan of top 3 tasks
4. View any new opportunities (UC-OPP-01)
5. Log morning habits (UC-HAB-01 â€” if applicable)
6. Start first focus session (UC-TIME-01)

**Total time: Target < 3 minutes**

---

### UC-CROSS-02: Project Impact Analysis

| Field | Value |
|---|---|
| **Modules** | PRJ, TIME, INC |
| **Title** | Analyze Project Impact |
| **Description** | ARIA shows how a project impacted income and skill development |
| **Trigger** | User views completed project |
| **Frequency** | Per project completion |
| **Priority** | Low |

**Steps:**
1. Project marked as completed
2. ARIA aggregates: total time spent (TIME), income generated (INC), skills used
3. Shows: "This project took 47 hours, earned Rs. 5,000 (Rs. 106/hr), used React + Node.js"
4. Links to related opportunities that match these skills

---

### UC-CROSS-03: Semester Planning Session

| Field | Value |
|---|---|
| **Modules** | CRS, TASK, GOALS, PRJ |
| **Title** | Plan New Semester |
| **Description** | User sets up their entire semester in one session |
| **Trigger** | Start of new semester (user clicks "New Semester" or auto-detected) |
| **Frequency** | Bi-annually |
| **Priority** | High |

**Steps:**
1. New semester detected or user initiates
2. User registers all enrolled courses (UC-CRS-01)
3. ARIA generates study schedule for semester duration
4. User sets semester goals (academic target GPA, project goals, career prep)
5. ARIA suggests weekly study hour allocation per course
6. ==>[Background] Generate recurring study tasks for the semester
7. ==>[Background] Set checkpoint reviews at mid-semester and before exams

---

## 16. Edge Case Catalog

| ID | Module | Edge Case | Handling |
|---|---|---|---|
| EC-01 | All | No network connection | IndexedDB queue, sync on reconnect |
| EC-02 | All | User has zero data | Show empty states with CTA prompts |
| EC-03 | TASK | Recurring task on Feb 29 | Roll to Feb 28 or Mar 1 |
| EC-04 | TASK | Task with 200+ character title | Truncate title at 200 chars, full in detail |
| EC-05 | CRS | Course with 5000+ hours | Cap at 5000, show "extensive course" badge |
| EC-06 | HAB | Habit logged at 11:59 PM vs 12:01 AM | Use local timezone, 5-min grace period |
| EC-07 | SLP | Sleep logged 3 days later | Show "Last logged: 3 days ago", new entry defaults to yesterday |
| EC-08 | INC | Negative income (refund) | Allow, show in red, exclude from hourly rate calc |
| EC-09 | OPP | Opportunity posted in a different country | Show location, distance from user, filter if > 500km |
| EC-10 | CHAT | User sends empty message | Don't send to API, show "Type something..." |
| EC-11 | ALL | User deletes all data | Confirm dialog: "This removes everything. Are you sure?" |
| EC-12 | ALL | Very long session (> 12 hours) | Prompt: "Still there? Take a break?" |
| EC-13 | ALL | Browser tab hidden for hours | Refresh data on tab focus |
| EC-14 | TASK | 100+ tasks created in one day | Show "You're on fire! Focus on completing, not adding." |
| EC-15 | PRJ | Project with no milestones | Default: "MVP", "Polish", "Ship" milestones |

---

## 17. Error Recovery Matrix

| Error | Scope | Detection | User Impact | Recovery Action |
|---|---|---|---|---|
| Supabase connection lost | All | API returns 503 | Read/write fail | Offline queue + retry |
| AI LLM timeout | AI features | No response in 30s | Briefing/chat fail | Algorithmic fallback |
| Google OAuth failure | Auth | OAuth error screen | Cannot login | Retry + email fallback |
| Cron job missed | Scheduled | Missed run detected | Briefing/scan miss | Catch-up on next user visit |
| Push notification fail | Notifications | FCM/APNS error | Missed reminders | Silent retry next cycle |
| Rate limit exceeded | API | 429 response | Request blocked | Show "Slow down" + retry-after |
| Calendar sync fail | Integrations | Google API error | Outdated calendar | Manual refresh button |
| Browser storage full | Offline | QuotaExceededError | Can't cache | Evict oldest cached data |

---

## 18. Use Case Priority Summary

| Priority | Count | Use Cases |
|---|---|---|
| **Critical** (P0) | 8 | DASH-01, TASK-01, TASK-02, TASK-03, CRS-01, OPP-01, CHAT-01, CROSS-01 |
| **High** (P1) | 12 | DASH-02, CRS-02, CRS-03, HAB-01, INC-01, PRJ-01, IDEA-01, OPP-02, CHAT-02, CROSS-03, RES-01, TIME-01 |
| **Medium** (P2) | 11 | HAB-02, SLP-01, SLP-02, INC-02, PRJ-02, IDEA-02, TIME-02, AUTO-01, RES-02, INC-02, CROSS-02 |
| **Low** (P3) | 5 | AUTO-02, RES-03, TIME-03, IDEA-03, PRJ-03 |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Product Team | Initial use cases document (36 use cases across 12 modules) |

---

*End of Use Cases Document*
