## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF07-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part VII â€” AI Agent Experiences

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `19_AI_Instructions.md` (agent framework), `20_Agent.md` (agent specification), `AgentOrchestration.md` (orchestration), `02-FeatureFlows.md` Â§2.11-2.13 (AI conversation flows).

---

## 7.1 Agent Recommendations

**Trigger:** Agent generates a suggestion for the user
**Display Locations:** Dashboard widget, Chat panel inline, Module page suggestion area, Notification

### Recommendation Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  âœ¨ ARIA Suggestion                     [X]  â”‚
â”‚                                              â”‚
â”‚  "Based on your goal to learn ML, you        â”‚
â”‚   should start with Andrew Ng's course."     â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ Source: @learning_agent               â”‚  â”‚
â”‚  â”‚ Confidence: 92% match                 â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  [Add to Roadmap] [View Course] [Dismiss]    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### States

| State | UI Treatment |
|---|---|
| **Appearing** | Slide-up from suggestion area + neon glow animation (300ms) |
| **Visible** | Full card with confidence badge, source attribution, action buttons |
| **Accepted** | Green pulse â†’ shrink â†’ "Applied!" confirmation + undo toast |
| **Dismissed** | Slide-right + fade (200ms) |
| **Loading** | Skeleton card (shimmer, 3 lines) |
| **Error** | "Couldn't generate suggestion" + retry link |
| **Empty** | "No suggestions right now" (periodically refreshes) |

---

## 7.2 Agent Collaboration

**Trigger:** ARIA orchestrator dispatches to multiple agents to fulfill a request
**Display:** Chat panel "Agent Activity" expandable section

### Collaboration Panel

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ARIA is consulting agents...        [Collapse]â”‚
â”‚                                              â”‚
â”‚  âœ… @task_agent     â€” Tasks analyzed         â”‚
â”‚  â³ @memory_agent   â€” Recalling context...   â”‚
â”‚  â³ @sleep_agent    â€” Checking sleep data... â”‚
â”‚  â³ @learning_agent â€” Finding patterns...    â”‚
â”‚  âŒ @opportunity_agent â€” Unavailable         â”‚
â”‚                                              â”‚
â”‚  Parallel dispatch: 3 of 4 agents active     â”‚
â”‚  â•â•â•â•â•â•â•â•â•â•â•â•ºâ•â•â•â•â•â•â•â•â•â• 65% complete         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### States

| State | UI Treatment |
|---|---|
| **Idle** | Hidden (collapsed by default) |
| **Dispatching** | "ARIA is consulting [N] agents..." fades in |
| **In Progress** | Per-agent status line: âœ… / â³ / âŒ with agent icon |
| **Complete â€” All OK** | All âœ… â†’ collapse automatically â†’ show result |
| **Partial Failure** | Some âœ… + some âŒ â†’ show available results + note on failures |
| **All Failed** | "ARIA couldn't process your request" + suggestion to retry |
| **Timeline** | Expand to see step-by-step ordering (sequential vs parallel) |

---

## 7.3 Agent Status

**Route:** `/settings/agents` or dashboard widget
**Purpose:** Monitor all agent health, last run, and trigger history

### Status Dashboard

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  AI Agent Status                  Last Sync  â”‚
â”‚                                              â”‚
â”‚  ðŸŸ¢ @briefing_agent       âœ… 7:02 AM (2.3s) â”‚
â”‚  ðŸŸ¢ @memory_agent         âœ… 7:00 AM (0.8s) â”‚
â”‚  ðŸŸ¡ @opportunity_agent    â³ Scanning... (4m)â”‚
â”‚  ðŸ”´ @analytics_agent      âŒ Failed (retry 2/3)â”‚
â”‚  âšª @career_agent         ðŸ’¤ Not configured  â”‚
â”‚  ðŸŸ¢ @sleep_agent          âœ… 9:30 PM (1.2s) â”‚
â”‚  ðŸŸ¢ @nudge_agent          âœ… 6:00 PM (0.5s) â”‚
â”‚  ðŸŸ¡ @learning_agent       â³ Analyzing... (8m)â”‚
â”‚                                              â”‚
â”‚  [Trigger All] [Configure] [View Logs]       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Status Indicators

| Icon | State | Meaning | User Action |
|---|---|---|---|
| ðŸŸ¢ | Online | Last run successful, within expected window | None |
| ðŸŸ¡ | Running | Currently executing | View current step |
| ðŸ”´ | Error | Last run failed, retry active | View error, manual trigger |
| âšª | Disabled | Agent turned off in user preferences | Enable in AI Settings |
| ðŸ’¤ | Dormant | Configured but no trigger window reached | None |

---

## 7.4 Agent Memory

**Route:** `/memory`
**Purpose:** View, edit, delete, and search AI-stored facts about the user

### Memory Browser

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Memory Browser                          ðŸ”  â”‚
â”‚                                              â”‚
â”‚  Filter: [All â–¼]  Sort: [Recent â–¼]          â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ ðŸ“Œ Preference                          â”‚  â”‚
â”‚  â”‚ "You prefer morning deep work blocks"  â”‚  â”‚
â”‚  â”‚ Source: Chat Â· June 15 Â· Confidence: 87%â”‚  â”‚
â”‚  â”‚ [Edit] [Delete] [Incorrect?]           â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ ðŸ” Pattern                             â”‚  â”‚
â”‚  â”‚ "Productivity drops after 3 PM"        â”‚  â”‚
â”‚  â”‚ Source: @learning_agent Â· June 14      â”‚  â”‚
â”‚  â”‚ [Edit] [Delete] [View Analysis]        â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Memory Card Anatomy

| Element | Description |
|---|---|
| Icon | ðŸ“Œ Preference, ðŸ” Pattern, ðŸ’¡ Fact, ðŸ”„ Habit, ðŸ“ Note |
| Category badge | Preference / Fact / Pattern / Habit |
| Content | The stored memory (AI-generated summary) |
| Source | Which conversation / agent created this |
| Confidence | 0-100% score (shown if < 90%) |
| Actions | Edit, Delete, Feedback ("Incorrect?") |

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No memories yet" + "ARIA learns from your conversations over time" |
| **Loading** | 4 skeleton memory cards (shimmer) |
| **Populated** | Filterable, searchable timeline grouped by category |
| **Editing** | Inline text edit â†’ Save / Cancel |
| **Deleting** | Confirm dialog â†’ delete with undo (30s) |
| **Error** | "Couldn't load memories" + retry button |
| **Search Results** | Filtered list with query highlighted in results |

---

## 7.5 Agent Actions

**Trigger:** ARIA performs an action on behalf of the user (e.g., create task, update goal)
**Display:** Chat panel "Actions" section + status badge

### Action List

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ARIA Actions                    [Clear All] â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ â˜‘ Create task: "Review ML paper"       â”‚  â”‚
â”‚  â”‚    âœ… Done Â· Undo (28s remaining)      â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ â˜‘ Update goal: "ML Learning" â†’ +5%     â”‚  â”‚
â”‚  â”‚    â³ Updating linked courses...        â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ â˜ Find course: "Neural Networks"       â”‚  â”‚
â”‚  â”‚    â³ Queued...                         â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Action States

| State | Icon | Treatment |
|---|---|---|
| **Queued** | â³ | Gray spinner + "Waiting..." |
| **Processing** | â³ | Animated spinner + "Working..." + current step |
| **Complete** | âœ… | Green check + undo timer (30s countdown) |
| **Failed** | âŒ | Red X + error message + retry button |
| **Requires Approval** | ðŸ”’ | Locked state + "Tap to approve" button |

---

## 7.6 Agent Workflows

**Trigger:** Multi-step agent process (e.g., daily briefing generation, opportunity radar scan)
**Display:** Dedicated workflow progress view (inline expandable)

### Workflow Progress

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Daily Briefing Generation                   â”‚
â”‚  â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•ºâ”â”â”â”â”â”â”â”â” 65%            â”‚
â”‚                                              â”‚
â”‚  Steps:                                      â”‚
â”‚  âœ… 1. Collect tasks due today               â”‚
â”‚  âœ… 2. Get sleep score                       â”‚
â”‚  âœ… 3. Get learning progress                 â”‚
â”‚  â³ 4. Generate briefing text (LLM)...       â”‚
â”‚  â¬œ 5. Store briefing                        â”‚
â”‚  â¬œ 6. Deliver notification                  â”‚
â”‚                                              â”‚
â”‚  Elapsed: 4.2s Â· Est. remaining: 12s         â”‚
â”‚  [Cancel Workflow]                           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### States

| State | UI Treatment |
|---|---|
| **Not Started** | Gray progress bar (0%) + "N steps" count |
| **In Progress** | Animated gradient progress + current step highlighted with neon glow |
| **Paused** | Pulsing amber animation + "Paused" label + resume button |
| **Completed** | Green progress bar (100%) + success animation |
| **Failed** | Red mark on failed step + "Failed at step [N]" + retry from failed step |
| **Cancelled** | Faded progress + "Cancelled by user" label |

---

## 7.7 Agent Approvals

**Trigger:** Agent action requires user confirmation (configurable threshold)
**Display:** Approval modal (P0 urgency), Inline chip (P1), Silent notification (P2)

### Approval Modal

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ðŸ”’ ARIA wants to:                           â”‚
â”‚                                              â”‚
â”‚  "Create 5 study tasks from your new         â”‚
â”‚   course schedule for this week."            â”‚
â”‚                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ Preview:                               â”‚  â”‚
â”‚  â”‚ â€¢ Mon: Study ML (2h)                   â”‚  â”‚
â”‚  â”‚ â€¢ Tue: Study ML (2h)                   â”‚  â”‚
â”‚  â”‚ â€¢ Wed: Review assignment (1h)          â”‚  â”‚
â”‚  â”‚ â€¢ Thu: Study ML (2h)                   â”‚  â”‚
â”‚  â”‚ â€¢ Fri: Practice problems (1.5h)        â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                              â”‚
â”‚  â˜ Remember for next time                    â”‚
â”‚                                              â”‚
â”‚  [Approve] [Modify] [Reject]                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### States

| State | UI Treatment |
|---|---|
| **Pending** | Modal with preview, action buttons, "Remember" checkbox |
| **Approved** | Modal closes â†’ execute action â†’ success toast |
| **Modified** | Opens edit interface â†’ user adjusts â†’ save â†’ execute |
| **Rejected** | Modal closes â†’ "Got it" toast â†’ optional feedback prompt |
| **Expired** | Auto-dismiss after 24h (configurable in AI Settings) |
| **Remembered** | Future similar actions auto-approved per threshold |

---

## 7.8 Agent Results

**Trigger:** Agent completes its processing
**Display:** Result card in Chat panel / Dashboard widget / Module inline

### Result Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  ðŸ“Š Learning Analysis                        â”‚
â”‚  @learning_agent Â· Just now (1.2s)           â”‚
â”‚                                              â”‚
â”‚  "Your productivity is 15% higher on days    â”‚
â”‚   when you sleep 7+ hours."                  â”‚
â”‚                                              â”‚
â”‚  ðŸ“ˆ [Productivity vs Sleep chart]            â”‚
â”‚                                              â”‚
â”‚  [View Full Analysis] [Export] [Share]       â”‚
â”‚                                              â”‚
â”‚  Was this helpful?    ðŸ‘ 42    ðŸ‘Ž 3          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Result Types

| Type | Visualization | Actions |
|---|---|---|
| **Insight** | Text paragraph + optional sparkline | View full, share, feedback |
| **Recommendation** | Card with primary CTA | Apply, dismiss, remind later |
| **Analysis** | Chart(s) + bullet summary | Export, save, share |
| **Summary** | Condensed bullet points | Expand, copy, share |
| **Data** | Table / grid | Sort, filter, export CSV |
| **Comparison** | Side-by-side / before-after | Share, save |

---

## 7.9 Agent Intervention Timing

### Timeline-Based UX

| Duration | UX Treatment | User Messaging |
|---|---|---|
| < 500ms | No indicator | Immediate result display |
| 500ms - 2s | Inline spinner (16px, accent color) | Subtle: no text needed |
| 2s - 5s | Skeleton result card (shimmer) | "Working on it..." |
| 5s - 15s | Progress bar + step indicator | "[Agent name] is [current step]..." |
| 15s - 30s | Background mode + notification | "I'll let you know when ready" â†’ push on complete |
| > 30s | Fallback + graceful degradation | "AI is taking longer than expected. Here's what I can do now:" + algorithmic result |
