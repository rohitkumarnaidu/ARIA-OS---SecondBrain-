# Part VII — AI Agent Experiences

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `19_AI_Instructions.md` (agent framework), `20_Agent.md` (agent specification), `AgentOrchestration.md` (orchestration), `02-FeatureFlows.md` §2.11-2.13 (AI conversation flows).

---

## 7.1 Agent Recommendations

**Trigger:** Agent generates a suggestion for the user
**Display Locations:** Dashboard widget, Chat panel inline, Module page suggestion area, Notification

### Recommendation Card

```
┌──────────────────────────────────────────────┐
│  ✨ ARIA Suggestion                     [X]  │
│                                              │
│  "Based on your goal to learn ML, you        │
│   should start with Andrew Ng's course."     │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ Source: @learning_agent               │  │
│  │ Confidence: 92% match                 │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  [Add to Roadmap] [View Course] [Dismiss]    │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Appearing** | Slide-up from suggestion area + neon glow animation (300ms) |
| **Visible** | Full card with confidence badge, source attribution, action buttons |
| **Accepted** | Green pulse → shrink → "Applied!" confirmation + undo toast |
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
┌──────────────────────────────────────────────┐
│  ARIA is consulting agents...        [Collapse]│
│                                              │
│  ✅ @task_agent     — Tasks analyzed         │
│  ⏳ @memory_agent   — Recalling context...   │
│  ⏳ @sleep_agent    — Checking sleep data... │
│  ⏳ @learning_agent — Finding patterns...    │
│  ❌ @opportunity_agent — Unavailable         │
│                                              │
│  Parallel dispatch: 3 of 4 agents active     │
│  ═══════════╺══════════ 65% complete         │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Idle** | Hidden (collapsed by default) |
| **Dispatching** | "ARIA is consulting [N] agents..." fades in |
| **In Progress** | Per-agent status line: ✅ / ⏳ / ❌ with agent icon |
| **Complete — All OK** | All ✅ → collapse automatically → show result |
| **Partial Failure** | Some ✅ + some ❌ → show available results + note on failures |
| **All Failed** | "ARIA couldn't process your request" + suggestion to retry |
| **Timeline** | Expand to see step-by-step ordering (sequential vs parallel) |

---

## 7.3 Agent Status

**Route:** `/settings/agents` or dashboard widget
**Purpose:** Monitor all agent health, last run, and trigger history

### Status Dashboard

```
┌──────────────────────────────────────────────┐
│  AI Agent Status                  Last Sync  │
│                                              │
│  🟢 @briefing_agent       ✅ 7:02 AM (2.3s) │
│  🟢 @memory_agent         ✅ 7:00 AM (0.8s) │
│  🟡 @opportunity_agent    ⏳ Scanning... (4m)│
│  🔴 @analytics_agent      ❌ Failed (retry 2/3)│
│  ⚪ @career_agent         💤 Not configured  │
│  🟢 @sleep_agent          ✅ 9:30 PM (1.2s) │
│  🟢 @nudge_agent          ✅ 6:00 PM (0.5s) │
│  🟡 @learning_agent       ⏳ Analyzing... (8m)│
│                                              │
│  [Trigger All] [Configure] [View Logs]       │
└──────────────────────────────────────────────┘
```

### Status Indicators

| Icon | State | Meaning | User Action |
|---|---|---|---|
| 🟢 | Online | Last run successful, within expected window | None |
| 🟡 | Running | Currently executing | View current step |
| 🔴 | Error | Last run failed, retry active | View error, manual trigger |
| ⚪ | Disabled | Agent turned off in user preferences | Enable in AI Settings |
| 💤 | Dormant | Configured but no trigger window reached | None |

---

## 7.4 Agent Memory

**Route:** `/memory`
**Purpose:** View, edit, delete, and search AI-stored facts about the user

### Memory Browser

```
┌──────────────────────────────────────────────┐
│  Memory Browser                          🔍  │
│                                              │
│  Filter: [All ▼]  Sort: [Recent ▼]          │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 📌 Preference                          │  │
│  │ "You prefer morning deep work blocks"  │  │
│  │ Source: Chat · June 15 · Confidence: 87%│  │
│  │ [Edit] [Delete] [Incorrect?]           │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 🔍 Pattern                             │  │
│  │ "Productivity drops after 3 PM"        │  │
│  │ Source: @learning_agent · June 14      │  │
│  │ [Edit] [Delete] [View Analysis]        │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Memory Card Anatomy

| Element | Description |
|---|---|
| Icon | 📌 Preference, 🔍 Pattern, 💡 Fact, 🔄 Habit, 📝 Note |
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
| **Editing** | Inline text edit → Save / Cancel |
| **Deleting** | Confirm dialog → delete with undo (30s) |
| **Error** | "Couldn't load memories" + retry button |
| **Search Results** | Filtered list with query highlighted in results |

---

## 7.5 Agent Actions

**Trigger:** ARIA performs an action on behalf of the user (e.g., create task, update goal)
**Display:** Chat panel "Actions" section + status badge

### Action List

```
┌──────────────────────────────────────────────┐
│  ARIA Actions                    [Clear All] │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ ☑ Create task: "Review ML paper"       │  │
│  │    ✅ Done · Undo (28s remaining)      │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ ☑ Update goal: "ML Learning" → +5%     │  │
│  │    ⏳ Updating linked courses...        │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ ☐ Find course: "Neural Networks"       │  │
│  │    ⏳ Queued...                         │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Action States

| State | Icon | Treatment |
|---|---|---|
| **Queued** | ⏳ | Gray spinner + "Waiting..." |
| **Processing** | ⏳ | Animated spinner + "Working..." + current step |
| **Complete** | ✅ | Green check + undo timer (30s countdown) |
| **Failed** | ❌ | Red X + error message + retry button |
| **Requires Approval** | 🔒 | Locked state + "Tap to approve" button |

---

## 7.6 Agent Workflows

**Trigger:** Multi-step agent process (e.g., daily briefing generation, opportunity radar scan)
**Display:** Dedicated workflow progress view (inline expandable)

### Workflow Progress

```
┌──────────────────────────────────────────────┐
│  Daily Briefing Generation                   │
│  ━━━━━━━━━━━━━━━━━━╺━━━━━━━━━ 65%            │
│                                              │
│  Steps:                                      │
│  ✅ 1. Collect tasks due today               │
│  ✅ 2. Get sleep score                       │
│  ✅ 3. Get learning progress                 │
│  ⏳ 4. Generate briefing text (LLM)...       │
│  ⬜ 5. Store briefing                        │
│  ⬜ 6. Deliver notification                  │
│                                              │
│  Elapsed: 4.2s · Est. remaining: 12s         │
│  [Cancel Workflow]                           │
└──────────────────────────────────────────────┘
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
┌──────────────────────────────────────────────┐
│  🔒 ARIA wants to:                           │
│                                              │
│  "Create 5 study tasks from your new         │
│   course schedule for this week."            │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ Preview:                               │  │
│  │ • Mon: Study ML (2h)                   │  │
│  │ • Tue: Study ML (2h)                   │  │
│  │ • Wed: Review assignment (1h)          │  │
│  │ • Thu: Study ML (2h)                   │  │
│  │ • Fri: Practice problems (1.5h)        │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ☐ Remember for next time                    │
│                                              │
│  [Approve] [Modify] [Reject]                  │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Pending** | Modal with preview, action buttons, "Remember" checkbox |
| **Approved** | Modal closes → execute action → success toast |
| **Modified** | Opens edit interface → user adjusts → save → execute |
| **Rejected** | Modal closes → "Got it" toast → optional feedback prompt |
| **Expired** | Auto-dismiss after 24h (configurable in AI Settings) |
| **Remembered** | Future similar actions auto-approved per threshold |

---

## 7.8 Agent Results

**Trigger:** Agent completes its processing
**Display:** Result card in Chat panel / Dashboard widget / Module inline

### Result Card

```
┌──────────────────────────────────────────────┐
│  📊 Learning Analysis                        │
│  @learning_agent · Just now (1.2s)           │
│                                              │
│  "Your productivity is 15% higher on days    │
│   when you sleep 7+ hours."                  │
│                                              │
│  📈 [Productivity vs Sleep chart]            │
│                                              │
│  [View Full Analysis] [Export] [Share]       │
│                                              │
│  Was this helpful?    👍 42    👎 3          │
└──────────────────────────────────────────────┘
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
| 15s - 30s | Background mode + notification | "I'll let you know when ready" → push on complete |
| > 30s | Fallback + graceful degradation | "AI is taking longer than expected. Here's what I can do now:" + algorithmic result |
