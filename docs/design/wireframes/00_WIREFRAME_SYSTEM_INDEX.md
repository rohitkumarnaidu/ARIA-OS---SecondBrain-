# Second Brain OS â€” Complete Enterprise Wireframe System

| Field | Value |
|---|---|
| Document ID | DSG-WIX-001 |
| Version | 2.0.0 |
| Status | Complete |
| Date | 2026-06-11 |
| Classification | Enterprise UX â€” Structural Wireframes |
| Scope | 20 Modules, 3 Breakpoints, All States, 7 Wireframe Parts |

---

## Document Map

This wireframe system is organized into 8 documents (this index + 7 parts):

| # | Document | Scope | Modules Covered |
|---|----------|-------|-----------------|
| 00 | **This Index** | System architecture, hierarchies, flows | All |
| 01 | [Application Shell & Navigation](file:///C:/Users/Dell/.gemini/antigravity/brain/564651ed-4a73-4095-9cdc-2acf8e3251be/01_APPLICATION_SHELL_AND_NAVIGATION.md) | App shell (Desktop/Tablet/Mobile), Sidebar, Top Nav, Mobile Nav, Command Center, Search, Notifications | Shell |
| 02 | [Dashboard Wireframes](file:///C:/Users/Dell/.gemini/antigravity/brain/564651ed-4a73-4095-9cdc-2acf8e3251be/02_DASHBOARD_WIREFRAMES.md) | Morning Briefing, Productivity, AI Insights, Learning, Opportunities, Projects, Analytics widgets | Dashboard |
| 03 | [Tasks & Courses](file:///C:/Users/Dell/.gemini/antigravity/brain/564651ed-4a73-4095-9cdc-2acf8e3251be/03_TASKS_AND_COURSES_WIREFRAMES.md) | Task List/Board/Calendar/Detail views, Course Library/Detail/Progress | Tasks, Courses |
| 04 | [Knowledge, Ideas & Roadmap](file:///C:/Users/Dell/.gemini/antigravity/brain/564651ed-4a73-4095-9cdc-2acf8e3251be/04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md) | Knowledge Vault, Search, Graph, Idea Capture/Analysis/Validation, Roadmap Canvas/Timeline/Dependencies | Resources, Ideas, Goals |
| 05 | [Opportunities, Projects & Income](file:///C:/Users/Dell/.gemini/antigravity/brain/564651ed-4a73-4095-9cdc-2acf8e3251be/05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md) | Opportunity Discovery/Matching/Filtering, Project Board/Timeline/Detail, Income Overview/Sources/Analytics | Opportunities, Projects, Income |
| 06 | [Analytics, AI, Settings & States](file:///C:/Users/Dell/.gemini/antigravity/brain/564651ed-4a73-4095-9cdc-2acf8e3251be/06_ANALYTICS_AI_SETTINGS_STATES_WIREFRAMES.md) | Analytics Overview/Reports/Insights, AI Chat/Context/Recommendations, Settings, Empty/Loading/Error States | Analytics, Chat, Settings |
| 07 | **`07_SUPPLEMENT_AI_MODULES_STATES.md`** | Time Tracking (Pomodoro/Log/Stats), Academics (Semester/Subject), YouTube (Library/Detail), Automation (Rules/Detail/Log), Learning (Dashboard/Skills/Paths), Memory (Viewer/Knowledge), AI Components (6 patterns), States Expansion (Empty/Offline) | Time, Academics, YouTube, Automation, Learning, Memory, AI Components |

---

## System Architecture Overview

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    SECOND BRAIN OS (ARIA OS)                     â”‚
â”‚                  Enterprise Wireframe System                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                  â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”          â”‚
â”‚  â”‚   DESKTOP    â”‚  â”‚   TABLET     â”‚  â”‚   MOBILE     â”‚          â”‚
â”‚  â”‚  1024px+     â”‚  â”‚  768-1023px  â”‚  â”‚  320-767px   â”‚          â”‚
â”‚  â”‚              â”‚  â”‚              â”‚  â”‚              â”‚          â”‚
â”‚  â”‚ â”Œâ”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â” â”‚  â”‚ â”Œâ”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚  â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚          â”‚
â”‚  â”‚ â”‚  â”‚       â”‚ â”‚  â”‚ â”‚ â”‚        â”‚â”‚  â”‚ â”‚  TopBar   â”‚â”‚          â”‚
â”‚  â”‚ â”‚S â”‚Contentâ”‚ â”‚  â”‚ â”‚Iâ”‚Content â”‚â”‚  â”‚ â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤â”‚          â”‚
â”‚  â”‚ â”‚i â”‚ Area  â”‚ â”‚  â”‚ â”‚câ”‚  Area  â”‚â”‚  â”‚ â”‚          â”‚â”‚          â”‚
â”‚  â”‚ â”‚d â”‚       â”‚ â”‚  â”‚ â”‚oâ”‚        â”‚â”‚  â”‚ â”‚ Content  â”‚â”‚          â”‚
â”‚  â”‚ â”‚e â”‚       â”‚ â”‚  â”‚ â”‚nâ”‚        â”‚â”‚  â”‚ â”‚          â”‚â”‚          â”‚
â”‚  â”‚ â”‚b â”‚       â”‚ â”‚  â”‚ â”‚ â”‚        â”‚â”‚  â”‚ â”‚          â”‚â”‚          â”‚
â”‚  â”‚ â”‚a â”‚       â”‚ â”‚  â”‚ â”‚ â”‚        â”‚â”‚  â”‚ â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤â”‚          â”‚
â”‚  â”‚ â”‚r â”‚       â”‚ â”‚  â”‚ â””â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”‚  â”‚ â”‚ BottomNavâ”‚â”‚          â”‚
â”‚  â”‚ â””â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”‚          â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜          â”‚
â”‚                                                                  â”‚
â”‚  15 Modules Ã— 3 Breakpoints Ã— Multiple Views = 120+ Wireframes  â”‚
â”‚                                                                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Wireframe Document System â€” Module Coverage Map

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#6366F1','primaryTextColor':'#F1F5F9','lineColor':'#00FFA3','secondaryColor':'#13151A','tertiaryColor':'#0A0B0F','fontFamily':'DM Sans'}}}%%
graph TD
    Index["00 â€” SYSTEM INDEX<br/>Doc Map + Hierarchy + Flows"]:::index

    Index --> Shell["01 â€” App Shell & Nav<br/>7 Components, 3 Breakpoints"]:::doc
    Index --> Dash["02 â€” Dashboard<br/>Bento Grid, 7 Widget Sections"]:::doc
    Index --> Tasks["03 â€” Tasks & Courses<br/>List / Board / Calendar / Detail"]:::doc
    Index --> Knowledge["04 â€” Knowledge & Ideas<br/>Vault / Pipeline / Canvas"]:::doc
    Index --> Opps["05 â€” Opportunities<br/>Discovery / Board / Income"]:::doc
    Index --> Analytics["06 â€” Analytics & AI<br/>Reports / Chat / Settings / Sleep / Habits"]:::doc
    Index --> Supp["07 â€” Supplement<br/>Time / Academics / YT / Auto / Learn / Mem / AI"]:::doc

    Shell --> Desktop["Desktop 1440px+"]:::bp
    Shell --> Tablet["Tablet 768-1023px"]:::bp
    Shell --> Mobile["Mobile 320-767px"]:::bp

    Tasks --> List["List View"]:::view
    Tasks --> Board["Board Kanban"]:::view
    Tasks --> Calendar["Calendar View"]:::view
    Tasks --> Detail["Detail View"]:::view

    Knowledge --> Resources["Resources Vault"]:::view
    Knowledge --> Ideas["Ideas Pipeline"]:::view
    Knowledge --> Roadmap["Roadmap Canvas"]:::view

    Analytics --> AOverview["Analytics Overview"]:::view
    Analytics --> Chat["ARIA Chat"]:::view
    Analytics --> Settings["Settings"]:::view

    classDef index fill:#6366F1,stroke:#818CF8,color:#F1F5F9,font-weight:700
    classDef doc fill:#13151A,stroke:#6366F1,color:#F1F5F9
    classDef bp fill:#0A0B0F,stroke:#00FFA3,color:#00FFA3
    classDef view fill:#13151A,stroke:#334155,color:#94A3B8
```

---

## Complete Page Hierarchy

```
L0 â€” Application Shell
â”‚
â”œâ”€â”€ L1 â€” Authentication
â”‚   â”œâ”€â”€ Login Page
â”‚   â””â”€â”€ OAuth Callback
â”‚
â”œâ”€â”€ L1 â€” Dashboard (Home)
â”‚   â”œâ”€â”€ L2 â€” Morning Briefing (expanded)
â”‚   â”œâ”€â”€ L2 â€” Widget Configuration
â”‚   â””â”€â”€ L2 â€” Layout Presets
â”‚
â”œâ”€â”€ L1 â€” Tasks
â”‚   â”œâ”€â”€ L2 â€” List View
â”‚   â”‚   â””â”€â”€ L3 â€” Task Detail (split/full)
â”‚   â”‚       â””â”€â”€ L4 â€” Edit Modal
â”‚   â”œâ”€â”€ L2 â€” Board View (Kanban)
â”‚   â”‚   â””â”€â”€ L3 â€” Task Detail
â”‚   â”œâ”€â”€ L2 â€” Calendar View
â”‚   â”‚   â”œâ”€â”€ L3 â€” Month View
â”‚   â”‚   â”œâ”€â”€ L3 â€” Week View
â”‚   â”‚   â””â”€â”€ L3 â€” Day View
â”‚   â””â”€â”€ L4 â€” Create Task Modal
â”‚
â”œâ”€â”€ L1 â€” Courses
â”‚   â”œâ”€â”€ L2 â€” Library View (Grid/List)
â”‚   â”œâ”€â”€ L2 â€” Course Detail
â”‚   â”‚   â”œâ”€â”€ L3 â€” Overview Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Lessons Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Notes Tab
â”‚   â”‚   â””â”€â”€ L3 â€” Analytics Tab
â”‚   â”œâ”€â”€ L2 â€” Progress Tracking
â”‚   â””â”€â”€ L4 â€” Add Course Modal
â”‚
â”œâ”€â”€ L1 â€” Knowledge Vault (Resources)
â”‚   â”œâ”€â”€ L2 â€” Resource Grid/List
â”‚   â”œâ”€â”€ L2 â€” Search Results
â”‚   â”œâ”€â”€ L2 â€” Knowledge Graph
â”‚   â”œâ”€â”€ L3 â€” Resource Detail
â”‚   â””â”€â”€ L4 â€” Add Resource Modal
â”‚
â”œâ”€â”€ L1 â€” Idea Vault (Ideas)
â”‚   â”œâ”€â”€ L2 â€” Capture View
â”‚   â”œâ”€â”€ L2 â€” Pipeline Board
â”‚   â”œâ”€â”€ L2 â€” Analysis View
â”‚   â”œâ”€â”€ L3 â€” Idea Detail
â”‚   â”‚   â”œâ”€â”€ L3 â€” AI Analysis Panel
â”‚   â”‚   â””â”€â”€ L3 â€” Validation Checklist
â”‚   â””â”€â”€ L4 â€” Quick Capture Modal
â”‚
â”œâ”€â”€ L1 â€” Roadmap Engine (Goals)
â”‚   â”œâ”€â”€ L2 â€” Canvas View
â”‚   â”œâ”€â”€ L2 â€” Timeline View (Gantt)
â”‚   â”œâ”€â”€ L2 â€” Milestones View
â”‚   â”œâ”€â”€ L2 â€” Dependencies View
â”‚   â”œâ”€â”€ L3 â€” Goal Detail
â”‚   â”‚   â”œâ”€â”€ L3 â€” Overview Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Tasks Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Milestones Tab
â”‚   â”‚   â””â”€â”€ L3 â€” Dependencies Tab
â”‚   â””â”€â”€ L4 â€” Create Goal Modal
â”‚
â”œâ”€â”€ L1 â€” Opportunity Radar
â”‚   â”œâ”€â”€ L2 â€” Discovery View (Grid/List)
â”‚   â”œâ”€â”€ L2 â€” Recommendations
â”‚   â”œâ”€â”€ L2 â€” Filter Panel
â”‚   â”œâ”€â”€ L3 â€” Opportunity Detail
â”‚   â”‚   â”œâ”€â”€ L3 â€” Match Breakdown
â”‚   â”‚   â”œâ”€â”€ L3 â€” Application Tracking
â”‚   â”‚   â””â”€â”€ L3 â€” AI Insights
â”‚   â””â”€â”€ L4 â€” Add Opportunity Modal
â”‚
â”œâ”€â”€ L1 â€” Projects
â”‚   â”œâ”€â”€ L2 â€” Board View (Kanban)
â”‚   â”œâ”€â”€ L2 â€” Timeline View (Gantt)
â”‚   â”œâ”€â”€ L2 â€” Grid View
â”‚   â”œâ”€â”€ L3 â€” Project Detail
â”‚   â”‚   â”œâ”€â”€ L3 â€” Overview Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Tasks Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Milestones Tab
â”‚   â”‚   â”œâ”€â”€ L3 â€” Files Tab
â”‚   â”‚   â””â”€â”€ L3 â€” Analytics Tab
â”‚   â””â”€â”€ L4 â€” Create Project Modal
â”‚
â”œâ”€â”€ L1 â€” Income Dashboard
â”‚   â”œâ”€â”€ L2 â€” Overview
â”‚   â”œâ”€â”€ L2 â€” Sources
â”‚   â”œâ”€â”€ L2 â€” Analytics
â”‚   â”œâ”€â”€ L3 â€” Source Detail
â”‚   â””â”€â”€ L4 â€” Log Income Modal
â”‚
â”œâ”€â”€ L1 â€” Habits
â”‚   â”œâ”€â”€ L2 â€” Tracker View (Calendar/Grid)
â”‚   â”œâ”€â”€ L3 â€” Habit Detail
â”‚   â””â”€â”€ L4 â€” Add Habit Modal
â”‚
â”œâ”€â”€ L1 â€” Sleep
â”‚   â”œâ”€â”€ L2 â€” Log View
â”‚   â”œâ”€â”€ L2 â€” Analytics
â”‚   â””â”€â”€ L4 â€” Log Sleep Modal
â”‚
â”œâ”€â”€ L1 â€” Time Tracking
â”‚   â”œâ”€â”€ L2 â€” Timer View (Pomodoro)
â”‚   â”œâ”€â”€ L2 â€” Entries Log
â”‚   â”œâ”€â”€ L2 â€” Statistics
â”‚   â””â”€â”€ L4 â€” Manual Entry Modal
â”‚
â”œâ”€â”€ L1 â€” Academics
â”‚   â”œâ”€â”€ L2 â€” Semester View
â”‚   â”œâ”€â”€ L2 â€” Subject Detail
â”‚   â””â”€â”€ L4 â€” Add Subject Modal
â”‚
â”œâ”€â”€ L1 â€” YouTube
â”‚   â”œâ”€â”€ L2 â€” Library View
â”‚   â”œâ”€â”€ L3 â€” Video Detail
â”‚   â””â”€â”€ L4 â€” Add Video Modal
â”‚
â”œâ”€â”€ L1 â€” Analytics
â”‚   â”œâ”€â”€ L2 â€” Overview
â”‚   â”œâ”€â”€ L2 â€” Reports
â”‚   â”‚   â”œâ”€â”€ L3 â€” Report Generator
â”‚   â”‚   â””â”€â”€ L3 â€” Generated Report
â”‚   â””â”€â”€ L2 â€” AI Insights
â”‚
â”œâ”€â”€ L1 â€” AI Assistant (ARIA Chat)
â”‚   â”œâ”€â”€ L2 â€” Chat View
â”‚   â”‚   â”œâ”€â”€ L3 â€” Chat Thread
â”‚   â”‚   â””â”€â”€ L3 â€” Context Panel
â”‚   â””â”€â”€ L2 â€” Chat History
â”‚
â”œâ”€â”€ L1 â€” Automation
â”‚   â”œâ”€â”€ L2 â€” Rules List
â”‚   â”œâ”€â”€ L3 â€” Rule Detail
â”‚   â””â”€â”€ L4 â€” Create Rule Modal
â”‚
â”œâ”€â”€ L1 â€” Settings
â”‚   â”œâ”€â”€ L2 â€” Profile
â”‚   â”œâ”€â”€ L2 â€” Appearance
â”‚   â”œâ”€â”€ L2 â€” Notifications
â”‚   â”œâ”€â”€ L2 â€” AI & Intelligence
â”‚   â”œâ”€â”€ L2 â€” Integrations
â”‚   â”œâ”€â”€ L2 â€” Data & Privacy
â”‚   â”œâ”€â”€ L2 â€” Keyboard Shortcuts
â”‚   â””â”€â”€ L2 â€” About
â”‚
â””â”€â”€ System Overlays (L4)
    â”œâ”€â”€ Command Center (Cmd+K)
    â”œâ”€â”€ Global Search
    â”œâ”€â”€ Notification Panel
    â”œâ”€â”€ Quick Create (âŠ•)
    â””â”€â”€ AI Quick Ask
```

**Total Routes:** 25+ top-level, 60+ sub-views, 15+ modals

---

## Complete Component Hierarchy

### Layout Components

| Component | Description | Used In |
|-----------|-------------|---------|
| `AppShell` | Root layout container | Every page |
| `Sidebar` | Left navigation (240px/64px/hidden) | Desktop, Tablet |
| `TopBar` | Top navigation bar (64px/48px) | All breakpoints |
| `BottomTabBar` | Mobile bottom navigation (5 items) | Mobile only |
| `ContentArea` | Main scrollable content zone | Every page |
| `ContextPanel` | Right sidebar (320px, slide-over) | Desktop, Tablet |
| `PageHeader` | Page title + actions + breadcrumb | Every module |
| `SplitView` | List + Detail side by side | Tasks, Resources |
| `FullScreenCanvas` | Full-viewport interactive area | Roadmap, Knowledge Graph |

### Navigation Components

| Component | Description | Variants |
|-----------|-------------|----------|
| `NavGroup` | Sidebar navigation group with label | Expanded, Collapsed |
| `NavItem` | Single navigation link with icon + badge | Active, Hover, Collapsed (icon-only) |
| `Breadcrumb` | Path breadcrumb trail | Standard, Truncated (mobile) |
| `TabBar` | Horizontal tab switcher | Underline, Pill, Scrollable |
| `ViewSwitcher` | Toggle between views (List/Board/Calendar) | Icon buttons, Segmented |
| `BackButton` | Navigation back arrow | Standard, With label |
| `BottomTab` | Single bottom tab item | Active, Inactive, Badge |
| `DrawerMenu` | Full-screen slide-out menu | Left slide, Right slide |

### Data Display Components

| Component | Description | Variants |
|-----------|-------------|----------|
| `MetricCard` | Single KPI with label + value + trend | Small, Medium, Large |
| `DataCard` | Content card with header + body | Interactive, Static, Compact |
| `DataTable` | Sortable, filterable table | Standard, Compact, Expandable row |
| `KanbanBoard` | Column-based drag-and-drop board | Standard, Swimlanes |
| `KanbanCard` | Single item card in board | Minimal, Detailed |
| `Timeline` | Gantt-style horizontal timeline | Standard, Compact |
| `Calendar` | Calendar grid (Month/Week/Day) | Month, Week, Day, Agenda |
| `Chart` | Data visualization container | Line, Bar, Donut, Heatmap, Radar |
| `ProgressBar` | Linear progress indicator | Standard, Labeled, Stacked |
| `ProgressRing` | Circular progress indicator | Small, Large, With label |
| `Badge` | Status/category indicator | Status, Priority, Count, Tag |
| `Avatar` | User or entity avatar | Image, Initials, AI bot |
| `List` | Vertical item list | Standard, Compact, Grouped |
| `Grid` | Card grid layout | 2-col, 3-col, 4-col, Auto-fill |
| `Heatmap` | Calendar heatmap (habit/activity) | Weekly, Monthly |
| `EmptyState` | No-content placeholder | Module-specific (10 variants) |
| `Skeleton` | Loading placeholder | Card, Row, Chart, Text |

### Input Components

| Component | Description | Variants |
|-----------|-------------|----------|
| `SearchBar` | Text search with icon | Inline, Expanded, Global |
| `FilterBar` | Active filter chips with add/remove | Horizontal, Collapsible |
| `FilterChip` | Single removable filter | Active, Inactive, With count |
| `TextInput` | Text input field | Standard, With icon, With error |
| `TextArea` | Multi-line text input | Standard, Auto-grow, Rich text |
| `Select` | Dropdown selector | Standard, Multi-select, Searchable |
| `DatePicker` | Date/time selector | Date, Date range, Time |
| `PrioritySelector` | Priority level picker | 4-level (Low-Urgent), Visual |
| `TagInput` | Multi-tag input with autocomplete | Standard, With suggestions |
| `Toggle` | On/off switch | Standard, With label |
| `Checkbox` | Checkable item | Standard, Indeterminate |
| `RadioGroup` | Single-select radio buttons | Vertical, Horizontal |
| `RangeSlider` | Value range selector | Single, Dual handle |
| `StarRating` | 1-5 star rating input | Interactive, Read-only |
| `QuickCapture` | Fast inline input bar | Task, Idea, Resource |

### Feedback Components

| Component | Description | Variants |
|-----------|-------------|----------|
| `Modal` | Centered overlay dialog | Standard, Full-screen, Side-sheet |
| `Dialog` | Confirmation dialog | Alert, Confirm, Destructive |
| `Toast` | Transient notification | Success, Error, Warning, Info |
| `Tooltip` | Hover info popup | Standard, Rich, Interactive |
| `Popover` | Click-triggered popup | Menu, Form, Info |
| `LoadingSpinner` | Circular loading indicator | Inline, Full-page, Button |
| `ProgressToast` | Long-operation progress | Determinate, Indeterminate |
| `ErrorState` | Error display with recovery | Network, Server, NotFound, Auth |
| `OfflineBanner` | Connectivity status | Offline, Reconnecting, Syncing |

### AI Components

| Component | Description | Variants |
|-----------|-------------|----------|
| `ChatBubble` | Chat message bubble | User, ARIA, System |
| `TypingIndicator` | ARIA is thinking dots | Standard |
| `SuggestionCard` | AI recommendation | Task, Resource, Schedule, Insight |
| `InsightCard` | AI-detected pattern/trend | Pattern, Risk, Achievement |
| `AIBanner` | Proactive AI notification | Suggestion, Alert, Nudge |
| `MatchScore` | Opportunity match indicator | Percentage, Breakdown |
| `ConfidenceBadge` | AI confidence level | High, Medium, Low |
| `QuickCommand` | Command chip in chat input | Standard, With description |
| `ContextChip` | Current AI context indicator | Page, Selection, Conversation |
| `GhostHint` | AI-suggested placeholder text | Input hint, Action hint |
| `StreamingText` | Typewriter-effect AI response | Standard, Code |

**Total Components: 70+ unique components**

---

## Layout Hierarchy

### Layout Pattern Catalog

```
1. SINGLE COLUMN (Mobile default)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚        Top Bar           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                          â”‚
â”‚      Content Area        â”‚
â”‚     (full width)         â”‚
â”‚                          â”‚
â”‚                          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Bottom Nav          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

2. TWO COLUMN â€” Sidebar + Content (Desktop default)
â”Œâ”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚    â”‚      Top Bar        â”‚
â”‚    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ S  â”‚                     â”‚
â”‚ i  â”‚   Content Area      â”‚
â”‚ d  â”‚                     â”‚
â”‚ e  â”‚                     â”‚
â”‚ b  â”‚                     â”‚
â”‚ a  â”‚                     â”‚
â”‚ r  â”‚                     â”‚
â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

3. THREE COLUMN â€” Sidebar + Content + Context Panel
â”Œâ”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”
â”‚    â”‚   Top Bar     â”‚     â”‚
â”‚    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤     â”‚
â”‚ S  â”‚               â”‚ C   â”‚
â”‚ i  â”‚  Content      â”‚ o   â”‚
â”‚ d  â”‚               â”‚ n   â”‚
â”‚ e  â”‚               â”‚ t   â”‚
â”‚ b  â”‚               â”‚ e   â”‚
â”‚ a  â”‚               â”‚ x   â”‚
â”‚ r  â”‚               â”‚ t   â”‚
â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”˜

4. SPLIT VIEW â€” List + Detail (Tasks, Resources)
â”Œâ”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚    â”‚  Top   â”‚  Bar       â”‚
â”‚    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ S  â”‚ List   â”‚  Detail    â”‚
â”‚ i  â”‚ Panel  â”‚  Panel     â”‚
â”‚ d  â”‚ (40%)  â”‚  (60%)     â”‚
â”‚ e  â”‚        â”‚            â”‚
â”‚ b  â”‚ Items  â”‚  Selected  â”‚
â”‚ a  â”‚  ...   â”‚  Item      â”‚
â”‚ r  â”‚  ...   â”‚  Content   â”‚
â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

5. BENTO GRID â€” Dashboard Cards
â”Œâ”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚    â”‚        Top Bar           â”‚
â”‚    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ S  â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ i  â”‚ â”‚   Hero / Briefing    â”‚ â”‚
â”‚ d  â”‚ â”œâ”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”¤ â”‚
â”‚ e  â”‚ â”‚  M  â”‚  M  â”‚ M  â”‚ M  â”‚ â”‚
â”‚ b  â”‚ â”œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¤ â”‚
â”‚ a  â”‚ â”‚  Wide     â”‚  Wide   â”‚ â”‚
â”‚ r  â”‚ â”œâ”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”¤ â”‚
â”‚    â”‚ â”‚  S  â”‚  S  â”‚ S  â”‚ S  â”‚ â”‚
â”‚    â”‚ â””â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”´â”€â”€â”€â”€â”˜ â”‚
â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

6. FULL CANVAS â€” Focus/Roadmap/Graph
â”Œâ”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚    â”‚        Top Bar           â”‚
â”‚    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ S  â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚ i  â”‚ â”‚                    â”‚   â”‚
â”‚ d  â”‚ â”‚   Canvas Area      â”‚   â”‚
â”‚ e  â”‚ â”‚   (interactive)    â”‚   â”‚
â”‚ b  â”‚ â”‚                    â”‚   â”‚
â”‚ a  â”‚ â”‚        [Controls]  â”‚   â”‚
â”‚ r  â”‚ â”‚   [Minimap]        â”‚   â”‚
â”‚    â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

7. GANTT / TIMELINE â€” Goals, Projects
â”Œâ”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚    â”‚         Top Bar             â”‚
â”‚    â”œâ”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ S  â”‚ Name â”‚   Time Axis â†’â†’â†’     â”‚
â”‚ i  â”œâ”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ d  â”‚ G1   â”‚ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ            â”‚
â”‚ e  â”‚ G2   â”‚     â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ      â”‚
â”‚ b  â”‚ G3   â”‚          â–ˆâ–ˆâ–ˆâ–ˆ      â”‚
â”‚ a  â”‚ M1   â”‚ â—†                   â”‚
â”‚ r  â”‚ M2   â”‚         â—†          â”‚
â””â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Responsive Breakpoint Behavior

| Breakpoint | Width | Sidebar | Top Bar | Bottom Nav | Layout | Grid Cols |
|------------|-------|---------|---------|------------|--------|-----------|
| Mobile S | 320-374px | Hidden (drawer) | 48px slim | 5 tabs | 1-col | 1 |
| Mobile L | 375-767px | Hidden (drawer) | 48px slim | 5 tabs | 1-col | 1-2 |
| Tablet | 768-1023px | 64px icons | 64px full | Hidden | 2-col | 2-3 |
| Desktop | 1024-1439px | 240px expanded | 64px full | Hidden | 2-col+ | 3-4 |
| Wide | 1440px+ | 240px expanded | 64px full | Hidden | 3-col+ | 4 |

---

## Content Hierarchy

### Information Priority Model

```
P0 â€” CRITICAL (Always visible, above fold)
â”œâ”€â”€ Today's date / greeting
â”œâ”€â”€ Top 3 priority tasks
â”œâ”€â”€ Overdue items count
â”œâ”€â”€ Active timer / focus state
â””â”€â”€ Urgent notifications

P1 â€” PRIMARY (Visible without scrolling on desktop)
â”œâ”€â”€ Task summary (due today, completed)
â”œâ”€â”€ Habit checklist (today's habits)
â”œâ”€â”€ Quick action buttons
â”œâ”€â”€ AI top recommendation
â””â”€â”€ Sleep score / streak

P2 â€” SECONDARY (Below fold, one scroll)
â”œâ”€â”€ Course progress
â”œâ”€â”€ Goal progress
â”œâ”€â”€ Weekly trend charts
â”œâ”€â”€ Opportunity alerts
â””â”€â”€ Income summary

P3 â€” TERTIARY (Requires navigation or expansion)
â”œâ”€â”€ Full analytics
â”œâ”€â”€ Historical data
â”œâ”€â”€ Settings
â”œâ”€â”€ Archived items
â””â”€â”€ Knowledge graph
```

### Content Density Zones

| Zone | Density | Items/Screen | Example |
|------|---------|-------------|---------|
| Dashboard Hero | High | 15-20 data points | Morning briefing |
| Dashboard Cards | High | 4-6 metrics per card | Productivity overview |
| List Views | High | 15-20 rows visible | Task list |
| Board Views | Medium | 5 columns Ã— 3-5 cards | Kanban boards |
| Detail Views | Low | 1 item, full context | Task detail |
| Canvas Views | Variable | User-controlled zoom | Roadmap canvas |
| Creation Forms | Low | 5-8 fields visible | Create task modal |
| Settings | Low | 3-5 settings per section | Profile settings |

---

## Interaction Hierarchy

### Interaction Priority Levels

```
TIER 1 â€” Primary Actions (Most prominent, always accessible)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ â€¢ Complete task (checkbox)                       â”‚
â”‚ â€¢ Start focus timer                              â”‚
â”‚ â€¢ Log habit (one-tap)                            â”‚
â”‚ â€¢ Quick create (âŠ• button / FAB)                 â”‚
â”‚ â€¢ Navigate between modules (sidebar/tabs)        â”‚
â”‚ â€¢ Global search (Cmd+K)                          â”‚
â”‚ â€¢ Send chat message                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

TIER 2 â€” Secondary Actions (Accessible, not competing with Tier 1)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ â€¢ View detail (click item)                       â”‚
â”‚ â€¢ Switch view (List/Board/Calendar)              â”‚
â”‚ â€¢ Apply filter                                   â”‚
â”‚ â€¢ Sort list                                      â”‚
â”‚ â€¢ Accept AI suggestion                           â”‚
â”‚ â€¢ Mark lesson complete                           â”‚
â”‚ â€¢ Drag card on board                             â”‚
â”‚ â€¢ Expand/collapse section                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

TIER 3 â€” Tertiary Actions (Available on demand)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ â€¢ Edit item details                              â”‚
â”‚ â€¢ Bulk select & operate                          â”‚
â”‚ â€¢ Customize dashboard layout                     â”‚
â”‚ â€¢ Change settings                                â”‚
â”‚ â€¢ Export data                                    â”‚
â”‚ â€¢ Delete item (requires confirmation)            â”‚
â”‚ â€¢ Link items cross-module                        â”‚
â”‚ â€¢ View analytics detail                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

TIER 4 â€” Administrative Actions (Intentionally hard to discover)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ â€¢ Delete account                                 â”‚
â”‚ â€¢ Clear AI memory                                â”‚
â”‚ â€¢ Reset preferences                              â”‚
â”‚ â€¢ Manage integrations                            â”‚
â”‚ â€¢ Export all data                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Interaction Patterns by Input Method

| Pattern | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| Navigate | Sidebar click, Cmd+K | Icon tap, Tab tap | Bottom tab, Drawer |
| Create | âŠ• button, Cmd+K > /new | âŠ• button | FAB (floating) |
| Complete | Checkbox click | Checkbox tap | Swipe right |
| Delete | â‹® menu > Delete | â‹® menu > Delete | Swipe left |
| Search | Cmd+K, Search bar click | Search bar tap | Search icon tap |
| Filter | Click filter chips | Tap filter chips | Bottom sheet |
| Sort | Click column header | Tap sort dropdown | Bottom sheet |
| Reorder | Drag & drop | Long press + drag | Long press + drag |
| View detail | Click row / card | Tap card | Tap card |
| Back | Breadcrumb click | Back arrow | Back arrow / swipe |
| Quick action | Keyboard shortcut | Tap action button | Tap action button |
| Context menu | Right click / â‹® | Long press | Long press |

---

## User Flow Diagrams

### 1. Daily Workflow Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Wake Up  â”‚â”€â”€â”€â†’â”‚ Open ARIA OS â”‚â”€â”€â”€â†’â”‚  Dashboard   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚  (Morning    â”‚
                                     â”‚   Briefing)  â”‚
                                     â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                                            â”‚
                              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                              â–¼             â–¼             â–¼
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚ Review Tasks â”‚ â”‚ Check    â”‚ â”‚ View AI  â”‚
                     â”‚ for Today    â”‚ â”‚ Habits   â”‚ â”‚ Insights â”‚
                     â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                            â”‚              â”‚             â”‚
                            â–¼              â–¼             â–¼
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚ Start Focus  â”‚ â”‚ Log      â”‚ â”‚ Act on   â”‚
                     â”‚ Timer        â”‚ â”‚ Habits   â”‚ â”‚ Suggest. â”‚
                     â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                            â”‚
                            â–¼
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚ Deep Work    â”‚
                     â”‚ Session      â”‚
                     â”‚ (Pomodoro)   â”‚
                     â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                            â”‚
                            â–¼
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚ Complete     â”‚â”€â”€â”€â†’â”‚ AI Suggests  â”‚
                     â”‚ Tasks        â”‚    â”‚ Next Task    â”‚
                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 2. Cross-Module Navigation Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Task      â”‚â”€â”€â”€â”€â†’â”‚ Linked     â”‚â”€â”€â”€â”€â†’â”‚ Goal       â”‚
â”‚  Detail    â”‚     â”‚ Goal       â”‚     â”‚  Detail    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
                                            â”‚
                                            â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Resource  â”‚â†â”€â”€â”€â”€â”‚ Related    â”‚â†â”€â”€â”€â”€â”‚ Project    â”‚
â”‚  Detail    â”‚     â”‚ Resources  â”‚     â”‚  Detail    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚
       â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Knowledge  â”‚â”€â”€â”€â”€â†’â”‚ Connected  â”‚
â”‚   Graph    â”‚     â”‚  Ideas     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 3. AI Interaction Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                 AI ENTRY POINTS                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Chat     â”‚ Command  â”‚ Inline   â”‚ Proactive       â”‚
â”‚ Page     â”‚ Palette  â”‚ AI Btn   â”‚ Notification    â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚          â”‚          â”‚          â”‚
     â–¼          â–¼          â–¼          â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚          ARIA INTENT CLASSIFICATION               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Planning â”‚ Info     â”‚ Action   â”‚ Reflection      â”‚
â”‚ Request  â”‚ Request  â”‚ Request  â”‚ Request         â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚          â”‚          â”‚          â”‚
     â–¼          â–¼          â–¼          â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           CONTEXT LOADING                         â”‚
â”‚  User data + Current page + Conversation history  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚
                   â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           AI RESPONSE GENERATION                  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Text     â”‚ Task     â”‚ Resource â”‚ Schedule        â”‚
â”‚ Response â”‚ Suggest. â”‚ Suggest. â”‚ Suggest.        â”‚
â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚          â”‚          â”‚          â”‚
     â–¼          â–¼          â–¼          â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚        USER ACTION ON RECOMMENDATION              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Accept   â”‚ Modify   â”‚ Dismiss  â”‚ Discuss         â”‚
â”‚ (create) â”‚ (edit)   â”‚ (skip)   â”‚ (follow-up)     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 4. Task Lifecycle Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ BACKLOG â”‚â”€â”€â†’â”‚ TO DO   â”‚â”€â”€â†’â”‚ IN PROG â”‚â”€â”€â†’â”‚ REVIEW  â”‚â”€â”€â†’â”‚  DONE   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â†‘              â”‚              â”‚              â”‚              â”‚
     â”‚              â–¼              â–¼              â–¼              â–¼
     â”‚        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
     â”‚        â”‚ AI breaksâ”‚  â”‚ Timer    â”‚  â”‚ AI check â”‚  â”‚ Celebrateâ”‚
     â”‚        â”‚ into sub â”‚  â”‚ tracking â”‚  â”‚ quality  â”‚  â”‚ + suggestâ”‚
     â”‚        â”‚ tasks    â”‚  â”‚ active   â”‚  â”‚          â”‚  â”‚ next     â”‚
     â””â”€â”€â”€â”€â”€â”€â”€â”€â”¤          â”‚  â”‚          â”‚  â”‚          â”‚  â”‚          â”‚
   (re-open)  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 5. Idea-to-Project Pipeline Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ CAPTURE  â”‚â”€â”€â†’â”‚ AI       â”‚â”€â”€â†’â”‚ VALIDATE â”‚â”€â”€â†’â”‚ BUILD    â”‚
â”‚          â”‚   â”‚ ANALYSIS â”‚   â”‚          â”‚   â”‚          â”‚
â”‚ Quick    â”‚   â”‚ Feasib.  â”‚   â”‚ Checklistâ”‚   â”‚ â†’ Create â”‚
â”‚ capture  â”‚   â”‚ Market   â”‚   â”‚ Research â”‚   â”‚   Projectâ”‚
â”‚ form     â”‚   â”‚ Skills   â”‚   â”‚ MVP Scopeâ”‚   â”‚ â†’ Create â”‚
â”‚          â”‚   â”‚ SWOT     â”‚   â”‚ Timeline â”‚   â”‚   Goal   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                   â”‚
                                                   â–¼
                                              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                              â”‚ LAUNCHED â”‚
                                              â”‚          â”‚
                                              â”‚ Ship +   â”‚
                                              â”‚ Archive  â”‚
                                              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 6. Opportunity Discovery Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ AI Daily     â”‚
â”‚ Scan         â”‚
â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚
       â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ New Matches  â”‚â”€â”€â”€â†’â”‚ User Reviews â”‚â”€â”€â”€â†’â”‚ Save / Apply â”‚
â”‚ Found (3)    â”‚    â”‚ in Radar     â”‚    â”‚ / Dismiss    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚                    â”‚
                           â–¼                    â–¼
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚ View Detail  â”‚    â”‚ Track App.   â”‚
                    â”‚ + Match %    â”‚    â”‚ Status       â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                              â”‚
                              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                              â–¼               â–¼              â–¼
                       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                       â”‚ Applied  â”‚â”€â”€â”€â†’â”‚Interview â”‚â”€â”€â†’â”‚ Offered  â”‚
                       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Navigation Flow Diagrams

### Primary Navigation (Desktop)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Sidebar (always visible)                                 â”‚
â”‚                                                          â”‚
â”‚  Click NavItem â”€â”€â†’ Route change â”€â”€â†’ Page component loads â”‚
â”‚                    URL updates      Content renders       â”‚
â”‚                    Active state     Breadcrumb updates    â”‚
â”‚                    updates                                â”‚
â”‚                                                          â”‚
â”‚  Keyboard: R then D = Dashboard, R then T = Tasks, etc. â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Command Palette Navigation

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Cmd + K â”‚â”€â”€â”€â†’â”‚ Palette open â”‚â”€â”€â”€â†’â”‚ Type query     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                           â”‚
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â–¼                 â–¼                 â–¼
                  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                  â”‚ Navigation â”‚   â”‚ Action     â”‚   â”‚ AI Command â”‚
                  â”‚ Result     â”‚   â”‚ Result     â”‚   â”‚ Result     â”‚
                  â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
                        â”‚                â”‚                 â”‚
                        â–¼                â–¼                 â–¼
                  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                  â”‚ Navigate   â”‚   â”‚ Execute    â”‚   â”‚ AI Process â”‚
                  â”‚ to page    â”‚   â”‚ action     â”‚   â”‚ + respond  â”‚
                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Mobile Navigation

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                                              â”‚
â”‚  Bottom Tab tap â”€â”€â†’ Module page loads        â”‚
â”‚                     Tab indicator moves       â”‚
â”‚                                              â”‚
â”‚  Drawer open â”€â”€â†’ Full nav tree visible       â”‚
â”‚                  Tap item â†’ navigate + close  â”‚
â”‚                                              â”‚
â”‚  Back gesture â”€â”€â†’ Previous page              â”‚
â”‚                   Or: scroll to top           â”‚
â”‚                                              â”‚
â”‚  FAB tap â”€â”€â†’ Quick create (context-aware)    â”‚
â”‚              On Tasks page â†’ New task         â”‚
â”‚              On Ideas page â†’ New idea         â”‚
â”‚              On Dashboard â†’ Choose type       â”‚
â”‚                                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Deep Linking

```
URL Pattern:
  /[module]                    â†’ Module list/default view
  /[module]?view=[view]        â†’ Specific view (list, board, calendar)
  /[module]/[id]               â†’ Item detail
  /[module]/[id]?tab=[tab]     â†’ Item detail with specific tab
  /[module]?filter=[filters]   â†’ Pre-filtered view
  /settings/[section]          â†’ Specific settings section

Examples:
  /tasks                       â†’ Task list (default view)
  /tasks?view=board            â†’ Task kanban board
  /tasks/abc-123               â†’ Task detail
  /tasks/abc-123?tab=subtasks  â†’ Task detail, subtasks tab
  /goals?view=timeline         â†’ Goals Gantt view
  /chat                        â†’ ARIA chat (new conversation)
  /settings/appearance         â†’ Appearance settings
```

---

## Accessibility Architecture

### ARIA Landmarks

```html
<body>
  <header role="banner">           <!-- TopBar -->
  <nav role="navigation">          <!-- Sidebar -->
  <main role="main">               <!-- ContentArea -->
    <nav role="navigation">        <!-- In-page tabs -->
    <section aria-label="...">     <!-- Content sections -->
  </main>
  <aside role="complementary">     <!-- ContextPanel -->
  <footer role="contentinfo">      <!-- BottomTabBar (mobile) -->
  <div role="search">              <!-- Global Search -->
</body>
```

### Focus Management Rules

| Scenario | Focus Behavior |
|----------|---------------|
| Page load | Focus on `<main>` heading (h1) |
| Modal open | Focus on modal title or first input |
| Modal close | Return focus to trigger element |
| Drawer open | Focus on first nav item |
| Drawer close | Return focus to trigger |
| Toast appear | Announce via aria-live, don't move focus |
| Error | Focus on first error field |
| Delete confirm | Focus on cancel button (safe default) |

### Keyboard Shortcuts

| Shortcut | Action | Scope |
|----------|--------|-------|
| `Cmd/Ctrl + K` | Open command palette | Global |
| `Cmd/Ctrl + /` | Open keyboard shortcut reference | Global |
| `Cmd/Ctrl + N` | Quick create | Global |
| `Escape` | Close modal/palette/panel | Global |
| `R then D` | Navigate to Dashboard | Global |
| `R then T` | Navigate to Tasks | Global |
| `R then C` | Navigate to Courses | Global |
| `R then G` | Navigate to Goals | Global |
| `R then P` | Navigate to Projects | Global |
| `Tab` | Next focusable element | Global |
| `Shift + Tab` | Previous focusable element | Global |
| `Space/Enter` | Activate focused element | Global |
| `â†‘ / â†“` | Navigate list items | Lists |
| `â† / â†’` | Navigate tabs / board columns | Tabs/Board |
| `J / K` | Next/previous item (vim-style) | Lists |
| `X` | Toggle select current item | Lists |
| `E` | Edit focused item | Detail views |
| `D` | Mark as done | Task views |

---

## Design Principles Applied

| Principle | How It's Expressed in Wireframes |
|-----------|----------------------------------|
| **Mobile First** | Every wireframe starts with mobile, then adapts up |
| **AI First** | AI components in every module (suggestions, analysis, insights) |
| **Accessibility First** | ARIA landmarks, keyboard nav, focus management documented |
| **High Info Density** | Dashboard cards pack 15-20 data points above fold |
| **Fast Scannability** | Z-pattern reading, priority-based content ordering |
| **Progressive Disclosure** | L0â†’L4 hierarchy, expand for detail, collapse for overview |
| **Graceful Degradation** | Error states, offline mode, AI unavailable fallback |
| **Cross-Module Intelligence** | Deep linking, related items, AI connections between modules |

---

> [!NOTE]
> This wireframe system is purely structural. It defines content placement, component hierarchy, interaction patterns, and user flows. Visual styling (colors, fonts, shadows, animations) is documented separately in Design.md and DesignSystem.md.

---

*Generated 2026-06-11 â€¢ ARIA OS Wireframe System v2.0.0 â€” All 20 modules covered across 7 wireframe documents*
