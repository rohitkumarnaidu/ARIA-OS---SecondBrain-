# Acceptance Criteria — Second Brain OS

## Document Control
| Field | Value |
|---|---|
| Document ID | SB-AC-001 |
| Version | 1.0.0 |
| Status | Draft |
| Date | 2026-06-11 |

---

## Module 1: Dashboard & Morning Briefing

### AC-DASH-01: Morning Briefing Delivery
**Given** the user has at least one active task, course, or goal
**When** the system clock reaches 7:00 AM IST
**Then** the system shall generate a briefing with exactly 6 sections (Today's Focus, Overnight Opportunities, Course Target, Roadmap Check, ARIA Top Pick, What to Skip)
**And** the briefing shall be saved to the daily_briefings table
**And** a push notification shall be sent with the title "Your morning briefing is ready"

### AC-DASH-02: Productivity Score
**Given** the user has tasks created for today
**When** the dashboard loads
**Then** the productivity score shall display as a number between 0 and 100
**And** the score shall equal (tasks_completed_today / tasks_due_today * 100)
**And** the score shall update in real-time when tasks are completed

### AC-DASH-03: Quick Capture
**Given** the user is on any page in the app
**When** the user clicks the quick capture button (floating action button)
**Then** a modal shall open with fields for type (task/idea/resource), title, and optional description
**And** the modal shall close after saving
**And** the captured item shall appear in the appropriate module immediately

### AC-DASH-04: Today's Schedule
**Given** the user has tasks with scheduled_start times for today
**When** the dashboard loads
**Then** a time-blocked schedule view shall display all today's tasks in chronological order
**And** each block shall show task title, time range, and priority color

---

## Module 2: Task Manager

### AC-TASK-01: Smart Task Creation
**Given** the user enters a task description in natural language (e.g., "Finish DSA assignment by Friday high priority")
**When** the user submits
**Then** the system shall extract and populate: title ("Finish DSA assignment"), priority (high), category (study), and due_date (Friday)
**And** the task shall appear in the task list immediately

### AC-TASK-02: Auto-Reschedule
**Given** a task exists with due_date < now() AND status NOT IN ('done', 'archived') AND rescheduled_from IS NULL
**When** the 15-minute cron runs
**Then** the system shall increment missed_count by 1
**And** set status to 'missed'
**And** set scheduled_start to now() + 2 hours
**And** set rescheduled_from to the original due_date

### AC-TASK-03: Zero Miss Escalation
**Given** a task has been missed (missed_count >= 1)
**When** the missed task checker runs
**Then** a push notification shall be sent every time the task is rescheduled
**And** if missed_count >= 2, an email shall be sent via Resend
**And** if missed_count >= 3 AND priority = 'high', an SMS shall be sent via Twilio

### AC-TASK-04: Subtask AI Breakdown
**Given** the user selects a task and asks ARIA to break it down
**When** ARIA processes the request
**Then** subtasks shall be created linked to the parent task ID
**And** each subtask shall inherit the parent's priority and category
**And** the parent shall show progress (subtasks_completed / subtasks_total * 100)

### AC-TASK-05: Task Dependencies
**Given** Task A and Task B exist
**When** the user links Task B as dependent on Task A
**Then** Task B shall be blocked until Task A is completed
**And** the UI shall show a visual arrow from Task A to Task B
**And** Task B shall not be actionable until Task A status = 'done'

### AC-TASK-06: Sleep-Aware Priority
**Given** the user's sleep score for today is < 50
**When** the dashboard loads in the morning
**Then** tasks categorized as 'study' or 'build' with high priority shall be demoted to medium priority
**And** admin/planning tasks shall be promoted if they exist
**And** a note shall appear: "Low sleep detected — heavy tasks moved"

---

## Module 3: Course Tracker

### AC-COURSE-01: Mandatory Deadline
**Given** the user is adding a new course
**When** the user attempts to save without a target_completion_date
**Then** the form shall display an error: "Target completion date is required"
**And** the course shall not be created

### AC-COURSE-02: Daily Minutes Calculation
**Given** a course has target_completion_date, total_duration_minutes, and progress_percent
**When** the course is saved or daily_minutes_target is viewed
**Then** the system shall calculate: remaining_minutes = total_duration * (1 - progress/100)
**And** days_remaining = (target_date - today) in days
**And** daily_minutes_needed = remaining_minutes / days_remaining

### AC-COURSE-03: Behind-Schedule Alert
**Given** a course has days_remaining < 14 AND daily_minutes_needed > user_available_minutes
**When** the Course Progress Nudge runs at 6 PM
**Then** an alert shall be generated: "[Course] needs [X] min/day now to finish by [date]"
**And** the course card shall display a red "Behind Schedule" badge

---

## Module 4: YouTube Knowledge Vault

### AC-YT-01: One-Tap Save
**Given** the user is on a YouTube video page
**When** they click the browser extension icon
**Then** the popup shall display the video title and thumbnail (auto-fetched)
**And** the user selects a category and clicks Save
**And** the video shall be saved to youtube_saves with status = 'unseen'

### AC-YT-02: AI Summary
**Given** a YouTube video has been saved
**When** the save is processed
**Then** ARIA shall generate a 3-sentence summary of what the video teaches
**And** the summary shall be stored in youtube_saves.summary

### AC-YT-03: 60-Day Expiry
**Given** a saved video has status = 'unseen' AND saved_at < now() - 60 days
**When** the user opens the YouTube Vault page
**Then** an expiry banner shall appear: "This video was saved 60+ days ago. Keep or Archive?"
**And** if the user selects Archive, status changes to 'archived'

---

## Module 5: Resource Library

### AC-RES-01: Auto-Tagging
**Given** a resource has been saved with a URL and title
**When** ARIA processes the resource
**Then** 3-5 topic tags shall be generated and stored in resources.tags
**And** the tags shall display as colored chips on the resource card

### AC-RES-02: Natural Language Search
**Given** the user types "React article saved 3 months ago" in the search bar
**When** the search is submitted
**Then** the system shall return resources where title or tags match "React" AND type = "article"
**And** results sorted by saved_at descending within the approximate date range

---

## Module 6: Idea Vault

### AC-IDEA-01: AI Market Check
**Given** an idea is saved with title and description
**When** ARIA processes the idea
**Then** the system shall call Brave Search to check for existing products
**And** store in ideas.ai_analysis: {competitors: [3 names], market_size: "small"|"medium"|"large", feasibility: "easy"|"medium"|"hard", insight: "string"}

### AC-IDEA-02: Status Pipeline
**Given** an idea exists with status = 'raw'
**When** the user moves the idea to 'researching'
**Then** status shall update immediately
**And** the pipeline UI shall show the current stage highlighted
**And** the stage duration timer shall start for the new stage

### AC-IDEA-03: Validation Plan
**Given** an idea exists with status = 'validating'
**When** the user clicks "Generate Validation Plan"
**Then** ARIA shall generate a 2-week step-by-step plan with zero-money actions
**And** each step shall have a checkbox
**And** the plan shall be saved to the idea record

---

## Module 7: Goal & Roadmap System

### AC-ROAD-01: Visual Builder
**Given** the user is on the roadmap editor page
**When** the page loads
**Then** a React Flow canvas shall render with all existing nodes and edges
**And** the user can drag existing nodes to reposition
**And** the user can add new nodes by clicking "Add Node" and placing on canvas
**And** node positions shall save on drag end

### AC-ROAD-02: Text to Roadmap
**Given** the user pastes text (e.g., a course syllabus)
**When** the user clicks "Generate Roadmap"
**Then** the system shall call Claude API to parse the text into nodes and edges
**And** display a preview of the parsed roadmap on the canvas
**And** the user can accept or edit before saving

### AC-ROAD-03: Hard Deadline Mode
**Given** a roadmap has hard_deadline set
**When** the user enables "Hard Deadline Mode"
**Then** all node completion dates shall be calculated backwards from the hard_deadline
**And** daily topic targets shall be generated for each day leading to the deadline
**And** the projected completion date shall equal the hard_deadline exactly

### AC-ROAD-04: AI Timing Sliders
**Given** a roadmap has nodes with estimated_weeks
**When** the user adjusts the hours_per_day slider
**Then** all node completion dates shall recalculate in real-time
**And** the projected end date at the top of the canvas shall update

### AC-ROAD-05: Task Generation
**Given** a roadmap node is active and not completed
**When** the daily briefing or task manager syncs
**Then** a task shall exist in the task manager linked to the roadmap node
**And** the task title shall include the roadmap name and node label

---

## Module 8: Opportunity Radar

### AC-OPP-01: Daily Scan
**Given** the system clock reaches 6:00 AM IST
**When** the Opportunity Radar cron runs
**Then** 8 search queries shall be generated based on user skills
**And** Brave Search API shall be called for each query
**And** results shall be parsed for match_score >= 50
**And** matched opportunities shall be saved to the opportunities table
**And** results shall appear in the 7 AM morning briefing

### AC-OPP-02: Critical Alert
**Given** an opportunity has deadline < now() + 48 hours AND match_score >= 50
**When** the opportunity is saved
**Then** an immediate push notification shall be sent: "[Title] closing soon — apply now"
**And** the opportunity shall have a red "Closing Soon" badge

### AC-OPP-03: Match Score Calculation
**Given** an opportunity has a requirements list
**When** the match score is calculated
**Then** the score shall be an integer between 0 and 100
**And** opportunities with score < 40 shall be filtered out (is_relevant = false)
**And** the match_reason shall be a personalized sentence explaining relevance

---

## Module 9: Income Sources Tracker

### AC-INC-01: Effective Hourly Rate
**Given** an income source has monthly_amount and hours_per_week
**When** the income dashboard loads
**Then** effective_hourly_rate = monthly_amount / (hours_per_week * 4.3)
**And** the rate shall display formatted as "Rs. X/hr"

### AC-INC-02: Income Milestones
**Given** the user logs an income entry
**When** total income across all time crosses Rs. 1000, 5000, 10000, or 25000
**Then** a milestone celebration shall display with confetti animation
**And** the milestone progress bar shall update to show progress toward the next milestone

---

## Module 10: Project Tracker

### AC-PROJ-01: Next Action Required
**Given** the user creates a new project or edits an existing one
**When** the user attempts to save without a next_action value
**Then** the form shall display an error: "Next action is required for every project"
**And** the project shall not be saved

### AC-PROJ-02: GitHub Inactivity Flag
**Given** a project has github_url set AND last_commit_at < now() - 7 days
**When** the project page loads
**Then** a red banner shall display: "No commits in [X] days"
**And** ARIA shall suggest a specific action: "Push a small fix or update the README"

---

## Module 11: Academic Planner

### AC-ACAD-01: CGPA Calculation
**Given** the user has subjects with marks_scored, max_marks, and credits
**When** the academic planner page loads
**Then** current CGPA = SUM(marks_scored/max_marks * credits) / SUM(credits) * 10
**And** projected CGPA shall be calculated using current average for remaining exams
**And** both values shall display with one decimal place

### AC-ACAD-02: At-Risk Alert
**Given** a subject has marks_scored/max_marks < 0.4
**When** the academic planner loads OR the Course Progress Nudge runs
**Then** at_risk_flag shall be set to true for that subject
**And** a task shall be auto-inserted: "Study [subject name] — at risk of failing"
**And** the subject card shall display a red "At Risk" badge

---

## Module 12: Habit Engine

### AC-HAB-01: Streak Tracking
**Given** a habit has frequency = 'daily'
**When** the user marks the habit as completed today
**Then** current_streak shall increment by 1
**And** if current_streak > best_streak, best_streak = current_streak
**And** consistency_percentage = (completions_last_30_days / 30) * 100

### AC-HAB-02: Miss Nudge
**Given** a habit was not completed yesterday AND not completed today
**When** the Habit Miss Checker runs at midnight
**Then** a push notification shall be sent: "[Habit name] — 2 days missed. Streak at risk."
**And** current_streak shall be reset to 0 if it was > 0

---

## Module 13: Sleep Monitor

### AC-SLEEP-01: Sleep Score Calculation
**Given** the user has logged sleep_start, sleep_end, and quality_rating
**When** the sleep is logged
**Then** duration_minutes = (sleep_end - sleep_start) in minutes
**And** sleep_score = Math.min(100, (duration_minutes/480 * 60) + (quality_rating * 8))
**And** the score shall display as a number between 0 and 100

### AC-SLEEP-02: Task Adjustment on Low Sleep
**Given** sleep_score < 50 for today
**When** the user opens the app
**Then** all tasks with category IN ('study', 'build') AND priority = 'high' shall have priority demoted to 'medium'
**And** a notification shall be shown: "Low sleep detected — heavy tasks moved to tomorrow"
**And** the change shall be reversible from the task manager

### AC-SLEEP-03: Sleep Debt Tracking
**Given** the user has sleep logs for the last 7 days
**When** the sleep page loads
**Then** sleep_debt = SUM(max(0, 480 - duration_minutes) for each day in last 7 days)
**And** if sleep_debt > 600 (10 hours), a warning shall display

---

## Module 14: Time Tracker

### AC-TIME-01: Start/Stop Timer
**Given** a task exists
**When** the user clicks the start button on the task
**Then** a timer shall begin counting up in real-time
**And** the task shall show a running timer badge
**When** the user clicks stop
**Then** a time_log entry shall be created with task_id, started_at, ended_at, and duration_seconds

### AC-TIME-02: Idle Auto-Stop
**Given** a timer is running for a task
**When** no mouse/keyboard activity is detected for 15 minutes
**Then** the timer shall auto-stop
**And** a dialog shall appear: "Timer auto-stopped due to inactivity. Log partial time?"

### AC-TIME-03: Deep Work Detection
**Given** a time_log has duration_seconds > 5400 (90 minutes)
**When** the time_log is saved
**Then** is_deep_work shall be set to true
**And** a badge "Deep Work — [duration formatted]" shall display in the time log

---

## Module 15: Weekly Review

### AC-WEEKLY-01: Sunday Generation
**Given** the system clock reaches Sunday 8:00 PM IST
**When** the Weekly Review cron runs
**Then** the system shall compile: tasks completed/missed count, study minutes per course, income logged total, opportunities applied/saved/dismissed, roadmap nodes completed
**And** call Claude API with the WEEKLY REVIEW system prompt
**And** save the generated review to weekly_reviews table
**And** send via Resend email to user's registered email
**And** send a push notification: "Your weekly review is ready"

### AC-WEEKLY-02: Pattern Insight
**Given** a weekly review is generated
**When** the review is displayed
**Then** exactly one pattern insight shall be present in the "The One Pattern I Noticed" section
**And** the insight shall be specific to the user's data, not generic

### AC-WEEKLY-03: Month-over-Month Comparison
**Given** the user has 4+ weekly reviews generated
**When** the latest weekly review is loaded
**Then** a comparison section shall display: tasks_completed change %, income change %, study_time change %
**And** trend arrows (up/down/flat) next to each metric

---

## Cross-Cutting Acceptance Criteria

### AC-CROSS-01: Row Level Security
**Given** a table has RLS enabled
**When** any query is executed
**Then** the RLS policy auth.uid() = user_id shall be enforced
**And** users shall only see and modify their own data
**And** unauthenticated requests shall receive a 401 error

### AC-CROSS-02: PWA Offline Mode
**Given** the user has visited the app at least once
**When** the user loses internet connectivity
**Then** the app shall load from the service worker cache
**And** existing data shall be readable from IndexedDB
**And** create/update actions shall be queued for sync when connectivity returns

### AC-CROSS-03: Onboarding Wizard
**Given** a new user signs up with Google OAuth (onboarding_completed = false)
**When** the user is redirected after auth
**Then** the 5-step onboarding wizard shall display
**And** step progression shall be tracked visually with a progress bar
**And** on completion, onboarding_completed shall be set to true
**And** the first daily briefing shall be triggered immediately

### AC-CROSS-04: Data Export
**Given** the user is on the Settings page
**When** the user clicks "Export All My Data"
**Then** all rows from all 21 tables for this user_id shall be fetched
**And** compiled into a single JSON object
**And** downloaded as "second-brain-export-YYYY-MM-DD.json"

### AC-CROSS-05: Rate Limiting
**Given** the user makes more than 20 AI API calls in one minute
**When** the 21st call is attempted
**Then** the system shall return a 429 Too Many Requests error
**And** include a Retry-After header with the number of seconds to wait

### AC-CROSS-06: Browser Extension Save
**Given** the user is on any webpage
**When** the user clicks the extension icon
**Then** a popup shall display with the current page URL pre-filled
**And** the user selects a category from the dropdown
**And** clicks Save
**And** the data shall be POSTed to Supabase and appear in the app immediately
