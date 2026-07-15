# Course Tracker Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-COURSES-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-14 |

---

## Introduction

The Course Tracker helps you manage your online courses across multiple platforms (Udemy, Coursera, NPTEL, YouTube) in one unified view. Track progress, deadlines, and video completion.

## Creating a Course

1. Go to **Courses** from the sidebar
2. Click **Add Course**
3. Fill in the details:

| Field | Description |
|---|---|
| Name | Course title (required) |
| Platform | Udemy, Coursera, NPTEL, YouTube, or other |
| Total Videos | Number of videos/lectures in the course |
| Duration | Estimated total time in hours |
| Deadline | Optional target completion date |
| URL | Link to the course page |
| Notes | Optional description or summary |

## Tracking Progress

- Update the **Videos Completed** count as you progress
- ARIA automatically calculates your completion percentage
- The progress ring shows green (on track), amber (needs attention), or red (behind)
- Set a deadline to receive progress nudges from the AI

## Using the Platform Badge

Each course displays a platform badge showing which provider it belongs to. This helps you quickly identify where to continue learning.

## AI Nudges

The Course Progress Nudge agent runs daily at 6 PM to:
- Check if you met your daily study target
- Alert you if you are behind on course deadlines
- Suggest which course to focus on next

## Managing Courses

### View and Filter Courses

The Courses page provides multiple ways to view your courses:
- **Grid view**: Visual cards with progress rings and platform badges
- **List view**: Compact table with sortable columns
- **Filter by platform**: Show only Udemy, Coursera, NPTEL, or YouTube courses
- **Filter by status**: Active, completed, or archived courses
- **Search**: Find courses by name or platform

### Editing a Course

1. Click on any course card to open the detail view
2. Click **Edit** to update any field
3. Update the **Videos Completed** count as you progress through the course
4. Change the **Status** to completed when finished
5. The progress bar and percentage update automatically

### Course Detail View

The detail view provides a comprehensive look at a single course:
- Progress ring with percentage and animated fill
- Video list with completion tracking per video
- Platform badge and direct link to the course
- Deadline countdown (or overdue warning)
- Notes section for personal takeaways
- Activity log showing progress over time

### Linking Courses to Goals

Courses can be linked to your goals for integrated progress tracking:
1. Open the course edit form
2. In the **Linked Goal** field, select a goal
3. The course progress contributes to the goal's overall progress
4. Related courses appear on the goal's detail page

### Creating Study Tasks from Courses

The system can generate study tasks from your courses:
- Each course can generate a recurring study task (e.g., "Complete 2 NPTEL videos")
- Tasks are created with the course name as a reference
- Completing study tasks automatically updates course progress
- Missed study tasks trigger the missed task checker (every 15 min)

## AI Nudges

The Course Progress Nudge agent runs daily at 6 PM to:
- Check if you met your daily study target (based on your self-defined pace)
- Alert you if you are behind on course deadlines with a reminder notification
- Suggest which course to focus on next based on upcoming deadlines
- Escalate after 3 days of missed study targets via email notification

### Nudge Escalation Levels

| Level | Trigger | Action |
|---|---|---|
| Level 1 | 1 day behind target | In-app notification with gentle reminder |
| Level 2 | 3+ days behind target | Push notification and email |
| Level 3 | Deadline within 7 days and behind | Urgent notification with time estimate |

## Data Model

Each course tracks the following fields in the database:

| Field | Type | Description |
|---|---|---|
| `name` | string | Course title |
| `platform` | string | Platform identifier (udemy, coursera, nptel, youtube, other) |
| `total_videos` | integer | Total number of videos/lectures |
| `videos_completed` | integer | Number of videos finished |
| `progress_pct` | integer | Auto-calculated completion percentage |
| `deadline` | date | Optional target completion date |
| `url` | string | Link to the course page |
| `status` | string | active, completed, archived |
| `linked_goal_id` | uuid | Optional link to a goal |

## Tips

- Break large courses into smaller daily targets (e.g., 2 videos/day)
- Use the deadline feature to get automatic AI reminders
- Link courses to goals for roadmap tracking
- Mark a course as completed when finished to track your learning history
- Set realistic daily targets based on your schedule -- consistency matters more than speed
- Use the platform badge to quickly scan which provider to open
- Archive completed courses to keep the active list focused
- Review course progress during the weekly review for adjustments

## Related Guides

- [Goals & Roadmap](goals.md) -- Link courses to learning goals
- [Tasks](tasks.md) -- Create study tasks from courses
- [Habits](habits.md) -- Build daily learning habits
- [Weekly Review](weekly-review.md) -- Review course progress in the weekly AI summary
- [Resources](resources.md) -- Save supplementary learning materials
