# Frontend Screen Flows â€” ARIA OS

## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-FSC-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-13 |
| Classification | Enterprise UX â€” Screen Flow Specification |
| Target Audience | Frontend Engineers, UX Designers, QA Engineers |
| Supersedes | â€” |
| Related Docs | Wireframe System (8 parts), `UserFlows.md`, `UseCases.md`, `UserJourneyArchitecture.md`, `FrontendRoutingNavigation.md`, `ModulesImplementationSpec.md` |

---

## 1. Executive Summary

This document defines every screen-to-screen transition, screen state machine, modal dependency, and navigation topology across all 18 pages of ARIA OS. It forms the bridge between the **wireframe system** (what the UI looks like) and the **implementation** (what the code does).

**What this document covers:**
- **Navigation topology** â€” every screen as a node, every transition as an edge
- **Screen state machines** â€” the 5 states each screen can be in (Loading, Empty, Error, Populated, Offline)
- **Transition triggers** â€” every action that moves the user from one screen state to another or to a different screen
- **Modal & overlay flows** â€” which overlays spawn from which screens, what dismisses them, where the user lands after
- **Deep link resolution** â€” how notifications and external links map to screens
- **Auth flow states** â€” unauthenticated â†’ authenticated session lifecycle
- **Wireframe-to-screen cross-reference** â€” every wireframe section mapped to its rendered screen

**Screen Flow Notation Key:**
```
[Screen Name]           â€” A distinct page/module route
{Screen State}          â€” One of Loading | Empty | Error | Populated | Offline
[Action â†’]              â€” User or system trigger
â”Œâ”€â” Â· â”€â”€ Â· â””â”€â”˜          â€” Decision branches
=> [Overlay]            â€” Modal, sheet, dialog, or panel spawns
==> [Background]         â€” Async background process
```

---

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
stateDiagram-v2
  direction LR
  [*] --> Landing: First Visit
  Landing --> Login: Click "Get Started"
  Login --> Dashboard: OAuth Success
  Landing --> Dashboard: Already Authenticated

  state Dashboard {
    [*] --> Loading
    Loading --> Populated: Data Fetched
    Loading --> Empty: No Data
    Loading --> Error: Fetch Failed
    Error --> Loading: Retry
    Empty --> Populated: User Creates Data
    Populated --> Offline: Connection Lost
    Offline --> Populated: Connection Restored
  }

  Dashboard --> Tasks: Nav Click
  Dashboard --> Courses: Nav Click
  Dashboard --> Goals: Nav Click
  Dashboard --> Habits: Nav Click
  Dashboard --> Sleep: Nav Click
  Dashboard --> Time: Nav Click
  Dashboard --> Income: Nav Click
  Dashboard --> Projects: Nav Click
  Dashboard --> Ideas: Nav Click
  Dashboard --> Resources: Nav Click
  Dashboard --> Opportunities: Nav Click
  Dashboard --> Chat: Nav Click
  Dashboard --> Automation: Nav Click

  Tasks --> Dashboard: Nav/Back
  Courses --> Dashboard: Nav/Back
  Goals --> Dashboard: Nav/Back
  Habits --> Dashboard: Nav/Back
  Sleep --> Dashboard: Nav/Back
  Time --> Dashboard: Nav/Back
  Income --> Dashboard: Nav/Back
  Projects --> Dashboard: Nav/Back
  Ideas --> Dashboard: Nav/Back
  Resources --> Dashboard: Nav/Back
  Opportunities --> Dashboard: Nav/Back
  Chat --> Dashboard: Nav/Back
  Automation --> Dashboard: Nav/Back

  state Offline {
    [*] --> CachedMode
    CachedMode --> [*]
  }

  Dashboard --> LoggedOut: Session Expired
  LoggedOut --> Login: Re-authenticate
```

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
graph TD
  subgraph Auth["ðŸ” Auth Boundary"]
    L[/Landing Page\] --> LG[/Login - OAuth\]
    LG --> DASH[/Dashboard\]
    L --> DASH
  end

  subgraph Core["ðŸ“Š Core Modules"]
    DASH --> TASKS[/Tasks\]
    DASH --> COURSES[/Courses\]
    DASH --> GOALS[/Goals\]
    DASH --> HABITS[/Habits\]
    DASH --> SLEEP[/Sleep\]
    DASH --> TIME[/Time Tracking\]
  end

  subgraph Growth["ðŸ“ˆ Growth Modules"]
    DASH --> INCOME[/Income\]
    DASH --> PROJECTS[/Projects\]
    DASH --> IDEAS[/Ideas\]
    DASH --> RESOURCES[/Resources\]
    DASH --> OPPORTUNITIES[/Opportunities\]
  end

  subgraph Intelligence["ðŸ¤– Intelligence Modules"]
    DASH --> CHAT[/Chat - ARIA\]
    DASH --> AUTO[/Automation\]
  end

  subgraph Overlays["â¬†ï¸ System Overlays"]
    CP[Command Palette<br/>Cmd+K] --> TASKS
    CP --> COURSES
    CP --> CHAT
    QC[Quick Create âŠ•] --> TASKS
    QC --> IDEAS
    NOTIF[Notifications ðŸ””] --> TASKS
    NOTIF --> DASH
  end

  LG -.->|Session Expires| LG

  style Core fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Growth fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Intelligence fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style Auth fill:#13151A,stroke:#818CF8,color:#F1F5F9
  style Overlays fill:#13151A,stroke:#F59E0B,color:#F1F5F9
```

---

## 2. Navigation Topology

### 2.1 Complete Navigation Graph

```
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚                          AUTH BOUNDARY                                     â”‚
                         â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                            â”‚
                         â”‚  â”‚  /      â”‚â”€â”€â”€â†’â”‚  /login  â”‚â”€â”€â”€â”€â†’â”‚  /dashboardâ”‚   (protected after auth)  â”‚
                         â”‚  â”‚ Landing â”‚    â”‚ OAuth    â”‚     â”‚           â”‚                            â”‚
                         â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜                            â”‚
                         â”‚       â”‚                                  â”‚                                â”‚
                         â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                â”‚
                         â”‚                                                                           â”‚
                         â”‚                          SIDEBAR (16 nav items)                           â”‚
                         â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
                         â”‚  â”‚ Dashboard â”‚  Tasks   â”‚ Courses  â”‚ YouTube  â”‚ Resources â”‚  Ideas   â”‚    â”‚
                         â”‚  â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”˜    â”‚
                         â”‚        â”‚          â”‚         â”‚         â”‚         â”‚          â”‚         â”‚
                         â”‚  â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”´â”€â”€â”€â”€â”€â”â”Œâ”€â”€â”´â”€â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”´â”€â”€â”€â”€â”   â”‚
                         â”‚  â”‚  /dashboardâ”‚â”‚ /tasks  â”‚â”‚ /coursesâ”‚â”‚ /youtubeâ”‚â”‚ /resrcs â”‚â”‚ /ideas  â”‚   â”‚
                         â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
                         â”‚        â”‚          â”‚         â”‚         â”‚         â”‚          â”‚         â”‚
                         â”‚  â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”´â”€â”€â”€â”€â”€â”â”Œâ”€â”€â”´â”€â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”´â”€â”€â”€â”€â”   â”‚
                         â”‚  â”‚   Goals  â”‚â”‚ Opport. â”‚â”‚ Income  â”‚â”‚ Projectsâ”‚â”‚Academicsâ”‚â”‚ Habits  â”‚   â”‚
                         â”‚  â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜   â”‚
                         â”‚        â”‚          â”‚         â”‚         â”‚         â”‚          â”‚         â”‚
                         â”‚  â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”´â”€â”€â”€â”€â”â”Œâ”€â”€â”´â”€â”€â”€â”€â”€â”â”Œâ”€â”€â”´â”€â”€â”€â”€â”€â”â”Œâ”€â”€â”€â”´â”€â”€â”€â”€â”   â”‚
                         â”‚  â”‚   Sleep  â”‚â”‚  Time   â”‚â”‚  Chat   â”‚â”‚  Auto   â”‚â”‚  (all   â”‚â”‚  route  â”‚   â”‚
                         â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

                                         SYSTEM OVERLAYS (accessible from any screen)
                          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                          â”‚  [Cmd+K] Command Palette  â”‚  [âŠ•] Quick Create  â”‚  [ðŸ””] Notifications â”‚
                          â”‚  [ðŸ”] Global Search Panel â”‚  [âœ•] Sign Out Dialog                   â”‚
                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 2.2 Edge Types

| Edge Type | Trigger | Example | Visual Cue |
|---|---|---|---|
| **Primary Nav** | Sidebar link click | `/dashboard` â†’ `/tasks` | Sidebar active state change |
| **Secondary Nav** | Content card/link click | `/dashboard` â†’ `/tasks` (via "View All") | ChevronRight icon |
| **Tertiary Nav** | Action button | `/tasks` â†’ Add Modal | Modal slide-up animation |
| **Deep Link** | Notification/external URL | Push notification â†’ `/tasks/abc-123` | Route param injection |
| **Auth Redirect** | Session change | `/dashboard` â†’ `/login` (on expiry) | Full page redirect |
| **System Overlay** | Keyboard shortcut | Any screen â†’ Command Palette (Cmd+K) | Overlay with backdrop |

### 2.3 Route Parameter Flow

| Route Pattern | Params | Example | Resolution |
|---|---|---|---|
| `/[module]` | â€” | `/tasks` | Module list/default view |
| `/[module]/[id]` | `id: string` | `/tasks/abc-123` | Detail view (future) |
| `/[module]?view=` | `view: string` | `/tasks?view=board` | View switcher (future) |
| `/[module]?filter=` | `filter: string` | `/opportunities?filter=internships` | Pre-filtered list (future) |
| `/login?redirect=` | `redirect: string` | `/login?redirect=/tasks/abc` | Post-auth redirect target |

**Current State:** Routes use zero URL parameters. All 18 pages are flat routes with no dynamic segments. The auth guard redirect is the only parameterized navigation (`router.push('/login')`). Dynamic route segments (`/[id]`), view params (`?view=`), and filter params (`?filter=`) are wireframe-specified but not implemented.

---

## 3. Application Shell State Machine

### 3.1 Shell Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      APPLICATION SHELL                         â”‚
â”‚                                                                â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”‚
â”‚  â”‚  NAVBAR (fixed top, 64px, z-40)                       â”‚     â”‚
â”‚  â”‚  [Search........]         [ðŸ”” Notif]  [ðŸ‘¤ User â–¼]    â”‚     â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚ SIDEBAR â”‚ â”‚                                           â”‚   â”‚
â”‚  â”‚ (fixed   â”‚ â”‚          CONTENT AREA                     â”‚   â”‚
â”‚  â”‚  left,   â”‚ â”‚    (scrollable, pt-20, px-6, pb-6)       â”‚   â”‚
â”‚  â”‚  240px)  â”‚ â”‚                                           â”‚   â”‚
â”‚  â”‚          â”‚ â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚   â”‚
â”‚  â”‚ nav itemsâ”‚ â”‚  â”‚     PAGE-SPECIFIC CONTENT           â”‚  â”‚   â”‚
â”‚  â”‚ 16 total â”‚ â”‚  â”‚     (rendered per route)            â”‚  â”‚   â”‚
â”‚  â”‚          â”‚ â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Critical Issue (Orphaned Layout):** The `(dashboard)/layout.tsx` wraps Sidebar + Navbar but NO pages are nested inside it. All 16 protected pages live at root `app/` level. The Sidebar + Navbar are **defined but never rendered** in the current routing structure. Every protected page renders as a bare content area with no chrome.

### 3.2 Shell States

| State | Condition | Sidebar | Navbar | Content Area |
|---|---|---|---|---|
| **Loading** | Auth check in progress (useAuth loading) | Not rendered | Not rendered | Full-screen spinner |
| **Unauthenticated** | `user === null` after auth check | Not rendered | Not rendered | Redirect to `/login` |
| **Authenticated** | `user !== null` | Rendered (but orphaned â€” not visible) | Rendered (but orphaned â€” not visible) | Page content |
| **Error** | Auth network failure | Not rendered | Not rendered | Error state (not implemented) |

### 3.3 Sidebar Navigation Map

```
Sidebar (240px fixed left)
â”œâ”€â”€ Dashboard    â†’  /dashboard       Icon: LayoutDashboard
â”œâ”€â”€ Tasks        â†’  /tasks           Icon: CheckSquare
â”œâ”€â”€ Courses      â†’  /courses         Icon: BookOpen
â”œâ”€â”€ YouTube      â†’  /youtube         Icon: Youtube
â”œâ”€â”€ Resources    â†’  /resources       Icon: FileText
â”œâ”€â”€ Ideas        â†’  /ideas           Icon: Lightbulb
â”œâ”€â”€ Goals        â†’  /goals           Icon: Target
â”œâ”€â”€ Opportunities â†’ /opportunities   Icon: Radar
â”œâ”€â”€ Income       â†’  /income          Icon: Wallet
â”œâ”€â”€ Projects     â†’  /projects        Icon: FolderKanban
â”œâ”€â”€ Academics    â†’  /academics       Icon: GraduationCap
â”œâ”€â”€ Habits       â†’  /habits          Icon: Moon
â”œâ”€â”€ Sleep        â†’  /sleep           Icon: Moon
â”œâ”€â”€ Time         â†’  /time            Icon: Clock
â”œâ”€â”€ Chat         â†’  /chat            Icon: MessageCircle
â””â”€â”€ Automation   â†’  /automation      Icon: Zap
```

**Active State Logic:**
```
pathname === item.href
  â†’ True:  bg-accent-primary/10 text-accent-primary (highlighted)
  â†’ False: text-text-secondary hover:bg-background-elevated (default)
```

### 3.4 Navbar Interaction Map

| Element | Trigger | Transition |
|---|---|---|
| Search input | Focus / click | Opens global search overlay (not implemented â€” placeholder only) |
| Bell icon | Click | Opens notification panel (not implemented â€” placeholder only) |
| User avatar | Click | Toggles dropdown: Sign Out |
| Sign Out | Click | `supabase.auth.signOut()` â†’ `router.push('/')` |

---

## 4. Screen Flow Specifications

### 4.1 System Pages

#### 4.1.1 `/` â€” Landing / Auth Redirector

| Property | Value |
|---|---|
| **Wireframe Ref** | Not in wireframe system (auth shell only) |
| **Type** | Auth boundary |
| **Auth Required** | No |

**State Machine:**
```
Entry: browser navigation to /
  â†’ {useAuth().loading === true}
      â†’ [State: Loading] â€” Full-screen centered spinner + "Loading..."
  â†’ {useAuth().loading === false}
      â†’ {user !== null}
          â†’ [Action: router.push('/dashboard')] â€” Immediate redirect
      â†’ {user === null}
          â†’ [Action: router.push('/login')] â€” Immediate redirect
```

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| Page load | â€” | Loading | `useEffect` on mount |
| Auth resolved (user) | Loading | `/dashboard` | `router.push('/dashboard')` |
| Auth resolved (no user) | Loading | `/login` | `router.push('/login')` |

**Component Visibility Matrix:**

| Component | Loading | Notes |
|---|---|---|
| Spinner + text | âœ… Visible | `Loader2` icon + "Loading..." |
| Background | âœ… Visible | `bg-background-dark` full viewport |

**Entry Points:** Browser URL bar, bookmark, external link.
**Exit Points:** `/dashboard` (if authed), `/login` (if not authed).

---

#### 4.1.2 `/login` â€” OAuth Login

| Property | Value |
|---|---|
| **Wireframe Ref** | Not in wireframe system (auth screen â€” standalone) |
| **Type** | Public authentication |
| **Auth Required** | No (public) |

**State Machine:**
```
Entry: /login (from redirect or direct nav)
  â†’ [State: Populated] â€” Login card rendered immediately
  â†’ User clicks "Continue with Google"
      â†’ [State: Loading (local)] â€” Button shows "Signing in...", disabled
      â†’ supabase.auth.signInWithOAuth({ provider: 'google' })
          â†’ {OAuth succeeds}
              â†’ Redirected to /dashboard (via Supabase OAuth redirect)
          â†’ {OAuth fails}
              â†’ [State: Error] â€” console.error log (no user-facing error)
              â†’ [Action: setLoading(false)] â€” Button re-enables
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
| Three.js background | âœ… Visible | âœ… Visible | `ThreeBackground` component |
| Gradient overlay | âœ… Visible | âœ… Visible | Readability overlay |
| Logo + title | âœ… Visible | âœ… Visible | Animated with framer-motion |
| Google button | âŒ Disabled | âœ… Enabled | Shows spinner when loading |
| Feature preview grid | âœ… Visible | âœ… Visible | 3-column stats always visible |

**Entry Points:** `/` redirect (unauthed), `/login` direct, session expiry redirect.
**Exit Points:** `/dashboard` (on successful OAuth), `/` (on manual nav away).

---

### 4.2 Dashboard

#### 4.2.1 `/dashboard` â€” Command Center

| Property | Value |
|---|---|
| **Wireframe Ref** | `02_DASHBOARD_WIREFRAMES.md` â€” Morning Briefing, Widget Configuration, Layout Presets |
| **Type** | Aggregation view |
| **Auth Required** | Yes |

**State Machine:**
```
Entry: /dashboard (internal redirect or direct nav)
  â†’ [State: Loading] â€” Full-screen spinner
  â†’ {useAuth resolves}
      â†’ {user === null}
          â†’ [Action: router.push('/login')]
      â†’ {user !== null}
          â†’ [Action: fetchTasks()] â€” Zustand store fetch
          â†’ {tasks.length === 0 && fetch complete}
              â†’ [State: Empty] â€” All sections render with zero-state
          â†’ {tasks.length > 0}
              â†’ [State: Populated] â€” Full dashboard rendered
```

**Sub-states (content sections):**

| Section | Populated | Empty | Loading |
|---|---|---|---|
| Hero greeting | âœ… Time-based greeting + date | Same | Not rendered |
| Stats grid (4 cards) | âœ… Computed metrics shown | All show 0 | Not rendered |
| Priority tasks | âœ… Up to 4 tasks with stagger animation | "All caught up!" CTA to /tasks | Not rendered |
| ARIA's Pick | âœ… Top task recommendation | "Add tasks..." prompt | Not rendered |
| Quick actions | âœ… 4 action buttons (always rendered) | Same | Not rendered |
| Activity heatmap | âœ… 30 random cells | Same (random) | Not rendered |

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

**Modal Dependency:** None â€” all navigations are full-page transitions.

---

### 4.3 Module Pages (CRUD List)

The following 15 pages follow an **identical screen flow pattern** with module-specific data. They are documented as a group with individual differences noted.

#### 4.3.1 Common Template (All CRUD Pages)

```
Entry: /[module]
  â†’ [State: Loading] â€” Full-screen centered spinner
      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
      â”‚  <div className="w-12 h-12 rounded-xl border-2          â”‚
      â”‚         border-accent-primary/30 animate-pulse-glow">    â”‚
      â”‚    <div className="w-8 h-8 border-2 border-accent-      â”‚
      â”‚         primary border-t-transparent rounded-full        â”‚
      â”‚         animate-spin" />                                 â”‚
      â”‚  </div>                                                  â”‚
      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
  â†’ {mounted === true, authLoading === false}
      â†’ {user === null}
          â†’ [Action: router.push('/login')]
      â†’ {user !== null}
          â†’ [Action: fetchData()] â€” module-specific query
          â†’ {fetchData() succeeds}
              â†’ {data.length === 0}
                  â†’ [State: Empty]
                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                      â”‚  Module icon (64px)                   â”‚
                      â”‚  "No [module items] found"            â”‚
                      â”‚  "Start by adding your first [item]"  â”‚
                      â”‚  [Button: "Add [Item]"] â†’ opens modal â”‚
                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â†’ {data.length > 0}
                  â†’ [State: Populated]
                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                      â”‚  Header: title + subtitle + Add btn  â”‚
                      â”‚  Stats grid (1-3 metric cards)       â”‚
                      â”‚  Filter tabs (module-specific)       â”‚
                      â”‚  Content list/grid with animations   â”‚
                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
          â†’ {fetchData() fails}
              â†’ [State: Error] â€” no user-facing error UI
              â†’ `console.error` log only (15/18 pages)
              â†’ Falls back to empty state
  â†’ User clicks "Add" button
      â†’ [Overlay: Add Modal]
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â”‚  Fixed overlay: bg-black/70 backdrop-blur-sm    â”‚
          â”‚  Centered card: max-w-lg, bg-background-card    â”‚
          â”‚  Header: title + X close button                 â”‚
          â”‚  Form fields (module-specific)                  â”‚
          â”‚  Footer: Cancel + Submit buttons                â”‚
          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
          â†’ User fills form â†’ clicks Submit
              â†’ [Action: supabase.insert() or store method]
              â†’ {success}
                  â†’ [Action: close modal, refetch data]
                  â†’ Optimistic: update local state directly
              â†’ {failure}
                  â†’ Modal stays open (no error toast)
          â†’ User clicks Cancel / X / Escape
              â†’ [Action: close modal]
              â†’ [State: Previous state]
  â†’ User clicks Edit on item
      â†’ [Overlay: Edit Modal] â€” same pattern as Add
  â†’ User clicks Delete on item
      â†’ [Action: supabase.delete() or store method]
      â†’ Optimistic: item removed from local state
```

**Component Visibility Matrix (all CRUD pages):**

| Component | Loading | Empty | Populated | Error |
|---|---|---|---|---|
| Spinner | âœ… | âŒ | âŒ | âŒ |
| Header (title + subtitle) | âŒ | âœ… | âœ… | âœ… |
| "Add" button | âŒ | âœ… | âœ… | âœ… |
| Stats cards | âŒ | âœ… (zeros) | âœ… (computed) | âŒ |
| Filter tabs | âŒ | âœ… | âœ… | âŒ |
| Content list | âŒ | âŒ | âœ… | âŒ |
| Empty state icon + message | âŒ | âœ… | âŒ | âŒ |
| Empty state CTA | âŒ | âœ… | âŒ | âŒ |
| Add Modal | âŒ | Spawned by button | Spawned by button | âŒ |
| Edit Modal | âŒ | N/A | Spawned by button | âŒ |

---

#### 4.3.2 Per-Module Screen Flow Variations

##### `/tasks` â€” Task Manager (Zustand-powered)

| Property | Value |
|---|---|
| **Wireframe Ref** | `03_TASKS_AND_COURSES_WIREFRAMES.md` â€” Task List, Board, Calendar, Detail, Create Modal |
| **Data Source** | Zustand store (`useTaskStore`) |
| **Store Methods** | `fetchTasks`, `addTask`, `updateTask`, `deleteTask`, `completeTask` |
| **State Variables** | `showAddModal`, `editingTask`, `filter`, `newTask` (7 fields) |
| **Filters** | `all` / `pending` / `in_progress` / `completed` (4 tabs with counts) |
| **Stats Cards** | To Do (count), In Progress (count), Done (count) â€” clickable filter shortcut |
| **Content** | Card list with drag handle, priority indicator, title, description, tags, actions |
| **Actions/Task** | Complete (check), Edit (pencil), Delete (trash) â€” revealed on hover |
| **Add Modal** | Title*, Description, Priority (select), Category (select), Est. Minutes, Due Date, Recurring toggle |
| **Edit Modal** | Title, Description, Priority, Category |
| **Error Handling** | âŒ â€” No try/catch on store operations (only on Supabase direct calls) |
| **Transition: Complete** | Optimistic â†’ store.updateTask â†’ re-render (no backend confirmation) |
| **Transition: Delete** | Optimistic â†’ store.deleteTask â†’ item fades out (AnimatePresence exit animation) |

**Entry Points:** `/tasks` direct, `/dashboard` "View All" or task card click, `/chat` intent â†’ task link.
**Exit Points:** `/dashboard` (sidebar), any module (sidebar), `/login` (auth expiry).

---

##### `/courses` â€” Course Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | `03_TASKS_AND_COURSES_WIREFRAMES.md` â€” Course Library, Detail, Progress |
| **Data Source** | Supabase direct (useState) |
| **Filters** | Not implemented (all courses shown) |
| **Stats Cards** | Total courses, Active courses, Completed courses |
| **Add Modal** | Name*, Platform (Udemy/Coursera/NPTEL/College/YouTube/Other), URL, Total hours, Hours/week, Deadline, Why enrolled |
| **Error Handling** | âŒ â€” No try/catch on Supabase queries |

---

##### `/habits` â€” Habit Engine

| Property | Value |
|---|---|
| **Wireframe Ref** | Habit section (supplement) â€” Tracker View, Detail, Add Modal |
| **Data Source** | Supabase direct (useState) |
| **Stats Cards** | Active habits, Total streak (sum), Avg consistency % |
| **Content** | Card list: name, frequency, streak, consistency %, active toggle, streak flame icon |
| **Actions/Habit** | Toggle active (switch), Delete (trash) |
| **Add Modal** | Name*, Frequency (daily/weekly), Time target (minutes) |
| **Error Handling** | âŒ â€” No try/catch on Supabase queries |

---

##### `/goals` â€” Goal/Roadmap

| Property | Value |
|---|---|
| **Wireframe Ref** | `04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` â€” Roadmap Canvas, Timeline, Milestones, Dependencies |
| **Data Source** | Supabase direct |

---

##### `/ideas` â€” Idea Vault

| Property | Value |
|---|---|
| **Wireframe Ref** | `04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` â€” Capture View, Pipeline Board, Analysis, Detail |
| **Data Source** | Supabase direct |
| **Detail Modal** | `selectedIdea` state â€” opens detail overlay for individual idea |

---

##### `/income` â€” Income Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | `05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` â€” Income Overview, Sources, Analytics |
| **Data Source** | Supabase direct |

---

##### `/projects` â€” Project Board

| Property | Value |
|---|---|
| **Wireframe Ref** | `05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` â€” Project Board, Timeline, Detail |
| **Data Source** | Supabase direct |

---

##### `/resources` â€” Knowledge Vault

| Property | Value |
|---|---|
| **Wireframe Ref** | `04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` â€” Resource Grid/List, Search, Graph, Detail |
| **Data Source** | Supabase direct |

---

##### `/opportunities` â€” Opportunity Radar

| Property | Value |
|---|---|
| **Wireframe Ref** | `05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` â€” Discovery, Recommendations, Filter, Detail |
| **Data Source** | Supabase direct |
| **Filters** | Category filter dropdown |

---

##### `/sleep` â€” Sleep Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement â€” Log View, Analytics, Log Modal |
| **Data Source** | Supabase direct |

---

##### `/youtube` â€” YouTube Library

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement â€” Library View, Video Detail, Add Modal |
| **Data Source** | Supabase direct |

---

##### `/academics` â€” Academic Tracker

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement â€” Semester View, Subject Detail, Add Subject Modal |
| **Data Source** | Supabase direct |
| **Special** | Custom CGPA calculation algorithm |

---

#### 4.3.3 `/time` â€” Time Tracker (Timer + Pomodoro)

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement â€” Timer View (Pomodoro), Entries Log, Statistics, Manual Entry Modal |
| **Data Source** | Supabase direct (useState) |
| **State Variables** | `activeTimer`, `elapsed`, `pomodoroMode`, `pomodoroPhase`, `pomodoroTimeLeft`, `showIdleWarning`, `lastActivity`, `focusHours` |

**State Machine:**
```
Entry: /time
  â†’ [State: Loading] â€” Standard spinner
  â†’ {user !== null}
      â†’ [Action: fetchEntries()] â€” supabase query
      â†’ {found active timer (entry with no end_time)}
          â†’ [Sub-state: Timer Running] â€” Shows elapsed time + Stop button
      â†’ {no active timer}
          â†’ [Sub-state: Timer Stopped] â€” Shows Start button
  â†’ User clicks "Start Timer"
      â†’ [Action: supabase.insert() with start_time]
      â†’ [Sub-state: Timer Running]
      â†’ 1-second interval: setElapsed(Math.floor(now - startTime / 1000))
      â†’ {15+ minutes no activity (lastActivity check)}
          â†’ [Sub-state: Idle Warning] â€” Yellow banner "No activity detected"
          â†’ User clicks "I'm still working" â†’ dismisses warning
  â†’ User clicks "Stop Timer"
      â†’ [Action: supabase.update() with end_time + duration]
      â†’ [Sub-state: Timer Stopped]
      â†’ Duration >= 90 min â†’ marked as deep_work
  â†’ User toggles "Pomodoro ON"
      â†’ [Sub-state: Pomodoro Active]
      â†’ 25-min countdown â†’ auto-switch to 5-min break â†’ auto-loop
  â†’ Work session ends (90+ min)
      â†’ [Action: focusHours analysis] â€” top 5 peak hours computed
```

**Transition Triggers:**

| Trigger | From State | To State / Screen | Mechanism |
|---|---|---|---|
| Start button | Timer Stopped | Timer Running | `startTimer()` â†’ supabase insert |
| Stop button | Timer Running | Timer Stopped | `stopTimer()` â†’ supabase update |
| Idle 15+ min | Timer Running | Idle Warning visible | `useEffect` interval check |
| "I'm working" | Idle Warning | Timer Running (reset) | `setLastActivity(Date.now())` |
| Pomodoro toggle | Any | Pomodoro Active / Inactive | `setPomodoroMode(!pomodoroMode)` |
| Timer completes | Work phase | Break phase | `pomodoroTimeLeft <= 1` â†’ phase swap |

**Entry Points:** `/time` direct, sidebar, `/tasks` â†’ "Start Focus" (future).
**Exit Points:** Sidebar modules, `/login`.

---

#### 4.3.4 `/chat` â€” ARIA Chat Interface

| Property | Value |
|---|---|
| **Wireframe Ref** | `06_ANALYTICS_AI_SETTINGS_STATES_WIREFRAMES.md` â€” Chat View, Thread, Context Panel, History |
| **Data Source** | Supabase (messages) + fetch(/api/chat) + demo fallback |
| **State Variables** | `messages`, `input`, `loading`, `mounted` |
| **Refs** | `messagesEndRef` â€” auto-scroll to bottom |

**State Machine:**
```
Entry: /chat
  â†’ [State: Loading] â€” Neon spinner with cyan glow animation
  â†’ {user !== null}
      â†’ [Action: fetchMessages()] â€” supabase query (50 latest)
      â†’ {messages.length === 0}
          â†’ [State: Empty] â€” ARIA avatar + greeting + instruction text
      â†’ {messages.length > 0}
          â†’ [State: Populated] â€” Message history with staggered Framer Motion
  â†’ User types message + presses Enter / Send
      â†’ {input.trim() === '' || loading === true}
          â†’ Blocked â€” no action
      â†’ [Action: setLoading(true)]
      â†’ [Action: Optimistic â€” add temp user message to UI]
      â†’ [Action: fetch('/api/chat')]
          â†’ {API responds successfully}
              â†’ [Action: Add assistant response to messages]
              â†’ [Action: supabase.insert() save both messages]
          â†’ {API fails (network error, 500)}
              â†’ [Fallback: getDemoResponse()]
              â†’ [Action: Add demo response to messages]
      â†’ [Action: setLoading(false)]
      â†’ [Action: scrollToBottom()]
  â†’ User presses Enter (without Shift)
      â†’ Trigger handleSend
  â†’ User presses Shift+Enter
      â†’ Newline in input (not send)
```

**Conversation Flow:**
```
User: "task buy groceries"
  API: â†’ intent: task â†’ response links to /tasks
  Demo: â†’ "I can help you manage tasks! Go to the Tasks page..."
  [Action: user may navigate to /tasks]

User: "help"
  API â†’ intent: general
  Demo â†’ feature overview

User: "what's my productivity score?"
  API â†’ intent: query â†’ supabase query
  Demo â†’ "I'm here to help!"
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

#### 4.3.5 `/automation` â€” Automation Config

| Property | Value |
|---|---|
| **Wireframe Ref** | Supplement â€” Rules List, Rule Detail, Create Rule Modal, Log |
| **Data Source** | fetch() to backend API + local useState |
| **State Variables** | `running`, `results`, `enabledAutomations` (6 toggles) |

**State Machine:**
```
Entry: /automation
  â†’ [State: Loading] â€” Standard spinner
  â†’ [State: Populated] â€” 6 automation cards rendered immediately (no data fetch)
  â†’ User clicks "Run Now" on an automation
      â†’ [Action: setRunning(type)]
      â†’ [Action: fetch(endpoint)]
          â†’ {response ok}
              â†’ [Action: setResults(data)] â€” Results panel appears below
          â†’ {response fails}
              â†’ [Action: setResults({status: 'error', message})] â€” Error panel
      â†’ [Action: setRunning(null)]
  â†’ User toggles automation switch
      â†’ [Action: setEnabledAutomations(prev => ...)] â€” Local state only
      â†’ (no backend persistence for toggles)
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
| **Add [Item]** | "Add" button click | Any CRUD page (tasks, courses, habits, etc.) | Cancel / X / Escape / Submit success | Same screen (refetch) | Scale 0.95â†’1 + fade |
| **Edit [Item]** | "Edit" icon click | Tasks (editingTask state) | Cancel / X / Submit success | Same screen (update) | Scale 0.95â†’1 + fade |
| **Quick Capture** | Cmd+K / âŠ• FAB | Any screen (future) | Escape / Submit | Same screen | Slide-up |
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
**Backdrop click:** Closes modal (not implemented â€” only X/Cancel buttons close).

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
| Browser bookmark | `/[module]` | Renders flat page | âœ… Working |
| URL bar direct | `/[module]` | Renders flat page | âœ… Working |
| OAuth redirect | `/dashboard` | Renders dashboard | âœ… Working |

### 6.2 Future Deep Link Schema (from Wireframe Spec)

```
Scheme: https://app.aria-os.com/[module]/[id]?[params]

Navigation:
  /tasks/abc-123                 â†’ Task detail view (not implemented)
  /tasks?view=board              â†’ Kanban board view (not implemented)
  /tasks?filter=high             â†’ Pre-filtered high priority (not implemented)
  /courses/abc-123?tab=lessons   â†’ Course detail, lessons tab (not implemented)
  /chat?thread=abc-123           â†’ Open specific chat thread (not implemented)
  /settings/appearance           â†’ Direct to settings section (not implemented)
```

### 6.3 Deep Link Resolution Flow (Planned)

```
Incoming URL /tasks/abc-123
  â†’ middleware.ts (not implemented) intercepts
  â†’ Parse params: module=tasks, id=abc-123
  â†’ Auth check (middleware)
      â†’ Not authed â†’ redirect /login?redirect=/tasks/abc-123
      â†’ Authed â†’ proceed
  â†’ Route: /tasks with query param id=abc-123
  â†’ Page renders list, then fetches detail for abc-123
  â†’ Opens detail modal automatically
```

---

## 7. Auth Flow State Machine

### 7.1 Complete Auth Lifecycle

```
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚                AUTH LIFECYCLE                     â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

  [Browser navigates to any protected route]
       â”‚
       â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚  Step 1: useAuth() hook initializes                                  â”‚
  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
  â”‚  â”‚  const { user, loading } = useAuth()                          â”‚  â”‚
  â”‚  â”‚  â†’ loading = true (initial)                                    â”‚  â”‚
  â”‚  â”‚  â†’ Supabase checks session (local storage token)               â”‚  â”‚
  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
  â”‚                                                                     â”‚
  â”‚  {loading === true}                                                 â”‚
  â”‚    â†’ [State: Auth Loading] â€” Full-screen spinner                    â”‚
  â”‚    â†’ App shell NOT rendered (Sidebar + Navbar hidden)               â”‚
  â”‚                                                                     â”‚
  â”‚  {loading === false}                                                â”‚
  â”‚    â†’ {user !== null}                                                â”‚
  â”‚    â”‚   â†’ [State: Authenticated] â€” Page renders                      â”‚
  â”‚    â”‚   â†’ useEffect: if (user) fetchData()                           â”‚
  â”‚    â”‚                                                                 â”‚
  â”‚    â†’ {user === null}                                                â”‚
  â”‚        â†’ [Action: router.push('/login')]                            â”‚
  â”‚        â†’ [State: Unauthenticated] â€” Login page renders              â”‚
  â”‚                                                                     â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

  [User on login page]
       â”‚
       â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚  Step 2: OAuth flow                                                 â”‚
  â”‚                                                                     â”‚
  â”‚  User clicks "Continue with Google"                                 â”‚
  â”‚    â†’ supabase.auth.signInWithOAuth({ provider: 'google',            â”‚
  â”‚        options: { redirectTo: '/dashboard' }})                      â”‚
  â”‚    â†’ Supabase opens Google OAuth popup/window                       â”‚
  â”‚    â†’ User authenticates with Google                                 â”‚
  â”‚    â†’ Google redirects back to Supabase callback URL                 â”‚
  â”‚    â†’ Supabase creates/updates user in auth.users                    â”‚
  â”‚    â†’ Supabase sets session cookie + local storage token             â”‚
  â”‚    â†’ Browser redirects to /dashboard                                â”‚
  â”‚    â†’ useAuth() initializes â†’ user is set â†’ page renders             â”‚
  â”‚                                                                     â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

  [Authenticated session â€” active use]
       â”‚
       â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚  Step 3: Session maintenance                                        â”‚
  â”‚                                                                     â”‚
  â”‚  {Access token expires (JWT expiry, default 1 hour)}                â”‚
  â”‚    â†’ Supabase client auto-refreshes using refresh_token             â”‚
  â”‚    â†’ Transparent to application code â€” no user impact               â”‚
  â”‚                                                                     â”‚
  â”‚  {Refresh token expires / invalidated}                              â”‚
  â”‚    â†’ Next Supabase request returns 401                              â”‚
  â”‚    â†’ useAuth detects user = null                                    â”‚
  â”‚    â†’ [Action: router.push('/login')]                                â”‚
  â”‚    â†’ [State: Unauthenticated]                                       â”‚
  â”‚                                                                     â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

  [User signs out]
       â”‚
       â–¼
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚  Step 4: Sign out                                                   â”‚
  â”‚                                                                     â”‚
  â”‚  User clicks "Sign Out" in Navbar dropdown                          â”‚
  â”‚    â†’ supabase.auth.signOut()                                        â”‚
  â”‚    â†’ Clears session from local storage                              â”‚
  â”‚    â†’ router.push('/')                                               â”‚
  â”‚    â†’ Root page detects no user â†’ redirects to /login                â”‚
  â”‚                                                                     â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
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

### 8.1 Page Loading â†’ Data States

```
[Page mounts]
  â†’ [State: Mounting]
      â†’ setMounted(true) â€” prevents hydration mismatch
  â†’ [State: Auth Loading]
      â†’ useAuth() resolves
      â†’ {user === null} â†’ [Redirect: /login]
      â†’ {user !== null} â†’ [State: Data Loading]
          â†’ fetchData() executes
          â†’ {fetch succeeds, data.length > 0} â†’ [State: Populated]
          â†’ {fetch succeeds, data.length === 0} â†’ [State: Empty]
          â†’ {fetch fails (network/Supabase error)}
              â†’ 15/18 pages: silently fail (no user feedback)
              â†’ 3/18 pages: try/catch with console.error
              â†’ Falls through to empty state (no error UI)
```

### 8.2 Offline â†’ Online Transition

```
{Network lost (navigator.onLine === false)}
  â†’ No offline indicator shown in current app
  â†’ All Supabase queries will fail silently
  â†’ No IndexedDB queue exists for offline writes
  â†’ App becomes non-functional until connectivity returns

{Network restored}
  â†’ Pages must be refreshed to recover
  â†’ No auto-retry or background sync mechanism
```

**Note:** Offline support is planned (see `FrontendOfflinePWA.md`) but not implemented. The app currently requires continuous connectivity.

### 8.3 Error Recovery Flow

```
{Any Supabase query fails}
  â†’ 15/18 pages:
      â†’ const { data } = await supabase.from(...).select(...)
      â†’ {error} is silently ignored (if (data) setState(data))
      â†’ Falls back to empty array state
      â†’ No toast, no error banner, no retry button
  â†’ 3/18 pages (chat, automation, tasks):
      â†’ try/catch block
      â†’ console.error log (visible in dev console only)
      â†’ chat: falls back to demo response
      â†’ automation: shows error result in UI
      â†’ tasks: no error handling on store operations

{AI LLM fails (chat)}
  â†’ try/catch on fetch('/api/chat')
  â†’ Falls back to getDemoResponse() â€” hardcoded keyword matching
  â†’ No user-visible error message
  â†’ Demo response replaces AI response transparently
```

---

## 9. Complex Flow Diagrams

### 9.1 Task Lifecycle: Create â†’ Complete â†’ Delete

```
                          TASK LIFECYCLE
                              â”Œâ”€â”€â”€â”€â”€â”
                              â”‚ LIST â”‚ (filtered: all/pending/in_progress/completed)
                              â””â”€â”€â”¬â”€â”€â”˜
            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
            â”‚                    â”‚                    â”‚
            â–¼                    â–¼                    â–¼
      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
      â”‚  Add (+) â”‚       â”‚ Click    â”‚          â”‚ Delete   â”‚
      â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜       â”‚ Complete â”‚          â”‚ (trash)  â”‚
           â”‚             â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜          â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
           â–¼                  â”‚                     â”‚
     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”           â–¼                     â–¼
     â”‚ ADD MODAL  â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
     â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚    â”‚ Optimistic   â”‚      â”‚ Optimisticâ”‚
     â”‚ Title*     â”‚    â”‚ UI: strikethrâ”‚      â”‚ remove    â”‚
     â”‚ Desc       â”‚    â”‚ + opac. 0.6  â”‚      â”‚ from list â”‚
     â”‚ Priority   â”‚    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜      â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚ Category   â”‚           â”‚                   â”‚
     â”‚ Est. min   â”‚           â–¼                   â–¼
     â”‚ Due date   â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
     â”‚ Recurring  â”‚    â”‚ store.       â”‚      â”‚ store.   â”‚
     â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚    â”‚ completeTask â”‚      â”‚ delete   â”‚
     â”‚ Cancel |   â”‚    â”‚ (id)         â”‚      â”‚ Task(id) â”‚
     â”‚ Create     â”‚    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜           â”‚
          â”‚                   â–¼
          â–¼            â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”‚ AnimatePresence  â”‚
     â”‚ store.   â”‚      â”‚ exit animation   â”‚
     â”‚ addTask  â”‚      â”‚ (opacity: 0,     â”‚
     â”‚ ({...})  â”‚      â”‚  scale: 0.95)    â”‚
     â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
          â”‚
          â–¼
     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
     â”‚ Modal    â”‚
     â”‚ closes   â”‚
     â”‚ State    â”‚
     â”‚ resets   â”‚
     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

BRANCH: Edit flow
  List â†’ Click Edit (pencil icon on hover)
      â†’ EDIT MODAL (pre-filled with task data)
          â†’ Cancel â†’ closes, no change
          â†’ Save Changes â†’ store.updateTask(id, {...})
              â†’ Modal closes, list updates
```

### 9.2 Chat â†’ Action Flow

```
                     CHAT â†’ ACTION FLOW

User: "add task buy groceries"
  â”Œâ”€â”€â”€ POST /api/chat â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚                                                  â”‚
  â†’ {API available}                                  â”‚
  â”‚   â†’ LLM classifies intent: "task"                â”‚
  â”‚   â†’ Generates response + suggested action        â”‚
  â”‚   â†’ Returns: { response: "...", action: null }   â”‚
  â”‚   â†’ Response rendered in chat bubble             â”‚
  â”‚                                                  â”‚
  â†’ {API unavailable}                                â”‚
  â”‚   â†’ Demo fallback: keyword match "task"          â”‚
  â”‚   â†’ Response: "I can help... Go to Tasks page"   â”‚
  â”‚   â†’ No action generated                          â”‚
  â”‚                                                  â”‚
  â†’ User reads response                              â”‚
  â†’ User navigates to /tasks (via sidebar)            â”‚
  â†’ Opens Add modal manually                         â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

FUTURE (planned):
  â†’ LLM returns action: { type: "create_task", data: {...} }
  â†’ Chat displays action card: "Create task: Buy groceries?"
  â†’ User clicks "Confirm" â†’ task created without leaving chat
  â†’ Toast confirmation
```

### 9.3 Daily Briefing Generation Flow

```
                 BRIEFING GENERATION FLOW

Trigger: 7:00 AM cron OR user clicks "Run Now" in Automation

  1. POST /api/automation/trigger/briefing
  2. Backend collects context:
       â”œâ”€â”€ Tasks: overdue + due today + high priority
       â”œâ”€â”€ Habits: yesterday completion rates
       â”œâ”€â”€ Sleep: last night score
       â”œâ”€â”€ Courses: upcoming deadlines
       â””â”€â”€ Opportunities: new matches
  3. Calls LLM with PromptLoader.get_agent("briefing_agent")
  4. {LLM succeeds}
       â†’ Parse JSON â†’ validate schema â†’ save to daily_briefings
       â†’ Push notification: "Your briefing is ready"
       â†’ User opens /dashboard â†’ briefing card at top
  5. {LLM fails}
       â†’ Algorithmic fallback: top 3 tasks + generic quote
       â†’ Save as algorithmic briefing
       â†’ Log LLM failure

User sees briefing on /dashboard:
  â”œâ”€â”€ Time-based greeting
  â”œâ”€â”€ Date display
  â”œâ”€â”€ Stats grid (4 cards: productivity, tasks today, courses, goals)
  â”œâ”€â”€ Priority tasks (up to 4, with stagger animation)
  â”œâ”€â”€ ARIA's Pick recommendation
  â”œâ”€â”€ Quick Actions (4 buttons â†’ /tasks, /ideas, /courses, /goals)
  â””â”€â”€ Activity heatmap (30-day random grid)

User interactions:
  â†’ Click task â†’ /tasks
  â†’ Click "View All" â†’ /tasks
  â†’ Click "Chat with ARIA" â†’ /chat
  â†’ Click quick action â†’ target module
```

### 9.4 Opportunity: Scan â†’ Apply â†’ Track

```
                 OPPORTUNITY LIFECYCLE

Trigger: 6:00 AM cron scan OR "Run Now" in Automation

  1. POST /api/automation/trigger/radar
  2. Backend queries opportunity sources (Internshala, LinkedIn, etc.)
  3. AI matching: score 0-100
  4. Score > 70 â†’ saved to opportunities table
  5. Score < 70 â†’ archived (not shown to user)
  6. New matches included in morning briefing

User on /opportunities:
  â”œâ”€â”€ Header + "Scan Now" button
  â”œâ”€â”€ Filter dropdown (category)
  â””â”€â”€ Card list: title, company, match score, deadline, tags

User clicks card:
  â†’ Full detail view (inline or expand)
  â†’ Actions: Save | Apply | Dismiss

User clicks "Track Application":
  â†’ Modal: Application date, Notes, Status (select)
  â†’ On save:
      â†’ Opportunity status updates
      â†’ Follow-up task auto-created (7 days)
      â†’ If paid â†’ linked to income

User clicks "Dismiss":
  â†’ Opportunity removed from active list
  â†’ Added to ignore list (prevents same match in future scans)
```

### 9.5 Habit Check-in â†’ Streak â†’ Nudge

```
                  HABIT CHECK-IN FLOW

User opens /habits:
  â”œâ”€â”€ Stats: Active habits (count), Total streak (sum), Avg consistency %
  â”œâ”€â”€ List: each habit shows:
  â”‚     name | frequency | current_streak | consistency %
  â”‚     active toggle | streak flame icon | delete
  â””â”€â”€ Add Habit button

User toggles habit active/inactive:
  â†’ supabase.update({ is_active: !isActive })
  â†’ Local state updates immediately
  â†’ (Habit logging â€” marking "Done" for the day â€” is NOT implemented
     in current frontend. Only habit definition CRUD exists.)

Streak calculation (backend):
  â†’ Query habit_logs for last 90 days
  â†’ Count consecutive days where status = "completed"
  â†’ 3+ missed consecutive days â†’ reset to 0
  â†’ Otherwise maintain streak

Nudge trigger (6 PM daily):
  â†’ Check courses: deadline < 7 days + pace behind â†’ nudge
  â†’ Check habits: not logged today by 6 PM â†’ nudge
  â†’ AI generates personalized message via nudge_agent

FUTURE (from wireframe):
  â†’ Daily check-in modal at 8 PM reminder
  â†’ Swipe-to-complete gesture on mobile
  â†’ Calendar heatmap view for past 30 days
  â†’ Streak milestone celebrations (7, 30, 60, 90 days)
```

---

## 10. Wireframe-to-Screen Cross-Reference

### 10.1 Complete Mapping

| Wireframe Document | Section | Wireframe View | Rendered Screen | Status | Notes |
|---|---|---|---|---|---|
| `01_APPLICATION_SHELL` | 1.1 Desktop Shell | Chrome layout | `(dashboard)/layout.tsx` | âš ï¸ Orphaned | Defined but never rendered |
| `01_APPLICATION_SHELL` | 1.2 Tablet Shell | Collapsed sidebar | â€” | âŒ Not implemented | Responsive breakpoints not active |
| `01_APPLICATION_SHELL` | 1.3 Mobile Shell | Bottom nav + FAB | â€” | âŒ Not implemented | No responsive shell |
| `01_APPLICATION_SHELL` | 2.0 Sidebar | Nav groups + items | `Sidebar.tsx` | âœ… Implemented | 16 items, active state |
| `01_APPLICATION_SHELL` | 2.4 Command Center | Cmd+K palette | â€” | âŒ Not implemented | No shortcut handler |
| `01_APPLICATION_SHELL` | 3.0 Global Search | Search overlay | Navbar search bar | â³ Partial | UI exists, no search logic |
| `01_APPLICATION_SHELL` | 4.0 Notifications | Bell panel | Navbar bell icon | â³ Partial | Icon exists, no panel |
| `02_DASHBOARD` | 1.0 Morning Briefing | Hero card | `/dashboard` hero | âœ… Implemented | Greeting + date |
| `02_DASHBOARD` | 2.0 Productivity Score | Gauge widget | `/dashboard` stats grid | âœ… Implemented | Text metric, no gauge |
| `02_DASHBOARD` | 3.0 AI Insights | Recommendation card | `/dashboard` ARIA's Pick | âœ… Implemented | Top task recommendation |
| `02_DASHBOARD` | 5.0 Quick Actions | Action grid | `/dashboard` quick actions | âœ… Implemented | 4 action buttons |
| `02_DASHBOARD` | 7.0 Widget Config | Layout editor | â€” | âŒ Not implemented | No drag-to-configure |
| `03_TASKS_COURSES` | 1.0 Task List | Card list | `/tasks` | âœ… Implemented | With filters + stats |
| `03_TASKS_COURSES` | 1.1 Board View | Kanban columns | â€” | âŒ Not implemented | No view switcher |
| `03_TASKS_COURSES` | 1.2 Calendar View | Month grid | â€” | âŒ Not implemented | No calendar view |
| `03_TASKS_COURSES` | 1.3 Task Detail | Split/full panel | `/tasks` edit modal | â³ Partial | Modal, not split view |
| `03_TASKS_COURSES` | 1.4 Create Modal | Task form | `/tasks` add modal | âœ… Implemented | 7 fields + recurring |
| `03_TASKS_COURSES` | 2.0 Course Library | Grid/list | `/courses` | âœ… Implemented | List view |
| `03_TASKS_COURSES` | 2.1 Course Detail | Tabs (Overview/Lessons/Notes/Analytics) | â€” | âŒ Not implemented | Flat list only |
| `04_KNOWLEDGE_IDEAS` | 1.0 Resource Grid | Grid/list | `/resources` | âœ… Implemented | Basic list |
| `04_KNOWLEDGE_IDEAS` | 1.2 Knowledge Graph | Interactive graph | â€” | âŒ Not implemented | No graph component |
| `04_KNOWLEDGE_IDEAS` | 2.0 Idea Capture | Capture view | `/ideas` | âœ… Implemented | Basic list |
| `04_KNOWLEDGE_IDEAS` | 2.1 Pipeline Board | Kanban stages | â€” | âŒ Not implemented | No pipeline view |
| `04_KNOWLEDGE_IDEAS` | 3.0 Roadmap Canvas | Gantt/timeline | `/goals` | â³ Partial | Basic list, no Gantt |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 1.0 Discovery View | Grid/list | `/opportunities` | âœ… Implemented | With filter |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 1.1 Match Breakdown | Score card | â€” | âŒ Not implemented | No score visualization |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 2.0 Project Board | Kanban | `/projects` | âœ… Implemented | Basic list |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 2.1 Timeline View | Gantt | â€” | âŒ Not implemented | No Gantt |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 3.0 Income Overview | Dashboard | `/income` | âœ… Implemented | Basic list |
| `05_OPPORTUNITY_PROJECTS_INCOME` | 3.1 Income Analytics | Charts | â€” | âŒ Not implemented | No charts |
| `06_ANALYTICS_AI` | 4.0 Chat View | Message list | `/chat` | âœ… Implemented | With demo fallback |
| `06_ANALYTICS_AI` | 4.1 Context Panel | Side panel | â€” | âŒ Not implemented | No context panel |
| `06_ANALYTICS_AI` | 4.2 Chat History | Thread list | â€” | âŒ Not implemented | No history sidebar |
| `06_ANALYTICS_AI` | 5.0 Empty State | Placeholder | All CRUD pages | âœ… Implemented | Icon + message + CTA |
| `06_ANALYTICS_AI` | 5.1 Loading State | Skeleton | All pages | âœ… Implemented | Spinner pattern |
| `06_ANALYTICS_AI` | 5.2 Error State | Error card | â€” | âŒ Not implemented | No error UI |
| `07_SUPPLEMENT` | 1.0 Timer View | Pomodoro | `/time` | âœ… Implemented | With idle detection |
| `07_SUPPLEMENT` | 1.1 Entries Log | Session list | `/time` recent sessions | âœ… Implemented | |
| `07_SUPPLEMENT` | 1.2 Statistics | Charts | `/time` peak hours | âœ… Implemented | Hour breakdown |
| `07_SUPPLEMENT` | 2.0 Semester View | Course grid | `/academics` | âœ… Implemented | With CGPA |
| `07_SUPPLEMENT` | 3.0 YouTube Library | Video grid | `/youtube` | âœ… Implemented | Basic list |
| `07_SUPPLEMENT` | 4.0 Automation Rules | Card list | `/automation` | âœ… Implemented | 6 cards with run |
| `07_SUPPLEMENT` | 5.0 AI Components | GhostHint, StreamingText | Across app | â³ Partial | Chat has thinking animation |

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
| 1.0.0 | 2026-06-13 | AI Engineering | Initial screen flows document â€” 18 pages, 5-state machines, modal registry, deep link map, auth lifecycle, wireframe cross-reference |

---

*End of Frontend Screen Flows Document â€” Enterprise v1.0.0*
