# Design Architecture — Second Brain OS

| Field | Value |
|---|---|
| Document ID | DSG-DESIGN-009 |
| Version | 3.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal — Design Reference |
| Target Audience | Designers, Frontend Developers, QA Engineers |

---

## 1. Executive Summary

ARIA OS uses a **layered design architecture** separating tokens, primitives, components, composed components, and pages. Each layer depends only on the layers below it, ensuring consistent theming and avoiding style drift across 16 modules. This document defines the complete visual design framework — from the cyberpunk visual direction through the layout system, component specifications, color system, typography scale, iconography, data visualization, form design, dark-mode decisions, and the design review process.

**Core Design Principle:** Every pixel serves a purpose. Nothing is decorative that cannot also be functional.

---

## 2. Visual Design Direction

### 2.1 Design Identity

| Attribute | Direction |
|---|---|
| **Genre** | Cyberpunk / Tech-noir |
| **Mood** | Focused, powerful, introspective |
| **Color temperature** | Cool (dark blues, indigos) with warm neon accents |
| **Texture** | Subtle noise, scan lines, grid overlays |
| **Lighting** | Self-illuminated (neon glow on dark) |
| **Typography** | Geometric sans (Syne) for display, humanist sans (DM Sans) for body |
| **Shapes** | Sharp corners (12px radius), clean lines, minimal ornamentation |
| **Motion** | Purposeful, 60fps, micro-interactions that communicate state |

### 2.2 Mood Board

```
┌─────────────────────────────────────────────────────────────┐
│  VISUAL REFERENCES                                          │
│                                                             │
│  Color: Blade Runner 2049 palette — deep blacks, neon teal, │
│         warm orange accents                                 │
│                                                             │
│  Typography: Arcane (Netflix) title cards — bold geometric  │
│              sans, tracking, uppercase headlines            │
│                                                             │
│  UI: Ghost in the Shell SAC_2045 interfaces — glass         │
│      morphism, holographic overlays, grid-based layouts     │
│                                                             │
│  Data viz: Minority Report — floating data points,          │
│            translucent overlays, real-time feeds            │
│                                                             │
│  Texture: Tron: Legacy — light trails, neon edges,          │
│           dark reflective surfaces                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Emotional Design Goals

| User State | Design Response |
|---|---|
| Overwhelmed (many tasks) | Clean, spaced layout with clear hierarchy. Progress bars show completion. |
| Focused (deep work) | Minimal UI, Pomodoro timer prominent, distractions hidden. |
| Curious (exploring features) | Interactive onboarding, progressive disclosure, tooltips. |
| Accomplished (task complete) | Celebratory micro-animation (confetti), streak updates. |
| Tired (late night) | Dark theme, reduced contrast on secondary elements, warm-toned accents. |
| Lost (new user) | Guided flows, contextual help, clear CTAs. |

---

## 3. Design Principles

| # | Principle | Definition | How We Apply It |
|---|---|---|---|
| 1 | **Hierarchy** | Every screen has one primary action. Visual weight communicates importance. | Card titles are Syne bold; secondary text is DM Sans normal. Primary buttons are the most saturated color on the page. |
| 2 | **Contrast** | Differentiate elements through color, size, spacing, and texture — never rely on color alone. | Task priority uses icon + color + label (e.g., "!" icon + red + "Urgent"). Interactive elements have distinct hover states. |
| 3 | **Consistency** | Similar elements look and behave similarly across the entire application. | All cards share the same padding (p-5), border radius (xl/16px), and background. All buttons share the same height (44px) and radius (lg/12px). |
| 4 | **Feedback** | Every action produces a visible, immediate response. | Button press scales to 0.97. Task completion strikes through text. Form errors shake the input. Toast appears on every mutation. |
| 5 | **Tolerance** | Prevent errors before they happen. When errors occur, make recovery easy. | Undo toasts (5s window). Confirmation on destructive actions. Auto-save on forms. Input validation with clear messages. |
| 6 | **Accessibility** | No feature is complete until it's accessible. | WCAG 2.1 AA minimum. Keyboard navigable. Screen reader compatible. Reduced motion respected. |
| 7 | **Performance as UX** | Perceived performance is a design concern, not just an engineering one. | Skeleton screens under 200ms. Optimistic UI updates. Route preloading. 60fps animations. |

---

## 4. Layout System

### 4.1 Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                      Pages (16 modules)                       │
│  Composed via PageLayout + StateHandler + DataView pattern    │
├───────────────────────────────────────────────────────────────┤
│                   CSS Grid Framework                          │
│  12-column grid | CSS Grid auto-fill | Flexbox compositions  │
├───────────────────────────────────────────────────────────────┤
│                   Spacing Scale (4px base)                    │
│  0(0) | 1(4) | 2(8) | 3(12) | 4(16) | 5(20) | 6(24) | ...  │
├───────────────────────────────────────────────────────────────┤
│               Container & Max-Width System                    │
│  App max: 1280px | Content max: 720px | Sidebar: 240px       │
├───────────────────────────────────────────────────────────────┤
│              Responsive Breakpoints (6 levels)                │
│  xs(375) | sm(640) | md(768) | lg(1024) | xl(1280) | 2xl(1536)│
└───────────────────────────────────────────────────────────────┘
```

### 4.2 CSS Grid Framework

| Property | Value | Notes |
|---|---|---|
| Grid columns | 12 | Standard layout grid |
| Column gap | 24px (gap-6) | Consistent across all grid uses |
| Horizontal padding | 32px (px-8) on desktop, 16px (px-4) on mobile |
| Max container width | 1280px | Applied to `.app-container` |
| Content max width | 720px | For long-form reading (goals, briefing) |

**Column Span Classes:**

| Span | Class | Usage |
|---|---|---|
| Full | `col-span-12` | Dashboard briefing, full-width banners |
| Two-thirds | `col-span-8` | Main content area with sidebar |
| Half | `col-span-6` | Split layouts, side-by-side panels |
| Third | `col-span-4` | Three-column card layouts |
| Quarter | `col-span-3` | Four-column stat grid |

### 4.3 Responsive Card Grid

```css
/* Primary card grid pattern */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

/* Stat grid (4 columns on desktop, 2 on tablet, 1 on mobile) */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

/* Compact card grid for dense screens */
.compact-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
```

### 4.4 Dashboard Grid Layout

```
Desktop (1280px+):
┌─────────────────────────────────────────────────────────────┐
│  Daily Briefing                                 (col-span-12) │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Tasks Today │  Courses     │  Income       │  Streak        │
│  (col-span-3)│  (col-span-3)│  (col-span-3) │  (col-span-3)  │
├──────────────┴──────────────┼───────────────┴────────────────┤
│  Activity Heatmap            │  Upcoming Deadlines           │
│  (col-span-8)                │  (col-span-4)                 │
├──────────────┬──────────────┴───────────────┬────────────────┤
│  Quick Stats │  Recent Resources            │  Top Goal      │
│  (col-span-3)│  (col-span-6)                │  (col-span-3)  │
└──────────────┴──────────────────────────────┴────────────────┘
```

### 4.5 Spacing Scale

Base unit: **4px**. All spacing values MUST be multiples of 4.

| Token | Pixels | Tailwind | Usage |
|---|---|---|---|
| 0 | 0px | `gap-0` `p-0` | Remove spacing |
| 1 | 4px | `gap-1` `p-1` | Tight inner paddings, icon gaps |
| 2 | 8px | `gap-2` `p-2` | Stack spacing, tight gaps, sidebar items |
| 3 | 12px | `gap-3` `p-3` | Button padding (vertical), list gaps |
| 4 | 16px | `gap-4` `p-4` | Card padding (compact), dashboard stat gaps |
| 5 | 20px | `gap-5` `p-5` | Card padding (default), card grid gap |
| 6 | 24px | `gap-6` `p-6` | Section spacing, modal padding, column gap |
| 7 | 28px | `gap-7` `p-7` | Page section gaps (optional) |
| 8 | 32px | `gap-8` `p-8` | Page horizontal padding, sidebar width |
| 10 | 40px | `gap-10` `p-10` | Large section separation |
| 12 | 48px | `gap-12` `p-12` | Page section margins |
| 16 | 64px | `gap-16` `p-16` | Major page sections |
| 20 | 80px | `gap-20` `p-20` | Hero sections, extra-large spacing |

### 4.6 Container and Layout Widths

| Element | Width | Notes |
|---|---|---|
| App container | max-w-7xl (1280px) | Centered with auto margins |
| Sidebar (desktop) | w-60 (240px) | Fixed position, full height |
| Navbar content | max-w-7xl (1280px) | Centered within navbar |
| Modal (default) | max-w-lg (512px) | Centered on viewport |
| Modal (large) | max-w-2xl (672px) | For complex forms |
| Modal (full screen) | 100vw x 100vh | Mobile only |
| Toast | max-w-sm (384px) | Top-right position |
| Dropdown menu | w-56 (224px) | Anchored to trigger |
| Search bar (navbar) | max-w-md (448px) | Centered in navbar |
| Content body | max-w-prose (720px) | Long-form reading |
| Card (minimum) | min-w-[320px] | Card grid auto-fill |

---

## 5. Component Design Specifications

### 5.1 Component Architecture Layers

```
Pages           → Dashboard, Tasks, Courses, Goals, Habits, Sleep, Income, etc.
Composed        → DataTable, KanbanBoard, RoadmapCanvas, Navbar, Sidebar, Heatmap, MessageList
Primitives      → Button, Card, Input, Modal, Badge, Progress, Spinner, Avatar, Tooltip, Dropdown
Tailwind Utils  → .btn, .card, .input, .badge, .spinner, .glass, .skeleton
Tailwind Config → colors | fonts | shadows | spacing | screens | animation
CSS Properties  → --font-* | @keyframes | @layer components | --color-*
```

### 5.2 Primitive Components

#### 5.2.1 Button

| Variant | Background | Text | Border | Hover | Active | Disabled |
|---|---|---|---|---|---|---|
| Primary | accent-primary (#6366F1) | white | none | accent-primary/90 + glow | scale(0.97) | opacity 50% |
| Secondary | bg-elevated (#1A1D28) | text-primary (#F0F2F5) | border (#2A2E3F) | bg-border (#2A2E3F) | scale(0.97) | opacity 50% |
| Ghost | transparent | text-secondary (#8B92A5) | none | bg-elevated + text-primary | scale(0.97) | opacity 50% |
| Danger | accent-error (#EF4444) | white | none | #DC2626 | scale(0.97) | opacity 50% |
| Icon | transparent | text-secondary | none | bg-elevated | scale(0.97) | opacity 50% |

**Specifications:**
- Height: 44px (h-11, touch target compliant)
- Min-width: 44px (icon-only), auto (with text)
- Border-radius: lg (12px)
- Padding: px-5 py-3 (20px x 12px) for text buttons, p-3 (12px) for icon buttons
- Font: DM Sans, base (15px), medium (500)
- Icon spacing: 8px gap between icon and text
- Loading state: icon replaced with 20px spinner

**Group Behavior:**
- Button groups use `gap-3` (12px) spacing
- Single primary CTA per view
- Destructive actions always use `.btn-danger`

#### 5.2.2 Card

| Variant | Background | Border | Shadow | Hover | Usage |
|---|---|---|---|---|---|
| Default | bg-card (#12141C) | border (#2A2E3F) | 0 4px 24px rgba(0,0,0,0.2) | — | Static content display |
| Interactive | bg-card (#12141C) | border (#2A2E3F) | 0 4px 24px rgba(0,0,0,0.2) | translateY(-3px), glow intensifies | Clickable cards (tasks, courses) |
| Highlighted | bg-card (#12141C) | accent-primary (#6366F1) | 0 4px 24px rgba(99,102,241,0.15) | — | Featured/active items |
| Compact | bg-card (#12141C) | border (#2A2E3F) | none | — | Dashboard stats, dense grids |
| Glass | rgba(18,20,28,0.8) | rgba(255,255,255,0.08) | 0 8px 32px rgba(0,0,0,0.3) | — | Modals, overlays |

**Specifications:**
- Border-radius: xl (16px)
- Background: `bg-card` (#12141C) with optional backdrop-blur(20px)
- Padding (default): p-5 (20px)
- Padding (compact): p-4 (16px)
- Border: 1px solid `border` (#2A2E3F)
- Structure: optional header (title + actions), body (content), footer (actions)
- Title truncation: 2 lines with `line-clamp-2`
- Description truncation: 3 lines with `line-clamp-3`

**Card Structure:**
```
┌──────────────────────────────────┐
│  Card Header                     │
│  ┌─ Title ──────────── Actions ─┐│
│  │  Card Title (DM Sans, 2xl)   │ │
│  │                     [⋮] [x]  │ │
│  └──────────────────────────────┘ │
│                                   │
│  Card Body                        │
│  Content area (flexible)          │
│                                   │
│  Card Footer                      │
│  ┌──────────────────────────────┐ │
│  │ [Primary]  [Secondary]       │ │
│  └──────────────────────────────┘ │
└──────────────────────────────────┘
```

#### 5.2.3 Input

| State | Background | Border | Text | Notes |
|---|---|---|---|---|
| Default | bg-input (#0D0F14) | border (#2A2E3F) | text-primary (#F0F2F5) | — |
| Focus | bg-input (#0D0F14) | accent-primary (#6366F1) + ring-1 | text-primary | Ring offset: 2px |
| Error | bg-input (#0D0F14) | accent-error (#EF4444) | text-primary | Error message below |
| Disabled | bg-card (#12141C) | border-subtle (#1E222E) | text-disabled (#475569) | opacity 50% |
| Filled | bg-input (#0D0F14) | border (#2A2E3F) | text-primary | — |
| Read-only | bg-card (#12141C) | border-subtle (#1E222E) | text-secondary | — |

**Input Variants:**

| Type | Height | Border-radius | Special |
|---|---|---|---|
| Text | 44px (h-11) | lg (12px) | — |
| Textarea | min-h-[120px] | lg (12px) | Resize: vertical |
| Select | 44px (h-11) | lg (12px) | Custom chevron icon |
| Search | 44px (h-11) | full (rounded) | Leading search icon |
| Checkbox | 20x20px | md (6px) | Custom checked state |
| Radio | 20x20px | full (circle) | Custom checked state |
| Toggle | 44x24px | full | Custom knob animation |
| Date | 44px (h-11) | lg (12px) | Native picker |

**Input Structure:**
```
┌──────────────────────────────────┐
│  Label (text-secondary, sm)      │
│  ┌──────────────────────────────┐│
│  │ [icon]  Input text   [icon]  ││
│  └──────────────────────────────┘│
│  Helper text / Error message     │
└──────────────────────────────────┘
```

#### 5.2.4 Badge

| Variant | Background (15% opacity) | Text | Border (20% opacity) |
|---|---|---|---|
| Primary | rgba(99,102,241,0.15) | #6366F1 | rgba(99,102,241,0.2) |
| Success | rgba(16,185,129,0.15) | #10B981 | rgba(16,185,129,0.2) |
| Warning | rgba(245,158,11,0.15) | #F59E0B | rgba(245,158,11,0.2) |
| Error | rgba(239,68,68,0.15) | #EF4444 | rgba(239,68,68,0.2) |
| Info | rgba(59,130,246,0.15) | #3B82F6 | rgba(59,130,246,0.2) |
| Neon | rgba(0,255,163,0.15) | #00FFA3 | rgba(0,255,163,0.2) |

**Specifications:**
- Font: xs (11px), medium (500)
- Padding: px-2.5 py-1 (10px x 4px)
- Border-radius: md (10px)
- Optional: leading dot for status indicators

#### 5.2.5 Modal

| Property | Default | Large | Full-Screen (Mobile) |
|---|---|---|---|
| Width | max-w-lg (512px) | max-w-2xl (672px) | 100vw |
| Max height | 80vh | 85vh | 100vh |
| Border-radius | xl (16px) | xl (16px) | 0 |
| Animation | scale(0.9)→1, opacity 0→1 | scale(0.9)→1, opacity 0→1 | slideInUp |
| Backdrop | bg-black/50, backdrop-blur-sm | bg-black/50 | bg-black/70 |

**States:**
- **Open**: Backdrop fades in (200ms), modal scales in (300ms)
- **Close**: Modal scales out (200ms), backdrop fades out (200ms)
- **Loading**: Skeleton within modal body
- **Error**: Error banner at top of modal content

**Modal Contents:**
```
┌──────────────────────────────────┐
│  Header                           │
│  ┌─ Title (DM Sans, 2xl) ─── [x] │
│  └─────────────────────────────── │
│                                   │
│  Body (scrollable, max-h 80vh)    │
│  ┌──────────────────────────────┐ │
│  │ Content here                  │ │
│  └──────────────────────────────┘ │
│                                   │
│  Footer                           │
│  ┌──────────────────────────────┐ │
│  │  [Secondary]    [Primary]    │ │
│  └──────────────────────────────┘ │
└──────────────────────────────────┘
```

#### 5.2.6 Tooltip

| Property | Value |
|---|---|
| Background | bg-elevated (#1A1D28) |
| Text | text-primary (#F0F2F5) |
| Font | DM Sans, sm (13px) |
| Border-radius | lg (12px) |
| Padding | px-3 py-2 (12px x 8px) |
| Arrow | 8px equilateral, color matches background |
| Show delay | 500ms (desktop), none (mobile) |
| Hide delay | 200ms |
| Max width | 280px |

#### 5.2.7 Dropdown

| Property | Value |
|---|---|
| Background | bg-elevated (#1A1D28) |
| Border | 1px solid border (#2A2E3F) |
| Shadow | 0 8px 32px rgba(0,0,0,0.4) |
| Width | w-56 (224px) |
| Item height | 44px (h-11) |
| Item padding | px-4 py-3 (16px x 12px) |
| Border-radius | lg (12px) |
| Z-index | z-dropdown (1000) |
| Animation | opacity 0→1 (150ms), slight scale |

**Item States:**
- Default: text-secondary, no background
- Hover: bg-border (#2A2E3F), text-primary
- Active/Selected: accent-primary/10 background, accent-primary text
- Disabled: text-disabled, no hover

#### 5.2.8 Avatar

| Size | Dimensions | Usage |
|---|---|---|
| sm | 24x24px | Inline badges, comment threads |
| md | 32x32px | Navbar, user lists |
| lg | 40x40px | Profile page, settings |
| xl | 64x64px | Empty states, welcome screens |

**Properties:**
- Border-radius: full (circular)
- Background: accent-primary (#6366F1) with User icon
- Image: cover fit, 1px solid border-subtle border
- Fallback: First letter of name, DM Sans semibold

#### 5.2.9 Progress Bar

| Property | Value |
|---|---|
| Track height | 6px (h-1.5) |
| Track background | bg-elevated (#1A1D28) |
| Fill gradient | linear-gradient(90deg, #6366F1 0%, #8B5CF6 50%, #00FFA3 100%) |
| Fill transition | width 500ms ease-out |
| Border-radius | full (9999px) |
| Label | DM Sans, xs (11px), text-secondary |

#### 5.2.10 Spinner

| Size | Dimensions | Usage |
|---|---|---|
| sm | 16px | Inline, button loading state |
| md | 20px | Section loading, action feedback |
| lg | 40px | Page-level loading |
| xl | 64px | Full-page loading |

**Properties:**
- Border: 2px (sm/md), 3px (lg), 4px (xl) — top border accent-primary, rest border-subtle
- Animation: `animate-spin` (Tailwind built-in)
- Accessible: `aria-label="Loading"`

---

### 5.3 Composed Components

#### 5.3.1 Navbar

| Property | Value |
|---|---|
| Height | h-16 (64px) |
| Position | fixed top, full width, left-60 on desktop |
| Background | bg-card (#12141C) |
| Border-bottom | 1px solid border (#2A2E3F) |
| Z-index | 40 |
| Padding | px-6 (24px) |
| Left section | Logo + page title or search bar |
| Right section | Notification bell + avatar dropdown |

#### 5.3.2 Sidebar

| Property | Value |
|---|---|
| Width | w-60 (240px) |
| Position | fixed left, full height |
| Background | bg-card (#12141C) |
| Border-right | 1px solid border (#2A2E3F) |
| Z-index | 30 |
| Item height | 44px (h-11) |
| Item padding | px-3 py-2 (12px x 8px) |
| Active item | bg-accent-primary/10 + text-accent-primary |
| Default item | text-text-secondary, hover → bg-elevated + text-primary |
| Icon size | 20px |
| Icon+label gap | gap-3 (12px) |
| Scroll | overflow-y-auto on overflow |

#### 5.3.3 DataTable

| Property | Value |
|---|---|
| Header background | bg-card (#12141C) |
| Row height | 52px (h-13) |
| Row hover | bg-elevated/50 (#1A1D28/50) |
| Border | 1px solid border-subtle (#1E222E) |
| Sort indicator | Arrow icon, accent-primary when active |
| Checkbox column | 44px width |
| Empty state | 64px icon + title + description + CTA |
| Pagination | Bottom-aligned, page numbers + prev/next |

#### 5.3.4 KanbanBoard

| Property | Value |
|---|---|
| Column width | min-w-[300px], max-w-[400px] |
| Column background | transparent |
| Column header | Sticky, title + count badge |
| Card margin | gap-3 (12px) between cards |
| Drag handle | 6-dot grip icon, visible on hover |
| Drag state | Elevated shadow, slight rotation, opacity 0.9 |
| Drop zone | Dashed border, accent-primary highlight |
| Empty column | "No items" with ghost card placeholder |

#### 5.3.5 CommandPalette

| Property | Value |
|---|---|
| Width | max-w-xl (576px) |
| Position | centered, top 20% |
| Input height | 56px (h-14) |
| Input font | DM Sans, lg (17px) |
| Result item height | 44px (h-11) |
| Z-index | z-modal (1030) |
| Backdrop | bg-black/60, backdrop-blur-sm |
| Shortcut hint | text-tertiary, xs, monospace |

---

## 6. Color System

### 6.1 Complete Color Reference

#### Background Colors

| Token | Hex | Usage | Contrast Ratio |
|---|---|---|---|
| `bg-background` | #0A0B0F | Main page background | Base |
| `bg-background-dark` | #050607 | Deepest level (search input, dropdowns) | Slightly higher |
| `bg-background-card` | #12141C | Card, sidebar, navbar backgrounds | 14.8:1 (text-primary) |
| `bg-background-elevated` | #1A1D28 | Elevated surfaces (dropdowns, modals) | 12.4:1 |
| `bg-background-input` | #0D0F14 | Input field backgrounds | 15.8:1 |

#### Text Colors

| Token | Hex | Usage | Contrast Ratio on bg-background |
|---|---|---|---|
| `text-text-primary` | #F0F2F5 | Headings, body text | 15.2:1 |
| `text-text-secondary` | #8B92A5 | Subheadings, metadata | 7.1:1 |
| `text-text-tertiary` | #5A6075 | Placeholders, disabled text | 4.6:1 |
| `text-text-inverse` | #0F172A | Text on light backgrounds | N/A |
| `text-text-disabled` | #475569 | Disabled element text | 3.5:1 |

#### Border Colors

| Token | Hex | Usage |
|---|---|---|
| `border-border-default` | #2A2E3F | Default card/component borders |
| `border-border-subtle` | #1E222E | Subtle separator lines |
| `border-border-accent` | #6366F1 | Active/focus border state |
| `border-border-light` | #E2E8F0 | Light mode borders (future) |

#### Accent Colors

| Token | Hex | Usage | Contrast Ratio |
|---|---|---|---|
| `accent-primary` | #6366F1 | Primary actions, links, active states | 5.2:1 |
| `accent-primary-hover` | #4F46E5 | Primary button hover | — |
| `accent-secondary` | #10B981 | Success states, completed | 7.8:1 |
| `accent-secondary-hover` | #059669 | Success hover | — |
| `accent-warning` | #F59E0B | Warning states, medium priority | 6.1:1 |
| `accent-warning-hover` | #D97706 | Warning hover | — |
| `accent-error` | #EF4444 | Error states, urgent priority | 4.8:1 |
| `accent-error-hover` | #DC2626 | Error hover | — |
| `accent-info` | #3B82F6 | Informational badges, links | 4.2:1 |
| `accent-success` | #22C55E | Positive indicators | 6.5:1 |
| `accent-neon` | #00FFA3 | Decorative highlights, low priority | 12.1:1 |
| `accent-cyber` | #FF3366 | Urgent indicators, critical badges | 5.5:1 |

#### Priority Colors

| Token | Hex | Usage |
|---|---|---|
| `priority-urgent` | #FF3366 | Critical tasks (cyber pink) |
| `priority-high` | #FF6B35 | High-importance tasks (orange) |
| `priority-medium` | #FFB800 | Normal tasks (amber) |
| `priority-low` | #00FFA3 | Low-priority tasks (neon green) |

#### Glass (RGBA)

| Token | Value | Usage |
|---|---|---|
| `glass-light` | rgba(255,255,255,0.03) | Subtle glass surfaces |
| `glass-medium` | rgba(255,255,255,0.08) | Card glass overlays |
| `glass-heavy` | rgba(255,255,255,0.15) | Highlighted glass states |

### 6.2 Color Usage Rules

| Rule | Description |
|---|---|
| **Primary actions only** | accent-primary used exclusively for primary CTAs (1 per view max) |
| **Semantic colors** | Never use accent-error for decoration; only for actual errors/urgency |
| **Neon sparingly** | accent-neon for decorative highlights, priority-low, streak effects only |
| **No color alone** | Never communicate status through color alone — always pair with icon + text |
| **Glass augment** | Glass colors add to background-color, don't replace it |
| **Priority mapping** | Priority colors map 1:1 to task priority levels |
| **Hover variants** | Every interactive color has a corresponding hover variant |
| **Disabled opacity** | Disabled elements use opacity 50% across the board |

---

## 7. Typography Scale

### 7.1 Complete Type Scale

| Level | Size | Line Height | Font Weight | Font Family | Tailwind | Usage |
|---|---|---|---|---|---|---|
| 7xl | 48px | 1.0 | 700 (bold) | Syne | `text-7xl` | Hero display, landing page |
| 6xl | 42px | 1.05 | 700 (bold) | Syne | `text-6xl` | Section hero titles |
| 5xl | 36px | 1.1 | 700 (bold) | Syne | `text-5xl` | Page titles (dashboard) |
| 4xl | 32px | 1.15 | 600 (semibold) | Syne | `text-4xl` | Module page headers |
| 3xl | 28px | 1.2 | 600 (semibold) | DM Sans | `text-3xl` | Section headers |
| 2xl | 24px | 1.25 | 600 (semibold) | DM Sans | `text-2xl` | Card titles |
| xl | 20px | 1.3 | 500 (medium) | DM Sans | `text-xl` | Subheadings, modal titles |
| lg | 18px | 1.35 | 500 (medium) | DM Sans | `text-lg` | Module subheadings |
| base | 16px | 1.5 | 400 (normal) | DM Sans | `text-base` | Body text, list items |
| sm | 14px | 1.5 | 400 (normal) | DM Sans | `text-sm` | Secondary info, metadata |
| xs | 13px | 1.4 | 500 (medium) | DM Sans | `text-xs` | Labels, badge text |
| 2xs | 12px | 1.3 | 500 (medium) | JetBrains Mono | `text-[12px]` | Timestamps, counters |
| micro | 11px | 1.2 | 600 (semibold) | JetBrains Mono | `text-[11px]` | Data labels, chart values |

### 7.2 Typography Usage Rules

| Rule | Description |
|---|---|
| **Syne is display only** | Syne used for headlines ≤ 3xl only. Never for body text. |
| **DM Sans is default** | 90% of text uses DM Sans. Body, labels, buttons, inputs. |
| **JetBrains Mono for data** | Code, timers, scores, percentages, technical data. |
| **Line height scales** | Larger text gets tighter line height. Smaller text gets looser. |
| **Font weight hierarchy** | bold (700) for page titles, semibold (600) for sections, medium (500) for sub-sections, normal (400) for body. |
| **Gradient text** | `.text-gradient-accent` for high-value numbers, scores, and key metrics only. |
| **No orphans** | `text-balance` on all headings that wrap. |
| **Max line length** | Body text max-width 720px for readability. |

### 7.3 Text Truncation

| Element | Lines | Class | Notes |
|---|---|---|---|
| Card title | 2 | `line-clamp-2` | Truncate with ellipsis |
| Card description | 3 | `line-clamp-3` | Truncate with ellipsis |
| Table cell | 1 | `truncate` | Truncate with ellipsis |
| Page title | 1 | `truncate` | No wrap, truncate |
| Notification message | 2 | `line-clamp-2` | Toast notification |
| Task title (list) | 1 | `truncate` | No wrap |

---

## 8. Iconography System

### 8.1 Icon Library

| Set | Source | License | Count Used |
|---|---|---|---|
| Primary | lucide-react | MIT / ISC | ~60 icons |
| Navigation | lucide-react | — | 16 sidebar icons |
| Status | lucide-react | — | 8 status icons |
| Actions | lucide-react | — | ~30 action icons |
| Custom | apps/web/public/icons/ | Proprietary | ~5 custom (ARIA logo, etc.) |

### 8.2 Icon Usage Rules

| Rule | Description |
|---|---|
| **Stroke width** | Default lucide-react stroke (1.5px). Never change. |
| **Size** | 20x20px for sidebar, 16x16px for inline, 24x24px for buttons with text |
| **Color** | Inherits current text color. Use `text-` utilities for overrides. |
| **Label** | Every standalone icon has `aria-label` or `aria-labelledby` |
| **Custom icons** | SVG files in `public/icons/`, optimized with SVGO |
| **No brand icons** | Use text labels instead of brand logos (limited set) |
| **Consistent metaphor** | Same icon always means same action (e.g., `Plus` always for create) |

### 8.3 Icon Mapping (Selected)

| Action | Icon (lucide-react) | Size |
|---|---|---|
| Create / Add | `Plus` | 20px |
| Edit | `Pencil` | 16px |
| Delete | `Trash2` | 16px |
| Close | `X` | 20px |
| Search | `Search` | 20px |
| Settings | `Settings` | 20px |
| Notifications | `Bell` | 20px |
| Menu | `Menu` | 24px |
| Back | `ArrowLeft` | 20px |
| Forward | `ArrowRight` | 20px |
| Up | `ChevronUp` | 16px |
| Down | `ChevronDown` | 16px |
| More | `MoreHorizontal` / `MoreVertical` | 20px |
| Filter | `Filter` | 16px |
| Sort | `ArrowUpDown` | 16px |
| Download | `Download` | 20px |
| Upload | `Upload` | 20px |
| Share | `Share2` | 20px |
| Drag | `GripVertical` | 16px |
| Check | `Check` | 16px |
| Warning | `AlertTriangle` | 20px |
| Error | `AlertCircle` | 20px |
| Info | `Info` | 20px |
| Success | `CheckCircle` | 20px |

---

## 9. Image Style Guide

### 9.1 Image Types

| Type | Format | Max Size | Usage |
|---|---|---|---|
| User avatar | JPEG/WebP | 200x200px, <50KB | Profile, navbar |
| Course thumbnail | JPEG/WebP | 640x360px, <100KB | Course cards |
| Resource preview | WebP | 1280x720px, <200KB | Resource cards |
| Empty state illustration | SVG | 64x64px | Module empty states |
| Custom illustration | SVG | Variable | Dashboard hero, branding |
| Background texture | PNG/WebP | Full width, <50KB | Page backgrounds |

### 9.2 Image Guidelines

- All raster images MUST be served in WebP format with JPEG fallback
- SVG MUST be optimized with SVGO (remove metadata, collapse groups)
- Icons and illustrations MUST be monochromatic (currentColor fill where possible)
- User-uploaded images MUST be processed server-side (resize, format convert)
- Decorative images MUST have `aria-hidden="true"` and empty `alt=""`

### 9.3 Image Fallbacks

| Scenario | Fallback |
|---|---|
| Avatar not set | Initials in accent-primary circle |
| Course thumbnail not available | Gradient placeholder (accent-primary → accent-secondary) |
| Resource preview fails | File type icon (PDF, Video, Link, etc.) |
| Image loading | Skeleton (card aspect ratio placeholder) |
| Image error | Broken image icon with "Image not available" text |

---

## 10. Data Visualization Design

### 10.1 Chart Components

| Chart Type | Module | Data | Visual Style |
|---|---|---|---|
| Bar chart | Time, Income | Hours per day, earnings per week | Neon gradient bars, rounded top, hover tooltip |
| Line chart | Habits, Streaks | Streak over 30 days | Smooth curved line, gradient fill below, dot on hover |
| Pie chart | Income | Category breakdown | Donut style, center total, hover segment expansion |
| Progress bar | Courses, Goals | Completion percentage | Gradient fill (indigo → green), animated width |
| Radar chart | Learning | Skills assessment (6 axes) | Translucent fill, animated vertices |
| Heatmap | Tasks, Productivity | 6-month daily activity | GitHub-style, intensity gradient, hover tooltip |

### 10.2 Chart Specifications

| Property | Value |
|---|---|
| Background | Transparent (no chart background) |
| Font | JetBrains Mono for values, DM Sans for labels |
| Axis labels | sm (14px), text-tertiary |
| Tooltip bg | bg-elevated (#1A1D28), border border-default |
| Tooltip text | DM Sans, sm (14px), text-primary |
| Grid lines | rgba(255,255,255,0.05) |
| Animation | Fade in on mount (300ms), data transitions (500ms ease-out) |
| Min height | 200px (compact), 400px (full) |
| Responsive | Auto-sizing via container query |

### 10.3 Progress Indicators

| Indicator | Style | Animation | When Used |
|---|---|---|---|
| Linear progress | 6px bar, gradient fill | 500ms width transition | Course progress, goal progress |
| Circular progress | 40px circle, stroke-dasharray | 800ms circumference animation | Daily score, sleep quality |
| Step progress | Horizontal dots, line connectors | 300ms dot fill | Onboarding, setup wizard |
| Countdown | Text + pulsing border | 1s pulse cycle | Deadline approaching (<24h) |
| Streak indicator | Flame icon + number | Scale pulse on streak extend | Habits, daily login |

### 10.4 Calendar Design

| View | Module | Display |
|---|---|---|
| Month grid | Habits, Tasks | 7-column grid, day cells with completion dots |
| Week row | Dashboard | 7-day horizontal scroll, compact |
| Year mini | Dashboard | 12-month grid, intensity heatmap |
| Single day | Sleep, Time | 24-hour timeline, event blocks |

**Calendar Cell Specifications:**
- Day cell: 40x40px (desktop), 36x36px (mobile)
- Today: accent-primary border ring
- Selected: accent-primary/15 background
- Has events: dot indicator (4px circle, accent-primary)
- Empty: no indicator
- Disabled (outside month): opacity 30%

---

## 11. Form Design

### 11.1 Form Layout Patterns

| Layout | Usage | Properties |
|---|---|---|
| Single column | Most forms (task, course, habit) | Max-width 480px, centered |
| Two column | Settings, profile | 2-column grid, gap-6 |
| Inline | Search, quick filters | Horizontal layout, items aligned |
| Accordion | Long forms (goal, project) | Sections collapsible, one open at a time |
| Stepped | Onboarding, setup wizard | Step indicator + content + prev/next |

### 11.2 Input States

#### Default
```
┌─────────────────────────────┐
│  Label (text-secondary, sm) │
│  ┌───────────────────────┐  │
│  │ Placeholder text      │  │
│  └───────────────────────┘  │
│  Helper text (sm, tertiary) │
└─────────────────────────────┘
```

#### Focus
```
┌─────────────────────────────┐
│  Label (text-accent, sm)    │
│  ┌───────────────────────┐  │ ← ring-1 accent-primary
│  │ Typed text            │  │
│  └───────────────────────┘  │
│  Helper text (sm, tertiary) │
└─────────────────────────────┘
```

#### Error
```
┌─────────────────────────────┐
│  Label (text-error, sm)     │
│  ┌───────────────────────┐  │ ← ring-1 accent-error
│  │ Typed text            │  │
│  └───────────────────────┘  │
│  ⚠ Error message (sm, err) │ ← aria-live="assertive"
└─────────────────────────────┘
```

#### Disabled
```
┌─────────────────────────────┐
│  Label (text-disabled, sm)  │
│  ┌───────────────────────┐  │ ← opacity 50%
│  │ Disabled text         │  │
│  └───────────────────────┘  │
│  Helper text (sm, disabled) │
└─────────────────────────────┘
```

#### Filled (Success)
```
┌─────────────────────────────┐
│  Label (text-secondary, sm) │
│  ┌───────────────────────┐  │
│  │ ✓ Valid input         │  │ ← trailing check icon
│  └───────────────────────┘  │
│  (no helper text needed)    │
└─────────────────────────────┘
```

### 11.3 Form Validation Rules

| Validation | Timing | Message Style |
|---|---|---|
| Required field | On blur + submit | "[Field label] is required" |
| Format validation | On blur | "Enter a valid [format]" |
| Max length | On input (live) | Character counter: "25/200" |
| Min length | On blur | "Must be at least X characters" |
| Pattern match | On blur | Specific format instructions |
| Async (unique check) | Debounced 500ms | "[Value] is already taken" |

### 11.4 Form Submission

| State | Button State | Feedback |
|---|---|---|
| Idle | Enabled | Normal |
| Submitting | Spinner replaces icon, disabled | Inline spinner |
| Success | Brief green flash, then reset | Toast "Saved successfully" |
| Error | Re-enable, shake animation | Inline error message + toast |
| Server error | Re-enable | Toast "Something went wrong" + retry |

---

## 12. Dark Mode Design Decisions

### 12.1 Dark Mode Strategy

| Decision | Implementation | Rationale |
|---|---|---|
| Always dark (v1) | `darkMode: 'class'`, body always has `dark` class | Primary users are students working late; light mode not needed |
| No toggle (v1) | No light/dark switch | Single theme reduces complexity; light mode planned for v2 |
| True black sparingly | #050607 for deepest surfaces | Avoids eye strain; true black used only for input fields |
| Glass overlays | rgba white overlays on dark surfaces | Creates depth without light colors |
| Neon glow | Box-shadow with accent colors | Replaces drop shadows (invisible on dark) |
| Gradient backgrounds | Dual radial gradients on body | Adds texture without affecting readability |

### 12.2 Dark Mode-Only Patterns

| Pattern | Implementation |
|---|---|
| **Text shadows** | None (text on dark needs no shadow) |
| **Box shadows** | Replace with glow effects (colored shadows) |
| **Focus rings** | accent-primary ring, visible on all surfaces |
| **Active states** | Scale down (0.97) instead of darkening |
| **Borders** | Visible borders on all cards and sections (light gray #2A2E3F) |
| **Skeleton loading** | Dark gray shimmer (#1A1D28 → #2A2E3F) |
| **Error states** | Red border + red glow, not just color change |
| **Disabled states** | Opacity 50% across all elements |

### 12.3 Dark Mode Color Tokens

All tokens are designed for dark backgrounds. No token maps to a light-equivalent in v1.

| Token | Hex | Light Alternative (Future) |
|---|---|---|
| `bg-page` | #0A0B0F | #F8FAFC |
| `bg-card` | #12141C | #FFFFFF |
| `bg-elevated` | #1A1D28 | #F1F5F9 |
| `border-default` | #2A2E3F | #E2E8F0 |
| `text-primary` | #F0F2F5 | #0F172A |

---

## 13. Design Tokens vs Hardcoded Values

### 13.1 The Rule

**NEVER hardcode colors, spacing, typography, shadows, or animation values in component files.**

All visual properties MUST reference design tokens defined in `tailwind.config.js` or `globals.css`.

### 13.2 Token Categories

| Category | Source | Example |
|---|---|---|
| Colors | `tailwind.config.js` → `theme.extend.colors` | `bg-background-card` |
| Fonts | `globals.css` → CSS custom properties | `font-display` |
| Spacing | `tailwind.config.js` → `theme.extend.spacing` | `gap-5`, `p-6` |
| Shadows | `tailwind.config.js` → `theme.extend.boxShadow` | `shadow-glow` |
| Animations | `tailwind.config.js` → `theme.extend.animation` | `animate-float` |
| Z-index | `tailwind.config.js` → `theme.extend.zIndex` | `z-dropdown` |
| Border radius | `tailwind.config.js` → `theme.extend.borderRadius` | `rounded-xl` |
| Breakpoints | `tailwind.config.js` → `theme.screens` | `lg:` |

### 13.3 Enforcement

| Mechanism | Scope | Tool |
|---|---|---|
| ESLint rule | JSX/TSX files | `eslint-plugin-tailwindcss` — no arbitrary values |
| Design review | PR review process | Manual check: "No hardcoded colors" |
| Component development | New components | Start from existing component patterns |
| Automated check | CI pipeline | Compare vs allowed tokens list |

---

## 14. Design Review Process

### 14.1 Review Stages

| Stage | Participants | Focus | Artifacts |
|---|---|---|---|
| **Self-review** | Designer | Compliance with design system, all states covered, accessibility basics | Figma file annotated |
| **Peer review** | 2+ designers | Consistency, visual quality, UX flow completeness | Figma comments |
| **Lead review** | Design lead | Brand alignment, quality bar, accessibility compliance | Sign-off checklist |
| **Engineering review** | Lead frontend dev | Technical feasibility, design token usage, effort estimate | Spec review |
| **PM sign-off** | Product manager | Requirements met, timeline aligned, scope confirmed | Final approval |

### 14.2 Review Checklist

- [ ] All component states designed (default, hover, active, disabled, loading, error, empty)
- [ ] Responsive layouts specified (mobile, tablet, desktop)
- [ ] Design tokens used (no hardcoded values)
- [ ] Color contrast verified (4.5:1 minimum)
- [ ] Focus indicators designed for interactive elements
- [ ] Touch targets ≥44x44px
- [ ] Typography hierarchy correct (h1→h2→h3→body)
- [ ] Icons have aria-labels or text alternatives
- [ ] Reduced motion alternatives considered
- [ ] Error states and validation messages defined
- [ ] Edge cases handled (long text, overflow, missing data)
- [ ] Copy approved

---

## 15. Figma File Organization

### 15.1 File Structure

```
Project: ARIA OS — Second Brain
├── 🎨 Design System
│   ├── 🎨 Colors — Color palette with tokens, contrast info, usage notes
│   ├── 🔤 Typography — Type scale, font families, line heights, examples
│   ├── 📐 Spacing — Spacing scale, padding/gap recommendations
│   ├── 🖼 Icons — Icon set reference, usage guidelines
│   ├── 🧩 Components
│   │   ├── Button — All variants, sizes, states (grid layout)
│   │   ├── Card — All variants, internal structure, responsive
│   │   ├── Input — All types, all states, error handling
│   │   ├── Modal — Desktop/mobile, empty, with content
│   │   ├── Badge — All variants, sizes
│   │   ├── Dropdown — Items, groups, dividers, scrolling
│   │   ├── Progress — Linear, circular, step indicators
│   │   ├── Tooltip — Positions, content types
│   │   ├── Skeleton — Card, list, chart placeholders
│   │   ├── Toast — All variants, stacked
│   │   ├── Spinner — All sizes, inline vs centered
│   │   ├── Avatar — All sizes, with image, fallback initials
│   │   └── Tabs — Horizontal, vertical, with icons
│   └── 🔄 Patterns
│       ├── Empty States — All 16 module empty states
│       ├── Loading States — Skeleton layouts for each module
│       ├── Error States — Error banners, error modals
│       └── Navigation — Sidebar, navbar, bottom nav, breadcrumbs
│
├── 🖥️ Screens
│   ├── 01 Dashboard — Default, empty, briefing detail
│   ├── 02 Tasks — List, kanban, detail, create, empty
│   ├── 03 Courses — Grid, detail, progress, empty
│   ├── 04 Goals — Canvas, detail, roadmap, empty
│   ├── 05 Habits — Grid, calendar, streak view, empty
│   ├── 06 Sleep — Dashboard, log, history
│   ├── 07 Income — Dashboard, entry list, add/edit
│   ├── 08 Projects — Kanban, detail, board settings
│   ├── 09 Ideas — Pipeline (raw→validating→building→shipped)
│   ├── 10 Resources — Grid, collections, detail
│   ├── 11 Opportunities — List, detail, match scores
│   ├── 12 Time — Dashboard, timer active, stats
│   ├── 13 Chat — Message list, ARIA response, empty
│   └── 14 Automation — Briefing, radar, weekly review
│
├── 🧪 Prototypes
│   ├── Onboarding Flow
│   ├── Task Creation Flow
│   ├── Weekly Review Flow
│   └── Mobile Navigation Flow
│
└── 📝 Research & Specs
    ├── Personas (3 core personas)
    ├── User Journey Maps (Aarav, Priya, Rohan)
    ├── Usability Test Reports
    └── Design Annotations
```

### 15.2 Component Organization Rules

- Every component is a **Figma component** with auto-layout
- Components are organized by type in the Assets panel
- Variants are used for different states (default, hover, active, disabled)
- Component descriptions include design token references
- Naming convention: `ComponentName/Variant/State` (e.g., `Button/Primary/Default`)
- Components use styles (color, text, effect styles) — never hardcoded values

---

## Reference

| Document | Link |
|---|---|
| UI/UX Specification | `docs/design/08_UIUX.md` |
| Design System | `docs/design/10_DesignSystem.md` |
| Design Tokens | `docs/design/35_DesignTokens.md` |
| Branding Guide | `docs/design/Branding.md` |
| Accessibility | `docs/design/Accessibility.md` |
| Motion System | `docs/design/MotionSystem.md` |
| Responsive Rules | `docs/design/ResponsiveRules.md` |
| Tailwind Configuration | `apps/web/tailwind.config.js` |
| Global CSS | `apps/web/app/globals.css` |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-05-15 | Design Team | Initial design architecture |
| 2.0.0 | 2026-06-01 | Design Team | Added component specifications, complete color system, typography scale |
| 3.0.0 | 2026-06-11 | Design Team | Enterprise upgrade: 15 sections, visual direction, layout system, 30+ component specs, data visualization, form design, Figma organization |
