# ARIA OS — Enterprise Frontend Implementation Backlog

> **Document ID:** FE-BACKLOG-001  
> **Version:** 1.0.0  
> **Status:** Active  
> **Last Updated:** 2026-06-15  
> **Classification:** Internal — Execution Reference

---

## Scoring Legend

| Score | Meaning |
|-------|---------|
| **P0** | Blocks all other work / core differentiator |
| **P1** | High priority — significant user or business impact |
| **P2** | Medium — enhances experience, not blocking |
| **P3** | Low — nice to have, post-MVP |

---

## Dependency Graph

```
EPIC 0: Foundation ──────────────────────────────────────┐
  ├── EPIC 1: Design System Tokens & Theme Engine ───────┤
  ├── EPIC 2: Responsive Shell Architecture ─────────────┤
  ├── EPIC 3: Navigation & Command Center ───────────────┤
  └── EPIC 4: UI Component Library ──────────────────────┤
                                                          │
EPIC 5: AI Interaction Platform ──────────────────────────┤
  ├── EPIC 6: Dashboard v2 ───────────────────────────────┤
  ├── EPIC 7: Tasks System Enhancement ───────────────────┤
  ├── EPIC 8: Knowledge Vault ────────────────────────────┤
  ├── EPIC 9: Analytics Intelligence ─────────────────────┤
  ├── EPIC 10: Opportunity Radar v2 ──────────────────────┤
  └── EPIC 11: Settings & System ─────────────────────────┤
                                                          │
EPIC 12: Enterprise Workflows ────────────────────────────┘
  ├── EPIC 13: Deep Work / Focus Mode
  ├── EPIC 14: Notification Center
  ├── EPIC 15: Weekly Review System
  └── EPIC 16: Global Search & Discovery

EPIC 17: Production Polish
  ├── Accessibility (WCAG 2.2 AA)
  ├── Responsive QA (5 breakpoints)
  ├── Performance Optimization
  └── Testing Suite
```

---

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'background': '#0A0B0F', 'primaryColor': '#6366F1', 'secondaryColor': '#00FFA3', 'tertiaryColor': '#818CF8', 'primaryTextColor': '#F1F5F9', 'secondaryTextColor': '#94A3B8', 'lineColor': '#6366F1', 'fontFamily': 'DM Sans', 'nodeBorder': '#6366F1', 'clusterBkg': '#13151A', 'clusterBorder': '#1E293B' }}}%%
gantt
    title ARIA OS Frontend Implementation Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Foundation
    EPIC 0: Foundation          :done, f0, 2026-06-01, 14d
    EPIC 1: Design System       :done, f1, 2026-06-05, 12d
    EPIC 2: Shell Architecture  :done, f2, 2026-06-08, 10d
    EPIC 3: Navigation          :active, f3, 2026-06-10, 10d
    EPIC 4: UI Component Lib    :active, f4, 2026-06-12, 14d

    section Core Features
    EPIC 5: AI Platform         :f5, 2026-06-15, 18d
    EPIC 6: Dashboard v2        :f6, 2026-06-18, 14d
    EPIC 7: Tasks Enhancement   :f7, 2026-06-20, 12d
    EPIC 8: Knowledge Vault     :f8, 2026-06-22, 16d
    EPIC 9: Analytics           :f9, 2026-06-25, 14d
    EPIC 10: Opportunity Radar  :f10, 2026-06-28, 10d
    EPIC 11: Settings           :f11, 2026-06-30, 8d

    section Enterprise
    EPIC 12: Enterprise Workflows :f12, 2026-07-05, 16d
    EPIC 13: Focus Mode          :f13, 2026-07-08, 10d
    EPIC 14: Notification Center :f14, 2026-07-10, 12d
    EPIC 15: Weekly Review       :f15, 2026-07-12, 10d
    EPIC 16: Global Search       :f16, 2026-07-15, 14d
    EPIC 17: Production Polish   :f17, 2026-07-20, 20d
```

---

## EPIC 0: Foundation

### FEATURE 0.1: Design Token Alignment
**Depends on:** Nothing  
**Priority:** P0  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P0 (blocks everything) | **User Impact:** Low | **Technical Risk:** Low

#### Screens/Components
- `tailwind.config.js` — align all color primitives with Antigravity OKLCH palette

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 0.1.1 | Align all color primitives with Antigravity OKLCH palette | All tokens match enterprise theme.css — slate/indigo/emerald/amber/rose scales |
| 0.1.2 | Add missing semantic tokens (sidebar, chart colors, glows) | Every enterprise token has a corresponding Tailwind class |
| 0.1.3 | Add light mode token overrides | `.light` class switches all tokens to light variant |
| 0.1.4 | Add high contrast token overrides | `.high-contrast` class toggles contrast boost on all surfaces |
| 0.1.5 | Add motion tokens (6 durations, 6 easings) | `motion-duration-*`, `motion-ease-*` classes exist and are usable |
| 0.1.6 | Add z-index scale (7 levels: base, dropdown, sticky, overlay, modal, popover, tooltip) | `z-base` through `z-tooltip` all defined |
| 0.1.7 | Add opacity tokens (6 levels: disabled, hover, active, ghost, skeleton, overlay) | All 6 opacity semantic tokens exist |
| 0.1.8 | Add shadow/glow tokens (11 levels: 5 elevation + 3 glow + 3 inner) | `shadow-elevation-*` and `shadow-glow-*` classes work |
| 0.1.9 | Add breakpoint tokens (5 custom: mobile, tablet, desktop, wide, ultra) | `bp-mobile`, `bp-tablet`, `bp-desktop`, `bp-wide`, `bp-ultra` defined |

---

### FEATURE 0.2: Theme Engine
**Depends on:** 0.1  
**Priority:** P0  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P0 | **User Impact:** Medium | **Technical Risk:** Medium

#### Screens/Components
- `components/providers/ThemeProvider.tsx`
- `components/settings/ThemeSwitcher.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 0.2.1 | Create `ThemeContext` with 3-axis theme state (dark/light × normal/high-contrast × 4 accents) | 24 theme combinations possible |
| 0.2.2 | Implement `ThemeProvider` wrapper component | Wraps entire app, applies theme class to `<html>` |
| 0.2.3 | Add localStorage persistence | Theme survives page refresh |
| 0.2.4 | Add Supabase `user_preferences` sync | Theme syncs across logged-in devices |
| 0.2.5 | Respect `prefers-color-scheme` on first visit | Uses OS preference for initial theme |
| 0.2.6 | Add 300ms crossfade transition on theme change | Theme switch is smooth, not jarring |
| 0.2.7 | Build `ThemeSwitcher` UI (accent color grid) | 4 accent colors shown with live preview swatches |
| 0.2.8 | Build contrast toggle in ThemeSwitcher | High contrast toggle visibly changes all surfaces |
| 0.2.9 | Add inline `<script>` to prevent FOUC | No flash of wrong theme on page load |

---

### FEATURE 0.3: Font & Typography System
**Depends on:** 0.1  
**Priority:** P0  
**Effort:** 1 day | **Agents:** 1  
**Business Criticality:** P0 | **User Impact:** High | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 0.3.1 | Verify Syne/DM Sans/JetBrains Mono load via `next/font/google` | All 3 fonts load, CSS variables work |
| 0.3.2 | Add fluid typography scale using `clamp()` | Headings scale smoothly between breakpoints |
| 0.3.3 | Add all type tokens to tailwind.config | `text-display-hero` through `text-caption` all map correctly |

---

## EPIC 1: Responsive Shell Architecture

### FEATURE 1.1: Desktop Shell (≥1024px)
**Depends on:** 0.1, 0.3  
**Priority:** P0  
**Effort:** 5 days | **Agents:** 2  
**Business Criticality:** P0 (primary UX) | **User Impact:** Very High | **Technical Risk:** Low

#### Screens/Components
- `components/layout/DesktopShellLayout.tsx`
- `components/layout/DesktopSidebar.tsx`
- `components/layout/TopNav.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 1.1.1 | Create full-height flex layout: sidebar (240px) + main area | Sidebar pinned left, content fills remainder |
| 1.1.2 | Add sticky TopNav (h-16, `backdrop-blur-md`) | Scrolls with content, glass effect on bg |
| 1.1.3 | Add main scrollable content area | Content scrolls independently of sidebar |
| 1.1.4 | Rebuild DesktopSidebar with proper ARIA (existing `layout/Sidebar.tsx` as base) | `role="navigation"`, `aria-label`, `aria-current="page"` on active |
| 1.1.5 | Add 6 nav groups with section dividers: Core, Track, Build, Intelligence, ARIA, System | Sections separated by `<hr>` or spacing |
| 1.1.6 | Add real-time badge counts via Realtime subscription | Counts update without page refresh |
| 1.1.7 | Add collapsed state (56px icon-only) with toggle | Click toggle collapses sidebar to show only icons |
| 1.1.8 | Rebuild TopNav: breadcrumbs + global search trigger + notification bell + user menu | All 4 elements present and functional |
| 1.1.9 | Add breadcrumb resolver (`Home > Module > [Item Title]`) | Max 3 levels, collapses on tablet |
| 1.1.10 | Add notification dropdown with Today/Yesterday sections | Shows grouped notifications |

---

### FEATURE 1.2: Tablet Shell (768-1199px)
**Depends on:** 1.1  
**Priority:** P1  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Screens/Components
- `components/layout/TabletShellLayout.tsx`
- `components/layout/TabletDrawer.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 1.2.1 | Create responsive wrapper that activates at 768-1199px | Sidebar collapses to icon drawer |
| 1.2.2 | Add hamburger menu toggle in TopNav | Opens off-canvas drawer |
| 1.2.3 | Build slide-in drawer (280px) with backdrop scrim | 0.3s cubic-bezier animation, transform translateX |
| 1.2.4 | Add body scroll lock when drawer is open | Body doesn't scroll |
| 1.2.5 | Build split-pane mode (30% list + 70% detail) | Resizable divider via react-resizable-panels |

---

### FEATURE 1.3: Mobile Shell (<768px)
**Depends on:** 1.1  
**Priority:** P1  
**Effort:** 4 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Screens/Components
- `components/layout/MobileShellLayout.tsx`
- `components/layout/BottomNav.tsx`
- `components/layout/MobileDrawer.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 1.3.1 | Create full-height flex layout: top bar + content + bottom bar | 3 zones stack vertically |
| 1.3.2 | Add safe area padding using `env(safe-area-inset-*)` | Content not obscured by notch/home indicator |
| 1.3.3 | Build 5-tab BottomNav: Home, Tasks, New (FAB), Chat, More | Active tab highlighted, FAB in center |
| 1.3.4 | Add glass morphism background on BottomNav (`backdrop-blur-md`) | Background shows through subtly |
| 1.3.5 | Add badge counts on tabs (Realtime subscribed) | Tasks count, Chat dot |
| 1.3.6 | Build hamburger drawer for full nav | Contains all sidebar links |
| 1.3.7 | Add gesture: swipe right to open drawer | Touch-compatible |

---

### FEATURE 1.4: Responsive Shell Selector
**Depends on:** 1.1, 1.2, 1.3  
**Priority:** P0  
**Effort:** 1 day | **Agents:** 1  
**Business Criticality:** P0 | **User Impact:** High | **Technical Risk:** Low

#### Screens/Components
- `hooks/useResponsive.ts`
- `components/layout/ShellSelector.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 1.4.1 | Create hook `useResponsive()` returning 'mobile'\|'tablet'\|'desktop' | Returns correct breakpoint string |
| 1.4.2 | Render correct shell based on breakpoint | ShellSelector swaps layout at each breakpoint |
| 1.4.3 | Add resize debounce (200ms) | No layout thrashing during window resize |
| 1.4.4 | Test all 5 breakpoints manually | Verified on 375/768/1024/1440/1920px |

---

## EPIC 2: Command Center & Global Search

### FEATURE 2.1: Command Palette (Cmd+K)
**Depends on:** 1.1  
**Priority:** P1  
**Effort:** 5 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** Very High | **Technical Risk:** Medium

#### Screens/Components
- `components/command-center/CommandCenter.tsx`
- `hooks/useCommandCenter.ts`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 2.1.1 | Build modal overlay with backdrop blur (20px) | Centered, max-w-2xl, max-height 80vh |
| 2.1.2 | Add search input with AI icon + placeholder | `font-display` 20px, auto-focuses on open |
| 2.1.3 | Implement keyboard navigation (↑↓↵ Esc) | Arrow keys navigate list, Enter selects, Esc closes |
| 2.1.4 | Add 5 result sections: Universal Search, AI Search, Commands, Recent Activity, Navigation | Each section has monospace uppercase header |
| 2.1.5 | Build result items with icons, type badges, keyboard hint | Uniform item height, hover/active states |
| 2.1.6 | Add Cmd+K/Ctrl+K global shortcut | Opens/closes toggle, prevents default browser behavior |
| 2.1.7 | Add radial gradient background (indigo + emerald) | SVG-based, no image request |
| 2.1.8 | Implement command execution: navigate, create, trigger | One click navigates to correct route or triggers action |
| 2.1.9 | Create `useCommandCenter` hook | Exposes `open`, `close`, `toggle`, `isOpen` |

---

### FEATURE 2.2: Global Search
**Depends on:** 2.1  
**Priority:** P1  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** High

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 2.2.1 | Add search input in TopNav with ⌘K hint badge | Focuses command center on click |
| 2.2.2 | Implement fuzzy search client-side (Fuse.js) | Results return in <100ms |
| 2.2.3 | Add module-scoped search shortcuts (Cmd+Shift+K/P/O) | Scoped to Knowledge/Projects/Opportunities |
| 2.2.4 | Connect to backend semantic search endpoint with fallback | Falls back to FTS when AI unavailable |
| 2.2.5 | Build search operators: /done, /snooze, /new task, /go dashboard | 10+ operators recognized and executed |

---

## EPIC 3: UI Component Library

### FEATURE 3.1: Core Primitives
**Depends on:** 0.1  
**Priority:** P0  
**Effort:** 3 days | **Agents:** 2  
**Business Criticality:** P0 | **User Impact:** High | **Technical Risk:** Low

#### Components & Tasks

| Component | Tasks | AC |
|-----------|-------|-----|
| `Button` (upgrade) | Add scale-press (0.96), icon position, group hover | All 5 variants × 3 sizes render correctly |
| `Card` (upgrade) | Add 4 variants: default/interactive/compact/highlight | 3-part anatomy enforced (header/content/footer) |
| `Input` (upgrade) | Add 7 states + validation icons + shake on error | Error state has border + icon + message |
| `Skeleton` (upgrade) | Add 5 variants: text/circle/card/chart/table-row | shimmer animation, configurable width/height |
| `Badge` (new) | 3 variants with color mapping | Colors match priority/status scheme |
| `Spinner` (new) | 3 sizes, configurable speed, accessible | `role="status"`, `aria-label` required |

---

### FEATURE 3.2: Radix Integration
**Depends on:** 3.1  
**Priority:** P1  
**Effort:** 5 days | **Agents:** 3  
**Business Criticality:** P1 | **User Impact:** Medium | **Technical Risk:** Low

#### Components & Tasks

| Component | Tasks | AC |
|-----------|-------|-----|
| `Dialog` | Build with Framer Motion + focus trap + Esc close | 5 sizes (sm/md/lg/xl/full), portal-based |
| `Sheet` | Build slide-over panel (right-side) | Configurable width, backdrop dismiss |
| `Drawer` | Build bottom sheet (mobile-first) | Drag to dismiss, snap points |
| `Popover` | Build with arrow positioning, auto-flip | Click outside closes |
| `Tooltip` | Build with delay (300ms show, 100ms hide) | Keyboard focus shows tooltip |
| `Select` | Build with search + virtual scroll | Dropdown at z-overlay level |
| `Switch` | Build with motion thumb animation | Label click toggles |
| `Tabs` | Build with underline animation | Keyboard arrow navigation, tab activation |
| `DropdownMenu` | Build with sub-menus | Radix context-menu compatible |

---

### FEATURE 3.3: Data Display Components
**Depends on:** 3.1  
**Priority:** P1  
**Effort:** 7 days | **Agents:** 4  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Components & Tasks

| Component | Tasks | AC |
|-----------|-------|-----|
| `KPIStrip` | Horizontal metric cards with icon + value + trend + mini sparkline | Scrolls horizontally on mobile (CSS snap) |
| `BentoGrid` | CSS grid with `grid-auto-flow: dense`, 1/2/4 column spans | Items visually weight by priority |
| `ProgressRing` | SVG-based circular progress (stroke-dasharray) | Configurable size, stroke, color |
| `ActivityHeatmap` | GitHub-style grid (52 weeks × 7 days) | 5 intensity levels, tooltip on hover |
| `Timeline` | Vertical/horizontal timeline with milestone nodes | Animated connection line (gradient) |
| `ChartContainer` | Recharts wrapper with consistent dark theming | Dark-themed tooltip, responsive container |
| `DataTable` (upgrade) | Add column visibility toggle + row expansion + batch actions | Virtual scrolling for 10k+ rows |

---

### FEATURE 3.4: AI Components
**Depends on:** 3.1  
**Priority:** P1  
**Effort:** 6 days | **Agents:** 3  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Components & Tasks

| Component | Tasks | AC |
|-----------|-------|-----|
| `ThinkingIndicator` | Pulsing emerald glow, 3 bounce dots animation | 5 states: idle/thinking/complete/error/cancelled |
| `StreamingText` | Token-by-token reveal (30ms delay), cursor blink, blur transition | Blur fades from 2px to 0px on each token |
| `GhostHint` | Muted italic suggestion, Tab key accepts | Hidden/visible/filled/dismissed states |
| `SuggestionChips` | Horizontal chips with gradient hover effect | Accept/dismiss with transition |
| `ConfidenceBadge` | Color-coded by %: green (85+), amber (60-84), red (<60) | Tooltip shows reasoning on hover |
| `AIInsightCard` | Gradient bg by type: recommendation/insight/alert | Action button appears on hover |
| `AIUndo` | 10s countdown toast with undo button | Expired state after timer runs out |

---

### FEATURE 3.5: Empty States & Error States
**Depends on:** 3.1  
**Priority:** P1  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P1 | **User Impact:** Medium | **Technical Risk:** Low

#### Components & Tasks

| Component | Tasks | AC |
|-----------|-------|-----|
| `EmptyCanvas` | Full component: illustration + badge + title + description + primary CTA + secondary CTA | All 6 sections render, responsive |
| `ErrorState` | Context-aware: different message per status code (400/404/429/500) | Recovery action calls correct function |
| `OfflineBanner` | Animated banner with sync icon + retry button | `role="alert"`, `aria-live="assertive"` |
| `LoadingScreen` | Skeleton that matches page content structure | Content-aware, not generic spinner |

---

## EPIC 4: AI Interaction Platform

### FEATURE 4.1: ARIA Intelligence 3-Panel Layout
**Depends on:** 1.1, 3.4  
**Priority:** P0 (core differentiator)  
**Effort:** 7 days | **Agents:** 3  
**Business Criticality:** P0 | **User Impact:** Very High | **Technical Risk:** High

#### Screens/Components
- `app/(dashboard)/chat/page.tsx` — rebuild as 3-panel
- `components/chat/ChatPanel.tsx`
- `components/chat/ConversationList.tsx`
- `components/chat/ContextPanel.tsx`
- `components/chat/MessageBubble.tsx`
- `components/ai/AIDock.tsx` — finalize

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 4.1.1 | Build 3-panel: left 280px (conversations) + center (chat) + right 320px (context) | Resizable panels with min-widths |
| 4.1.2 | Left panel: conversation history with search + "New Thread" CTA | Shows last 50 conversations |
| 4.1.3 | Center panel: welcome state (ARIA avatar), message list (auto-scroll), input area | Scrolls to bottom on new message |
| 4.1.4 | Right panel: agent status list, system context, memory stats | Agent active/idle indicators |
| 4.1.5 | Build message bubbles: user (right, primary bg) / assistant (left, elevated bg) | Staggered AnimatePresence entrance |
| 4.1.6 | Add AI agent badge (which agent is responding) | Agent name + icon + confidence badge |
| 4.1.7 | Add thought process expand/collapse (agent reasoning) | Expandable section within AI messages |
| 4.1.8 | Finalize AIDock: fixed bottom-right, links to active chat | Opens chat on click, shows avatar |
| 4.1.9 | Add 4 AIDock states: idle (collapsed button), open (chat widget), thinking, streaming | Each state has distinct visual |

---

### FEATURE 4.2: AI Response Streaming
**Depends on:** 4.1  
**Priority:** P1  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P1 | **User Impact:** Very High | **Technical Risk:** High

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 4.2.1 | Add SSE client for streaming responses | Chunks display as received |
| 4.2.2 | Implement token reveal animation (30ms per token) | Blur fade-in from 2px to 0px |
| 4.2.3 | Add cursor blink during streaming (500ms) | Blinking vertical bar at end of text |
| 4.2.4 | Add "Stop generation" button | Aborts fetch, shows partial response |
| 4.2.5 | Add complete state transition | Subtle success indicator (checkmark or color shift) |

---

### FEATURE 4.3: Ghost Hint System
**Depends on:** 4.1  
**Priority:** P2  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 4.3.1 | Detect user intent from input context after 2s idle | Shows after 2s of no typing in empty input |
| 4.3.2 | Render muted italic suggestion below input | Tab key accepts, continued typing dismisses |
| 4.3.3 | Add accept animation (ghost text morphs to real text) | 200ms morph animation |
| 4.3.4 | Integrate with ARIA suggestion engine | Suggests task names, goal links, resource references |

---

## EPIC 5: Dashboard v2

### FEATURE 5.1: Dashboard Page Redesign
**Depends on:** 1.1, 3.3, 3.4  
**Priority:** P0 (first impression)  
**Effort:** 8 days | **Agents:** 4  
**Business Criticality:** P0 | **User Impact:** Very High | **Technical Risk:** Medium

#### Screens/Components
- `app/(dashboard)/dashboard/page.tsx` — rebuild
- `components/dashboard/KPIStrip.tsx`
- `components/dashboard/MorningBriefing.tsx`
- `components/dashboard/TodayFocus.tsx`
- `components/dashboard/CourseProgress.tsx`
- `components/dashboard/OpportunityFeed.tsx`
- `components/dashboard/ActivityHeatmap.tsx`
- `components/dashboard/WeeklyVelocity.tsx`
- `components/dashboard/MilestoneTimeline.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 5.1.1 | Rebuild with 7 content zones (Z1-Z7) | Time-of-day greeting (morning/midday/evening/night) |
| 5.1.2 | Build KPI Strip (6 metrics with trend arrows + sparklines) | Mobile: snap-scroll with 3 visible at a time |
| 5.1.3 | Build Morning Briefing banner with gradient | Shows AI greeting + priority highlight |
| 5.1.4 | Build Today's Focus section with checkboxes | Checked → line-through → optimistic complete |
| 5.1.5 | Add AI suggested focus block (emerald border, time range) | Shows as card with gradient |
| 5.1.6 | Build Course Progress (3 cards with rings + status) | Status: On Track (indigo), Needs Attn (amber), Almost Done (emerald) |
| 5.1.7 | Build Opportunity Feed (top 2 matches with score badges) | Match score 92% = green glow, 85% = neutral |
| 5.1.8 | Build Active Projects (2 cards with progress bars) | Blocked status shows warning icon |
| 5.1.9 | Build Activity Heatmap (52×7 GitHub-style grid) | 5 intensity levels, tooltip on hover shows count |
| 5.1.10 | Build Weekly Velocity (7-day bar chart) — desktop only | Today highlighted with shadow glow |
| 5.1.11 | Build Milestone Timeline (5-point milestone progress) | Gradient connection line |

---

### FEATURE 5.2: Dashboard Widget System
**Depends on:** 5.1  
**Priority:** P2  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 5.2.1 | Build widget visibility toggles per zone (8 zones) | Persisted to Supabase |
| 5.2.2 | Add drag-to-reorder within bento grid | react-dnd or @dnd-kit |

---

## EPIC 6: Tasks System Enhancement

### FEATURE 6.1: Kanban Board
**Depends on:** 1.1, 3.2  
**Priority:** P1  
**Effort:** 5 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Screens/Components
- `app/(dashboard)/tasks/kanban/page.tsx`
- `components/tasks/KanbanBoard.tsx`
- `components/tasks/KanbanCard.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 6.1.1 | Build 4-column layout: Backlog, In Progress, Review, Done | Horizontal scroll with `scroll-snap` |
| 6.1.2 | Add drag-and-drop between columns (@dnd-kit) | Smooth animation, no flicker |
| 6.1.3 | Add task card with priority bar + assignee + tags | Compact card fits column width |
| 6.1.4 | Add column count badges (live count) | Realtime update via subscription |
| 6.1.5 | Add "Add Card" button per column | Opens inline form |
| 6.1.6 | Add AI suggestion card floating above columns | Emerald pulse when thinking |

---

### FEATURE 6.2: Task Detail View
**Depends on:** 1.1  
**Priority:** P1  
**Effort:** 4 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Low

#### Screens/Components
- `app/(dashboard)/tasks/[id]/page.tsx`
- `components/tasks/TaskDetail.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 6.2.1 | Build detail layout: breadcrumb + header + description + subtasks + activity | Full CRUD for subtasks |
| 6.2.2 | Add subtask list with checkboxes + nested progress bar | Completed subtask = line-through + dim |
| 6.2.3 | Add notes section (textarea with auto-save) | Auto-saves 2s after last keystroke |
| 6.2.4 | Add activity feed (timeline of status changes, comments, edits) | Reverse chronological |
| 6.2.5 | Add related items sidebar (linked goals, projects, resources) | Cross-module links are clickable |
| 6.2.6 | Add "Mark Complete" CTA with success animation | Checkmark animation, optional redirect |

---

### FEATURE 6.3: Bulk Operations
**Depends on:** 6.1  
**Priority:** P2  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 6.3.1 | Add checkbox selection per row with select-all toggle | Shows count of selected items |
| 6.3.2 | Build floating bulk action bar (complete/delete/move/assign) | Appears when ≥1 item selected |
| 6.3.3 | Add confirmation dialog for bulk delete | "Delete N items?" with count |

---

### FEATURE 6.4: Keyboard Shortcuts
**Depends on:** 6.1, 6.2  
**Priority:** P2  
**Effort:** 1 day | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 6.4.1 | `n` — new task | Opens create modal |
| 6.4.2 | `j/k` — navigate list | Moves focus up/down |
| 6.4.3 | `Enter` — open selected task | Navigates to detail |
| 6.4.4 | `e` — edit task | Opens edit modal |
| 6.4.5 | `d` — delete task (with confirmation) | Confirms, then deletes |
| 6.4.6 | `c` — complete task | Optimistic update |

---

## EPIC 7: Knowledge Vault

### FEATURE 7.1: Knowledge Graph
**Depends on:** 1.1  
**Priority:** P1  
**Effort:** 8 days | **Agents:** 3  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Very High

#### Screens/Components
- `app/(dashboard)/knowledge/page.tsx`
- `components/knowledge/KnowledgeGraph.tsx`
- `components/knowledge/NodeDetail.tsx`
- `components/knowledge/KnowledgeSearch.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 7.1.1 | Build canvas with force-directed layout (d3-force or vis-network) | Nodes repel, edges attract, stable layout |
| 7.1.2 | Add zoom/pan with grab cursor | Touch-compatible pinch zoom |
| 7.1.3 | Add node types: notes/resources/ideas with distinct colors | 3 shapes × 3 colors |
| 7.1.4 | Add click-to-select node → opens detail slide-over | Right panel slides in |
| 7.1.5 | Add search bar with semantic search → highlights matching nodes | Search results glow on graph |
| 7.1.6 | Add view toggles: Graph, List, Map | Each view preserves state |
| 7.1.7 | Build NodeDetail: title, description, properties, relationships | Connected entities shown as links |
| 7.1.8 | Build KnowledgeSearch with filters (type, tag, date range) | Results render as both list + graph highlights |

---

### FEATURE 7.2: Resource Library Enhancement
**Depends on:** 7.1  
**Priority:** P1  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P1 | **User Impact:** Medium | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 7.2.1 | Add grid/list view toggle | Preference persists |
| 7.2.2 | Add tag filtering with multi-select | OR/AND toggle |
| 7.2.3 | Add collection grouping | Drag resources into collections |

---

### FEATURE 7.3: Knowledge Discovery
**Depends on:** 7.1  
**Priority:** P2  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 7.3.1 | Add "Daily Knowledge Nudge" AI card | Agent A02 output rendered as glass card |
| 7.3.2 | Add trending topics (tags with growth indicator) | Auto-calculated from recent usage |
| 7.3.3 | Add "Active Collections" horizontal scroll row | Recently edited appear first |

---

## EPIC 8: Analytics Intelligence

### FEATURE 8.1: Analytics Dashboard
**Depends on:** 1.1, 3.3  
**Priority:** P1  
**Effort:** 5 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Screens/Components
- `app/(dashboard)/analytics/page.tsx`
- `components/analytics/AnalyticsPage.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 8.1.1 | Build KPI tile grid (6 metrics with sparklines + trends) | Each tile shows metric + trend badge |
| 8.1.2 | Build Focus Heatmap (time-of-day × day-of-week) | D3 heatmap or CSS grid |
| 8.1.3 | Build Skill Vector radar chart (Recharts RadarChart) | 6 skills plotted, interactive |
| 8.1.4 | Build Deep Analysis reports list | Timestamped, filterable by type |
| 8.1.5 | Add AI Intelligence Hub banner with shimmer animation | Shows latest AI insight |

---

### FEATURE 8.2: Report Generator
**Depends on:** 8.1  
**Priority:** P2  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 8.2.1 | Build date range picker with presets (7d/30d/90d/custom) | Calendar-based selection |
| 8.2.2 | Add metric multi-selector (19 core metrics) | Select/deselect all |
| 8.2.3 | Add CSV/JSON export | Downloads formatted file |

---

## EPIC 9: Opportunity Radar v2

### FEATURE 9.1: Radar Visualization
**Depends on:** 1.1, 3.4  
**Priority:** P1  
**Effort:** 6 days | **Agents:** 3  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** High

#### Screens/Components
- `app/(dashboard)/opportunities/page.tsx` — rebuild
- `components/opportunities/RadarScanner.tsx`
- `components/opportunities/MatchCard.tsx`
- `components/opportunities/SignalList.tsx`
- `components/opportunities/OpportunityDetail.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 9.1.1 | Build radar visualization (CSS concentric circles + rotating scan line) | Continuous rotation animation |
| 9.1.2 | Plot signals as dots positioned by score × category | 4 quadrants: Strategic, Financial, Partnership, Career |
| 9.1.3 | Add signal pulse animation on new detection | Green ping effect |
| 9.1.4 | Build MatchCard with large score badge + drop-shadow | Score 94% has prominent display |
| 9.1.5 | Build SignalList with type icon + description + action button | Category filter tabs at top |
| 9.1.6 | Build OpportunityDetail overlay with full details + status dropdown | Apply link, save, dismiss actions |

---

### FEATURE 9.2: Match Scoring UI
**Depends on:** 9.1  
**Priority:** P2  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 9.2.1 | Build score breakdown tooltip (skill match, interest, goal alignment, timing, location) | Hover on badge shows radar or list |
| 9.2.2 | Add "Refresh Scan" action with spin animation | Spinning animation during scan |
| 9.2.3 | Add match tier filter pills: ≥90% (exceptional), 70-89% (strong), 50-69% (moderate) | Each pill filters list |

---

## EPIC 10: Settings & System

### FEATURE 10.1: Settings Page (6 Sections)
**Depends on:** 0.2, 1.1  
**Priority:** P1  
**Effort:** 5 days | **Agents:** 3  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Low

#### Screens/Components
- `app/(dashboard)/settings/page.tsx`
- `components/settings/SettingsPage.tsx`

#### Sections & Tasks

| Section | Tasks | AC |
|---------|-------|-----|
| User Profile | Avatar upload + name + email display | Supabase profile update |
| AI & Personalization | AI model selector (Ollama/Claude), temperature slider, briefing time, per-agent toggles | Toggle each of 10 agents on/off |
| Notifications | Per-category enable/disable (7 categories), priority threshold slider | Changes persist immediately |
| Privacy & Data | Data export button, AI usage toggle, analytics opt-out, memory visibility | Export downloads JSON |
| Appearance | Theme picker (7 combos shown as cards), sidebar mode toggle, font size slider, reduced motion toggle, compact mode toggle | Preview updates live |
| System | Integration status list, storage usage, cache clear, about section | Shows version + build date |

---

## EPIC 11: Enterprise Workflows

### FEATURE 11.1: Deep Work / Focus Mode
**Depends on:** 1.1  
**Priority:** P2  
**Effort:** 5 days | **Agents:** 2  
**Business Criticality:** P2 | **User Impact:** High | **Technical Risk:** Medium

#### Screens/Components
- `app/(dashboard)/focus/page.tsx`
- `components/focus/FocusMode.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 11.1.1 | Build minimal UI with ambient glow animation | Full-screen, no navigation chrome |
| 11.1.2 | Add session config: timer (Pomodoro 25/5 or custom), objective, tags | "Focus Protocol Active" status pill |
| 11.1.3 | Left panel: session context, timer controls (start/pause/reset), linked resources | Timer counts down visually |
| 11.1.4 | Center: work area (syntax-highlighted code block or blank canvas) | Line numbers, themes |
| 11.1.5 | Right panel: AI Copilot with context-aware buttons | "Regenerate", "Refactor", "Document", "Explain" |
| 11.1.6 | Add "Exit Mode" button with confirmation | Session summary on exit |

---

### FEATURE 11.2: Notification Center
**Depends on:** 1.1  
**Priority:** P1  
**Effort:** 4 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Screens/Components
- `components/notifications/NotificationPanel.tsx`
- `components/notifications/NotificationBadge.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 11.2.1 | Build slide-over panel from right (380px, backdrop blur) | 0.3s ease slide animation |
| 11.2.2 | Add 7 collapsible sections (Task, Learning, Opportunity, Goal, Habit, System, AI) | Each section header with count |
| 11.2.3 | Add 5 priority levels with color coding | P0 (red) → P4 (transparent/low opacity) |
| 11.2.4 | Add "Mark all read" and "View all" actions | Badge count updates on mark-read |
| 11.2.5 | Add real-time subscription (Supabase Realtime) | New notifications appear instantly |
| 11.2.6 | Build NotificationBadge component | Red dot with count on bell icon |

---

### FEATURE 11.3: Weekly Review System
**Depends on:** 1.1, 4.1  
**Priority:** P2  
**Effort:** 4 days | **Agents:** 2  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Medium

#### Screens/Components
- `app/(dashboard)/review/page.tsx`
- `components/review/WeeklyReview.tsx`

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 11.3.1 | Build 5-section layout: Overview, Metrics, AI Analysis, Key Decisions, Action Items | Agent A10 output rendered |
| 11.3.2 | Add week selector (previous weeks browsable via arrow navigation) | Dropdown or arrow keys |
| 11.3.3 | Add PDF export action | Generates styled PDF |
| 11.3.4 | Add AI-generated summary with confidence badge | Shows which data sources were used |

---

## EPIC 12: Deep Work & Remaining Modules

### FEATURE 12.1: YouTube Vault Enhancement
**Depends on:** 1.1  
**Priority:** P2  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 12.1.1 | Add grid/list view toggle | Persists preference |
| 12.1.2 | Add collection grouping (drag to organize) | Draggable between collections |
| 12.1.3 | Add search + tag filter (comma-separated, autocomplete) | Tags autocomplete from existing |
| 12.1.4 | Add status badges with date tracking (to watch/watching/watched) | Date stamp on each status change |

---

### FEATURE 12.2: Project Command / Portfolio
**Depends on:** 1.1  
**Priority:** P2  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 12.2.1 | Add portfolio grid view with GitHub integration | Shows stars, forks, last commit date |
| 12.2.2 | Add project timeline (milestone view with progress bars) | Phases shown as connected nodes |
| 12.2.3 | Add AI project summary card | Shows latest AI insight per project |

---

### FEATURE 12.3: System Automation Enhancement
**Depends on:** 1.1  
**Priority:** P2  
**Effort:** 2 days | **Agents:** 1  
**Business Criticality:** P2 | **User Impact:** Medium | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 12.3.1 | Add schedule visualization (24h timeline per automation) | Each automation shown at its trigger time |
| 12.3.2 | Add last-run status + duration display | Green (success) / red (error) indicators |
| 12.3.3 | Add manual override with countdown | "Run Now" shows progress spinner |

---

## EPIC 13: Production Polish

### FEATURE 13.1: Accessibility (WCAG 2.2 AA)
**Depends on:** All previous Epics  
**Priority:** P1  
**Effort:** 5 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Low

#### Tasks & Acceptance Criteria

| # | Task | AC |
|---|------|-----|
| 13.1.1 | Add 3 skip links: main content, navigation, search | Visible on focus, keyboard-operable |
| 13.1.2 | Add 6 ARIA landmarks to all pages | banner, navigation, main, complementary, contentinfo, search |
| 13.1.3 | Complete focus management (10 interaction patterns) | Tab order matches visual order |
| 13.1.4 | Add keyboard navigation to all interactive elements | Enter/Space on buttons, Arrow on selects |
| 13.1.5 | Validate contrast ratios (4.5:1 text, 3:1 large text) | All 7 theme combos pass |
| 13.1.6 | Enforce 44×44px touch targets on mobile | All interactive elements meet minimum |
| 13.1.7 | Add `prefers-reduced-motion` alternative animations | Animations replaced with instant transitions |
| 13.1.8 | Add screen reader announcements for dynamic content | `aria-live="polite"` on loading/status changes |
| 13.1.9 | Add form validation announcements | `aria-describedby` on all error states |
| 13.1.10 | Add visible focus indicators on all interactive | 3px outline, high contrast visible |

---

### FEATURE 13.2: Responsive QA (5 Breakpoints)
**Depends on:** All previous Epics  
**Priority:** P1  
**Effort:** 3 days | **Agents:** 1  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Low

#### Breakpoints & Tasks

| Breakpoint | Tasks | AC |
|------------|-------|-----|
| 375px (Mobile) | Verify bottom nav, FAB, snap-scroll, bottom sheets, safe areas | All modules navigable via touch |
| 834px (Tablet P) | Verify drawer sidebar, split pane, icon nav | No overlapping, no horizontal scroll |
| 1024px (Tablet L) | Verify medium sidebar, 12-column grid | Content not compressed |
| 1440px (Desktop) | Verify full sidebar, 3-panel layouts, KPI strip | All content visible without scroll |
| 1920px (Wide) | Verify fluid layout, optional menu bar | Content not stretched, max-width respected |

---

### FEATURE 13.3: Performance Optimization
**Depends on:** All previous Epics  
**Priority:** P1  
**Effort:** 4 days | **Agents:** 2  
**Business Criticality:** P1 | **User Impact:** High | **Technical Risk:** Medium

#### Tasks & Acceptance Criteria

| # | Task | Target |
|---|------|--------|
| 13.3.1 | Add bundle analysis (next/bundle-analyzer) | Main JS <300KB gzip |
| 13.3.2 | Add route-level code splitting | Each page chunk <100KB |
| 13.3.3 | Add image optimization (next/image) | All images lazy-loaded |
| 13.3.4 | Add virtual scrolling to all list views (DataTable >100 rows) | >100 rows virtualizes |
| 13.3.5 | Add debounced search (300ms) | No API call on every keystroke |
| 13.3.6 | Add CSS containment to cards | `contain: layout style paint` |
| 13.3.7 | Lighthouse CI enforcement | Perf ≥90, A11y ≥90, Best Practices ≥90 |

---

### FEATURE 13.4: Testing Suite
**Depends on:** All previous Epics  
**Priority:** P1  
**Effort:** 8 days | **Agents:** 3  
**Business Criticality:** P1 | **User Impact:** Low | **Technical Risk:** Medium

#### Test Types

| Type | Count | Coverage |
|------|-------|----------|
| Unit (Vitest) | 100+ | All hooks, stores, utils, helpers ≥80% coverage |
| Component (RTL) | 50+ | All UI components — all variants + states + events |
| E2E (Playwright) | 15+ | Auth, nav, dashboard CRUD, tasks CRUD, chat, search, responsive, theme, keyboard |
| A11y (axe) | 20+ | Every unique page template — 0 violations enforced |
| Visual (Playwright) | 10+ | Dashboard, Tasks, Chat, Login — <1% diff threshold |

---

## Execution Wave Plan

| Wave | Weeks | Epics | Parallel Agents | Agent-Weeks | Key Deliverables |
|------|-------|-------|----------------|-------------|------------------|
| **1** | 1-2 | 0 (Foundation), 1 (Shells) | 4 | 8 | Design tokens, ThemeProvider, 3 responsive shells, navigation |
| **2** | 3-4 | 2 (Command), 3 (UI Lib) | 6 | 12 | Cmd+K, 25+ UI components, AI components |
| **3** | 5-6 | 4 (AI Platform), 5 (Dashboard) | 6 | 12 | 3-panel chat, streaming, ghost hints, full dashboard |
| **4** | 7-8 | 6 (Tasks), 7 (Knowledge) | 5 | 10 | Kanban, detail view, knowledge graph |
| **5** | 9-10 | 8 (Analytics), 9 (Opportunity), 10 (Settings) | 5 | 10 | Analytics dash, radar viz, 6-section settings |
| **6** | 11-12 | 11 (Workflows), 12 (Remaining) | 5 | 10 | Focus mode, notifications, review, remaining modules |
| **7** | 13-15 | 13 (Polish) | 6 | 18 | A11y, responsive QA, perf, 150+ tests |
| **TOTAL** | **15 weeks** | **17 Epics** | **Peak 6** | **80** | Production-ready enterprise frontend |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-15 | Developer | Initial backlog — 17 Epics, 50+ Features, 200+ Tasks |
