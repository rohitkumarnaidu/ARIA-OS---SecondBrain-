# User Flows — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-UF-001 |
| Version | 1.0.0 |
| Status | Draft |
| Date | 2026-06-11 |
| Author | Product Team |
| Classification | Internal |

---

## 1. Introduction

This document defines every user flow across Second Brain OS. Each flow includes the complete journey from trigger to outcome, covering happy paths, error states, edge cases, and decision branching. Flows are organized by module and sequenced by typical user progression.

**Design Philosophy:** Every flow must complete in under 30 seconds for capture actions and under 3 minutes for review actions. Flows that exceed these thresholds must be broken into sub-flows.

**Flow Notation Key:**
- `[Action]` — User or system action
- `{Decision}` — Branching point
- `->` — Flow direction
- `==>` — Async/background process
- `(Error)` — Error recovery path
- `[Metric]` — Success metric captured

---

## 2. Onboarding Flow

### 2.1 First-Time User Onboarding

```
[User lands on /login] -> {Has account?}
    |-- No --> [Google OAuth Sign-In] -> [Supabase creates user row]
    |              -> [ARIA sends welcome chat message]
    |              -> [Onboarding wizard starts]
    |              -> [Step 1: Set display name + timezone]
    |              -> [Step 2: Select 3-5 goals from templates]
    |              -> [Step 3: Connect calendar (optional)]
    |              -> [Step 4: Set study preferences]
    |              -> [Step 5: First task capture demo]
    |              ==> [Background: Create default categories]
    |              ==> [Background: Generate onboarding briefing]
    |              -> [Redirect to /dashboard] [Metric: signup_completed]
    |-- Yes --> [JWT validation] -> {Valid session?}
                   |-- Yes --> [Redirect to /dashboard]
                   |-- No --> [Refresh token] -> {Success?}
                                 |-- Yes --> [Redirect to /dashboard]
                                 |-- No --> [Redirect to /login]
```

### 2.2 Profile Setup Sub-Flow

| Step | Screen | Fields | Validation | Skip Allowed? |
|---|---|---|---|---|
| 1 | Welcome | Name, Timezone, Semester | Name: 2-50 chars, Timezone: valid IANA | No |
| 2 | Goals | 5 goal templates (Study, Career, Health, Finance, Skills) | Min 1 selected | No |
| 3 | Integrations | Google Calendar toggle, Browser extension | None | Yes |
| 4 | Preferences | Study hours/day, deep work start time, focus duration | Hours: 1-12 | Yes (defaults applied) |
| 5 | First Task | Quick capture input | Min 1 char | No (enforced) |

**Edge Cases:**
- **Partial completion:** User closes browser during Step 3. On next login, resume at Step 3.
- **Timezone mismatch:** Detect via IP geolocation, allow override. If IP detection fails, default to IST (UTC+5:30).
- **Duplicate account:** Google OAuth handles this — same email = same user. Merge preferences if re-onboarding.
- **Network failure during save:** Queue changes locally, retry on reconnection. Show toast: "Your preferences will sync when you're back online."

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| OAuth failure | Supabase returns auth_error | "Unable to sign in with Google. Please try again." | Retry button + email login fallback |
| Profile save fails | API returns 500 | "We couldn't save your profile. Don't worry, we'll retry automatically." | Auto-retry 3x with exponential backoff |
| Calendar sync fails | Google API timeout | "Calendar sync failed. You can connect it later from Settings." | Skip + enable in Settings later |
| Invalid timezone | Select picks UTC | "Using UTC (Coordinated Universal Time). You can change this in Settings." | Silently fix + log warning |

**Success Metrics:**
- Onboarding completion rate: Target > 85%
- Time to complete onboarding: Target < 120 seconds
- Step-drop-off rate per step (target: < 5% per step)

---

## 3. Daily Briefing Flow

### 3.1 Morning Briefing Generation

Trigger: 7:00 AM (user's timezone) via APScheduler cron job

```
[Cron job fires at 7:00 AM user timezone]
   -> [scheduler/main.py calls POST /api/automation/trigger/briefing]
   -> [BriefingAgent collects context:]
       -> Query tasks: due today + overdue + high priority
       -> Query habits: yesterday's completion rates
       -> Query sleep: last night's sleep score
       -> Query courses: upcoming deadlines, today's study tasks
       -> Query opportunities: new matches from radar
       -> Query weather: current + forecast (via OpenWeatherMap)
   -> [Assemble context into prompt input]
   -> [Call PromptLoader.get_agent("briefing_agent")]
   -> [Call LLM.generate_json with context]
   -> {LLM succeeds?}
       |-- Yes --> [Parse JSON response]
       |              -> Validate schema (3 tasks, insights, quote, score)
       |              -> [Save to daily_briefings table]
       |              -> [Push notification: "Your briefing is ready"]
       |              -> [Update dashboard cache]
       |-- No --> [Fallback: algorithmic briefing]
                     -> Top 3 tasks by priority + due date
                     -> Missed habits summary
                     -> Generic quote
                     -> [Save as algorithmic briefing]
                     -> [Log LLM failure warning]
```

**Context Assembly (Input to Agent):**

```json
{
  "user_id": "uuid",
  "date": "2026-06-11",
  "tasks": {
    "overdue": [{"title": "Submit DBMS assignment", "priority": "high", "days_overdue": 2}],
    "due_today": [{"title": "Complete React tutorial", "priority": "medium"}],
    "high_priority": [{"title": "Apply to Google STEP internship", "priority": "urgent"}]
  },
  "sleep": {"score": 72, "duration_hours": 6.5, "debt_hours": 2.0},
  "habits": {"streak_current": 5, "yesterday_completed": 3, "total": 5},
  "courses": {
    "active": 3,
    "deadlines_this_week": [{"name": "NPTEL Machine Learning", "days_remaining": 4}],
    "study_tasks_today": 2
  },
  "opportunities": {"new_matches": 1, "title": "Hackathon: Build with AI"},
  "productivity_score": 68,
  "week_progress": "Wednesday — 42% through week"
}
```

**Output Schema (Briefing):**

```json
{
  "top_three": [
    {"task": "Apply to Google STEP internship", "reason": "Deadline in 3 days", "estimated_minutes": 30}
  ],
  "focus_suggestion": "Deep work block: 10 AM - 12 PM on ML project",
  "sleep_insight": "You're 2 hours behind on sleep. Consider lighter schedule today.",
  "opportunity_alert": "New: Build with AI Hackathon — apply by Friday",
  "quote": "The best time to start was yesterday. The next best time is now.",
  "morning_momentum_tip": "Start with your 5-minute task to build momentum",
  "productivity_forecast": 65
}
```

**Decision Tree: Sleep-Adjusted Briefing:**

```
{Sleep score < 60?}
  |-- Yes --> {Score < 40?}
  |              |-- Yes --> [Remove all deep work from top 3]
  |              |              [Prioritize review/light tasks]
  |              |              [Suggest rest or nap]
  |              |-- No --> [Reduce top 3 to 2 deep + 1 shallow]
  |                           [Add 15-min break reminders]
  |-- No --> [Standard briefing with 3 tasks]
```

### 3.2 User Views Briefing

```
[User opens dashboard] -> {Briefing exists for today?}
    |-- Yes --> [Display briefing card at top of dashboard]
    |              -> [Top 3 tasks with checkboxes]
    |              -> [Productivity score gauge]
    |              -> [Sleep insight banner]
    |              -> [Opportunity alert badge]
    |              -> [ARIA quote of the day]
    |              -> [Actions: Start Focus, Dismiss, Snooze (30 min)]
    |-- No --> [Trigger on-demand briefing generation]
                  -> [Show loading skeleton]
                  -> [Display generated briefing]
```

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| No data for context | Empty query results | Show partial briefing with available data | Include note: "Some sections couldn't be loaded" |
| Briefing not generated | No row in daily_briefings for today | "Your briefing is being prepared..." | Trigger on-demand generation |
| LLM returns malformed JSON | JSON parse failure | Fall back to algorithmic briefing | Log error + alert admin |
| Supabase query timeout | > 5s query duration | Show cached briefing from yesterday | Retry in background |

**Success Metrics:**
- Briefing viewed within 1 hour: Target > 70%
- Top 3 tasks completion rate: Target > 60%
- Briefing generation time: Target < 8 seconds (including LLM)
- User satisfaction score: Target > 4.0/5.0 (via weekly prompt)

---

## 4. Task Creation to Completion Flow

### 4.1 Natural Language Task Creation

```
[User activates quick capture] -> [Modal or keyboard shortcut (Cmd+K)]
    -> [User types: "finish dbms assignment by tomorrow evening high priority"]
    -> [On every keystroke (debounced 500ms):]
        -> [Call AI for task parsing]
        -> [Parse result with fields: title, priority, due_date, category]
        -> {AI confidence > 0.8?}
            |-- Yes --> [Display parsed fields inline]
            |-- No --> [Show raw input with "AI suggested" label]
        -> [Show live preview: "Task: finish dbms assignment\nPriority: High\nDue: Tomorrow 6 PM"]
    -> [User presses Enter / clicks Add]
    -> [POST /api/tasks/]
    -> [Supabase inserts task row]
    -> [Update local Zustand state]
    -> [Show success toast: "Task created. Linked to course: DBMS."]
    -> {Task has deadline < 24h?}
        |-- Yes --> [Set ARIA reminder for 2 hours before deadline]
        |-- No --> [No immediate action]
    -> {Task mentions existing course/project?}
        |-- Yes --> [Auto-link to course/project by name match]
        |-- No --> [Task remains unlinked]
```

**Parsing Examples (AI Extraction):**

| Input | Title | Priority | Due Date | Category | Linked To |
|---|---|---|---|---|---|
| "finish dbms assignment by tomorrow evening high priority" | Finish DBMS assignment | High | Tomorrow 6 PM | Academics | DBMS course |
| "leetcode daily challenge" | LeetCode Daily Challenge | Medium | Today 11:59 PM | Coding | — |
| "buy groceries list milk eggs bread" | Buy groceries | Low | No date | Personal | — |
| "prepare for google interview next friday urgent" | Prepare for Google interview | Urgent | Next Friday 9 AM | Career | — |
| "review pull request for project X" | Review pull request for project X | High | No date | Projects | Project X |

### 4.2 Task Completion Flow

```
[User checks task checkbox / clicks "Complete"]
    -> [POST /api/tasks/{id}/complete]
    -> [Supabase sets completed_at = NOW(), status = "completed"]
    -> [Update Zustand store (remove from active list)]
    -> [Show subtle animation: task crosses out, fades, "ding" sound]
    -> [Metric: task_completed logged]
    -> [Check if all today's top 3 done]
        -> {Top 3 completed?}
            |-- Yes --> [Confetti animation + "Morning goal achieved!"]
            |              [ARIA message: "You crushed your morning. Build momentum."]
            |-- No --> [Subtle progress indicator update]
    -> [Check task chain implications]
        -> {Was this a blocker for other tasks?}
            |-- Yes --> [Unblock dependent tasks]
            |              [Notify: "Task X is ready to start now"]
            |-- No --> [No additional action]
```

### 4.3 Task Rescheduling Flow

```
[User long-presses / right-clicks task]
    -> [Context menu: Complete | Reschedule | Drop | Edit]
    -> [User selects "Reschedule"]
    -> [Date picker appears]
    -> [User picks new date/time]
    -> [PUT /api/tasks/{id} with new due_date]
    -> [Check: was this already overdue?]
        -> {Overdue > 3 days?}
            |-- Yes --> [Log as "stale task rescheduled"]
            |              [ARIA note: "This has been pending a while. Consider breaking it down."]
            |-- No --> [Normal reschedule logged]
    -> [Update task in store]
    -> [Show toast: "Task moved to Friday"]
```

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| Save fails (network) | POST returns 500 | "Task saved offline. Will sync when connected." | Queue in IndexedDB, sync on reconnect |
| AI parsing fails | API returns no parse | "Could you be more specific? Try including what, when, and priority." | Fallback to manual field entry |
| Duplicate detection | Title similarity > 95% to active task | "A similar task already exists: '...'. Add anyway?" | Merge option or create duplicate |
| Dependency cycle detected | Task A blocks B, B blocks A | Circular dependency detected. Please adjust task links. | Highlight cycle in UI |

**Success Metrics:**
- Tasks created per day: Target > 3
- Tasks completed per day: Target > 2
- Completion rate (completed/created): Target > 60%
- Time to create task: Target < 10 seconds
- Natural language parse accuracy: Target > 90%
- Overdue task rate: Target < 20%

---

## 5. Course Tracking Flow

### 5.1 Course Registration Flow

```
[User navigates to /courses]
    -> [Clicks "Add Course"]
    -> [Modal: Course registration form]
    -> [Fields: Name, Platform (Udemy/Coursera/NPTEL/College/YouTube/Other),
        URL, Deadline, Why enrolled, Total hours, Hours/week]
    -> [Clicks "Calculate Deadline" optionally]
        -> {Total hours + Hours/week provided?}
            |-- Yes --> [Auto-calculate suggested deadline]
            |              [Show: "At 5 hrs/week, you'll finish by Dec 15"]
            |              [User confirms or overrides]
            |-- No --> [Manual deadline entry]
    -> [Clicks Save]
    -> [POST /api/courses/]
    -> [Supabase inserts course]
    -> ==>[Background: Generate study task template for course duration]
    -> ==>[Background: Check if URL already exists (duplicate detection)]
    -> [Redirect to course detail page]
```

### 5.2 Course Progress & Deadline Warning Flow

```
[Cron job runs daily at 6:00 AM]
    -> [Query all active courses with deadlines]
    -> [For each course:]
        -> [Calculate: hours_remaining / days_remaining vs hours_available]
        -> {At risk of missing deadline?}
            |-- Yes --> {Days to deadline < 3?}
            |              |-- Yes --> [High priority notification]
            |              |              [Create urgent study task]
            |              |              [ARIA message: "URGENT: Course deadline approaching"]
            |              |-- No --> [Medium priority notification]
            |                           [Create catch-up study task]
            |                           [Dashboard warning badge]
            |-- No --> [On track, no action]
```

**Progress Calculation:**

```
completion_pct = (hours_completed / total_hours) * 100
pace_needed = hours_remaining / days_remaining
pace_actual = avg_hours_per_day_last_7_days
on_track = pace_actual >= pace_needed
```

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| Duplicate course detected | Same URL + active status | "You already registered this course on [date]. Track it? Or add a different one?" | Merge or confirm duplicate |
| Deadline passed without mark | deadline < today, status != completed | "Your deadline for [course] passed. Update your progress?" | Update progress or extend deadline |
| Progress > 100% | hours_completed > total_hours | Progress capped at 100%. Course marked for completion review. | Auto-cap at 100%, prompt completion |

**Success Metrics:**
- Courses registered per user: Target > 3
- Course completion rate: Target > 60%
- Daily study tasks completed: Target > 80%
- Deadline miss rate: Target < 15%

---

## 6. Habit Logging Flow

### 6.1 Daily Habit Check-In

```
[System: 8:00 PM reminder OR User opens /habits]
    -> [Display today's habits with toggle/swipe UI]
    -> [For each habit:]
        -> [Show: habit name, current streak, goal, completion status]
        -> [User toggles: Done / Not Done / Skip]
    -> {All habits logged?}
        |-- Yes --> [Show today's habit summary]
        |              [Streak celebration if milestone (7, 30, 60, 90 days)]
        |              [Update productivity score +5 for full completion]
        |-- No --> [Show progress: "3 of 5 habits logged"]
        |              [Gentle reminder habit: "Don't break your X-day streak!"]
    -> [POST /api/habit_logs/ batch]
    -> [Supabase inserts habit_log rows]
    -> [Update streak calculations in habits table]
```

### 6.2 Habit Streak Calculation

```
streak_break_detection:
  -> Query habit_logs for last 90 days
  -> Sort by date DESC
  -> Count consecutive days where status = "completed"
  -> {Missed >= 3 consecutive days?}
      |-- Yes --> [Reset streak to 0]
      |              [Flag for weekly review: "habit needs reassessment"]
      |-- No --> {Daily check-ins happen but sporadic?}
                    |-- Yes --> [Maintain streak but flag low consistency]
                    |-- No --> [Maintain streak normally]
  -> Update habits.streak_current
  -> If streak_current > streak_best, update streak_best
```

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| Duplicate log (same date) | Unique constraint violation | "Today's habit was already logged. It's been updated." | Update existing record |
| Missed habit notification | No log by 10 PM | "You haven't logged [habit] today. Quick check-in?" | Push notification + badge |
| Streak data inconsistency | streak_current != calculated | "Your streak has been recalculated. Check your habit history." | Recalculate from logs |

**Success Metrics:**
- Habits logged per day: Target > 80% of defined habits
- 7-day streak achievement rate: Target > 50%
- 30-day streak achievement rate: Target > 20%
- Habit abandonment rate: Target < 15% (reactivated > 7 days idle)

---

## 7. Weekly Review Flow

### 7.1 Automated Weekly Review Generation

Trigger: Sunday 8:00 PM user timezone via APScheduler

```
[Cron job fires at 8:00 PM Sunday]
    -> [POST /api/automation/trigger/weekly-review]
    -> [WeeklyReviewAgent collects past 7 days data:]
        -> Query tasks: completed, missed, created, overdue
        -> Query habits: streak changes, completion rate
        -> Query courses: progress delta, deadlines approaching
        -> Query income: entries, total, hourly rate
        -> Query sleep: average score, debt trend
        -> Query opportunities: saved, applied, outcome
        -> Query time_entries: total focused hours, categories
    -> [Assemble weekly context window]
    -> [Call PromptLoader.get_agent("weekly_review_agent")]
    -> [Call LLM.generate_json with weekly context]
    -> {LLM succeeds?}
        |-- Yes --> [Parse weekly review JSON]
        |              [Validate schema]
        |              [Save to weekly_reviews table]
        |              [Push notification: "Your weekly review is ready"]
        |-- No --> [Fallback: algorithmic review]
        |              [Generate stats summary without insights]
    -> [Update productivity score for the week]
```

**Output Schema (Weekly Review):**

```json
{
  "week_overview": "Strong week — completed 12 of 18 planned tasks (67%)",
  "wins": ["Completed DBMS project milestone", "5-day coding streak"],
  "improvements": ["Sleep debt increased by 4 hours", "Missed 2 habit check-ins"],
  "patterns": [
    {"pattern": "Low productivity on Wednesdays", "suggestion": "Schedule lighter tasks on Wednesdays"}
  ],
  "focus_next_week": "Prioritize ML course — deadline in 10 days",
  "metric_changes": {
    "productivity_score": {"previous": 65, "current": 72, "change": "+7"},
    "sleep_avg": {"previous": 7.2, "current": 6.1, "change": "-1.1"},
    "tasks_completed": {"previous": 9, "current": 12, "change": "+3"},
    "habit_completion": {"previous": "83%", "current": "76%", "change": "-7%"},
    "focus_hours": {"previous": 18.5, "current": 22, "change": "+3.5"}
  },
  "achievements": [
    {"title": "10-day coding streak", "icon": "fire", "unlocked": true}
  ],
  "next_week_goals": [
    {"goal": "Complete ML course module 5-8", "priority": "high"},
    {"goal": "Sleep 7+ hours every night", "priority": "high"}
  ],
  "weekly_score": 72
}
```

**Decision Tree: Low Score Intervention:**

```
{Weekly score < 50?}
  |-- Yes --> {Score < 35?}
  |              |-- Yes --> [Crisis mode: ARIA sends encouraging message]
  |              |              [Suggest: "Let's reset. Pick 1 goal for next week."]
  |              |              [Reduce task load recommendation by 50%]
  |              |              [Highlight: overwork pattern detected]
  |              |-- No --> [Gentle correction mode]
  |                           [Flag: "You had a tough week. Here's how to bounce back."]
  |                           [Suggest: "Focus on sleep recovery first"]
  |-- No --> [Normal review with growth areas]
```

**Success Metrics:**
- Weekly reviews viewed: Target > 60% of users
- Action items completed from review: Target > 40%
- Score accuracy (self-reported vs calculated): Target > 85%

---

## 8. Chat with ARIA Flow

### 8.1 User Initiates Chat

```
[User opens /chat or uses Cmd+Shift+C]
    -> [Chat interface loads with message history]
    -> [ARIA greeting based on context:]
        -> {After 9 PM?} -> "Evening. Ready to wind down?"
        -> {Morning before 10 AM?} -> "Good morning. Here's your day ahead."
        -> {Tasks overdue?} -> "You have 3 pending tasks. Want to review?"
        -> {Default} -> "I'm here. What's on your mind?"
    -> [User types message]
    -> [POST /api/chat/ with message + context]
    -> [Backend assembles full context:]
        -> Load PromptLoader.get_system("aria_system")
        -> Load PromptLoader.get_system("guardrails")
        -> Gather user context (recent tasks, last 10 messages, current projects)
        -> Call LLM.generate with system + user + context
    -> [Stream response back to frontend via SSE]
    -> [Display streaming response in chat UI]
    -> [User can interrupt, edit, or follow up]
```

### 8.2 Intent Classification (ARIA Router)

```
[User message received]
    -> [Classify intent:]
        -> {Task intent?} -> [Delegate to task_agent]
        -> {Course intent?} -> [Query courses API directly]
        -> {Habit intent?} -> [Query habits API directly]
        -> {Opportunity intent?} -> [Query opportunities API]
        -> {Memory intent?} -> [Call memory_agent for recall]
        -> {General question?} -> [ARIA responds directly]
        -> {Command: "brief me"} -> [Trigger briefing generation]
        -> {Command: "review my week"} -> [Trigger weekly review]
        -> {Unclear} -> [Ask clarifying question]
    -> {Requires database query?}
        |-- Yes --> [Execute query -> format results -> include in response]
        |-- No --> [Direct LLM response]
    -> {Requires action?}
        |-- Yes --> [Execute action (create task, update habit)]
        |              [Confirm action in response]
        |-- No --> [Informational response only]
```

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| LLM timeout | No response in 30s | "I'm thinking... just a moment longer." | Retry once, then escalate |
| LLM hallucination | Guardrail violation | Response filtered, fallback: "Let me check my data instead." | Query database directly |
| Context overflow | Tokens > context window | Truncate old messages from context | Keep last 20 messages + summary of earlier |
| API failure (Supabase down) | Supabase returns 503 | "My memory is having trouble. I'll use what I remember." | Use cached context, retry |

**Success Metrics:**
- Messages per session: Target > 4
- Session completion rate: Target > 70% (user gets answer)
- Intent classification accuracy: Target > 92%
- Response time: Target < 3 seconds
- User satisfaction (thumbs up/down): Target > 85% positive

---

## 9. Opportunity Discovery Flow

### 9.1 Opportunity Radar Daily Scan

Trigger: 6:00 AM daily via APScheduler

```
[Cron job fires at 6:00 AM]
    -> [Query user profile: skills, interests, goals, semester, location]
    -> [Build search queries from profile tags]
    -> [Scrape/query opportunity sources:]
        -> [Internshala API -> internships matching skills]
        -> [LinkedIn scraping -> relevant job postings]
        -> [Devfolio/Devpost -> hackathons near user]
        -> [ScholarshipsIndia -> relevant scholarships]
        -> [GitHub trending -> relevant repos/projects]
    -> [Call PromptLoader.get_agent("opportunity_radar_agent")]
    -> [Run AI matching algorithm on collected opportunities:]
        -> [Score each opportunity 0-100 based on skill match, location, deadline, user goals]
    -> {Match score > 70?}
        |-- Yes --> [Save to opportunities table with match_reason]
        |              [Include in morning briefing]
        |              [Push notification if urgent (deadline < 3 days)]
        |-- No --> [Archive low-score opportunities]
    -> [Run duplicate detection: URL + title similarity > 85%]
        -> [Merge or discard duplicates]
```

### 9.2 User Applies to Opportunity

```
[User views opportunity card]
    -> [Options: Save | Apply | Dismiss | Share]
    -> [User clicks "Apply"]
        -> [Show application tracker modal]
        -> [Fields: Applied date, Notes, Status (Applied/Interviewing/Offer/Rejected)]
        -> [Auto-fill: company name, role, url from opportunity]
        -> [User saves application record]
        -> [Create follow-up task: "Follow up on [company] application" in 7 days]
        -> [Log to income_entries if paid internship]
    -> [User clicks "Save"]
        -> [Move to saved opportunities]
        -> [Set reminder for 3 days before deadline]
    -> [User clicks "Dismiss"]
        -> [Mark as dismissed, add to ignore list for similar]
```

**Error Paths:**

| Error | Detection | User Message | Recovery |
|---|---|---|---|
| No sources reachable | All APIs timeout | "Couldn't scan today. Will retry in 6 hours." | Retry at noon |
| Match score too low | All scores < 50 | "No strong matches today. I'll keep watching." | Reduce threshold temporarily |
| Duplicate opportunity | Same URL already saved | "You already saved this on [date]. Check your applications page." | Open existing record |
| Application link broken | URL returns 404 | "The application link may be expired. Let me search for alternatives." | Manual search suggestion |

**Success Metrics:**
- Opportunities surfaced per week: Target > 5
- User applies to > 1 opportunity/week: Target > 40%
- Match-to-application rate: Target > 20%
- Opportunity source coverage: Target > 5 sources

---

## 10. Income Tracking Flow

### 10.1 Income Entry Flow

```
[User navigates to /income]
    -> [Clicks "Add Income Entry"]
    -> [Modal fields: Amount (Rs.), Source (Freelance/Internship/Scholarship/Other),
        Description, Hours worked, Date, Project linked?]
    -> {Hours worked > 0?}
        |-- Yes --> [Auto-calculate hourly rate]
        |              [Show: "Effective rate: Rs. 450/hr"]
        |              [Compare to previous: "↑12% from last month"]
        |-- No --> [Hourly rate not calculated]
    -> [Clicks Save]
    -> [POST /api/income/]
    -> [Update dashboard income summary]
    -> [Update monthly earning total]
```

**Success Metrics:**
- Income entries per month: Target > 4
- Monthly income tracked: Target > Rs. 5,000 average
- Hourly rate trend visibility: Target > 80% entries have hours

---

## 11. Cross-Module Flows

### 11.1 Flow: Idea → Project → Task → Income

```
[User captures idea in Idea Vault]
    -> [Idea status: Raw]
    -> [ARIA detects high feasibility score]
        -> [Suggests moving to "Researching" phase]
        -> [Creates project shell with idea details]
    -> [User moves to "Building" phase]
        -> [ARIA generates initial task breakdown]
        -> [Creates project in Projects module]
        -> [Links existing tasks from task manager]
    -> [User completes project milestone]
        -> [ARIA suggests monetization channels]
        -> [Creates income entry when payment received]
        -> [Opportunity radar searches for similar paid work]
```

### 11.2 Flow: Course → Sleep → Productivity Correlation

```
[Course deadlines approaching]
    -> [User sacrifices sleep (logged in sleep_logs)]
    -> [Next day: low sleep score, high fatigue]
    -> [Morning briefing adjusts: fewer deep work tasks]
    -> [Habit completion drops]
    -> [Weekly review detects pattern]
    -> [ARIA flags: "You consistently lose sleep before deadlines.
        Consider starting course material 2 weeks earlier."]
```

### 11.3 Flow: Opportunity → Application → Prep Tasks

```
[Opportunity radar matches internship]
    -> [User applies]
    -> [Auto-creates application tracker]
    -> [Generates preparation tasks:]
        -> [Create task: "Research company background" - due 3 days before interview]
        -> [Create task: "Practice technical interview questions on LeetCode" - recurring]
        -> [Create task: "Prepare portfolio/examples" - due 1 week before]
        -> [Suggest relevant saved resources from library]
```

---

## 12. Error Recovery Flows

### 12.1 Network Offline Flow

```
[Network connectivity lost detected (navigator.onLine = false)]
    -> [Show offline indicator badge]
    -> [Queue all writes to IndexedDB]
    -> [Continue reading cached data]
    -> [Switch to algorithmic mode for AI features]
    -> {Network restored?}
        |-- Yes --> [Sync queued writes to Supabase]
        |              [Resolve conflicts (last-write-wins)]
        |              [Refresh stale cache]
        |              [Show sync complete toast]
        |-- No --> [Remain in offline mode]
```

### 12.2 AI Service Down Flow

```
[LLM request returns timeout or 503]
    -> [Retry 1 with exponential backoff (2s)]
    -> [Retry 2 with exponential backoff (4s)]
    -> {Claude fallback available?}
        |-- Yes --> [Route to Claude API]
        |              [Log: "Ollama down, using Claude fallback"]
        |-- No --> [Fallback to algorithmic mode]
        |              [Log: "AI unavailable, using algorithm"]
    -> [Cache algorithmic result]
    -> [Continue service without AI]
```

### 12.3 Session Expiry Flow

```
[API returns 401 on any request]
    -> [Attempt token refresh with refresh_token]
    -> {Refresh successful?}
        |-- Yes --> [Update access_token in memory]
        |              [Retry original request]
        |-- No --> [Clear auth state]
        |              [Redirect to /login]
        |              [Show: "Your session expired. Please sign in again."]
```

---

## 13. Future Flows

### 13.1 Offline-First Sync (Planned)

```
[PWA installation flow]
    -> [Service worker registration]
    -> [Cache app shell + static assets]
    -> [Background sync for writes]
    -> [Conflict resolution: last-write-wins + manual for same-second conflicts]
    -> [Periodic background sync every 15 min when online]
```

### 13.2 Mobile App Flow (Planned)

```
[React Native app launch]
    -> [Biometric authentication (fingerprint/face)]
    -> [Bottom tab navigation: Dashboard | Quick Capture | Chat | Profile]
    -> [Push notification handling -> deep link to relevant screen]
    -> [Quick capture widget on home screen]
    -> [Offline support with local SQLite]
    -> [Sync with backend on connectivity]
```

### 13.3 Browser Extension Flow (Planned)

```
[User browses any webpage]
    -> [Extension icon detects page type:]
        -> {Course page (Udemy/Coursera)?} -> [Offer to save as course]
        -> {YouTube video?} -> [Offer to save to knowledge vault]
        -> {Job posting?} -> [Offer to save as opportunity]
        -> {Interesting article?} -> [Offer to save as resource]
        -> {Default} -> [Quick capture overlay on Cmd+Shift+K]
    -> [One-click save to Second Brain OS]
    -> [Auto-tagging and categorization]
```

---

## 14. Flow Success Metrics Dashboard

| Flow | Primary Metric | Target | Secondary Metric | Target |
|---|---|---|---|---|
| Onboarding | Completion rate | > 85% | Time to complete | < 120s |
| Daily Briefing | View rate within 1h | > 70% | Top 3 completion | > 60% |
| Task Creation | Create time | < 10s | Parse accuracy | > 90% |
| Task Completion | Completion rate | > 60% | Overdue rate | < 20% |
| Course Tracking | Course completion | > 60% | Deadline accuracy | < 15% miss |
| Habit Logging | Daily log rate | > 80% | 7-day streak | > 50% |
| Weekly Review | View rate | > 60% | Action completion | > 40% |
| Chat | Session quality | > 85% positive | Response time | < 3s |
| Opportunities | Applied rate | > 20% | Sources covered | > 5 |
| Income Tracking | Entries/month | > 4 | Hourly rate tracking | > 80% |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Product Team | Initial user flows document |

---

*End of User Flows Document*
