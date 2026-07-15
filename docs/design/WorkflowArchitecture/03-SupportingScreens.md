## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF03-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part III â€” Supporting Screens

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `01-UserFlows.md` (module flows), `02-FeatureFlows.md` (feature flows), `FrontendScreenFlows.md` (screen-to-screen transitions).

---

## 3.1 Screen Hierarchy Notation

Every workflow in this architecture maps to a screen hierarchy. The hierarchy defines every screen, sub-view, overlay, modal, toast, and banner required to complete the workflow.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#0A0B0F', 'primaryColor': '#13151A', 'primaryBorderColor': '#6366F1', 'primaryTextColor': '#F1F5F9', 'lineColor': '#818CF8', 'secondaryColor': '#1A1D24', 'tertiaryColor': '#00FFA3', 'fontFamily': 'DM Sans'}}}%%
flowchart TD
    subgraph Shell["Persistent Shell"]
        S[Sidebar<br/>240px / 64px / bottom tabs]
        T[TopBar<br/>Search, Actions, Avatar]
        N[Notification Bell<br/>Badge + Dropdown]
        CC[Command Center<br/>Cmd+K Overlay]
    end

    subgraph Page["Module Page"]
        H[PageHeader<br/>Title + Actions]
        V[View Selector<br/>List / Grid / Kanban / Calendar]
        C[ContentArea]
    end

    subgraph Overlays["Overlay Layer"]
        DE[Detail Slide-Over<br/>Right 50% / Full mobile]
        CR[Create/Edit Sheet<br/>Slide-up modal]
        CD[Confirm Dialog<br/>Destructive action]
        AI[AI Suggestions Panel<br/>Inline / Sidebar]
        SH[Share Dialog<br/>Permissions + Link]
    end

    subgraph Toast["Toast Layer"]
        ST[Success Toast<br/>Green Â· 3s auto-dismiss]
        ET[Error Toast<br/>Red Â· persistent]
        UT[Undo Toast<br/>30s timer]
        OB[Offline Banner<br/>Amber Â· persistent]
    end

    Shell --> Page
    Page --> Overlays
    Page --> Toast
    CC --> CR
    CC --> DE
    N --> DE
    T --> CC
    T --> N
    CR --> AI
    CR --> CD
    DE --> SH
    DE --> CD
    SH --> ST
    CR --> ST
    CR --> ET
    AI --> UT
    CD --> ST
    CD --> ET
```

### Standard Screen Hierarchy

```
ROUTE: /module
â”œâ”€â”€ Shell (persistent)
â”‚   â”œâ”€â”€ Sidebar (240px desktop / 64px tablet / bottom tab mobile)
â”‚   â”œâ”€â”€ TopBar (64px)
â”‚   â”‚   â”œâ”€â”€ Search bar (expandable)
â”‚   â”‚   â”œâ”€â”€ Quick actions
â”‚   â”‚   â””â”€â”€ Notification bell
â”‚   â”œâ”€â”€ Command Center (Cmd+K overlay)
â”‚   â””â”€â”€ Toast container (fixed position)
â”œâ”€â”€ PageHeader
â”‚   â”œâ”€â”€ Module title
â”‚   â”œâ”€â”€ Action buttons (primary + secondary)
â”‚   â””â”€â”€ View toggle (list/grid/kanban/calendar)
â”œâ”€â”€ ContentArea
â”‚   â”œâ”€â”€ FilterBar (chips, search, sort)
â”‚   â”œâ”€â”€ ListView (default)
â”‚   â”‚   â”œâ”€â”€ LoadingSkeleton (3-5 shimmer items)
â”‚   â”‚   â”œâ”€â”€ EmptyState (illustration + CTA)
â”‚   â”‚   â”œâ”€â”€ ErrorState (banner + retry)
â”‚   â”‚   â””â”€â”€ Item (icon, title, metadata, actions)
â”‚   â”œâ”€â”€ GridView (alternative)
â”‚   â”œâ”€â”€ KanbanView (pipeline modules)
â”‚   â””â”€â”€ CalendarView (time-based modules)
â”œâ”€â”€ SlideOverPanel (detail)
â”‚   â”œâ”€â”€ Header (title, status, menu)
â”‚   â”œâ”€â”€ Content (full item detail)
â”‚   â”œâ”€â”€ ActivityFeed (chronological events)
â”‚   â””â”€â”€ RelatedItems (cross-module links)
â”œâ”€â”€ CreateModal / EditSheet
â”‚   â”œâ”€â”€ Form (fields, selects, date pickers)
â”‚   â”œâ”€â”€ AISuggestions (auto-fill chips)
â”‚   â””â”€â”€ Actions (submit, cancel)
â”œâ”€â”€ ConfirmDialog
â”‚   â”œâ”€â”€ Warning icon
â”‚   â”œâ”€â”€ Description + details
â”‚   â””â”€â”€ Confirm / Cancel buttons
â”œâ”€â”€ ShareDialog
â”‚   â”œâ”€â”€ Permission selector (view/comment/edit)
â”‚   â”œâ”€â”€ Share channel (link/email/app)
â”‚   â””â”€â”€ Expiry settings
â””â”€â”€ Toast (transient, auto-dismiss)
    â”œâ”€â”€ Success (green, 3s)
    â”œâ”€â”€ Error (red, persistent)
    â”œâ”€â”€ Undo (green, 30s timer)
    â””â”€â”€ Offline (amber, persistent)
```

---

## 3.2 Overlay & Modal Dependency Map

### Overlay Stacking Rules

| Rule | Description |
|---|---|
| **Max 2 overlays** | Maximum two overlays visible at a time (e.g., Create Modal + AI Suggestions) |
| **Toast always on top** | Toast layer is non-blocking, always highest z-index |
| **Command Center clears all** | Cmd+K closes all other overlays when opened |
| **Modal preserves state** | Modals retain their state if a toast or notification appears |
| **Mobile = full-screen** | All modals become full-screen sheets on mobile |
| **Escape = close topmost** | Escape key closes the topmost overlay only |

### Overlay State Matrix

| Overlay | Open Trigger | Close Trigger | Data Persistence |
|---|---|---|---|
| Command Center | Cmd+K from any screen | Escape, click outside, action executed | None (transient) |
| Quick Capture | Cmd+K (when not in command mode) | Escape, submit, click outside | Auto-save draft to localStorage |
| Create/Edit Modal | Add/Edit button | Escape, save, click outside | Auto-save draft to localStorage |
| Detail Slide-Over | Item click | Escape, click outside, nav away | None (read-only) |
| Confirm Dialog | Destructive action | Confirm, cancel, escape | None |
| Share Dialog | Share button | Close, generate link, escape | None |
| AI Suggestions | AI generates recommendation | Accept, dismiss, timeout | Preference stored in memory |
| Notification Dropdown | Bell click | Click notification, click outside | Mark read on action |

---

## 3.3 Deep Link Resolution

Notifications and external links must resolve to the correct screen:

| Notification Type | Deep Link | Screen | Scroll To |
|---|---|---|---|
| Task reminder | `/tasks/{id}` | Tasks | Detail slide-over |
| Course deadline | `/courses/{id}` | Courses | Detail view |
| Goal milestone | `/goals/{id}` | Goals | Detail with KRs |
| Opportunity match | `/opportunities/{id}` | Opportunities | Detail card |
| Habit nudge | `/habits` | Habits | Today's log section |
| Sleep reminder | `/sleep` | Sleep | Log modal |
| Briefing ready | `/dashboard#briefing` | Dashboard | Briefing widget (scroll) |
| AI insight | `/chat?insight={id}` | Chat | Specific message |

---

## 3.4 Auth-Guarded Transitions

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'background': '#0A0B0F', 'primaryColor': '#13151A', 'primaryBorderColor': '#6366F1', 'primaryTextColor': '#F1F5F9', 'lineColor': '#818CF8', 'secondaryColor': '#1A1D24', 'tertiaryColor': '#00FFA3', 'fontFamily': 'DM Sans'}}}%%
stateDiagram-v2
    [*] --> Landing: First Visit
    Landing --> Login: Click Get Started
    Login --> Dashboard: OAuth Success
    Landing --> Dashboard: Already Authenticated (JWT check)

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

    Dashboard --> Settings: Profile Menu
    Settings --> Dashboard: Back/Save

    note right of Login: OAuth handles token refresh<br/>Auto-redirect on success
    note right of Dashboard: 5 state machine<br/>Loading/Empty/Error/Populated/Offline
```
