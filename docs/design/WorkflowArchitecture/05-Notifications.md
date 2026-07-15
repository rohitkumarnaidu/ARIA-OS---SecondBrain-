## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF05-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part V â€” Notifications Experience

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `NotificationSystem.md` (backend delivery, 25+ types), `InformationArchitecture.md` (notification IA), `09-Settings.md` (notification settings).

---

## Notification UI Anatomy

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#0A0B0F', 'primaryColor': '#13151A', 'primaryBorderColor': '#6366F1', 'primaryTextColor': '#F1F5F9', 'lineColor': '#818CF8', 'secondaryColor': '#1A1D24', 'tertiaryColor': '#00FFA3', 'fontFamily': 'DM Sans'}}}%%
flowchart TD
    A[Event Source] --> B{Check priority + quiet hours + rate limit}
    B --> C[INSERT INTO notifications (Supabase)]
    C --> D{Delivery channel}
    D -->|In-App| E[Realtime push to NotificationBell]
    D -->|Push| F[Web Push API]
    D -->|Email| G[Resend API]
    E --> H[Bell badge count ++]
    E --> I{Is P0/P1?}
    I -->|Yes| J[Show toast slide-in]
    I -->|No| K[Silent update (dashboard only)]
    H --> L[User clicks bell]
    L --> M[Fetch /api/v1/notifications]
    M --> N[Show dropdown grouped by type]
    N --> O[User clicks notification]
    O --> P[Mark as read]
    P --> Q[Navigate to target / open modal]
```

### Notification Dropdown Layout

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Notifications                    [Mark read] â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”                â”‚
â”‚  â”‚ All â”‚ Unreadâ”‚ AI   â”‚Systemâ”‚                â”‚
â”‚  â”‚     â”‚ (5)  â”‚      â”‚      â”‚                â”‚
â”‚  â””â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”˜                â”‚
â”‚                                              â”‚
â”‚  TODAY                                       â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ ðŸ”µ ðŸ”¥ Google STEP â€” 92% match!        â”‚  â”‚
â”‚  â”‚    2m ago Â· @opportunity_agent          â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ âšª ðŸ“‹ Task: Submit DBMS assignment     â”‚  â”‚
â”‚  â”‚    15m ago Â· Due in 2h                  â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  YESTERDAY                                   â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ âšª ðŸ“Š Weekly review is ready            â”‚  â”‚
â”‚  â”‚    8h ago Â· @weekly_review_agent        â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Per-Type Specification

### 5.1 System Notifications

| Property | Value |
|---|---|
| **Priority** | P0 (Critical) / P1 (High) |
| **Delivery** | In-app toast + push (P0), in-app only (P1) |
| **Sound** | Urgent (P0), Subtle (P1) |
| **Grouping** | Single items (never grouped) |

| Type | Trigger | Message | Action |
|---|---|---|---|
| Sync Conflict | Data conflict on sync | "Changes conflict with another device" | Review / Keep theirs / Keep mine |
| Storage Warning | 80% storage used | "Storage almost full" | Open Settings â†’ Data |
| Auth Expired | Token expired | "Session expired" | Re-authenticate |
| Version Update | New feature available | "New update available" | View changelog |
| Backup Complete | Automated backup | "Backup complete" | View backup |
| Automation Failed | Cron job fails | "[Job] failed. Will retry." | View Automation |

### 5.2 AI Notifications

| Property | Value |
|---|---|
| **Priority** | P1 (High) / P2 (Medium) |
| **Delivery** | In-app toast + dashboard bell |
| **Sound** | Subtle (P1), None (P2) |
| **Grouping** | Daily digest if > 3 per day |

| Type | Agent | Message | Action |
|---|---|---|---|
| Briefing Ready | @briefing_agent | "Your morning briefing is ready" | View briefing |
| Weekly Review Ready | @weekly_review_agent | "Your weekly review is ready" | View review |
| Insight Found | @learning_agent | "I noticed a pattern in your sleep" | View insight |
| Memory Saved | @memory_agent | "I remembered something about you" | View memory |
| Study Nudge | @nudge_agent | "Time to study for NPTEL ML" | View course |

### 5.3 Opportunity Notifications

| Property | Value |
|---|---|
| **Priority** | P1 (Hot > 80%) / P2 (Warm 60-80%) / P3 (Cool < 60%) |
| **Delivery** | Push + in-app (P1), in-app only (P2-P3) |
| **Sound** | Urgent (P1), Subtle (P2), None (P3) |
| **Grouping** | "3 new opportunities" summary card |

| Type | Score | Message | Action |
|---|---|---|---|
| Hot Match | > 80% | "ðŸ”¥ Google STEP internship â€” 92% match!" | View â†’ Apply |
| Warm Match | 60-80% | "New hackathon matching your skills" | View |
| Cool Match | < 60% | "1 new opportunity in your area" | View |
| Application Update | Any | "Application status â†’ Interviewing" | View |
| Deadline Approaching | Any | "Application deadline in 3 days" | View |

### 5.4 Project Notifications

| Property | Value |
|---|---|
| **Priority** | P1 (Blockers) / P2 (Milestones) / P3 (Updates) |
| **Delivery** | In-app toast + push (P1), in-app only (P2-P3) |
| **Sound** | Subtle (P1), None (P2-P3) |

| Type | Trigger | Message | Action |
|---|---|---|---|
| Blocker Detected | Project blocker logged | "Blocker on ML Project" | View â†’ Resolve |
| Milestone Due | Milestone due in 3 days | "Milestone due in 3 days" | View |
| Phase Complete | Phase marked complete | "Phase 2 complete!" | View summary |
| New Suggestion | AI finds resource | "Found tutorial for your project" | View resource |

### 5.5 Learning Notifications

| Property | Value |
|---|---|
| **Priority** | P1 (Course danger) / P2 (Nudge) / P3 (Progress) |
| **Delivery** | In-app toast (P1-P2), bell (P3) |
| **Sound** | Subtle (P1), None (P2-P3) |

| Type | Trigger | Message | Action |
|---|---|---|---|
| Course at Risk | Progress < 50% at 75% time | "NPTEL ML is behind schedule" | View â†’ Adjust |
| Daily Study Time | 6 PM daily | "Time for your daily study session" | View course |
| Streak Milestone | 7-day study streak | "7-day study streak! ðŸ”¥" | Celebrate |
| Course Complete | 100% progress | "NPTEL ML complete!" | View â†’ Next |
| Gap Detected | Skill gap identified | "You're missing [skill] for [goal]" | View roadmap |

### 5.6 Success Notifications

| Property | Value |
|---|---|
| **Priority** | P3 (Informational) |
| **Delivery** | In-app toast only |
| **Sound** | None |
| **Grouping** | Never grouped |

| Type | Trigger | Message |
|---|---|---|
| Task Created | Task saved | "Task created" |
| Goal Milestone | Milestone reached | "Milestone: [name] reached!" |
| Habit Streak | 30-day streak | "30-day habit streak! ðŸ”¥" |
| Income Logged | Income recorded | "Income logged: â‚¹X,XXX" |
| Project Complete | Project archived | "Project [name] complete! ðŸŽ‰" |
| Data Synced | Background sync | "All changes synced" |

### 5.7 Warning Notifications

| Property | Value |
|---|---|
| **Priority** | P2 (Warning) |
| **Delivery** | In-app toast + bell |
| **Sound** | Subtle |
| **Grouping** | Stacked by category |

| Type | Trigger | Message | Action |
|---|---|---|---|
| Overdue Tasks | Task > 3 days overdue | "5 overdue tasks need attention" | View overdue |
| Low Sleep Score | Score < 40 for 3 days | "Your sleep score is consistently low" | View sleep |
| Income Target | < 50% at 75% of month | "Income target at risk" | View income |
| Habit Miss Streak | 3+ days missed | "You've missed [habit] for 3 days" | View habit |
| Budget Warning | AI tokens > 80% used | "AI token budget 80% used" | View AI settings |

### 5.8 Critical Notifications

| Property | Value |
|---|---|
| **Priority** | P0 (Critical) |
| **Delivery** | Push + in-app toast + email |
| **Sound** | Urgent |
| **Grouping** | Never grouped |

| Type | Trigger | Message | Action |
|---|---|---|---|
| Data Loss Risk | Sync failure > 5 retries | "Data sync failing. Manual backup needed." | Backup now |
| Security Alert | Suspicious login | "New login from [location]" | Review activity |
| Service Down | Backend unreachable | "Service temporarily unavailable" | Check status |
| Deadline Critical | Task due in < 1 hour | "[Task] due in 45 minutes!" | View task |

---

## Notification UI States

| State | Icon | Treatment |
|---|---|---|
| **Unread** | ðŸ”µ (blue dot) | Bold title + full color |
| **Read** | âšª (gray dot) | Normal weight + dimmed text |
| **Grouped** | ðŸ”µ (count badge) | "3 new opportunities" summary |
| **Expired** | âŒ› (clock) | Grayed + faded (after 7 days) |
| **Dismissed** | â€” | Slide-out animation + undo toast (5s) |
| **Snoozed** | ðŸ”” (bell off) | Clock icon + "Resume at [time]" |
| **Actioned** | âœ… (check) | Green check + action timestamp |
| **Failed** | âŒ (error) | Red warning + retry button |
