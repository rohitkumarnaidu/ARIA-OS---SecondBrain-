# Time Tracking Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-TIME-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-14 |

---

## Introduction

The Time Tracker helps you log how you spend your time, run Pomodoro sessions, and track deep work periods. View daily stats and breakdowns to understand your productivity patterns.

## Logging a Time Entry

1. Go to **Time** from the sidebar
2. Click **New Entry**
3. Fill in the details:

| Field | Description |
|---|---|
| Category | Study, Work, Personal, Fitness, Leisure, etc. |
| Duration | How long the session lasted |
| Start Time | When you began |
| End Time | When you finished |
| Deep Work | Toggle if this was a focused, uninterrupted session |
| Notes | Optional description of what you worked on |

## Using the Pomodoro Timer

1. Open the **Pomodoro** section on the Time page
2. Set your focus duration (default: 25 minutes)
3. Click **Start** to begin the timer
4. Work until the timer rings, then take a short break (5 minutes)
5. After 4 Pomodoros, take a longer break (15-30 minutes)
6. Each completed Pomodoro is automatically logged as a time entry

## Tracking Deep Work

Mark entries as **Deep Work** when you:
- Work without interruptions for 60+ minutes
- Achieve a state of focused flow
- Complete significant progress on a task

Deep work entries are highlighted in your daily stats and count toward your weekly deep work goal.

## Viewing Daily Stats

The Time page shows:
- Total hours tracked today
- Breakdown by category (pie chart)
- Deep work vs standard time
- Number of Pomodoros completed
- Weekly trend chart

## Managing Time Entries

### Viewing and Filtering

The Time page provides:
- **Daily view**: All entries for today with duration breakdown
- **Weekly view**: Entries across the current week with daily totals
- **Monthly view**: Aggregate statistics for the month
- **Category breakdown**: Pie chart showing time distribution
- **Deep work tracking**: Separate section for deep work sessions
- **Trend chart**: Bar chart showing daily totals over time

### Editing and Deleting Entries

1. Click on any time entry to open the detail view
2. Edit the category, duration, start/end times, or notes
3. Toggle the **Deep Work** flag if the session was focused
4. Delete entries that were logged in error

### Pomodoro Timer Features

The built-in Pomodoro timer includes:
- **Configurable focus duration**: Default 25 minutes, adjustable from 5-60 minutes
- **Short break**: Default 5 minutes between Pomodoros
- **Long break**: Default 15 minutes after 4 Pomodoros
- **Auto-logging**: Completed Pomodoros automatically create time entries
- **Notifications**: Browser notification when timer completes
- **Session counter**: Shows how many Pomodoros completed today
- **Pause and resume**: Pause the timer if interrupted
- **Skip break**: Skip the break and start the next focus session

### Deep Work Tracking

Deep work is defined as focused, uninterrupted work for 60+ minutes. The system helps you track:
- **Auto-detection**: Sessions over 60 minutes prompt you to mark as deep work
- **Deep work goal**: Set a weekly deep work hours target
- **Deep work ratio**: Percentage of total time spent in deep work
- **Deep work streak**: Consecutive days with deep work sessions
- **Best time analysis**: Identifies when you do your best deep work

### Daily Stats View

The daily statistics display:
- Total hours tracked
- Breakdown by category (study, work, personal, fitness, leisure, other)
- Deep work hours and percentage
- Number of Pomodoros completed
- Average session length
- Most productive time block
- Comparison with yesterday and weekly average

## Using Time Data in Weekly Review

The weekly review (A10) uses your time tracking data to:
- Calculate deep work ratio for the week
- Identify which categories consumed the most time
- Compare current week vs previous week trends
- Suggest focus improvements based on patterns
- Highlight time spent on priority vs non-priority activities

## Data Model

| Field | Type | Description |
|---|---|---|
| `category` | string | study, work, personal, fitness, leisure, other |
| `duration_minutes` | integer | Session duration in minutes |
| `start_time` | timestamptz | When the session began |
| `end_time` | timestamptz | When the session ended |
| `is_deep_work` | boolean | Whether marked as deep work |
| `linked_task_id` | uuid | Optional link to a task |
| `notes` | text | Optional session description |

## Tips

- Start the timer before you begin working, not after -- it is more accurate
- Use Pomodoro for tasks that need focused attention and structured breaks
- Be honest about deep work -- genuine focus with no distractions, not just sitting at your desk
- Review time stats during the weekly review to identify patterns and optimize your schedule
- Link time entries to specific tasks for better productivity analysis
- Log even small time blocks (15 min) for accurate daily totals
- Track your most productive hours and schedule important work accordingly

## Related Guides

- [Tasks](tasks.md) -- Link time entries to specific tasks
- [Weekly Review](weekly-review.md) -- Review time usage patterns
- [Dashboard](features-overview.md) -- Time stats appear on dashboard
- [Income](income.md) -- Track hours against income for rate analysis
