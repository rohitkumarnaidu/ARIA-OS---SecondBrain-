# Frontend Screen Flows — ARIA OS

## Document Control

| Field | Value |
|---|---|
| Document ID | DES-SF-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-13 |
| Classification | Enterprise UX — Screen Flow Specification |
| Target Audience | Frontend Engineers, UX Designers, QA Engineers |
| Supersedes | — |
| Related Docs | Wireframe System (8 parts), `UserFlows.md`, `UseCases.md`, `UserJourneyArchitecture.md`, `FrontendRoutingNavigation.md`, `ModulesImplementationSpec.md` |

---

## 1. Executive Summary

This document defines every screen-to-screen transition, screen state machine, modal dependency, and navigation topology across all 18 pages of ARIA OS. It forms the bridge between the **wireframe system** (what the UI looks like) and the **implementation** (what the code does).

**What this document covers:**
- **Navigation topology** — every screen as a node, every transition as an edge
- **Screen state machines** — the 5 states each screen can be in (Loading, Empty, Error, Populated, Offline)
- **Transition triggers** — every action that moves the user from one screen state to another or to a different screen
- **Modal & overlay flows** — which overlays spawn from which screens, what dismisses them, where the user lands after
- **Deep link resolution** — how notifications and external links map to screens
- **Auth flow states** — unauthenticated → authenticated session lifecycle
- **Wireframe-to-screen cross-reference** — every wireframe section mapped to its rendered screen

**Screen Flow Notation Key:**
```
[Screen Name]           — A distinct page/module route
{Screen State}          — One of Loading | Empty | Error | Populated | Offline
[Action →]              — User or system trigger
┌─┐ · ── · └─┘          — Decision branches
=> [Overlay]            — Modal, sheet, dialog, or panel spawns
==> [Background]         — Async background process
```

---

## 2. Navigation Topology

### 2.1 Complete Navigation Graph

```
                         ┌────────────────────────────────────────────────────────────────────────────┐
                         │                          AUTH BOUNDARY                                     │
                         │  ┌─────────┐    ┌──────────┐     ┌───────────┐                            │
                         │  │  /      │───→│  /login  │────→│  /dashboard│   (protected after auth)  │
                         │  │ Landing │    │ OAuth    │     │           │                            │
                         │  └─────────┘    └──────────┘     └─────┬─────┘                            │
                         │       │                                  │                                │
                         │       └──────────────────────────────────┘                                │
                         │                                                                           │
                         │                          SIDEBAR (16 nav items)                           │
                         │  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐    │
                         │  │ Dashboard │  Tasks   │ Courses  │ YouTube  │ Resources │  Ideas   │    │
                         │  └─────┬────┘─────┬────┘────┬────┘────┬────┘────┬────┘─────┬───┘    │
                         │        │          │         │         │         │          │         │
                         │  ┌─────┴────┐┌────┴────┐┌───┴────┐┌──┴─────┐┌──┴─────┐┌───┴────┐   │
                         │  │  /dashboard││ /tasks  ││ /courses││ /youtube││ /resrcs ││ /ideas  │   │
                         │  └──────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘   │
                         │        │          │         │         │         │          │         │
                         │  ┌─────┴────┐┌────┴────┐┌───┴────┐┌──┴─────┐┌──┴─────┐┌───┴────┐   │
                         │  │   Goals  ││ Opport. ││ Income  ││ Projects││Academics││ Habits  │   │
                         │  └─────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘   │
                         │        │          │         │         │         │          │         │
                         │  ┌─────┴────┐┌────┴────┐┌───┴────┐┌──┴─────┐┌──┴─────┐┌───┴────┐   │
                         │  │   Sleep  ││  Time   ││  Chat   ││  Auto   ││  (all   ││  route  │   │
                         │  └──────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘   │
                         └────────────────────────────────────────────────────────────────────────────┘

                                         SYSTEM OVERLAYS (accessible from any screen)
                          ┌───────────────────────────────────────────────────────────────────┐
                          │  [Cmd+K] Command Palette  │  [⊕] Quick Create  │  [🔔] Notifications │
                          │  [🔍] Global Search Panel │  [✕] Sign Out Dialog                   │
                          └───────────────────────────────────────────────────────────────────┘
```

### 2.2 Edge Types

| Edge Type | Trigger | Example | Visual Cue |
|---|---|---|---|
| **Primary Nav** | Sidebar link click | `/dashboard` → `/tasks` | Sidebar active state change |
| **Secondary Nav** | Content card/link click | `/dashboard` → `/tasks` (via "View All") | ChevronRight icon |
| **Tertiary Nav** | Action button | `/tasks` → Add Modal | Modal slide-up animation |
| **Deep Link** | Notification/external URL | Push notification → `/tasks/abc-123` | Route param injection |
| **Auth Redirect** | Session change | `/dashboard` → `/login` (on expiry) | Full page redirect |
| **System Overlay** | Keyboard shortcut | Any screen → Command Palette (Cmd+K) | Overlay with backdrop |

### 2.3 Route Parameter Flow

| Route Pattern | Params | Example | Resolution |
|---|---|---|---|
| `/[module]` | — | `/tasks` | Module list/default view |
| `/[module]/[id]` | `id: string` | `/tasks/abc-123` | Detail view (future) |
| `/[module]?view=` | `view: string` | `/tasks?view=board` | View switcher (future) |
| `/[module]?filter=` | `filter: string` | `/opportunities?filter=internships` | Pre-filtered list (future) |
| `/login?redirect=` | `redirect: string` | `/login?redirect=/tasks/abc` | Post-auth redirect target |

**Current State:** Routes use zero URL parameters. All 18 pages are flat routes with no dynamic segments. The auth guard redirect is the only parameterized navigation (`router.push('/login')`). Dynamic route segments (`/[id]`), view params (`?view=`), and filter params (`?filter=`) are wireframe-specified but not implemented.

---

## 3. Application Shell State Machine

### 3.1 Shell Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      APPLICATION SHELL                         │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  NAVBAR (fixed top, 64px, z-40)                       │     │
│  │  [Search........]         [🔔 Notif]  [👤 User ▼]    │     │
│  └──────────────────────────────────────────────────────┘     │
│  ┌──────────┐ ┌───────────────────────────────────────────┐   │
│  │ SIDEBAR │ │                                           │   │
│  │ (fixed   │ │          CONTENT AREA                     │   │
│  │  left,   │ │    (scrollable, pt-20, px-6, pb-6)       │   │
│  │  240px)  │ │                                           │   │
│  │          │ │  ┌─────────────────────────────────────┐  │   │
│  │ nav items│ │  │     PAGE-SPECIFIC CONTENT           │  │   │
│  │ 16 total │ │  │     (rendered per route)            │  │   │
│  │          │ │  └─────────────────────────────────────┘  │   │
│  └──────────┘ └───────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**Critical Issue (Orphaned Layout):** The `(dashboard)/layout.tsx` wraps Sidebar + Navbar but NO pages are nested inside it. All 16 protected pages live at root `app/` level. The Sidebar + Navbar are **defined but never rendered** in the current routing structure. Every protected page renders as a bare content area with no chrome.

### 3.2 Shell States

| State | Condition | Sidebar | Navbar | Content Area |
|---|---|---|---|---|
| **Loading** | Auth check in progress (useAuth loading) | Not rendered | Not rendered | Full-screen spinner |
| **Unauthenticated** | `user === null` after auth check | Not rendered | Not rendered | Redirect to `/login` |
| **Authenticated** | `user !== null` | Rendered (but orphaned — not visible) | Rendered (but orphaned — not visible) | Page content |
| **Error** | Auth network failure | Not rendered | Not rendered | Error state (not implemented) |

### 3.3 Sidebar Navigation Map

```
Sidebar (240px fixed left)
├── Dashboard    →  /dashboard       Icon: LayoutDashboard
├── Tasks        →  /tasks           Icon: CheckSquare
├── Courses      →  /courses         Icon: BookOpen
├── YouTube      →  /youtube         Icon: Youtube
├── Resources    →  /resources       Icon: FileText
├── Ideas        →  /ideas           Icon: Lightbulb
├── Goals        →  /goals           Icon: Target
├── Opportunities → /opportunities   Icon: Radar
├── Income       →  /income          Icon: Wallet
├── Projects     →  /projects        Icon: FolderKanban
├── Academics    →  /academics       Icon: GraduationCap
├── Habits       →  /habits          Icon: Moon
├── Sleep        →  /sleep           Icon: Moon
├── Time         →  /time            Icon: Clock
├── Chat         →  /chat            Icon: MessageCircle
└── Automation   →  /automation      Icon: Zap
```

**Active State Logic:**
```
pathname === item.href
  → True:  bg-accent-primary/10 text-accent-primary (highlighted)
  → False: text-text-secondary hover:bg-background-elevated (default)
```

### 3.4 Navbar Interaction Map

| Element | Trigger | Transition |
|---|---|---|
| Search input | Focus / click | Opens global search overlay (not implemented — placeholder only) |
| Bell icon | Click | Opens notification panel (not implemented — placeholder only) |
| User avatar | Click | Toggles dropdown: Sign Out |
| Sign Out | Click | `supabase.auth.signOut()` → `router.push('/')` |

---

## 4. Screen Flow Specifications

### 4.1 System Pages

#### 4.1.1 `/` — Landing / Auth Redirector

| Property | Value |
|---|---|
| **Wireframe Ref** | Not in wireframe system (auth shell only) |
| **Type** | Auth boundary |
| **Auth Required** | No |

**State Machine:**
```
Entry: browser navigation to /
  → {useAuth().loading === true}
      → [State: Loading] — Full-screen centered spinner + "Loading..."
  → {useAuth().loading === false}
      → {user !== null}
          → [Action: router.push('/dashboard')] — Immediate redirect
      → {user === null}
          → [Action: router.push('/login')] — Immediate redirect
```

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| Page load | — | Loading | `useEffect` on mount |
| Auth resolved (user) | Loading | `/dashboard` | `router.push('/dashboard')` |
| Auth resolved (no user) | Loading | `/login` | `router.push('/login')` |

**Component Visibility Matrix:**

| Component | Loading | Notes |
|---|---|---|
| Spinner + text | ✅ Visible | `Loader2` icon + "Loading..." |
| Background | ✅ Visible | `bg-background-dark` full viewport |

**Entry Points:** Browser URL bar, bookmark, external link.
**Exit Points:** `/dashboard` (if authed), `/login` (if not authed).

---

#### 4.1.2 `/login` — OAuth Login

| Property | Value |
|---|---|
| **Wireframe Ref** | Not in wireframe system (auth screen — standalone) |
| **Type** | Public authentication |
| **Auth Required** | No (public) |

**State Machine:**
```
Entry: /login (from redirect or direct nav)
  → [State: Populated] — Login card rendered immediately
  → User clicks "Continue with Google"
      → [State: Loading (local)] — Button shows "Signing in...", disabled
      → supabase.auth.signInWithOAuth({ provider: 'google' })
          → {OAuth succeeds}
              → Redirected to /dashboard (via Supabase OAuth redirect)
          → {OAuth fails}
              → [State: Error] — console.error log (no user-facing error)
              → [Action: setLoading(false)] — Button re-enables
```

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| Google button click | Populated | Loading (local) | `setLoading(true)` |
| OAuth success | Loading | `/dashboard` (Supabase redirect) | `signInWithOAuth` redirectTo |
| OAuth failure | Loading | Populated (error) | `setLoading(false)` + console.error |

**Component Visibility Matrix:**

| Component | Loading | Error | Notes |
|---|---|---|---|
| Three.js background | ✅ Visible | ✅ Visible | `ThreeBackground` component |
| Gradient overlay | ✅ Visible | ✅ Visible | Readability overlay |
| Logo + title | ✅ Visible | ✅ Visible | Animated with framer-motion |
| Google button | ❌ Disabled | ✅ Enabled | Shows spinner when loading |
| Feature preview grid | ✅ Visible | ✅ Visible | 3-column stats always visible |

**Entry Points:** `/` redirect (unauthed), `/login` direct, session expiry redirect.
**Exit Points:** `/dashboard` (on successful OAuth), `/` (on manual nav away).

---

### 4.2 Dashboard

#### 4.2.1 `/dashboard` — Command Center

| Property | Value |
|---|---|
| **Wireframe Ref** | `02_DASHBOARD_WIREFRAMES.md` — Morning Briefing, Widget Configuration, Layout Presets |
| **Type** | Aggregation view |
| **Auth Required** | Yes |

**State Machine:**
```
Entry: /dashboard (internal redirect or direct nav)
  → [State: Loading] — Full-screen spinner
  → {useAuth resolves}
      → {user === null}
          → [Action: router.push('/login')]
      → {user !== null}
          → [Action: fetchTasks()] — Zustand store fetch
          → {tasks.length === 0 && fetch complete}
              → [State: Empty] — All sections render with zero-state
          → {tasks.length > 0}
              → [State: Populated] — Full dashboard rendered
```

**Sub-states (content sections):**

| Section | Populated | Empty | Loading |
|---|---|---|---|
| Hero greeting | ✅ Time-based greeting + date | Same | Not rendered |
| Stats grid (4 cards) | ✅ Computed metrics shown | All show 0 | Not rendered |
| Priority tasks | ✅ Up to 4 tasks with stagger animation | "All caught up!" CTA to /tasks | Not rendered |
| ARIA's Pick | ✅ Top task recommendation | "Add tasks..." prompt | Not rendered |
| Quick actions | ✅ 4 action buttons (always rendered) | Same | Not rendered |
| Activity heatmap | ✅ 30 random cells | Same (random) | Not rendered |

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| "View All" click | Populated/Empty | `/tasks` | `router.push('/tasks')` |
| Task card click | Populated | `/tasks` | `router.push('/tasks')` |
| "Add Task" CTA | Empty | `/tasks` | `router.push('/tasks')` |
| "Chat with ARIA" | Populated/Empty | `/chat` | `router.push('/chat')` |
| Quick Action click | Populated/Empty | Target module route | `router.push(action.path)` |
| Auth expiry | Any | `/login` | `router.push('/login')` |

**Entry Points:** `/` redirect (authed), `/login` redirect, direct nav, bookmark.
**Exit Points:** `/tasks`, `/chat`, `/courses`, `/ideas`, `/goals`, `/login`.

**Modal Dependency:** None — all navigations are full-page transitions.

---

### 4.3 Module Pages (CRUD List)

The following 15 pages follow an **identical screen flow pattern** with module-specific data. They are documented as a group with individual differences noted.

#### 4.3.1 Common Template (All CRUD Pages)

```
Entry: /[module]
  → [State: Loading] — Full-screen centered spinner
      ┌─────────────────────────────────────────────────────────┐
      │  <div className="w-12 h-12 rounded-xl border-2          │
      │         border-accent-primary/30 animate-pulse-glow">    │
      │    <div className="w-8 h-8 border-2 border-accent-      │
      │         primary border-t-transparent rounded-full        │
      │         animate-spin" />                                 │
      │  </div>                                                  │
      └─────────────────────────────────────────────────────────┘
  → {mounted === true, authLoading === false}
      → {user === null}
          → [Action: router.push('/login')]
      → {user !== null}
          → [Action: fetchData()] — module-specific query
          → {fetchData() succeeds}
              → {data.length === 0}
                  → [State: Empty]
                      ┌─────────────────────────────────────┐
                      │  Module icon (64px)                   │
                      │  "No [module items] found"            │
                      │  "Start by adding your first [item]"  │
                      │  [Button: "Add [Item]"] → opens modal │
                      └─────────────────────────────────────┘
              → {data.length > 0}
                  → [State: Populated]
                      ┌─────────────────────────────────────┐
                      │  Header: title + subtitle + Add btn  │
                      │  Stats grid (1-3 metric cards)       │
                      │  Filter tabs (module-specific)       │
                      │  Content list/grid with animations   │
                      └─────────────────────────────────────┘
          → {fetchData() fails}
              → [State: Error] — no user-facing error UI
              → `console.error` log only (15/18 pages)
              → Falls back to empty state
  → User clicks "Add" button
      → [Overlay: Add Modal]
          ┌─────────────────────────────────────────────────┐
          │  Fixed overlay: bg-black/70 backdrop-blur-sm    │
          │  Centered card: max-w-lg, bg-background-card    │
          │  Header: title + X close button                 │
          │  Form fields (module-specific)                  │
          │  Footer: Cancel + Submit buttons                │
          └─────────────────────────────────────────────────┘
          → User fills form → clicks Submit
              → [Action: supabase.insert() or store method]
              → {success}
                  → [Action: close modal, refetch data]
                  → Optimistic: update local state directly
              → {failure}
                  → Modal stays open (no error toast)
          → User clicks Cancel / X / Escape
              → [Action: close modal]
              → [State: Previous state]
  → User clicks Edit on item
      → [Overlay: Edit Modal] — same pattern as Add
  → User clicks Delete on item
      → [Action: supabase.delete() or store method]
      → Optimistic: item removed from local state
```

**Component Visibility Matrix (all CRUD pages):**

| Component | Loading | Empty | Populated | Error |
|---|---|---|---|---|
| Spinner | ✅ | ❌ | ❌ | ❌ |
| Header (title + subtitle) | ❌ | ✅ | ✅ | ✅ |
| "Add" button | ❌ | ✅ | ✅ | ✅ |
| Stats cards | ❌ | ✅ (zeros) | ✅ (computed) | ❌ |
| Filter tabs | ❌ | ✅ | ✅ | ❌ |
| Content list | ❌ | ❌ | ✅ | ❌ |
| Empty state icon + message | ❌ | ✅ | ❌ | ❌ |
| Empty state CTA | ❌ | ✅ | ❌ | ❌ |
| Add Modal | ❌ | Spawned by button | Spawned by button | ❌ |
| Edit Modal | ❌ | N/A | Spawned by button | ❌ |

---

#### 4.3.2 Per-Module Screen Flow Variations

##### `/tasks` — Task Manager (Zustand-powered)

| Property | Value |
|---|---|
| **Wireframe Ref** | `03_TASKS_AND_COURSES_WIREFRAMES.md` — Task List, Board, Calendar, Detail, Create Modal |
| **Data Source** | Zustand store (`useTaskStore`) |
| **Store Methods** | `fetchTasks`, `addTask`, `updateTask`, `deleteTask`, `completeTask` |
| **State Variables** | `showAddModal`, `editingTask`, `filter`, `newTask` (7 fields) |
| **Filters** | `all` / `pending` / `in_progress` / `completed` (4 tabs with counts) |
| **Stats Cards** | To Do (count), In Progress (count), Done (count) — clickable filter shortcut |
| **Content** | Card list with drag handle, priority indicator, title, description, tags, actions |
| **Actions/Task** | Complete (check), Edit (pencil), Delete (trash) — revealed on hover |
| **Add Modal** | Title*, Description, Priority (select), Category (select), Est. Minutes, Due Date, Recurring toggle |
| **Edit Modal** | Title, Description, Priority, Category |
| **Error Handling** | ❌ — No try/catch on store operations (only on Supabase direct calls) |
| **Transition: Complete** | Optimistic → store.updateTask → re-render (no backend confirmation) |
| **Transition: Delete** | Optimistic → store.deleteTask → item fades out (AnimatePresence exit animation) |

**Entry Points:** `/tasks` direct, `/dashboard` "View All" or task card click, `/chat` intent → task link.
**Exit Points:** `/dashboard` (sidebar), any module (sidebar), `/login` (auth expiry).

---

##### `/courses` — Course Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | `03_TASKS_AND_COURSES_WIREFRAMES.md` — Course Library, Detail, Progress |
| **Data Source** | Supabase direct (useState) |
| **Filters** | Not implemented (all courses shown) |
| **Stats Cards** | Total courses, Active courses, Completed courses |
| **Add Modal** | Name*, Platform (Udemy/Coursera/NPTEL/College/YouTube/Other), URL, Total hours, Hours/week, Deadline, Why enrolled |
| **Error Handling** | ❌ — No try/catch on Supabase queries |

---

##### `/habits` — Habit Engine

| Property | Value |
|---|---|
| **Wireframe Ref** | Habit section (supplement) — Tracker View, Detail, Add Modal |
| **Data Source** | Supabase direct (useState) |
| **Stats Cards** | Active habits, Total streak (sum), Avg consistency % |
| **Content** | Card list: name, frequency, streak, consistency %, active toggle, streak flame icon |
| **Actions/Habit** | Toggle active (switch), Delete (trash) |
| **Add Modal** | Name*, Frequency (daily/weekly), Time target (minutes) |
| **Error Handling** | ❌ — No try/catch on Supabase queries |

---

##### `/goals` — Goal/Roadmap

| Property | Value |
|---|---|
| **Wireframe Ref** | `04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` — Roadmap Canvas, Timeline, Milestones, Dependencies |
| **Data Source** | Supabase direct |

---

##### `/ideas` — Idea Vault

| Property | Value |
|---|---|
| **Wireframe Ref** | `04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` — Capture View, Pipeline Board, Analysis, Detail |
| **Data Source** | Supabase direct |
| **Detail Modal** | `selectedIdea` state — opens detail overlay for individual idea |

---

##### `/income` — Income Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | `05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` — Income Overview, Sources, Analytics |
| **Data Source** | Supabase direct |

---

##### `/projects` — Project Board

| Property | Value |
|---|---|
| **Wireframe Ref** | `05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` — Project Board, Timeline, Detail |
| **Data Source** | Supabase direct |

---

##### `/resources` — Knowledge Vault

| Property | Value |
|---|---|
| **Wireframe Ref** | `04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` — Resource Grid/List, Search, Graph, Detail |
| **Data Source** | Supabase direct |

---

##### `/opportunities` — Opportunity Radar

| Property | Value |
|---|---|
| **Wireframe Ref** | `05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` — Discovery, Recommendations, Filter, Detail |
| **Data Source** | Supabase direct |
| **Filters** | Category filter dropdown |

---

##### `/sleep` — Sleep Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement — Log View, Analytics, Log Modal |
| **Data Source** | Supabase direct |

---

##### `/youtube` — YouTube Library

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement — Library View, Video Detail, Add Modal |
| **Data Source** | Supabase direct |

---

##### `/academics` — Academic Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement — Semester View, Subject Detail, Add Subject Modal |
| **Data Source** | Supabase direct |
| **Special** | Custom CGPA calculation algorithm |

---

#### 4.3.3 `/time` — Time Tracker (Timer + Pomodoro)

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement — Timer View (Pomodoro), Entries Log, Statistics, Manual Entry Modal |
| **Data Source** | Supabase direct (useState) |
| **State Variables** | `activeTimer`, `elapsed`, `pomodoroMode`, `pomodoroPhase`, `pomodoroTimeLeft`, `showIdleWarning`, `lastActivity`, `focusHours` |

**State Machine:**
```
Entry: /time
  → [State: Loading] — Standard spinner
  → {user !== null}
      → [Action: fetchEntries()] — supabase query
      → {found active timer (entry with no end_time)}
          → [Sub-state: Timer Running] — Shows elapsed time + Stop button
      → {no active timer}
          → [Sub-state: Timer Stopped] — Shows Start button
  → User clicks "Start Timer"
      → [Action: supabase.insert() with start_time]
      → [Sub-state: Timer Running]
      → 1-second interval: setElapsed(Math.floor(now - startTime / 1000))
      → {15+ minutes no activity (lastActivity check)}
          → [Sub-state: Idle Warning] — Yellow banner "No activity detected"
          → User clicks "I'm still working" → dismisses warning
  → User clicks "Stop Timer"
      → [Action: supabase.update() with end_time + duration]
      → [Sub-state: Timer Stopped]
      → Duration >= 90 min → marked as deep_work
  → User toggles "Pomodoro ON"
      → [Sub-state: Pomodoro Active]
      → 25-min countdown → auto-switch to 5-min break → auto-loop
  → Work session ends (90+ min)
      → [Action: focusHours analysis] — top 5 peak hours computed
```

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| Start button | Timer Stopped | Timer Running | `startTimer()` → supabase insert |
| Stop button | Timer Running | Timer Stopped | `stopTimer()` → supabase update |
| Idle 15+ min | Timer Running | Idle Warning visible | `useEffect` interval check |
| "I'm working" | Idle Warning | Timer Running (reset) | `setLastActivity(Date.now())` |
| Pomodoro toggle | Any | Pomodoro Active / Inactive | `setPomodoroMode(!pomodoroMode)` |
| Timer completes | Work phase | Break phase | `pomodoroTimeLeft <= 1` → phase swap |

**Entry Points:** `/time` direct, sidebar, `/tasks` → "Start Focus" (future).
**Exit Points:** Sidebar modules, `/login`.

---

#### 4.3.4 `/chat` — ARIA Chat Interface

| Property | Value |
|---|---|
| **Wireframe Ref** | `06_ANALYTICS_AI_SETTINGS_STATES_WIREFRAMES.md` — Chat View, Thread, Context Panel, History |
| **Data Source** | Supabase (messages) + fetch(/api/chat) + demo fallback |
| **State Variables** | `messages`, `input`, `loading`, `mounted` |
| **Refs** | `messagesEndRef` — auto-scroll to bottom |

**State Machine:**
```
Entry: /chat
  → [State: Loading] — Neon spinner with cyan glow animation
  → {user !== null}
      → [Action: fetchMessages()] — supabase query (50 latest)
      → {messages.length === 0}
          → [State: Empty] — ARIA avatar + greeting + instruction text
      → {messages.length > 0}
          → [State: Populated] — Message history with staggered Framer Motion
  → User types message + presses Enter / Send
      → {input.trim() === '' || loading === true}
          → Blocked — no action
      → [Action: setLoading(true)]
      → [Action: Optimistic — add temp user message to UI]
      → [Action: fetch('/api/chat')]
          → {API responds successfully}
              → [Action: Add assistant response to messages]
              → [Action: supabase.insert() save both messages]
          → {API fails (network error, 500)}
              → [Fallback: getDemoResponse()]
              → [Action: Add demo response to messages]
      → [Action: setLoading(false)]
      → [Action: scrollToBottom()]
  → User presses Enter (without Shift)
      → Trigger handleSend
  → User presses Shift+Enter
      → Newline in input (not send)
```

**Conversation Flow:**
```
User: "task buy groceries"
  API: → intent: task → response links to /tasks
  Demo: → "I can help you manage tasks! Go to the Tasks page..."
  [Action: user may navigate to /tasks]

User: "help"
  API → intent: general
  Demo → feature overview

User: "what's my productivity score?"
  API → intent: query → supabase query
  Demo → "I'm here to help!"
```

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| Send message | Populated/Empty | Loading (per-message) | `handleSend()` |
| API success | Loading | Populated (new message) | `setMessages(prev => [...prev, assistantMsg])` |
| API failure | Loading | Populated (demo response) | `getDemoResponse()` fallback |
| Auth expiry | Any | `/login` | `router.push('/login')` |
| Chat message link | Populated | `/tasks`, `/courses`, etc. | User navigates via sidebar |

**Entry Points:** `/chat` direct, `/dashboard` "Chat with ARIA" button, sidebar.
**Exit Points:** Sidebar, `/login`.

---

#### 4.3.5 `/automation` — Automation Config

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement — Rules List, Rule Detail, Create Rule Modal, Log |
| **Data Source** | fetch() to backend API + local useState |
| **State Variables** | `running`, `results`, `enabledAutomations` (6 toggles) |

**State Machine:**
```
Entry: /automation
  → [State: Loading] — Standard spinner
  → [State: Populated] — 6 automation cards rendered immediately (no data fetch)
  → User clicks "Run Now" on an automation
      → [Action: setRunning(type)]
      → [Action: fetch(endpoint)]
          → {response ok}
              → [Action: setResults(data)] — Results panel appears below
          → {response fails}
              → [Action: setResults({status: 'error', message})] — Error panel
      → [Action: setRunning(null)]
  → User toggles automation switch
      → [Action: setEnabledAutomations(prev => ...)] — Local state only
      → (no backend persistence for toggles)
```

**Automation Trigger Endpoints:**

| Automation | Endpoint | Schedule |
|---|---|---|
| Daily Briefing | `POST /api/automation/trigger/briefing` | 7 AM daily |
| Opportunity Radar | `POST /api/automation/trigger/radar` | 6 AM daily |
| Weekly Review | `POST /api/automation/trigger/weekly-review` | Sunday 8 PM |
| Sleep Analysis | `POST /api/automation/trigger/sleep-analysis` | On-demand |
| Bedtime Suggestion | `POST /api/automation/trigger/sleep-bedtime` | On-demand |
| Course & Habit Nudges | `POST /api/automation/trigger/nudges` | 6 PM daily |

**Transition Triggers:**

| Trigger | From State | To State/Screen | Mechanism |
|---|---|---|---|
| "Run Now" click | Populated | Running (per-card) | `setRunning(type)` |
| Run completes | Running | Results visible | `setResults(data)` |
| Toggle switch | Populated | Toggle state changed | `setEnabledAutomations()` |

**Entry Points:** `/automation` direct, sidebar.
**Exit Points:** Sidebar, `/login`.

---

## 5. Modal & Overlay Flow Registry

### 5.1 Global Modal Inventory

| Modal | Trigger | Source Screen | Dismiss Action | Post-Dismiss | Animation |
|---|---|---|---|---|---|
| **Add [Item]** | "Add" button click | Any CRUD page (tasks, courses, habits, etc.) | Cancel / X / Escape / Submit success | Same screen (refetch) | Scale 0.95→1 + fade |
| **Edit [Item]** | "Edit" icon click | Tasks (editingTask state) | Cancel / X / Submit success | Same screen (update) | Scale 0.95→1 + fade |
| **Quick Capture** | Cmd+K / ⊕ FAB | Any screen (future) | Escape / Submit | Same screen | Slide-up |
| **Command Palette** | Cmd+K | Any screen (future) | Escape | Same screen | Slide-down |
| **Notification Panel** | Bell icon click | Any screen (future) | Escape / click outside | Same screen | Slide-over right |
| **Sign Out Confirm** | "Sign Out" in dropdown | Any screen (via Navbar) | Click outside | Stay on same screen | Dropdown close |
| **User Dropdown** | Avatar click | Any screen (via Navbar) | Click outside / Sign Out | Same screen | Dropdown toggle |

### 5.2 Modal Stacking Rules

```
Z-index hierarchy (highest to lowest):
  z-modal (50):    Active modal dialog
  z-overlay (40):  Modal backdrop (bg-black/70 backdrop-blur-sm)
  z-dropdown (30): User dropdown, filter menus
  z-nav (20):      Navbar (fixed, z-40)
  z-sidebar (10):  Sidebar (fixed)
  z-base (0):      Content area
```

**Stacking constraint:** Maximum 1 modal visible at a time. No nested modals.
**Scrolling:** Body scroll locked when any modal is open.
**Backdrop click:** Closes modal (not implemented — only X/Cancel buttons close).

### 5.3 Modal Animation Contract

```typescript
// All add/edit modals follow this exact pattern:
// Overlay container:
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-modal p-4"
  role="dialog"
  aria-modal="true"
>
  {/* Card */}
  <motion.div
    initial={{ scale: 0.95, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    exit={{ scale: 0.95, opacity: 0 }}
    className="bg-background-card border border-border rounded-2xl p-6 w-full max-w-lg shadow-2xl"
  >
    {/* Title + X button */}
    {/* Form fields */}
    {/* Cancel + Submit buttons */}
  </motion.div>
</motion.div>
```

---

## 6. Deep Link Resolution Map

### 6.1 Current Deep Link Capabilities

| Source | Format | Resolution | Status |
|---|---|---|---|
| Push notification | N/A | N/A | Not implemented |
| Email link | N/A | N/A | Not implemented |
| Browser bookmark | `/[module]` | Renders flat page | ✅ Working |
| URL bar direct | `/[module]` | Renders flat page | ✅ Working |
| OAuth redirect | `/dashboard` | Renders dashboard | ✅ Working |

### 6.2 Future Deep Link Schema (from Wireframe Spec)

```
Scheme: https://app.aria-os.com/[module]/[id]?[params]

Navigation:
  /tasks/abc-123                 → Task detail view (not implemented)
  /tasks?view=board              → Kanban board view (not implemented)
  /tasks?filter=high             → Pre-filtered high priority (not implemented)
  /courses/abc-123?tab=lessons   → Course detail, lessons tab (not implemented)
  /chat?thread=abc-123           → Open specific chat thread (not implemented)
  /settings/appearance           → Direct to settings section (not implemented)
```

### 6.3 Deep Link Resolution Flow (Planned)

```
Incoming URL /tasks/abc-123
  → middleware.ts (not implemented) intercepts
  → Parse params: module=tasks, id=abc-123
  → Auth check (middleware)
      → Not authed → redirect /login?redirect=/tasks/abc-123
      → Authed → proceed
  → Route: /tasks with query param id=abc-123
  → Page renders list, then fetches detail for abc-123
  → Opens detail modal automatically
```

---

## 7. Auth Flow State Machine

### 7.1 Complete Auth Lifecycle

```
                         ┌──────────────────────────────────────────────────┐
                         │                AUTH LIFECYCLE                     │
                         └──────────────────────────────────────────────────┘

  [Browser navigates to any protected route]
       │
       ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  Step 1: useAuth() hook initializes                                  │
  │  ┌──────────────────────────────────────────────────────────────┐  │
  │  │  const { user, loading } = useAuth()                          │  │
  │  │  → loading = true (initial)                                    │  │
  │  │  → Supabase checks session (local storage token)               │  │
  │  └──────────────────────────────────────────────────────────────┘  │
  │                                                                     │
  │  {loading === true}                                                 │
  │    → [State: Auth Loading] — Full-screen spinner                    │
  │    → App shell NOT rendered (Sidebar + Navbar hidden)               │
  │                                                                     │
  │  {loading === false}                                                │
  │    → {user !== null}                                                │
  │    │   → [State: Authenticated] — Page renders                      │
  │    │   → useEffect: if (user) fetchData()                           │
  │    │                                                                 │
  │    → {user === null}                                                │
  │        → [Action: router.push('/login')]                            │
  │        → [State: Unauthenticated] — Login page renders              │
  │                                                                     │
  └────────────────────────────────────────────────────────────────────┘

  [User on login page]
       │
       ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  Step 2: OAuth flow                                                 │
  │                                                                     │
  │  User clicks "Continue with Google"                                 │
  │    → supabase.auth.signInWithOAuth({ provider: 'google',            │
  │        options: { redirectTo: '/dashboard' }})                      │
  │    → Supabase opens Google OAuth popup/window                       │
  │    → User authenticates with Google                                 │
  │    → Google redirects back to Supabase callback URL                 │
  │    → Supabase creates/updates user in auth.users                    │
  │    → Supabase sets session cookie + local storage token             │
  │    → Browser redirects to /dashboard                                │
  │    → useAuth() initializes → user is set → page renders             │
  │                                                                     │
  └────────────────────────────────────────────────────────────────────┘

  [Authenticated session — active use]
       │
       ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  Step 3: Session maintenance                                        │
  │                                                                     │
  │  {Access token expires (JWT expiry, default 1 hour)}                │
  │    → Supabase client auto-refreshes using refresh_token             │
  │    → Transparent to application code — no user impact               │
  │                                                                     │
  │  {Refresh token expires / invalidated}                              │
  │    → Next Supabase request returns 401                              │
  │    → useAuth detects user = null                                    │
  │    → [Action: router.push('/login')]                                │
  │    → [State: Unauthenticated]                                       │
  │                                                                     │
  └────────────────────────────────────────────────────────────────────┘

  [User signs out]
       │
       ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  Step 4: Sign out                                                   │
  │                                                                     │
  │  User clicks "Sign Out" in Navbar dropdown                          │
  │    → supabase.auth.signOut()                                        │
  │    → Clears session from local storage                              │
  │    → router.push('/')                                               │
  │    → Root page detects no user → redirects to /login                │
  │                                                                     │
  └────────────────────────────────────────────────────────────────────┘
```

### 7.2 Auth Guard Code Pattern (Identical on All 18 Protected Pages)

```typescript
const { user, loading: authLoading } = useAuth()
const router = useRouter()
const [mounted, setMounted] = useState(false)

useEffect(() => { setMounted(true) }, [])

useEffect(() => {
  if (!authLoading && !user) {
    router.push('/login')         // Redirect unauthenticated
  }
  if (user) {
    fetchData()                   // Fetch data when authenticated
  }
}, [user, authLoading, router])

// Loading guard (block render until auth resolves + mount completes)
if (!mounted || authLoading) {
  return <Spinner />
}
```

**Duplication:** This exact pattern appears in 17 files (all protected pages). No `middleware.ts` exists for server-side protection.

---

## 8. Cross-Cutting State Transitions

### 8.1 Page Loading → Data States

```
[Page mounts]
  → [State: Mounting]
      → setMounted(true) — prevents hydration mismatch
  → [State: Auth Loading]
      → useAuth() resolves
      → {user === null} → [Redirect: /login]
      → {user !== null} → [State: Data Loading]
          → fetchData() executes
          → {fetch succeeds, data.length > 0} → [State: Populated]
          → {fetch succeeds, data.length === 0} → [State: Empty]
          → {fetch fails (network/Supabase error)}
              → 15/18 pages: silently fail (no user feedback)
              → 3/18 pages: try/catch with console.error
              → Falls through to empty state (no error UI)
```

### 8.2 Offline → Online Transition

```
{Network lost (navigator.onLine === false)}
  → No offline indicator shown in current app
  → All Supabase queries will fail silently
  → No IndexedDB queue exists for offline writes
  → App becomes non-functional until connectivity returns

{Network restored}
  → Pages must be refreshed to recover
  → No auto-retry or background sync mechanism
```

**Note:** Offline support is planned (see `FrontendOfflinePWA.md`) but not implemented. The app currently requires continuous connectivity.

### 8.3 Error Recovery Flow

```
{Any Supabase query fails}
  → 15/18 pages:
      → const { data } = await supabase.from(...).select(...)
      → {error} is silently ignored (if (data) setState(data))
      → Falls back to empty array state
      → No toast, no error banner, no retry button
  → 3/18 pages (chat, automation, tasks):
      → try/catch block
      → console.error log (visible in dev console only)
      → chat: falls back to demo response
      → automation: shows error result in UI
      → tasks: no error handling on store operations

{AI LLM fails (chat)}
  → try/catch on fetch('/api/chat')
  → Falls back to getDemoResponse() — hardcoded keyword matching
  → No user-visible error message
  → Demo response replaces AI response transparently
```

---

## 9. Complex Flow Diagrams

### 9.1 Task Lifecycle: Create → Complete → Delete

```
                          TASK LIFECYCLE
                              ┌─────┐
                              │ LIST │ (filtered: all/pending/in_progress/completed)
                              └──┬──┘
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
      ┌──────────┐       ┌──────────┐          ┌──────────┐
      │  Add (+) │       │ Click    │          │ Delete   │
      └────┬─────┘       │ Complete │          │ (trash)  │
           │             └────┬─────┘          └────┬─────┘
           ▼                  │                     │
     ┌────────────┐           ▼                     ▼
     │ ADD MODAL  │    ┌──────────────┐      ┌──────────┐
     │ ─────────  │    │ Optimistic   │      │ Optimistic│
     │ Title*     │    │ UI: strikethr│      │ remove    │
     │ Desc       │    │ + opac. 0.6  │      │ from list │
     │ Priority   │    └──────┬───────┘      └────┬───────┘
     │ Category   │           │                   │
     │ Est. min   │           ▼                   ▼
     │ Due date   │    ┌──────────────┐      ┌──────────┐
     │ Recurring  │    │ store.       │      │ store.   │
     │ ─────────  │    │ completeTask │      │ delete   │
     │ Cancel |   │    │ (id)         │      │ Task(id) │
     │ Create     │    └──────┬───────┘      └──────────┘
     └────┬───────┘           │
          │                   ▼
          ▼            ┌──────────────────┐
     ┌──────────┐      │ AnimatePresence  │
     │ store.   │      │ exit animation   │
     │ addTask  │      │ (opacity: 0,     │
     │ ({...})  │      │  scale: 0.95)    │
     └────┬─────┘      └──────────────────┘
          │
          ▼
     ┌──────────┐
     │ Modal    │
     │ closes   │
     │ State    │
     │ resets   │
     └──────────┘

BRANCH: Edit flow
  List → Click Edit (pencil icon on hover)
      → EDIT MODAL (pre-filled with task data)
          → Cancel → closes, no change
          → Save Changes → store.updateTask(id, {...})
              → Modal closes, list updates
```

### 9.2 Chat → Action Flow

```
                     CHAT → ACTION FLOW

User: "add task buy groceries"
  ┌─── POST /api/chat ──────────────────────────────┐
  │                                                  │
  → {API available}                                  │
  │   → LLM classifies intent: "task"                │
  │   → Generates response + suggested action        │
  │   → Returns: { response: "...", action: null }   │
  │   → Response rendered in chat bubble             │
  │                                                  │
  → {API unavailable}                                │
  │   → Demo fallback: keyword match "task"          │
  │   → Response: "I can help... Go to Tasks page"   │
  │   → No action generated                          │
  │                                                  │
  → User reads response                              │
  → User navigates to /tasks (via sidebar)            │
  → Opens Add modal manually                         │
  └──────────────────────────────────────────────────┘

FUTURE (planned):
  → LLM returns action: { type: "create_task", data: {...} }
  → Chat displays action card: "Create task: Buy groceries?"
  → User clicks "Confirm" → task created without leaving chat
  → Toast confirmation
```

### 9.3 Daily Briefing Generation Flow

```
                 BRIEFING GENERATION FLOW

Trigger: 7:00 AM cron OR user clicks "Run Now" in Automation

  1. POST /api/automation/trigger/briefing
  2. Backend collects context:
       ├── Tasks: overdue + due today + high priority
       ├── Habits: yesterday completion rates
       ├── Sleep: last night score
       ├── Courses: upcoming deadlines
       └── Opportunities: new matches
  3. Calls LLM with PromptLoader.get_agent("briefing_agent")
  4. {LLM succeeds}
       → Parse JSON → validate schema → save to daily_briefings
       → Push notification: "Your briefing is ready"
       → User opens /dashboard → briefing card at top
  5. {LLM fails}
       → Algorithmic fallback: top 3 tasks + generic quote
       → Save as algorithmic briefing
       → Log LLM failure

User sees briefing on /dashboard:
  ├── Time-based greeting
  ├── Date display
  ├── Stats grid (4 cards: productivity, tasks today, courses, goals)
  ├── Priority tasks (up to 4, with stagger animation)
  ├── ARIA's Pick recommendation
  ├── Quick Actions (4 buttons → /tasks, /ideas, /courses, /goals)
  └── Activity heatmap (30-day random grid)

User interactions:
  → Click task → /tasks
  → Click "View All" → /tasks
  → Click "Chat with ARIA" → /chat
  → Click quick action → target module
```

### 9.4 Opportunity: Scan → Apply → Track

```
                 OPPORTUNITY LIFECYCLE

Trigger: 6:00 AM cron scan OR "Run Now" in Automation

  1. POST /api/automation/trigger/radar
  2. Backend queries opportunity sources (Internshala, LinkedIn, etc.)
  3. AI matching: score 0-100
  4. Score > 70 → saved to opportunities table
  5. Score < 70 → archived (not shown to user)
  6. New matches included in morning briefing

User on /opportunities:
  ├── Header + "Scan Now" button
  ├── Filter dropdown (category)
  └── Card list: title, company, match score, deadline, tags

User clicks card:
  → Full detail view (inline or expand)
  → Actions: Save | Apply | Dismiss

User clicks "Track Application":
  → Modal: Application date, Notes, Status (select)
  → On save:
      → Opportunity status updates
      → Follow-up task auto-created (7 days)
      → If paid → linked to income

User clicks "Dismiss":
  → Opportunity removed from active list
  → Added to ignore list (prevents same match in future scans)
```

### 9.5 Habit Check-in → Streak → Nudge

```
                  HABIT CHECK-IN FLOW

User opens /habits:
  ├── Stats: Active habits (count), Total streak (sum), Avg consistency %
  ├── List: each habit shows:
  │     name | frequency | current_streak | consistency %
  │     active toggle | streak flame icon | delete
  └── Add Habit button

User toggles habit active/inactive:
  → supabase.update({ is_active: !isActive })
  → Local state updates immediately
  → (Habit logging — marking "Done" for the day — is NOT implemented
     in current frontend. Only habit definition CRUD exists.)

Streak calculation (backend):
  → Query habit_logs for last 90 days
  → Count consecutive days where status = "completed"
  → 3+ missed consecutive days → reset to 0
  → Otherwise maintain streak

Nudge trigger (6 PM daily):
  → Check courses: deadline < 7 days + pace behind → nudge
  → Check habits: not logged today by 6 PM → nudge
  → AI generates personalized message via nudge_agent

FUTURE (from wireframe):
  → Daily check-in modal at 8 PM reminder
  → Swipe-to-complete gesture on mobile
  → Calendar heatmap view for past 30 days
  → Streak milestone celebrations (7, 30, 60, 90 days)
```

---

## 10. Wireframe-to-Screen Cross-Reference

### 10.1 Complete Mapping

| Wireframe Document | Section | Wireframe View | Rendered Screen | Status | Notes |
|---|---|---|---|---|---|
| `01_APPLICATION_SHELL` | 1.1 Desktop Shell | Chrome layout | `(dashboard)/layout.tsx` | ⚠️ Orphaned | Defined but never rendered |
| `01_APPLICATION_SHELL` | 1.2 Tablet Shell | Collapsed sidebar | — | ❌ Not implemented | Responsive breakpoints not active |
| `01_APPLICATION_SHELL` | 1.3 Mobile Shell | Bottom nav + FAB | — | ❌ Not implemented | No responsive shell |
| `01_APPLICATION_SHELL` | 2.0 Sidebar | Nav groups + items | `Sidebar.tsx` | ✅ Implemented | 16 items, active state |
| `01_APPLICATION_SHELL` | 2.4 Command Center | Cmd+K palette | — | ❌ Not implemented | No shortcut handler |
| `01_APPLICATION_SHELL` | 3.0 Global Search | Search overlay | Navbar search bar | ⏳ Partial | UI exists, no search logic |
| `01_APPLICATION_SHELL` | 4.0 Notifications | Bell panel | Navbar bell icon | ⏳ Partial | Icon exists, no panel |
| `02_DASHBOARD` | 1.0 Morning Briefing | Hero card | `/dashboard` hero | ✅ Implemented | Greeting + date |
| `02_DASHBOARD` | 2.0 Productivity Score | Gauge widget | `/dashboard` stats grid | ✅ Implemented | Text metric, no gauge |
| `02_DASHBOARD` | 3.0 AI Insights | Recommendation card | `/dashboard` ARIA's Pick | ✅ Implemented | Top task recommendation |
| `02_DASHBOARD` | 5.0 Quick Actions | Action grid | `/dashboard` quick actions | ✅ Implemented | 4 action buttons |
| `02_DASHBOARD` | 7.0 Widget Config | Layout editor | — | ❌ Not implemented | No drag-to-configure |
| `03_TASKS_COURSES` | 1.0 Task List | Card list | `/tasks` | ✅ Implemented | With filters + stats |
| `03_TASKS_COURSES` | 1.1 Board View | Kanban columns | — | ❌ Not implemented | No view switcher |
| `03_TASKS_COURSES` | 1.2 Calendar View | Month grid | — | ❌ Not implemented | No calendar view |
| `03_TASKS_COURSES` | 1.3 Task Detail | Split/full panel | `/tasks` edit modal | ⏳ Partial | Modal, not split view |
| `03_TASKS_COURSES` | 1.4 Create Modal | Task form | `/tasks` add modal | ✅ Implemented | 7 fields + recurring |
| `03_TASKS_COURSES` | 2.0 Course Library | Grid/list | `/courses` | ✅ Implemented | List view |
| `03_TASKS_COURSES` | 2.1 Course Detail | Tabs (Overview/Lessons/Notes/Analytics) | — | ❌ Not implemented | Flat list only |
| `04_KNOWLEDGE_IDEAS` | 1.0 Resource Grid | Grid/list | `/resources` | ✅ Implemented | Basic list |
| `04_KNOWLEDGE_IDEAS` | 1.2 Knowledge Graph | Interactive graph | — | ❌ Not implemented | No graph component |
| `04_KNOWLEDGE_IDEAS` | 2.0 Idea Capture | Capture view | `/ideas` | ✅ Implemented | Basic list |
| `04_KNOWLEDGE_IDEAS` | 2.1 Pipeline Board | Kanban stages | — | ❌ Not implemented | No pipeline view |
| `04_KNOWLEDGE_IDEAS` | 3.0 Roadmap Canvas | Gantt/timeline | `/goals` | ⏳ Partial | Basic list, no Gantt |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 1.0 Discovery View | Grid/list | `/opportunities` | ✅ Implemented | With filter |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 1.1 Match Breakdown | Score card | — | ❌ Not implemented | No score visualization |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 2.0 Project Board | Kanban | `/projects` | ✅ Implemented | Basic list |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 2.1 Timeline View | Gantt | — | ❌ Not implemented | No Gantt |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 3.0 Income Overview | Dashboard | `/income` | ✅ Implemented | Basic list |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 3.1 Income Analytics | Charts | — | ❌ Not implemented | No charts |
| `06_ANALYTICS_AI` | 4.0 Chat View | Message list | `/chat` | ✅ Implemented | With demo fallback |
| `06_ANALYTICS_AI` | 4.1 Context Panel | Side panel | — | ❌ Not implemented | No context panel |
| `06_ANALYTICS_AI` | 4.2 Chat History | Thread list | — | ❌ Not implemented | No history sidebar |
| `06_ANALYTICS_AI` | 5.0 Empty State | Placeholder | All CRUD pages | ✅ Implemented | Icon + message + CTA |
| `06_ANALYTICS_AI` | 5.1 Loading State | Skeleton | All pages | ✅ Implemented | Spinner pattern |
| `06_ANALYTICS_AI` | 5.2 Error State | Error card | — | ❌ Not implemented | No error UI |
| `07_SUPPLEMENT` | 1.0 Timer View | Pomodoro | `/time` | ✅ Implemented | With idle detection |
| `07_SUPPLEMENT` | 1.1 Entries Log | Session list | `/time` recent sessions | ✅ Implemented | |
| `07_SUPPLEMENT` | 1.2 Statistics | Charts | `/time` peak hours | ✅ Implemented | Hour breakdown |
| `07_SUPPLEMENT` | 2.0 Semester View | Course grid | `/academics` | ✅ Implemented | With CGPA |
| `07_SUPPLEMENT` | 3.0 YouTube Library | Video grid | `/youtube` | ✅ Implemented | Basic list |
| `07_SUPPLEMENT` | 4.0 Automation Rules | Card list | `/automation` | ✅ Implemented | 6 cards with run |
| `07_SUPPLEMENT` | 5.0 AI Components | GhostHint, StreamingText | Across app | ⏳ Partial | Chat has thinking animation |

### 10.2 Coverage Summary

| Category | Total Views (Wireframe) | Implemented | Partial | Not Implemented | Coverage % |
|---|---|---|---|---|---|
| Application Shell | 10 | 1 | 2 | 7 | 30% |
| Dashboard | 8 | 4 | 0 | 4 | 50% |
| Tasks & Courses | 8 | 3 | 1 | 4 | 50% |
| Knowledge & Ideas | 8 | 2 | 1 | 5 | 38% |
| Opportunities, Projects, Income | 9 | 4 | 0 | 5 | 44% |
| Analytics, AI, Settings | 6 | 2 | 0 | 4 | 33% |
| Supplement (Time, Academics, etc.) | 8 | 6 | 0 | 2 | 75% |
| **Total** | **57** | **22** | **4** | **31** | **46%** |

---

## 11. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-13 | AI Engineering | Initial screen flows document — 18 pages, 5-state machines, modal registry, deep link map, auth lifecycle, wireframe cross-reference |

---

*End of Frontend Screen Flows Document — Enterprise v1.0.0*
