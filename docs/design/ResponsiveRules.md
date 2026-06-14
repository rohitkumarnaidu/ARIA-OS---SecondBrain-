# Responsive Design Rules — Second Brain OS (ARIA)

> **Document ID:** SB-RESP-001  
> **Version:** 1.0.0  
> **Status:** Active  
> **Last Updated:** 2026-06-11  
> **Classification:** Internal — Engineering & Design  
> **Owner:** Frontend Engineering Team

---

## Table of Contents

1. [Responsive Design Philosophy](#1-responsive-design-philosophy)
2. [Breakpoint Definitions](#2-breakpoint-definitions)
3. [Layout System](#3-layout-system)
4. [Navigation Adaptation](#4-navigation-adaptation)
5. [Dashboard Grid Reflow](#5-dashboard-grid-reflow)
6. [Card Density & Sizing](#6-card-density--sizing)
7. [Typography Scaling](#7-typography-scaling)
8. [Touch Target Sizing](#8-touch-target-sizing)
9. [Content Prioritization](#9-content-prioritization)
10. [Hide/Show Patterns](#10-hideshow-patterns)
11. [Data Table Responsive Patterns](#11-data-table-responsive-patterns)
12. [Form Adaptation](#12-form-adaptation)
13. [Modal & Overlay Behavior](#13-modal--overlay-behavior)
14. [Testing Matrix](#14-testing-matrix)

---

## 1. Responsive Design Philosophy

### 1.1 Core Principles

ARIA OS is designed **mobile-first** in spirit but **desktop-primary** in practice — recognizing that its core audience (BTech CSE students) spends most of their time on laptops but needs mobile access between classes, during commutes, and late-night study sessions.

| Principle | Definition | Impact |
|---|---|---|
| **Content-first, chrome-second** | Navigation and chrome recede on smaller screens; content takes priority | Bottom nav replaces sidebar on mobile; full-screen modals on mobile |
| **Progressive enhancement** | Start with the essential mobile layout, add features and density as viewport grows | Mobile gets core CRUD; desktop gets advanced filtering, drag-reorder, multi-select |
| **One codebase, three experiences** | Same React components, different layout compositions per breakpoint group | No separate mobile/desktop code paths — CSS and layout props handle adaptation |
| **Touch-first mobile, precision desktop** | Touch targets ≥44px on mobile; keyboard shortcuts + hover states on desktop | Buttons grow on mobile; tooltips work on desktop hover |
| **Performance parity** | Mobile gets optimized bundles, reduced animations, and data-efficient rendering | Dynamic imports, reduced motion, paginated lists on mobile |

### 1.2 Design Approach

```typescript
// Responsive values are handled via Tailwind breakpoint prefixes + container queries
// Where layout differs fundamentally, use conditional rendering based on breakpoint hooks

function useBreakpoint() {
  // Returns 'mobile' | 'tablet' | 'desktop' | 'wide'
  // Used for fundamentally different layout components
  // NOT for visibility — use Tailwind responsive classes for show/hide
}

// CSS prefers media queries for layout, container queries for component adaptation
```

---

## 2. Breakpoint Definitions

### 2.1 Official Breakpoint System

```css
/* Tailwind CSS breakpoint extensions for ARIA OS */

:root {
  /* Primary breakpoints */
  --bp-mobile: 320px;    /* Minimum supported width */
  --bp-mobile-max: 639px;
  --bp-tablet: 640px;
  --bp-tablet-max: 1023px;
  --bp-desktop: 1024px;
  --bp-desktop-max: 1511px;
  --bp-wide: 1512px;

  /* Sub-breakpoints for fine-tuning */
  --bp-mobile-sm: 375px;  /* iPhone SE / small Android */
  --bp-mobile-lg: 414px;  /* iPhone Plus / large Android */
  --bp-tablet-sm: 768px;  /* iPad portrait */
  --bp-tablet-lg: 1024px; /* iPad landscape / iPad Pro */
  --bp-desktop-lg: 1280px; /* Standard laptop */
  --bp-desktop-xl: 1440px; /* Large laptop / small external */
}
```

### 2.2 Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'mobile': '320px',
      'mobile-sm': '375px',
      'mobile-lg': '414px',
      'tablet': '640px',
      'tablet-sm': '768px',
      'tablet-lg': '1024px',
      'desktop': '1024px',
      'desktop-lg': '1280px',
      'desktop-xl': '1440px',
      'wide': '1512px',
    },
    // Container queries must be implemented via the @tailwindcss/container-queries plugin
  },
};
```

### 2.3 Viewport Meta Tag

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

### 2.4 Orientation Handling

```css
/* Landscape phone (mobile content, wider aspect) */
@media (max-width: 639px) and (orientation: landscape) {
  /* Reduce vertical chrome: smaller header, collapsed bottom nav labels */
  .nav-label { display: none; }
  .header { padding: 8px 16px; }
}

/* Portrait tablet */
@media (min-width: 640px) and (max-width: 1023px) and (orientation: portrait) {
  /* Hybrid layout: collapsed sidebar with bottom nav */
}
```

---

## 3. Layout System

### 3.1 CSS Grid Breakpoint Behavior

```css
/* Base page layout — 3 zones */
.page-layout {
  display: grid;
  grid-template-rows: auto 1fr auto;  /* header, main, bottom-nav (mobile only) */
  min-height: 100vh;
  min-height: 100dvh; /* Dynamic viewport height — handles mobile browser chrome */
}

/* Desktop: sidebar + main content */
@media (min-width: 1024px) {
  .page-layout {
    grid-template-columns: var(--sidebar-width, 240px) 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "sidebar header"
      "sidebar main";
  }
}

/* Tablet: collapsible sidebar + bottom nav */
@media (min-width: 640px) and (max-width: 1023px) {
  .page-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header"
      "main"
      "bottom-nav";
  }
}
```

### 3.2 Content Area Grid

```css
/* Dashboard / list pages: responsive grid for content cards */
.content-grid {
  display: grid;
  gap: 16px;
  padding: 16px;
}

/* Mobile: single column */
@media (max-width: 639px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
  }
}

/* Tablet: 2 columns */
@media (min-width: 640px) and (max-width: 1023px) {
  .content-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    padding: 16px;
  }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) and (max-width: 1511px) {
  .content-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    padding: 24px;
  }
}

/* Wide: 4 columns (with max-width constraint) */
@media (min-width: 1512px) {
  .content-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    padding: 32px;
    max-width: 1600px;
    margin: 0 auto;
  }
}
```

### 3.3 Flexbox Behavior per Breakpoint

| Property | Mobile | Tablet | Desktop | Wide |
|---|---|---|---|---|
| `flex-direction` | `column` (stack) | `row` (wrap) | `row` (nowrap) | `row` (nowrap) |
| `flex-wrap` | `nowrap` | `wrap` | `nowrap` | `nowrap` |
| `gap` | 8px | 12px | 16px | 20px |
| Item `flex-basis` | 100% | calc(50% - 12px) | 1 (equal) | 1 (equal) |

### 3.4 Container Queries for Components

```css
/* Component-level responsive behavior based on available width */
/* Requires @container support — use with @tailwindcss/container-queries */

.task-card {
  container-type: inline-size;
  container-name: task-card;
}

@container task-card (max-width: 300px) {
  /* Compact layout: icon above text, smaller fonts */
  .task-card-content {
    flex-direction: column;
    gap: 4px;
  }
  .task-card-title {
    font-size: 0.875rem;
  }
  .task-card-meta {
    display: none;
  }
}

@container task-card (min-width: 301px) and (max-width: 500px) {
  /* Standard layout: icon + text in row */
  .task-card-content {
    flex-direction: row;
    gap: 8px;
  }
}

@container task-card (min-width: 501px) {
  /* Expanded layout: full detail, metadata visible */
  .task-card-meta {
    display: flex;
  }
  .task-card-actions {
    display: flex;
  }
}
```

---

## 4. Navigation Adaptation

### 4.1 Navigation Mode by Breakpoint

| Breakpoint | Primary Navigation | Secondary Navigation | Accessibility |
|---|---|---|---|
| **Mobile** (320-639px) | Bottom tab bar (5 items, 48px height) | None (all nav in bottom bar) | Hamburger menu for secondary pages |
| **Tablet portrait** (640-767px) | Collapsed sidebar (64px, icons only) | Bottom tab bar (secondary) | Sidebar expands on tap |
| **Tablet landscape** (768-1023px) | Collapsed sidebar (64px) + bottom tabs | Top tabs within modules | Sidebar slides open on tap |
| **Desktop** (1024-1511px) | Expanded sidebar (240px) | None needed | Collapse to 64px via toggle |
| **Wide** (1512px+) | Expanded sidebar (280px) | None needed | Optional second-level nav appears |

### 4.2 Sidebar States

```css
/* Desktop sidebar: three states */
.sidebar {
  --sidebar-width: 240px;
  --sidebar-collapsed: 64px;
  transition: width 250ms cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.sidebar--expanded {
  width: var(--sidebar-width);
}

.sidebar--collapsed {
  width: var(--sidebar-collapsed);
}

/* Collapsed sidebar hover expansion */
@media (hover: hover) and (pointer: fine) {
  .sidebar--collapsed:hover {
    width: var(--sidebar-width);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
  }
}

/* Mobile sidebar: full-screen overlay when open */
@media (max-width: 639px) {
  .sidebar {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 50;
    background: #0A0B0F;
    transform: translateX(-100%);
    transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .sidebar--open {
    transform: translateX(0);
  }
}
```

### 4.3 Bottom Navigation Bar

```typescript
// Mobile bottom navigation — always visible on mobile and tablet portrait
// Contains: Dashboard, Tasks, Habits, Courses, More (overflow menu)

const BOTTOM_NAV_ITEMS = [
  { label: 'Home', icon: HomeIcon, href: '/dashboard', primary: true },
  { label: 'Tasks', icon: TaskIcon, href: '/tasks', primary: true },
  { label: 'Habits', icon: HabitIcon, href: '/habits', primary: true },
  { label: 'Courses', icon: CourseIcon, href: '/courses', primary: true },
  { label: 'More', icon: MoreIcon, href: null, overflow: true },
];
```

| Breakpoint | Bottom Nav Style | Behavior |
|---|---|---|
| Mobile (320-639px) | 48px height, icons + labels below | Labels visible, 5 items max |
| Mobile landscape | 40px height, icons only | Labels hidden to save vertical space |
| Tablet portrait (640-767px) | 48px height, icons only | Labels hidden, 5 items |
| Tablet landscape+ | Hidden (sidebar becomes primary) | Not rendered |

```css
.bottom-nav {
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 48px;
  background: #13151A;
  border-top: 1px solid #1E293B;
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

@media (min-width: 1024px) {
  .bottom-nav {
    display: none;
  }
}
```

---

## 5. Dashboard Grid Reflow

### 5.1 Dashboard Layout by Breakpoint

The dashboard is the primary landing page and the most layout-intensive screen. It uses a CSS Grid with named areas that reflow at each breakpoint.

```css
/* Dashboard grid areas */
.dashboard {
  display: grid;
  gap: 16px;
  padding: 16px;
}

/* Mobile: single column, content prioritized */
@media (max-width: 639px) {
  .dashboard {
    grid-template-columns: 1fr;
    grid-template-areas:
      "greeting"
      "quick-stats"
      "tasks-today"
      "upcoming-deadlines"
      "habit-streak"
      "focus-score"
      "recent-activity"
      "ai-briefing";
  }
}

/* Tablet: 2 columns, secondary content moves right */
@media (min-width: 640px) and (max-width: 1023px) {
  .dashboard {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "greeting       greeting"
      "quick-stats    quick-stats"
      "tasks-today    habit-streak"
      "upcoming-deadlines focus-score"
      "ai-briefing    recent-activity";
  }
}

/* Desktop: 3 columns, full layout */
@media (min-width: 1024px) and (max-width: 1511px) {
  .dashboard {
    grid-template-columns: 2fr 1fr 1fr;
    grid-template-areas:
      "greeting       greeting       greeting"
      "tasks-today    quick-stats    habit-streak"
      "tasks-today    focus-score    upcoming-deadlines"
      "ai-briefing    recent-activity recent-activity";
  }
}

/* Wide: 4 columns, maximum density */
@media (min-width: 1512px) {
  .dashboard {
    grid-template-columns: 2fr 1fr 1fr 1fr;
    grid-template-areas:
      "greeting       greeting       greeting       greeting"
      "tasks-today    quick-stats    habit-streak   focus-score"
      "tasks-today    upcoming-deadlines recent-activity ai-briefing";
    max-width: 1600px;
    margin: 0 auto;
  }
}
```

### 5.2 Module Dashboard Sections

Each dashboard section has a defined `grid-area` and responds differently to breakpoint:

| Section | Priority | Mobile Behavior | Desktop Behavior |
|---|---|---|---|
| **Greeting** | Always visible | Compact: "Hey [Name]" + date | Full: "Good morning, [Name]. Here's your day." + weather/quote |
| **Quick Stats** | Always visible | 2×2 grid of metrics (tasks due, streak, score, courses) | 4-in-a-row metrics with labels |
| **Tasks Today** | High | 3 tasks, no actions beyond checkbox | 5+ tasks with priority, drag, quick-actions |
| **Habit Streak** | Medium | Compact: 7-day mini-calendar | Full: 30-day streak calendar with stats |
| **Focus Score** | Medium | Single number + trend arrow | Full chart + comparison to average |
| **AI Briefing** | Medium | 2-line summary, expandable | Full briefing card with sections |
| **Upcoming Deadlines** | Low | Collapsed: count + next 1 | Visible: next 5 with days remaining |
| **Recent Activity** | Low | Hidden (accessible via nav) | Visible: timeline of last 10 actions |

---

## 6. Card Density & Sizing

### 6.1 Card Density by Breakpoint

| Breakpoint | Card Width | Content Density | Show/Hide Elements |
|---|---|---|---|
| Mobile (320-639px) | Full-width (100% - 24px margin) | Low | Title, status, 1 action button |
| Tablet (640-1023px) | calc(50% - 16px) | Medium | Title, status, priority, date, 2 actions |
| Desktop (1024-1511px) | calc(33% - 20px) | High | Title, status, priority, date, tags, category, 3+ actions |
| Wide (1512px+) | calc(25% - 24px) | Full | Everything + metadata + progress + inline edit |

### 6.2 Task Card Adaptation

```typescript
// Task card shows different information based on available space
function TaskCard({ task, containerWidth }: Props) {
  const density = containerWidth < 300 ? 'compact'
    : containerWidth < 450 ? 'standard'
    : 'expanded';

  return (
    <div className="task-card">
      <Checkbox checked={task.completed} />
      <div className="task-card-body">
        <h3 className="task-title">{task.title}</h3>
        {density !== 'compact' && <p className="task-desc">{task.description}</p>}
        {density === 'expanded' && (
          <div className="task-meta">
            <PriorityBadge priority={task.priority} />
            <DueDate date={task.dueDate} />
            <CategoryTag tag={task.category} />
          </div>
        )}
      </div>
      {density !== 'compact' && (
        <div className="task-actions">
          <button aria-label="Edit">Edit</button>
          <button aria-label="More">...</button>
        </div>
      )}
    </div>
  );
}
```

### 6.3 Card Grid Container Query

```css
@container card-grid (max-width: 400px) {
  .card { --card-density: compact; }
}

@container card-grid (min-width: 401px) and (max-width: 700px) {
  .card { --card-density: standard; }
}

@container card-grid (min-width: 701px) {
  .card { --card-density: expanded; }
}
```

---

## 7. Typography Scaling

### 7.1 Fluid Type System

All type sizes use `clamp()` for smooth scaling across breakpoints. This eliminates the need for breakpoint-specific font-size overrides in most cases.

```css
:root {
  /* Fluid type scale — mobile to desktop */
  --fs-display-xl: clamp(2rem, 5vw + 0.5rem, 3rem);       /* 32px → 48px */
  --fs-display-l:  clamp(1.75rem, 4vw + 0.5rem, 2.5rem);  /* 28px → 40px */
  --fs-display-m:  clamp(1.5rem, 3vw + 0.5rem, 2rem);     /* 24px → 32px */
  --fs-heading-l:  clamp(1.25rem, 2vw + 0.5rem, 1.5rem);  /* 20px → 24px */
  --fs-heading-m:  clamp(1.125rem, 1.5vw + 0.25rem, 1.25rem); /* 18px → 20px */
  --fs-heading-s:  clamp(1rem, 1vw + 0.25rem, 1.125rem);  /* 16px → 18px */
  --fs-body-l:     clamp(0.9375rem, 0.5vw + 0.75rem, 1rem); /* 15px → 16px */
  --fs-body-m:     clamp(0.8125rem, 0.25vw + 0.75rem, 0.875rem); /* 13px → 14px */
  --fs-body-s:     clamp(0.75rem, 0.25vw + 0.625rem, 0.8125rem); /* 12px → 13px */
  --fs-code:       clamp(0.75rem, 0.25vw + 0.625rem, 0.8125rem); /* 12px → 13px */
}

/* No breakpoint-specific overrides needed for most text */
/* Only adjust line-height and letter-spacing at extremes */

@media (max-width: 639px) {
  :root {
    --lh-body: 1.65;       /* More relaxed for mobile reading */
    --ls-heading: -0.005em; /* Tighter tracking on mobile for fit */
  }
}

@media (min-width: 1024px) {
  :root {
    --lh-body: 1.55;
    --ls-heading: -0.01em;
  }
}
```

### 7.2 Typography Changes by Breakpoint

| Element | Mobile | Tablet | Desktop | Wide |
|---|---|---|---|---|
| Page title (Display XL) | 32px | clamp to 40px | 40px | 48px |
| Section heading (Heading L) | 20px | 22px | 24px | 24px |
| Body text | 15px | 15px | 16px | 16px |
| Code | 12px | 12px | 13px | 14px |
| Overline (badges) | 10px | 10px | 11px | 11px |
| Max line length | Unrestricted (full width) | 65ch | 75ch | 75ch (centered) |

### 7.3 Safe Typography Overrides

```css
/* When users increase system font size on mobile, respect it */
/* Never set font-size in px for body text — use rem or clamp */

html {
  font-size: 100%; /* Respects browser/OS base font size */
}

/* If user sets browser to "Large text" or similar */
@media (max-width: 639px) {
  /* Ensure line length doesn't exceed viewport on large text */
  .content-area {
    max-width: 100%;
    padding: 0 12px;
  }
}
```

---

## 8. Touch Target Sizing

### 8.1 Touch Target Minimums

| Element | Mobile (320-639px) | Tablet (640-1023px) | Desktop (1024px+) |
|---|---|---|---|
| Primary buttons | 48px height | 44px height | 40px height |
| Icon buttons | 44×44px hit area | 40×40px hit area | 36×36px hit area |
| Navigation items | 48×48px (bottom nav) | 64×64px (sidebar icons) | 40px (vertical) |
| Form inputs | 48px height | 44px height | 40px height |
| Checkboxes / Radios | 24×24px | 20×20px | 18×18px |
| Toggle switches | 48×24px | 44×22px | 40×20px |
| Link targets | 44px min height (with padding) | 40px | Natural (text height) |
| Filter chips | 32px height | 32px height | 28px height |
| Slider handles | 44×44px hit area | 40×40px hit area | 24×24px + padding |
| Bottom sheet handle | 32×4px (visual), 44px touch | 32×4px | N/A |

### 8.2 Spacing Between Touch Targets

```css
/* Minimum gap between interactive elements */
/* Prevents accidental taps on adjacent targets */

.mobile-touch-group {
  display: flex;
  gap: 12px;  /* Mobile: larger gap */
}

@media (min-width: 640px) {
  .mobile-touch-group {
    gap: 8px;  /* Tablet/desktop: standard gap */
  }
}

/* Adjacent buttons in a toolbar */
.toolbar {
  display: flex;
  gap: 4px;
}

@media (max-width: 639px) {
  .toolbar {
    gap: 8px;
  }
}
```

### 8.3 Safe Area Handling

```css
/* Handle notches, home indicators, and rounded corners on modern devices */

.page-layout {
  padding-top: env(safe-area-inset-top, 0px);
  padding-bottom: env(safe-area-inset-bottom, 0px);
  padding-left: env(safe-area-inset-left, 0px);
  padding-right: env(safe-area-inset-right, 0px);
}

.bottom-nav {
  padding-bottom: max(8px, env(safe-area-inset-bottom, 8px));
  height: calc(48px + env(safe-area-inset-bottom, 0px));
}

.header {
  padding-top: max(12px, env(safe-area-inset-top, 12px));
}
```

---

## 9. Content Prioritization

### 9.1 Content Priority Levels

Every piece of UI content is assigned a priority level that determines its visibility at each breakpoint.

| Priority | Label | Mobile | Tablet | Desktop | Wide |
|---|---|---|---|---|---|
| **P0 — Critical** | Always visible | ✅ | ✅ | ✅ | ✅ |
| **P1 — Important** | Visible on tablet+ | ❌ | ✅ | ✅ | ✅ |
| **P2 — Standard** | Visible on desktop+ | ❌ | ❌ | ✅ | ✅ |
| **P3 — Extra** | Visible only on wide | ❌ | ❌ | ❌ | ✅ |

### 9.2 Priority Assignment by Module

| Module | P0 (Always) | P1 (Tablet+) | P2 (Desktop+) | P3 (Wide Only) |
|---|---|---|---|---|
| **Tasks** | Title, checkbox, due date | Description, priority badge | Tags, category, subtask count | Time estimate, attachments, comments |
| **Courses** | Name, progress bar | Grade, next deadline | Instructor, materials link | Syllabus, schedule, announcements |
| **Habits** | Name, streak count | Frequency, last done | Streak history chart | Group, notes, reminder settings |
| **Dashboard** | Greeting, quick stats, 3 tasks | AI briefing snippet | Habit streak, focus score | Recent activity, suggestions |
| **Sleep** | Score, duration | Deep/light/REM breakdown | Trend chart (7-day) | Recommendations, comparison |
| **Income** | Amount, source, date | Hourly rate, hours worked | Monthly comparison | Category breakdown, projections |
| **Projects** | Name, phase, deadline | Blocker list, URLs | Team members, milestones | Chat history, file attachments |
| **Ideas** | Title, status | Description, tags | Related tasks/projects | Market research, notes |
| **Resources** | Title, URL | Tags, category | Rating, notes | Related resources |
| **Opportunities** | Title, match score, deadline | Company, location | Application status, notes | Contacts, preparation checklist |
| **Chat** | Message, timestamp | Sender, status | Thread context | Attachments, reactions |
| **Time tracking** | Entry description, duration | Project tag | Start/end times | Location, notes |

### 9.3 Progressive Disclosure Pattern

```typescript
// Pattern for showing more content as viewport grows
function PrioritizedContent({ item }: Props) {
  return (
    <div className="card">
      {/* P0 — Always visible */}
      <h3 className="card-title">{item.title}</h3>

      {/* P1 — Hidden on mobile */}
      <p className="hidden tablet:block">{item.description}</p>

      {/* P2 — Hidden on mobile + tablet */}
      <div className="hidden desktop:flex">
        <PriorityBadge priority={item.priority} />
        <DueDate date={item.dueDate} />
      </div>

      {/* P3 — Wide only */}
      <div className="hidden wide:block">
        <MetadataSection item={item} />
      </div>
    </div>
  );
}
```

### 9.4 Content Collapse Patterns

| Pattern | Implementation | Use Case |
|---|---|---|
| **"Show more" link** | Button truncates long text, expands on tap | Descriptions, notes, AI briefing content |
| **Accordion sections** | Collapsible sections with expand indicator | Module detail pages, settings |
| **Tab bar overflow** | Extra tabs go into "More" dropdown | Mobile tab navigation |
| **Progressive loading** | Lazy load below-fold content | Dashboard secondary sections |
| **Horizontal scroll** | Scrollable row of cards with fade edges | Tag filters, quick actions |

---

## 10. Hide/Show Patterns

### 10.1 Responsive Visibility Classes

```css
/* Tailwind responsive prefixes used for show/hide */
/* Standard Tailwind approach — no custom classes needed for basic visibility */

/* Hide on mobile, show on tablet+ */
.hidden-mobile { display: none; }
@media (min-width: 640px) { .hidden-mobile { display: revert; } }

/* Show on mobile, hide on tablet+ */
.show-mobile { display: revert; }
@media (min-width: 640px) { .show-mobile { display: none; } }

/* Desktop-only (hide on mobile + tablet) */
@media (max-width: 1023px) { .desktop-only { display: none !important; } }

/* Mobile-only */
@media (min-width: 640px) { .mobile-only { display: none !important; } }
```

### 10.2 Element Visibility by Breakpoint

| Element | Mobile | Tablet | Desktop | Wide |
|---|---|---|---|---|
| Bottom navigation | ✅ | ✅ (portrait only) | ❌ | ❌ |
| Desktop sidebar (expanded) | ❌ | ❌ | ✅ | ✅ |
| Desktop sidebar (collapsed) | ❌ | ✅ | Optional | ❌ |
| Dashboard greeting full | ❌ | ❌ | ✅ | ✅ |
| Dashboard greeting compact | ✅ | ✅ | ❌ | ❌ |
| Page breadcrumbs | ❌ | ❌ | ✅ | ✅ |
| Table of contents | ❌ | ❌ | ✅ | ✅ |
| Floating action button | ✅ | ✅ | ❌ | ❌ |
| Quick search (Ctrl+K) | ❌ (button instead) | ❌ | ✅ | ✅ |
| Module-specific filters | In modal/overlay | In sidebar | Inline | Inline |
| Data export buttons | ❌ | ❌ | ✅ | ✅ |
| Drag handle (reorder) | ❌ (long-press instead) | ❌ | ✅ | ✅ |

### 10.3 Content Toggle Patterns

```typescript
// For content that can be toggled on any breakpoint:
// "Show filters" button on mobile opens filter panel as bottom sheet
// Filter panel is always visible on desktop

function FilterPanel() {
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const isMobile = useIsMobile(); // Breakpoint hook

  return (
    <>
      {/* Mobile: toggle button */}
      {isMobile && (
        <button onClick={() => setShowMobileFilters(true)}>
          Show Filters
        </button>
      )}

      {/* Mobile: bottom sheet */}
      {isMobile && showMobileFilters && (
        <BottomSheet onClose={() => setShowMobileFilters(false)}>
          <Filters />
        </BottomSheet>
      )}

      {/* Desktop: always visible sidebar */}
      {!isMobile && (
        <aside className="desktop-only">
          <Filters />
        </aside>
      )}
    </>
  );
}
```

---

## 11. Data Table Responsive Patterns

### 11.1 Table Adaptation Strategy

| Method | Mobile | Tablet | Desktop | Wide |
|---|---|---|---|---|
| **Horizontal scroll** | ✅ (with sticky first column) | ✅ | ❌ (fits) | ❌ |
| **Collapsible rows** | ❌ | ✅ (alternative) | ❌ | ❌ |
| **Card view** | ✅ (primary) | ❌ | ❌ | ❌ |
| **Full table** | ❌ | ❌ | ✅ | ✅ |

### 11.2 Card View (Mobile)

```typescript
// On mobile, tables become card lists
// Each table row becomes a card with stacked fields

function ResponsiveTable({ data, columns }) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <div className="table-card-list">
        {data.map(row => (
          <div key={row.id} className="table-card">
            <div className="table-card-primary">
              <span className="table-card-title">{row.title}</span>
              <span className="table-card-status">{row.status}</span>
            </div>
            <div className="table-card-details">
              <DetailRow label="Due" value={row.dueDate} />
              <DetailRow label="Priority" value={row.priority} />
              <DetailRow label="Category" value={row.category} />
            </div>
            <div className="table-card-actions">
              <button>Edit</button>
              <button>Delete</button>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map(col => <th key={col.key}>{col.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.id}>
              {columns.map(col => <td key={col.key}>{row[col.key]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 11.3 Column Priority for Tables

| Column | Priority | Mobile (card) | Tablet (scroll) | Desktop (full) |
|---|---|---|---|---|
| Name / Title | P0 | ✅ Card header | ✅ Sticky first col | ✅ |
| Status | P0 | ✅ Badge | ✅ | ✅ |
| Priority | P1 | ✅ Detail row | ✅ | ✅ |
| Due date | P1 | ✅ Detail row | ✅ | ✅ |
| Category / Tags | P2 | ❌ | ✅ | ✅ |
| Assigned to | P2 | ❌ | ✅ | ✅ |
| Created date | P3 | ❌ | ❌ | ✅ |
| Last modified | P3 | ❌ | ❌ | ✅ |
| Progress % | P2 | ❌ (visual bar) | ✅ | ✅ |
| Actions | P0 | ✅ Card footer | ✅ Last col | ✅ Last col |

### 11.4 Scrollable Table Pattern

```css
/* Desktop table: handle overflow gracefully */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch; /* Smooth iOS scrolling */
  scrollbar-width: thin;
}

/* Sticky first column for context */
.data-table th:first-child,
.data-table td:first-child {
  position: sticky;
  left: 0;
  background: #13151A;
  z-index: 1;
}

.data-table th:first-child {
  z-index: 2; /* Above regular cells */
}

/* Fade edge on scroll */
.table-wrapper::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 32px;
  background: linear-gradient(to right, transparent, #0A0B0F);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
}

.table-wrapper.is-scrolled::after {
  opacity: 1;
}
```

---

## 12. Form Adaptation

### 12.1 Form Layout by Breakpoint

| Form Element | Mobile | Tablet | Desktop |
|---|---|---|---|
| Single-line inputs | Full width | Full width | Max 480px |
| Multi-column fields | Stacked vertically | 2-column grid | 2-3 column grid |
| Labels | Above input (stacked) | Above input | Side (left) or above |
| Submit buttons | Full width, bottom of form | Right-aligned, inline | Right-aligned |
| Date picker | Native input (type=date) | Native or custom | Custom calendar picker |
| Select / dropdown | Native `<select>` | Custom or native | Custom dropdown |
| File upload | Full-width area | Medium area | Inline button |

### 12.2 Form Responsive Rules

```css
/* Form grid adaptation */
.form-grid {
  display: grid;
  gap: 16px;
}

@media (max-width: 639px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 640px) and (max-width: 1023px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  /* Full-width elements span both columns */
  .form-grid .full-width {
    grid-column: 1 / -1;
  }
}

@media (min-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(3, 1fr);
    max-width: 800px;
  }
}

/* Mobile: full-width buttons at bottom */
.form-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

@media (max-width: 639px) {
  .form-actions {
    flex-direction: column-reverse; /* Primary button on bottom (thumb reach) */
    gap: 12px;
  }

  .form-actions button {
    width: 100%;
    height: 48px;
  }
}
```

### 12.3 Input Group Behavior

```typescript
// On mobile, field groups that are side-by-side on desktop stack vertically
// E.g., "First Name" + "Last Name" → two lines on mobile, one row on desktop

<fieldset className="form-group">
  <div className="form-field">
    <label>First Name</label>
    <input />
  </div>
  <div className="form-field">
    <label>Last Name</label>
    <input />
  </div>
</fieldset>

<style>
.form-group {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 640px) {
  .form-group {
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
}
</style>
```

---

## 13. Modal & Overlay Behavior

### 13.1 Modal Adaptation

| Modal Type | Mobile | Tablet | Desktop | Wide |
|---|---|---|---|---|
| **Dialog** (confirm/cancel) | Full-screen, bottom sheet | Centered, 400px max | Centered, 420px | Centered, 480px |
| **Form modal** (create/edit) | Full-screen, slide up | Centered, 600px max | Centered, 640px | Centered, 720px |
| **Detail modal** (view item) | Full-screen, slide from right | Slide from right, 80% width | Slide from right, 560px | Right panel, 560px |
| **Image viewer** | Full-screen, no chrome | Full-screen, dark overlay | Dark overlay, centered | Dark overlay, centered |
| **Search** | Full-screen, overlays everything | Full-screen, overlays everything | Overlay, 640px wide | Overlay, 720px wide |
| **Command palette** | Full-screen, top | Centered, 560px | Centered, 560px | Centered, 600px |

### 13.2 Modal DOM Behavior

```typescript
// Mobile: modals are full-screen sheets that slide from the bottom
// Desktop: modals are centered dialogs with backdrop

function ResponsiveModal({ isOpen, onClose, children }) {
  const isMobile = useIsMobile();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop — same on all breakpoints */}
          <motion.div
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {isMobile ? (
            // Bottom sheet (mobile)
            <motion.div
              className="modal-sheet"
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            >
              <div className="sheet-handle" />
              <div className="sheet-content">{children}</div>
            </motion.div>
          ) : (
            // Centered dialog (tablet+)
            <motion.div
              className="modal-dialog"
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97 }}
              role="dialog"
              aria-modal="true"
            >
              <button className="modal-close" onClick={onClose} aria-label="Close">
                <XIcon />
              </button>
              {children}
            </motion.div>
          )}
        </>
      )}
    </AnimatePresence>
  );
}
```

### 13.3 Full-Screen Overlay Rules

| Rule | Mobile | Desktop |
|---|---|---|
| Backdrop dismiss | Tap outside sheet = close | Click outside dialog = close |
| Escape key | Closes sheet | Closes dialog |
| Scroll behavior | Content scrolls within sheet | Content scrolls within dialog |
| Max height | 90% of viewport (leaves 10% visible of background) | Auto (fits content, max 80vh) |
| Corner radius | 16px top corners | 12px all corners |
| Safe area | `padding-bottom: env(safe-area-inset-bottom)` | Standard padding |

---

## 14. Testing Matrix

### 14.1 Device Testing Matrix

| Device Category | Device | OS | Screen | Browser | Orientation |
|---|---|---|---|---|---|
| **Small phone** | iPhone SE (3rd gen) | iOS 18 | 375×667px | Safari, Chrome | Portrait / Landscape |
| **Standard phone** | iPhone 15 | iOS 18 | 393×852px | Safari, Chrome | Portrait / Landscape |
| **Large phone** | iPhone 15 Pro Max | iOS 18 | 430×932px | Safari, Chrome | Portrait / Landscape |
| **Small Android** | Google Pixel 6a | Android 14 | 412×915px | Chrome, Firefox | Portrait / Landscape |
| **Large Android** | Samsung Galaxy S24+ | Android 14 | 412×896px | Chrome, Samsung Internet | Portrait / Landscape |
| **Foldable** | Samsung Galaxy Z Fold 5 | Android 14 | 904×1812px (unfolded) | Chrome | Portrait / Landscape |
| **Small tablet** | iPad Mini (6th gen) | iPadOS 18 | 744×1133px | Safari | Portrait / Landscape |
| **Large tablet** | iPad Air (M2) | iPadOS 18 | 820×1180px | Safari, Chrome | Portrait / Landscape |
| **Small laptop** | MacBook Air 13" | macOS 15 | 1280×832px | Safari, Chrome, Firefox | Landscape |
| **Standard laptop** | MacBook Pro 14" | macOS 15 | 1512×982px | Safari, Chrome, Firefox | Landscape |
| **External display** | 27" monitor | macOS / Windows | 2560×1440px | Chrome, Firefox, Edge | Landscape |

### 14.2 Browser Testing Matrix

| Browser | Version (Min) | Engine | Priority |
|---|---|---|---|
| Chrome | 125+ | Blink | Primary (daily) |
| Firefox | 130+ | Gecko | Primary (daily) |
| Safari | 18+ | WebKit | Primary (daily) |
| Edge | 125+ | Blink | Secondary (per release) |
| Samsung Internet | 24+ | Blink | Secondary (per release) |

### 14.3 Responsive Testing Checklist

```markdown
# Per-Release Responsive Testing Checklist

## Layout & Grid
- [ ] No horizontal scroll at any breakpoint (test at 320px, 640px, 1024px, 1512px)
- [ ] Content does not overflow containers at any width
- [ ] Dashboard grid reflows correctly at each breakpoint
- [ ] Cards resize and reflow within grid
- [ ] Flexbox items wrap correctly

## Navigation
- [ ] Bottom nav visible on mobile, hidden on desktop
- [ ] Sidebar collapses/expands correctly at tablet breakpoint
- [ ] Sidebar becomes full-screen overlay on mobile
- [ ] All navigation links are reachable on all breakpoints

## Touch & Interaction
- [ ] All touch targets ≥44px on mobile (verify with dev tools)
- [ ] Minimum 4px gap between interactive elements on mobile
- [ ] Swipe gestures work on mobile (task complete, pull-to-refresh)
- [ ] Long-press actions work on mobile
- [ ] Hover states don't get "stuck" on touch devices

## Typography
- [ ] All text is readable at 320px width
- [ ] No text truncation or overflow at any breakpoint
- [ ] Line length does not exceed 75ch on desktop
- [ ] Font sizes scale smoothly (verify clamp() behavior)

## Forms
- [ ] Inputs are full width on mobile
- [ ] Multi-column forms collapse to single column on mobile
- [ ] Submit buttons are full-width and thumb-reachable on mobile
- [ ] Date pickers use native controls on mobile

## Modals & Overlays
- [ ] Modals become bottom sheets on mobile
- [ ] Modals are centered dialogs on desktop
- [ ] Backdrop opacity is correct on all breakpoints
- [ ] Escape key closes all overlays
- [ ] Scroll is locked behind modal on all breakpoints

## Data Tables
- [ ] Tables scroll horizontally on tablet (with sticky first column)
- [ ] Tables become cards on mobile
- [ ] Card view shows correct priority fields

## Safe Areas
- [ ] Content is not hidden behind notches on iPhone X+ devices
- [ ] Bottom nav accounts for home indicator
- [ ] Top content accounts for status bar

## Zoom
- [ ] No content loss at 200% browser zoom
- [ ] No horizontal scroll at 200% zoom on any breakpoint
- [ ] Text reflows correctly when zoomed

## Performance
- [ ] No layout shifts during responsive breakpoint changes
- [ ] Animations don't cause jank on mobile devices
- [ ] Images load appropriately sized for breakpoint
- [ ] Largest Contentful Paint (LCP) ≤ 2.5s on mobile 3G
```

### 14.4 Automated Responsive Testing

```typescript
// Playwright / Cypress responsive test pattern
describe('Responsive layout', () => {
  const viewports = [
    { width: 320, height: 667, name: 'mobile' },
    { width: 768, height: 1024, name: 'tablet-portrait' },
    { width: 1024, height: 768, name: 'tablet-landscape' },
    { width: 1280, height: 800, name: 'desktop' },
    { width: 1512, height: 982, name: 'wide' },
  ];

  viewports.forEach(({ width, height, name }) => {
    it(`renders dashboard correctly at ${name} (${width}×${height})`, () => {
      cy.viewport(width, height);
      cy.visit('/dashboard');
      cy.contains('Good morning').should('be.visible');
      cy.get('.dashboard-grid').should('be.visible');

      // Verify no horizontal scroll
      cy.window().then(win => {
        expect(win.document.documentElement.scrollWidth)
          .to.be.at.most(win.document.documentElement.clientWidth + 1);
      });

      // Verify navigation mode
      if (width < 1024) {
        cy.get('.bottom-nav').should('be.visible');
      } else {
        cy.get('.sidebar').should('be.visible');
      }
    });
  });
});
```

### 14.5 Breakpoint Smoke Test Script

```bash
# Quick responsive check via CLI (requires Playwright)
npx playwright test --grep "@responsive"

# Or use browserstack/local testing tools
# Check: navigation, content grid, modals, tables, forms at each breakpoint
```

---

## Appendix A: Responsive Decision Flowchart

```
User opens ARIA OS
       │
       ▼
Viewport width?
       │
       ├── < 640px ────────────── MOBILE ─── Single column, bottom nav,
       │                                            full-width inputs,
       │                                            cards instead of tables,
       │                                            sheet modals
       │
       ├── 640px - 1023px ────── TABLET ─── 2-column grid, collapsed sidebar,
       │                                            hybrid nav, scrollable tables,
       │                                            centered dialogs
       │
       ├── 1024px - 1511px ──── DESKTOP ── 3-column grid, expanded sidebar,
       │                                            full tables, inline filters,
       │                                            centered modals
       │
       └── 1512px+ ────────────── WIDE ──── 4-column grid, max-width 1600px,
                                                    expanded details, full metadata,
                                                    second-level nav
```

## Appendix B: Quick Reference — CSS Snippets

```css
/* Mobile-first base */
.container { padding: 12px; }
.grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
.hide-mobile { display: none; }
.show-desktop { display: none; }

/* Tablet */
@media (min-width: 640px) {
  .container { padding: 16px; }
  .grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .hide-mobile { display: revert; }
  .show-tablet { display: revert; }
}

/* Desktop */
@media (min-width: 1024px) {
  .container { padding: 24px; }
  .grid { grid-template-columns: repeat(3, 1fr); gap: 20px; }
  .show-desktop { display: revert; }
  .hide-desktop { display: none; }
}

/* Wide */
@media (min-width: 1512px) {
  .container { padding: 32px; max-width: 1600px; margin: 0 auto; }
  .grid { grid-template-columns: repeat(4, 1fr); gap: 24px; }
}
```

---

> **Maintenance:** This document is updated per release cycle when new layouts or components are added. Every new component must define its responsive behavior at all 4 breakpoint groups. Component reviews must reference this document.
>
> **Related documents:** `docs/design/10_DesignSystem.md` (component tokens), `docs/design/Accessibility.md` (touch targets, zoom), `docs/design/MotionSystem.md` (responsive animation behavior).
