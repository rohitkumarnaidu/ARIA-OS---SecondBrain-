# Modules Implementation Specification

## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-MIS-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-13 |
| Classification | Internal — Engineering |
| Target Audience | Frontend Developers |
| Total Pages | 18 module pages across 3 categories |

---

## 1. Executive Summary

ARIA OS ships **18 client-rendered pages** across three categories: **System** (2), **Dashboard** (1), and **Module** (15). Every page follows a consistent template: `'use client'` directive, `useAuth()` hook for session validation, `useState` for local state (or Zustand for tasks), direct Supabase queries (or `fetch` for automation/chat), Framer Motion animations, and design-system component classes. This document specifies the implementation of every page: its components, data flow, state matrix, loading/empty/error/happy paths, and edge cases.

---

## 2. Page Architecture Summary

### 2.1 Common Template

Every page follows this exact structure (derived from 18 page files):

```
1. 'use client' directive
2. useEffect/mount guard: setMounted(true)
3. useAuth() → { user, loading: authLoading }
4. useEffect: if !authLoading && !user → router.push('/login')
5. useEffect: if user → fetchData()
6. Loading guard: if !mounted || authLoading || loading → Spinner
7. Return JSX:
   a. motion.div header (title + subtitle + action button)
   b. Stats grid (2-6 cards with computed metrics)
   c. Content list/grid with AnimatePresence
   d. Empty state (conditional, icon + message + CTA)
   e. Add/Edit modal (AnimatePresence, fixed overlay)
```

### 2.2 Data Source Decision Tree

```
Page needs realtime cross-page consistency?
├─ YES → Zustand store
│   ├─ tasks → useTaskStore (fetchTasks, addTask, updateTask, deleteTask, completeTask)
│   └─ dashboard → reads useTaskStore state (read-only consumer)
└─ NO → Local useState + direct Supabase queries
    ├─ courses, habits, goals, sleep, ideas, income, projects
    ├─ resources, opportunities, youtube, academics, time
    └─ Special cases:
        ├─ chat → supabase + fetch(/api/chat) + demo fallback
        └─ automation → fetch() to backend API endpoints
```

### 2.3 Data Fetching Pattern Comparison

| Pattern | Pages | Pros | Cons |
|---|---|---|---|
| Zustand store | tasks, dashboard | Cross-page consistency, cache, CRUD methods | Higher setup cost |
| Direct Supabase | 12 pages | Simpler, no boilerplate | No cache, manual refetch |
| `fetch()` API | automation, chat | Backend processing | CORS, error handling |
| Mixed | chat | Graceful degradation | Two code paths to maintain |

### 2.4 State Variable Catalog

| Variable | Type | Used By | Purpose |
|---|---|---|---|
| `mounted` | `boolean` | All pages | Prevent hydration mismatch |
| `loading` | `boolean` | All pages | Data fetch indicator |
| `showAddModal` | `boolean` | CRUD pages | Toggle add form modal |
| `selectedIdea` | `Idea \| null` | ideas | Detail modal state |
| `activeTimer` | `TimeEntry \| null` | time | Running timer session |
| `elapsed` | `number` | time | Timer display seconds |
| `pomodoroMode` | `boolean` | time | Pomodoro toggle |
| `pomodoroTimeLeft` | `number` | time | Countdown seconds |
| `filter` | `string` | opportunities | Category filter |
| `results` | `any \| null` | automation | API response display |
| `enabledAutomations` | `Record` | automation | Toggle switches |
| `showIdleWarning` | `boolean` | time | Idle detection |
| `focusHours` | `array` | time | Peak hour analysis |

---

## 3. System Pages

### 3.1 Root `/` (`app/page.tsx`)

| Property | Value |
|---|---|
| Lines | 30 |
| Type | Redirect |
| State | 1: `loading` from `useAuth()` |

**Purpose:** Entry point — redirects authenticated users to `/dashboard`, unauthenticated users to `/login`.

**Data Flow:**
```
useAuth() → { user, loading }
  ├─ loading=true → render spinner
  ├─ loading=false && user → router.push('/dashboard')
  └─ loading=false && !user → router.push('/login')
```

**States:**

| State | Render | Behavior |
|---|---|---|
| Loading | `Loader2` spinner centered | Momentary flash while Supabase session resolves |
| Authenticated | — | Redirect to `/dashboard` |
| Unauthenticated | — | Redirect to `/login` |

**Edge Cases:**
- Session token expired → Supabase returns `null`, user redirected to `/login`
- Direct URL access → Instant redirect, no visible UI

### 3.2 Login `/login` (`app/login/page.tsx`)

| Property | Value |
|---|---|
| Lines | 119 |
| Type | Auth entry |
| State | 1: `mounted` |

**Purpose:** Google OAuth authentication via Supabase. Presents brand identity with 3D background.

**Data Flow:**
```
Click "Continue with Google"
  └─ supabase.auth.signInWithOAuth({ provider: 'google', redirectTo: '/dashboard' })
      └─ OAuth popup → Supabase callback → session → router.push('/dashboard')
```

**Components:**
| Element | Detail |
|---|---|
| Background | `ThreeBackground` (Three.js animated 3D scene) |
| Brand | Brain icon + "ARIA OS" + "Your Second Brain" |
| Stats | 3 feature badges: "15+ Modules", "AI-Powered", "100% Free" |
| Auth | Google OAuth button with `FcGoogle` icon |
| Animation | Framer Motion fade-in, staggered children, floating particles CSS |

**States:**

| State | Render |
|---|---|
| Initial | Full login page with 3D background |
| OAuth in progress | Browser popup (handled by Supabase) |
| Post-login | Redirect to `/dashboard` |
| Error | (Not handled — Supabase redirect handles errors) |

---

## 4. Dashboard

### 4.1 Dashboard `/dashboard` (`app/dashboard/page.tsx`)

| Property | Value |
|---|---|
| Lines | 344 |
| State Management | Zustand (read-only consumer of `useTaskStore`) |
| Data Source | `useTaskStore` methods + computed metrics |

**Purpose:** Aggregate overview of all modules — tasks due today, task completion rate, AI briefings.

**Data Flow:**
```
useEffect:
  useTaskStore.getState().fetchTasks()  // populate store
  Set greeting based on hour of day
  Set quick stats from store state
```

**Component Breakdown:**
| Section | Components | State |
|---|---|---|
| Header | Greeting ("Good Morning"), date, avatar | Computed |
| ARIA Pick | AI-generated task of the day | Zustand (tasks) |
| Stats Row | Total tasks, Completed %, Due today, Streak | Computed from Zustand |
| Quick Actions | 4 action buttons (task, course, habit, idea) | Navigation |
| Today's Tasks | Task list from store, limited to 5 | Zustand filter |
| Recent Activity | Placeholder section | Static |

**State Matrix:**
| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading \|\| !tasks.length` | Pulse spinner |
| Empty | No tasks in store | "No tasks yet" with CTA |
| With data | Tasks exist | Full dashboard grid |
| Greeting variations | Hour-based | "Good Morning/Afternoon/Evening" |

**Edge Cases:**
- No tasks → ARIA Pick section shows "Create your first task to get an ARIA pick"
- All tasks completed → Stats show 100%, confetti pulse on completion rate
- Store empty after mount → Brief flash of loading state

---

## 5. Task Module

### 5.1 Tasks `/tasks` (`app/tasks/page.tsx`)

| Property | Value |
|---|---|
| Lines | 587 |
| State Management | Zustand (`useTaskStore`) |
| Data Source | `taskStore.ts` — Supabase CRUD via Zustand actions |
| Complexity | Highest — filters, search, multi-modal, priority system |

**Purpose:** Full task management — CRUD, priority levels, status pipeline, search, filtering, dependencies.

**Interface:**
```typescript
interface Task {
  id: string
  title: string
  description?: string
  priority: 'urgent' | 'high' | 'medium' | 'low'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  due_date?: string
  goal_id?: string
  created_at: string
}
```

**Zustand Store Actions:**
| Action | Supabase Call | State Update |
|---|---|---|
| `fetchTasks()` | `select *` | Replaces `tasks[]` |
| `addTask(task)` | `insert` | Prepends to `tasks[]` |
| `updateTask(id, data)` | `update` | Maps over array |
| `deleteTask(id)` | `delete` | Filters out |
| `completeTask(id)` | `update status=completed` | Maps + status change |

**State Variables (page-local):**
| Variable | Type | Purpose |
|---|---|---|
| `searchQuery` | `string` | Text search filter |
| `statusFilter` | `string` | Status tab filter |
| `priorityFilter` | `string` | Priority dropdown filter |
| `sortBy` | `string` | Sort field |
| `showAddModal` | `boolean` | Add task modal |
| `editingTask` | `Task \| null` | Edit modal data |
| `showDeleteConfirm` | `string \| null` | Delete confirmation |

**Data Flow:**
```
User opens /tasks
  ├─ useAuth() → session check
  ├─ useTaskStore.getState().fetchTasks() → populate store
  ├─ Apply filters/search from local state
  └─ Render filtered tasks with AnimatePresence

User creates task
  ├─ Form validation (title required, priority defaults to 'medium')
  ├─ useTaskStore.getState().addTask({...})
  ├─ Supabase INSERT → store prepends
  └─ Toast: "Task created"

User completes task
  ├─ Checkbox toggle
  ├─ useTaskStore.getState().completeTask(id)
  ├─ Animate exit (scale: 0.9 + opacity: 0)
  └─ Toast: "Task completed"
```

**States:**

| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading \|\| loading` | Animated pulse spinner with ring |
| Empty | `tasks.length === 0` | `ClipboardList` icon + "No tasks yet" + CTA |
| Filtered empty | No tasks match filters | `Search` icon + "No tasks match" + "Clear filters" |
| With data | Tasks exist | Grouped by priority/status, stagger animation |
| Editing | `editingTask !== null` | Modal with pre-filled form |
| Deleting | `showDeleteConfirm !== null` | Confirmation dialog |

**Filter Pipeline:**
```
allTasks
  ├─ searchQuery ? title.includes(query) : all
  ├─ statusFilter !== 'all' ? status === filter : all
  ├─ priorityFilter !== 'all' ? priority === filter : all
  └─ sortBy === 'due_date' ? sort by date : sort by priority weight
```

**Priority Color System:**
| Priority | Badge Class | Icon Color | Weight |
|---|---|---|---|
| Urgent | `priority-urgent` (bg-red) | `text-accent-error` | 40 |
| High | `priority-high` (bg-orange) | `text-accent-warning` | 30 |
| Medium | `priority-medium` (bg-blue) | `text-accent-primary` | 20 |
| Low | `priority-low` (bg-gray) | `text-text-muted` | 10 |

**Error Handling:**
```typescript
// Every store action wraps Supabase in try/catch
try {
  const { data, error } = await supabase.from('tasks').insert(task).select()
  if (error) throw error
  // Success path
} catch (err) {
  console.error('[Tasks] CRUD failed:', err)
  // Optimistic update with rollback
}
```

---

## 6. Content Modules (Standard CRUD Pattern)

The following 8 modules share a near-identical pattern: 5-phase lifecycle, direct Supabase queries, local `useState`, and a consistent component layout.

### 6.1 Courses `/courses` (409 lines)

| Property | Value |
|---|---|
| Table | `courses` |
| Stats | Total, Active, Completed, Progress % |
| Key UI | Progress bars, semester grouping |
| Icon | `BookOpen` |

### 6.2 Goals `/goals` (418 lines)

| Property | Value |
|---|---|
| Table | `goals` |
| Stats | Active, Completed, At Risk |
| Key UI | Roadmap visualization, milestone checkboxes |
| Icon | `Target` |
| Special | Imports `RoadmapEditor` (ReactFlow component) |

### 6.3 Habits `/habits` (296 lines)

| Property | Value |
|---|---|
| Tables | `habits` + `habit_logs` |
| Stats | Active, Streak (max), Today (completed count) |
| Key UI | Weekly calendar grid, streak counter, check-in toggle |
| Icon | `Moon` |

### 6.4 Sleep `/sleep` (209 lines)

| Property | Value |
|---|---|
| Table | `sleep_logs` |
| Stats | Avg duration, Sleep score, Debt hours |
| Key UI | Sleep score gauge, weekly trend, bedtime suggestion |
| Icon | `Moon` (duplicate) |

### 6.5 Income `/income` (213 lines)

| Property | Value |
|---|---|
| Table | `income_entries` |
| Stats | This Month, Total Earned, Total Hours, Avg Rate |
| Key UI | Income list with hourly rate, source badges |
| Icon | `Wallet` |

### 6.6 Projects `/projects` (242 lines)

| Property | Value |
|---|---|
| Table | `projects` |
| Stats | Per-phase counts (6 phases) |
| Key UI | Phase selector, blocker system, GitHub/Live links |
| Icon | `FolderKanban` |
| Special | Blockers (add/resolve), phase state machine |

### 6.7 Ideas `/ideas` (399 lines)

| Property | Value |
|---|---|
| Table | `ideas` |
| Stats | Per-status counts (5 statuses) |
| Key UI | Pipeline grid, detail modal with status update |
| Icon | `Lightbulb` |
| Special | Dual modals (add + detail), status pipeline |

### 6.8 Resources `/resources` (270 lines)

| Property | Value |
|---|---|
| Table | `resources` |
| Stats | Active, Archived, Total |
| Key UI | Tag badges, type filters, external links |
| Icon | `FileText` |
| Special | Tag system (comma-separated input), archive toggle |

### 6.9 Common 5-Phase Lifecycle

Every standard CRUD module follows this exact lifecycle:

```
Phase 1: MOUNT
  useEffect → setMounted(true)
  useEffect → auth check → fetchData()
  └─ fetchData:
      1. setLoading(true)
      2. supabase.from(table).select('*').order('created_at', { ascending: false })
      3. if (data) setItems(data)
      4. setLoading(false)

Phase 2: ADD
  handleAdd:
    1. Validation (title.trim() required, type-specific rules)
    2. supabase.from(table).insert(data)
    3. Close modal, reset form
    4. fetchData() // full refetch

Phase 3: UPDATE
  handleUpdate:
    1. supabase.from(table).update(data).eq('id', id)
    2. setItems(items.map(i => i.id === id ? updated : i))

Phase 4: DELETE
  handleDelete:
    1. supabase.from(table).delete().eq('id', id)
    2. setItems(items.filter(i => i.id !== id))

Phase 5: REFETCH (used after add, sometimes after update/delete)
  fetchData() — full select
```

### 6.10 Common Component Structure

```typescript
// Header
<motion.div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold text-gradient">{title}</h1>
    <p className="text-text-secondary">{subtitle}</p>
  </div>
  <button className="btn btn-primary flex items-center gap-2">
    <Plus size={20} /> {actionLabel}
  </button>
</motion.div>

// Stats Grid (2-6 cards)
<motion.div className="grid grid-cols-{N} gap-4">
  {stats.map((stat, i) => (
    <motion.div
      key={stat.label}
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: i * 0.1 }}
    >
      <div className="text-2xl font-bold text-text-primary">{stat.value}</div>
      <div className="text-text-secondary text-sm">{stat.label}</div>
    </motion.div>
  ))}
</motion.div>

// Content List/Grid with AnimatePresence
<motion.div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <AnimatePresence mode="popLayout">
    {items.map(item => (
      <motion.div
        key={item.id}
        layout
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
      >
        {/* Card content */}
      </motion.div>
    ))}
  </AnimatePresence>
</motion.div>

// Empty State (conditional)
{items.length === 0 && (
  <motion.div className="text-center py-12">
    <Icon size={48} className="text-text-muted mx-auto mb-3" />
    <p className="text-text-secondary">No items yet</p>
  </motion.div>
)}

// Add Modal (AnimatePresence)
<AnimatePresence>
  {showAddModal && (
    <motion.div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <motion.div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
        {/* Form fields */}
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

---

## 7. Opportunity Radar

### 7.1 Opportunities `/opportunities` (`app/opportunities/page.tsx`)

| Property | Value |
|---|---|
| Lines | 191 |
| Table | `opportunities` |
| Stats | New, Applied, Accepted, Total |
| Key UI | Type icons, filter tabs, status dropdown |
| Icon | `Radar` |

**Unique Features:**
- **Type icon mapping:** `{ internship: Briefcase, hackathon: Code, open_source: Code, fellowship: Heart, freelance: DollarSign, competition: Trophy }`
- **Filter bar:** 7 filter buttons (All + 6 types)
- **Status pipeline:** new → saved → applied → rejected → accepted

**State Variables:**
| Variable | Type | Purpose |
|---|---|---|
| `filter` | `string` | Type filter (default `'all'`) |
| `showAddModal` | `boolean` | Add form toggle |
| `newOpp` | object | Form state |

**Data Flow:**
```
fetchOpportunities:
  supabase.from('opportunities').select('*').order('created_at', { ascending: false })

handleAdd:
  Validation: title AND url required
  supabase.from('opportunities').insert({ ...newOpp, status: 'new' })
  fetchOpportunities() // full refetch

filtered = filter === 'all' ? opportunities : opportunities.filter(o => o.opportunity_type === filter)
```

**Error Handling:**
- No try/catch on Supabase calls
- No `.select()` after insert — relies on full refetch

---

## 8. Time Tracker

### 8.1 Time `/time` (`app/time/page.tsx`)

| Property | Value |
|---|---|
| Lines | 348 |
| Table | `time_entries` |
| Stats | Today Total, Deep Work, Sessions |
| Key UI | Live timer, Pomodoro mode, idle detection, peak focus hours |
| Icon | `Clock` |
| Complexity | Highest after tasks — 6 `useState`, 4 `useEffect`, `useRef` |

**Unique Features:**
1. **Live timer:** `setInterval` updates `elapsed` every second from `activeTimer.start_time`
2. **Pomodoro mode:** 25 min work / 5 min break cycle with auto-switch
3. **Idle detection:** Warns after 15 min inactivity via `lastActivity` timestamp
4. **Deep work auto-tagging:** Sessions >= 90 min auto-labeled as deep work
5. **Peak focus hours:** Computes top 5 productive hours from entry data

**State Variables:**
| Variable | Type | Purpose |
|---|---|---|
| `entries` | `TimeEntry[]` | All time entries |
| `activeTimer` | `TimeEntry \| null` | Currently running session |
| `elapsed` | `number` | Seconds since timer start |
| `pomodoroMode` | `boolean` | Pomodoro toggle |
| `pomodoroPhase` | `'work' \| 'break'` | Current phase |
| `pomodoroTimeLeft` | `number` | Seconds remaining |
| `showIdleWarning` | `boolean` | Idle alert visibility |
| `lastActivity` | `number` | Timestamp of last activity |
| `focusHours` | `{hour, count}[]` | Peak hours analysis |

**Data Flow:**
```
Start timer:
  supabase.from('time_entries').insert({ start_time: now, description, is_deep_work: false })

Stop timer:
  duration = (endTime - startTime) / 60000
  isDeepWork = duration >= 90
  supabase.from('time_entries').update({ end_time, duration_minutes, is_deep_work })

Pomodoro:
  setInterval → decrement pomodoroTimeLeft
  When 0 → switch phase (25m ↔ 5m)

Idle detection:
  Every second while timer active → if (now - lastActivity > 15min) → showIdleWarning

Peak hours:
  Reduce entries → group by hour → sum deep work minutes → sort descending → top 5
```

**States:**

| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading \|\| loading` | Spinner with pulse ring |
| Timer stopped | `activeTimer === null` | "Start Timer" play button |
| Timer running | `activeTimer !== null` | Live elapsed display + "Stop" square button |
| Pomodoro on | `pomodoroMode === true` | Gradient card with countdown |
| Idle detected | `showIdleWarning === true` | Yellow warning with "I'm still working" button |
| Peak hours | `focusHours.length > 0` | Horizontal scrollable hour cards |
| Empty history | `recentEntries.length === 0` | "No sessions yet" |

**Edge Cases:**
- Timer across page refresh → Session stored in Supabase, resumes on mount
- Multiple browser tabs → Each tab has independent timer instance
- Deep work at exactly 89:59 → Not tagged as deep work (threshold is >= 90)

---

## 9. Chat

### 9.1 Chat `/chat` (`app/chat/page.tsx`)

| Property | Value |
|---|---|
| Lines | 320 |
| Tables | `chat_messages` (read) |
| Data Source | Supabase (history) + `fetch('/api/chat')` (AI) + demo fallback |
| Key UI | Message list, input bar, streaming-ready layout, demo responses |

**Unique Features:**
- **Dual data path:** Reads messages from Supabase, sends new messages to FastAPI `/api/chat`
- **Demo fallback:** If `fetch()` fails, falls back to `getDemoResponse()` — hardcoded keyword matcher
- **Message types:** User messages and AI assistant messages with distinct styling

**State Variables:**
| Variable | Type | Purpose |
|---|---|---|
| `messages` | `Message[]` | Chat history |
| `input` | `string` | Current message input |
| `isLoading` | `boolean` | AI response pending |

**Data Flow:**
```
Fetch history:
  supabase.from('chat_messages').select('*').order('created_at', { ascending: true }).limit(50)

Send message:
  1. Append user message to local state
  2. Fetch POST /api/chat { message, userId }
  3. On success → append AI response
  4. On failure → getDemoResponse(input) → append fallback response
  5. Save user + AI messages to Supabase chat_messages table

Demo fallback:
  getDemoResponse(input) → keyword matching → canned response
  Example: "task" → returns task-related suggestion
  Example: "sleep" → returns sleep recommendation
  Default: "I'm your ARIA assistant..."
```

**Message Interface:**
```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}
```

**States:**

| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading \|\| loading` | Spinner |
| Empty | `messages.length === 0` | Brand intro + suggestion chips |
| Typing | User is typing | Input bar with send button |
| AI generating | `isLoading === true` | "Thinking..." indicator |
| AI response | Response received | Animated message bubble |
| Error | fetch fails | Demo fallback response (silent) |

**Edge Cases:**
- Empty input → Button disabled
- Long messages → Scrollable container, no hard truncation
- Network error during send → Message saved locally, demo fallback returned
- Multiple rapid sends → Each send awaits previous (sequential processing)

---

## 10. Automation Center

### 10.1 Automation `/automation` (`app/automation/page.tsx`)

| Property | Value |
|---|---|
| Lines | 280 |
| Data Source | `fetch()` to backend API endpoints |
| Key UI | Automation cards, toggle switches, schedule list, results panel |

**Purpose:** Manual trigger for 6 AI automations + settings panel.

**Automation List:**
| ID | Name | Schedule | API Endpoint |
|---|---|---|---|
| `briefing` | Daily Briefing | 7 AM daily | `/api/automation/trigger/briefing` |
| `radar` | Opportunity Radar | 6 AM daily | `/api/automation/trigger/radar` |
| `weekly` | Weekly Review | Sunday 8 PM | `/api/automation/trigger/weekly-review` |
| `sleep_analysis` | Sleep Analysis | On-demand | `/api/automation/trigger/sleep-analysis` |
| `sleep_bedtime` | Bedtime Suggestion | On-demand | `/api/automation/trigger/sleep-bedtime` |
| `nudges` | Course & Habit Nudges | 6 PM daily | `/api/automation/trigger/nudges` |

**Data Flow:**
```
Run automation:
  1. setRunning(automationId) → card shows spinner
  2. fetch(endpoint)
  3. Parse JSON response
  4. setResults(data) → results panel appears
  5. setRunning(null) → card restores button

Toggle automation:
  setEnabledAutomations(prev => ({ ...prev, [id]: !prev[id] }))
  // NOTE: This is UI-only — no backend persistence for toggle state
```

**States:**

| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading` | Pulse spinner |
| Idle | All automations ready | "Run Now" buttons |
| Running | `running === automationId` | Spinning icon + "Running..." |
| Success | `results.status === 'success'` | Green-bordered result card with JSON |
| Error | `results.status === 'error'` | Red-bordered result card with error |
| Disabled | `enabledAutomations[id] === false` | Grayed button with `cursor-not-allowed` |

**Edge Cases:**
- API unreachable → catch block sets `{ status: 'error', message: 'Failed to run automation' }`
- Toggle state not persisted → Refreshing page resets all toggles to `true`
- Rapid clicks → Button disabled while running, prevents double-trigger

---

## 11. YouTube Vault

### 11.1 YouTube `/youtube` (`app/youtube/page.tsx`)

| Property | Value |
|---|---|
| Lines | 207 |
| Table | `videos` |
| Stats | To Watch, Watched, Total Saved |
| Key UI | Thumbnail cards, status toggle, YouTube URL parser |
| Icon | `Youtube` |

**Unique Features:**
- **URL parser:** `extractVideoId(url)` extracts YouTube video ID via regex
- **Auto-thumbnail:** Constructs `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`
- **Status toggle:** Single button cycles between `pending` ⇄ `watched`

**Data Flow:**
```
Add video:
  1. Extract videoId from URL
  2. Generate thumbnail URL
  3. supabase.from('videos').insert({ url, title, thumbnail_url, status: 'pending' })

Toggle status:
  supabase.from('videos').update({ status: status === 'watched' ? 'pending' : 'watched' })
```

**States:**

| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading \|\| loading` | Pulse ring spinner |
| Empty | `videos.length === 0` | YouTube icon + "No videos saved yet" |
| With videos | Videos exist | Thumbnail cards grid |
| Adding | Modal open | URL + Title form |

**Edge Cases:**
- Invalid YouTube URL → `extractVideoId` returns `null`, thumbnail is `null`, card renders without image
- Duplicate URL → No dedup — multiple entries allowed
- Title not provided → Auto-generates "Video {N}"

---

## 12. Academic Planner

### 12.1 Academics `/academics` (`app/academics/page.tsx`)

| Property | Value |
|---|---|
| Lines | 454 |
| Tables | `subjects` + `marks` |
| Stats | Subjects, Marks Logged, CGPA |
| Key UI | Subject cards with progress bars, mark logging, at-risk alerts, exam countdown |
| Icon | `GraduationCap` |
| Complexity | Highest custom business logic — CGPA calculation, grade points, projections |

**Unique Features:**
1. **Dual-table data:** Subjects + Marks fetched via `Promise.all`
2. **CGPA calculation:** Grade point system (10-point scale based on percentage)
3. **Projected CGPA:** At-risk subjects reduce projection by 0.2
4. **At-risk detection:** Subjects with average < 40% shown in red alert
5. **Exam countdown:** Days until next exam, sorted ascending
6. **Progress color coding:** `>= 60% green`, `>= 40% yellow`, `< 40% red`

**CGPA Algorithm:**
```typescript
calculateCGPA():
  for each subject:
    avg = getSubjectAverage(subject.id) // percentage from all marks
    gradePoint = map percentage to 0-10 scale
    totalPoints += gradePoint * credits
    totalCredits += credits
  return totalPoints / totalCredits

getGradePoint(percentage):
  >= 90 → 10
  >= 80 → 9
  >= 70 → 8
  >= 60 → 7
  >= 50 → 6
  >= 40 → 5
  < 40  → 0
```

**Data Flow:**
```
fetchData():
  Promise.all([
    supabase.from('subjects').select('*').order('name'),
    supabase.from('marks').select('*').order('date', { ascending: false })
  ])

Add subject:
  supabase.from('subjects').insert(newSubject)
  fetchData() // full refetch

Log marks:
  supabase.from('marks').insert({ ...newMark, subject_id: selectedSubject })
  fetchData() // full refetch (recalculates all averages)
```

**States:**

| State | Condition | Render |
|---|---|---|
| Loading | `!mounted \|\| authLoading \|\| loading` | Pulse spinner with ring |
| Empty | `subjects.length === 0` | GraduationCap icon + "No subjects yet" + CTA |
| At risk | Any subject avg < 40% | Red alert banner with subject names + percentages |
| Exams upcoming | Any exam_date in future | Countdown cards (days until exam) |
| With data | Subjects exist | Subject grid with progress bars |
| Adding subject | Modal open | Name, Code, Credits, Target Marks form |
| Logging marks | Modal open | Subject select, Type dropdown, Marks fields |

**Edge Cases:**
- No marks logged for a subject → Average defaults to 0% → Shows at-risk (red)
- All subjects have 0 credits → Division by zero guard: `totalCredits > 0`
- Past exam dates → Filtered out by `s.days > 0` check
- Subject deleted → Associated marks become orphaned (no cascade delete shown)

---

## 13. Loading Spinner Variants

Despite all pages showing a spinner during loading, each uses a slightly different animation implementation:

| Variant | Pages | Implementation |
|---|---|---|
| **Pulse ring + spin** | time, projects, academics, resources, ideas | Outer pulse ring + inner spinning border |
| **Simple spin ring** | opportunities, youtube, income, habits | `border-2 border-accent-primary border-t-transparent rounded-full animate-spin` |
| **Pulse glow ring** | courses, goals, sleep, chat | `animate-pulse-glow` on a rounded-full div |
| **Rotating motion div** | ideas, dashboard | `<motion.div animate={{ rotate: 360 }}>` |
| **Loader2 icon** | `/` (root) | `<Loader2 className="animate-spin" />` |
| **Pulse + scale** | automation | `<motion.div animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}>` |

---

## 14. Modal Patterns

All modals follow the same structure with minor variations:

```typescript
<AnimatePresence>
  {showModal && (
    <motion.div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={() => setShowModal(false)}  // Close on backdrop click
    >
      <motion.div
        className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={e => e.stopPropagation()}  // Prevent close on inner click
      >
        {/* ... form content ... */}
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

**Modal Variants:**
| Page | Modal Size | Has backdrop click | Has X button | Special |
|---|---|---|---|---|
| tasks | `max-w-md` | Yes | Yes | Delete confirmation modal |
| courses | `max-w-md` | Yes | Yes | — |
| habits | `max-w-md` | Yes | Yes | — |
| goals | `max-w-lg` | Yes | Yes | RoadmapEditor integration |
| ideas | `max-w-md` + `max-w-lg` | Yes | Yes | Dual modals (add + detail) |
| projects | `max-w-md` | Yes | Yes | Spring animation transition |
| resources | `max-w-md` | Yes | Yes | `motion.button` on close |
| sleep | `max-w-md` | Yes | Yes | — |
| income | `max-w-md` | Yes | Yes | Grid layout inside form |
| opportunities | `max-w-md` | Yes | Yes | Clean card variant |
| youtube | `max-w-md` | No backdrop click | Yes | — |
| academics | `max-w-md` | Yes | Yes | `z-modal` class, `aria-modal` |

---

## 15. Animation Pattern Reference

| Animation | Implementation | Used By |
|---|---|---|
| Header fade-in | `initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}` | All pages |
| Stats stagger | `transition={{ delay: index * 0.1 }}` | All pages |
| Card pop-in | `initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}` | All list pages |
| Layout popLayout | `AnimatePresence mode="popLayout"` | tasks, courses, ideas, etc. |
| Stagger children | `containerVariants` with `staggerChildren: 0.05` | projects, automation |
| Hover spring | `whileHover={{ scale: 1.02 }} transition={{ type: 'spring', stiffness: 400 }}` | ideas, resources, income |
| Tap feedback | `whileTap={{ scale: 0.98 }}` | income, resources |
| Modal spring | `transition={{ type: 'spring', duration: 0.3 }}` | projects |
| Progress bar | `initial={{ width: 0 }} animate={{ width: X% }}` | courses, academics |
| Exit animation | `exit={{ opacity: 0, scale: 0.9 }}` | All CRUD lists |
| Slide from left | `initial={{ opacity: 0, x: -20 }}` | income, time |

---

## 16. Page Size & Complexity Ranking

| Rank | Page | Lines | State Count | Data Sources | Unique Complexity |
|---|---|---|---|---|---|
| 1 | tasks | 587 | 6 | Zustand + Supabase | Filters, search, multi-modal, priority system |
| 2 | academics | 454 | 7 | Supabase (2 tables) | CGPA math, dual-table, at-risk, countdown |
| 3 | goals | 418 | 5 | Supabase | RoadmapEditor, milestones |
| 4 | courses | 409 | 5 | Supabase | Progress bars, semester grouping |
| 5 | ideas | 399 | 6 | Supabase | Dual modals, status pipeline |
| 6 | dashboard | 344 | 3 | Zustand (read) | Aggregation, greeting, ARIA pick |
| 7 | time | 348 | 9 | Supabase | Live timer, pomodoro, idle detection, peak hours |
| 8 | chat | 320 | 3 | Supabase + API + fallback | Mixed data path, demo fallback |
| 9 | habits | 296 | 5 | Supabase (2 tables) | Calendar grid, streak calc |
| 10 | automation | 280 | 3 | fetch() API | 6 automation endpoints, toggle UI |
| 11 | resources | 270 | 5 | Supabase | Tag system, archive |
| 12 | projects | 242 | 5 | Supabase | Phase state machine, blocker system |
| 13 | income | 213 | 4 | Supabase | Hourly rate calc, form grid |
| 14 | sleep | 209 | 4 | Supabase | Score gauge, contextual suggestions |
| 15 | youtube | 207 | 4 | Supabase | URL parser, auto-thumbnails |
| 16 | opportunities | 191 | 5 | Supabase | Type icons, filter bar |
| 17 | login | 119 | 1 | Supabase OAuth | 3D background, brand identity |
| 18 | / (root) | 30 | 1 | None | Redirect-only |

**State Count Key:** `mounted`, `loading`, `data[]`, `showAddModal`, + module-specific states.

---

## 17. Cross-Cutting Concerns

### 17.1 Error Handling Coverage

| Page | try/catch | Error UI | Silent Fail |
|---|---|---|---|
| tasks | ✅ (in store) | None | No |
| dashboard | ❌ | None | Yes |
| courses | ❌ | None | Yes |
| habits | ❌ | None | Yes |
| goals | ❌ | None | Yes |
| ideas | ❌ | None | Yes |
| income | ❌ | None | Yes |
| projects | ❌ | None | Yes |
| resources | ❌ | None | Yes |
| opportunities | ❌ | None | Yes |
| sleep | ❌ | None | Yes |
| time | ❌ | None | Yes |
| chat | ✅ | None (demo fallback) | No (fallback) |
| automation | ✅ | Error result card | No |
| youtube | ❌ | None | Yes |
| academics | ❌ | None | Yes |

**Observation:** Only 3 of 18 pages have explicit error handling. Most pages silently fail on Supabase errors. This is a known debt item.

### 17.2 Accessibility

| Feature | Coverage |
|---|---|
| `role="status"` on spinners | All pages |
| `aria-label="Loading"` on spinners | Most pages |
| `sr-only` text | Spinners |
| `role="dialog"` on modals | academics only |
| `aria-modal="true"` on modals | academics only |
| `role="switch"` on toggles | automation |
| `aria-checked` on toggles | automation |
| Keyboard navigation | None explicit |
| Focus trap in modals | None |

### 17.3 Code Duplication

The auth guard pattern appears in **all 18 pages**, totaling approximately 200 lines of duplicated code:

```typescript
const { user, loading: authLoading } = useAuth()
const router = useRouter()
const [mounted, setMounted] = useState(false)

useEffect(() => { setMounted(true) }, [])
useEffect(() => {
  if (!authLoading && !user) router.push('/login')
  if (user) fetchData()
}, [user, authLoading, router])
```

**Recommendation:** Extract into a `withAuth` HOC or `AuthGate` wrapper component.

---

## 18. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-13 | Developer | Initial document — all 18 module pages with component breakdown, data flow, state matrices, loading/empty/error paths, animation reference, and cross-cutting analysis |
