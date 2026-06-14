# Motion System — Second Brain OS (ARIA)

> **Document ID:** SB-MOTION-001  
> **Version:** 1.0.0  
> **Status:** Active  
> **Last Updated:** 2026-06-11  
> **Classification:** Internal — Engineering & Design  
> **Owner:** Design Engineering Team

---

## Table of Contents

1. [Motion Design Principles](#1-motion-design-principles)
2. [Animation Parameters](#2-animation-parameters)
3. [Page Transition System](#3-page-transition-system)
4. [Micro-interactions](#4-micro-interactions)
5. [Loading & Progress States](#5-loading--progress-states)
6. [Notification & Feedback Animations](#6-notification--feedback-animations)
7. [List & Feed Animations](#7-list--feed-animations)
8. [Gesture-Based Animations](#8-gesture-based-animations)
9. [Data Visualization Animations](#9-data-visualization-animations)
10. [Performance Budget](#10-performance-budget)
11. [Framer Motion Implementation Patterns](#11-framer-motion-implementation-patterns)
12. [Reduced Motion & Fallback Strategy](#12-reduced-motion--fallback-strategy)
13. [Motion Dev Tools & Debugging](#13-motion-dev-tools--debugging)

---

## 1. Motion Design Principles

### 1.1 Philosophy

Motion in ARIA OS serves three purposes: **orientation**, **feedback**, and **delight** — in that order. Every animation must answer "where am I, what just happened, and what should I do next?" before it adds visual flair.

### 1.2 Core Principles

| Principle | Definition | Application |
|---|---|---|
| **Purposeful** | Every animation has a reason — never animate for decoration alone | Page transitions orient; button presses confirm; loading states reassure |
| **Fast & Responsive** | Animations complete within 100-300ms for micro-interactions | Users should never wait for an animation to finish before interacting |
| **Natural** | Easing curves mimic physical motion (ease-out for entries, ease-in for exits) | No linear animations unless data-driven (progress bars) |
| **Consistent** | Same interaction = same animation, everywhere in the product | Button press = 100ms scale, never varies by context |
| **Respectful** | Reduced motion is first-class, not an afterthought | `prefers-reduced-motion` respected at the system level; in-app controls for granularity |
| **Hierarchical** | More important content moves faster and with more emphasis | Main content before sidebar; primary action before secondary |

### 1.3 Animation Categories

| Category | Duration | Easing | Purpose |
|---|---|---|---|
| **Micro-interaction** | 80-150ms | Ease-out (fast response) | Button presses, toggles, hover states |
| **Feedback** | 150-300ms | Ease-out | Form validation, notifications, status changes |
| **Navigation** | 200-400ms | Custom ease | Page transitions, route changes, modals |
| **Reveal** | 300-600ms | Custom ease with stagger | Staggered lists, card reveals, content loading |
| **Decorative** | 2000-4000ms (loop) | Linear or ease-in-out | Background glow pulses, ambient effects |
| **Celebration** | 500-2000ms | Bounce/spring | Streak milestones, task completion, achievements |

---

## 2. Animation Parameters

### 2.1 Duration Reference

```css
/* CSS custom properties for animation durations */
--duration-instant: 0ms;
--duration-fast: 80ms;
--duration-normal: 150ms;
--duration-slow: 250ms;
--duration-nav: 300ms;
--duration-reveal: 400ms;
--duration-decorative: 3000ms;
--duration-celebration: 1000ms;
```

### 2.2 Easing Curves

```css
/* Standard easing curves */
--ease-out-fast: cubic-bezier(0.0, 0.0, 0.2, 1);     /* Micro-interactions, exits */
--ease-in-slow:  cubic-bezier(0.4, 0.0, 1.0, 1);     /* Entries that should feel heavier */
--ease-in-out:   cubic-bezier(0.4, 0.0, 0.2, 1);     /* Moderate motion, most UI animations */
--ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);   /* Celebrations, playful elements */
--ease-linear:   cubic-bezier(0.0, 0.0, 1.0, 1);      /* Progress bars, data visualizations */
--ease-emphasis: cubic-bezier(0.2, 0.0, 0.0, 1);      /* Important content arriving */
```

### 2.3 Stagger Patterns

```css
/* Standard stagger delays for list/feed animations */
--stagger-fast: 30ms;    /* Dense lists (20+ items) */
--stagger-normal: 50ms;  /* Standard lists (5-20 items) */
--stagger-slow: 80ms;    /* Sparse content (<5 items) */
--stagger-card: 100ms;   /* Card grids, dashboard tiles */

/* Usage rules */
--stagger-total-max: 500ms;  /* Never stagger beyond 500ms total */
--stagger-direction: 'down'; /* Items enter top-to-bottom, LTR content */
```

### 2.4 Transform Scales

```css
/* Consistent transform values for interaction states */
--scale-press: 0.96;       /* On mousedown / touchstart */
--scale-hover: 1.02;       /* On hover (cards, buttons) */
--scale-hover-icon: 1.05;  /* On hover (icon-only buttons) */
--scale-active-tab: 1.04;  /* Active navigation tab */
--scale-modal-bg: 0.95;    /* Modal background scale on entry (paired with opacity) */
```

### 2.5 Opacity Values

```css
--opacity-hidden: 0;
--opacity-subtle: 0.5;    /* Disabled elements, subtle hints */
--opacity-overlay: 0.6;   /* Modal/drawer backdrops */
--opacity-visible: 1;
```

---

## 3. Page Transition System

### 3.1 Route Change Architecture

> **Implementation:** See MotionArchitecture.md §7 for the production `PageTransition` wrapper that uses  
> centralized presets (`fadeUp`/`fadeOut`) and `useReducedMotionContext()`. The example below is conceptual.

```typescript
// Page transitions use an AnimatePresence wrapper at the layout level
// Route changes: old page exits → new page enters (parallel when possible)

import { AnimatePresence, motion } from 'framer-motion';
import { usePathname } from 'next/navigation';

function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <AnimatePresence mode="wait">
      <motion.main
        key={pathname}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
      >
        {children}
      </motion.main>
    </AnimatePresence>
  );
}
```

### 3.2 Transition Types by Navigation Context

| Navigation Action | Entry Animation | Exit Animation | Duration | Easing |
|---|---|---|---|---|
| **Sidebar link click** | Fade up (y: 12 → 0) | Fade up (y: 0 → -8) | 250ms | ease-in-out |
| **Tab switch** | Crossfade (opacity 0 → 1) | Crossfade (opacity 1 → 0) | 200ms | ease-in-out |
| **Back/forward browser** | Slide from left/right (x: ±30 → 0) | Slide to opposite (x: 0 → ∓30) | 300ms | ease-out-fast |
| **Deep link (external)** | Scale in (0.98 → 1) + fade | Instant | 300ms | ease-in-out |
| **Command palette > navigate** | Instant (no transition) | Instant | 0ms | — |
| **Modal route** | Scale up (0.95 → 1) + fade (0 → 1) | Scale down + fade | 250ms | ease-spring |

### 3.3 Layout Shift Animations

When content changes without a route change (e.g., filter results update, sidebar collapse):

```typescript
// LayoutAnimation for content-area changes
import { LayoutGroup, motion } from 'framer-motion';

function FilterableList() {
  return (
    <LayoutGroup>
      <motion.div layout="position" transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}>
        {items.map(item => (
          <motion.div key={item.id} layout>
            <TaskCard item={item} />
          </motion.div>
        ))}
      </motion.div>
    </LayoutGroup>
  );
}
```

### 3.4 Sidebar & Panel Transitions

| Element | Open | Close | Width | Duration |
|---|---|---|---|---|
| Desktop sidebar | Slide from left | Slide to left | 240px → 64px (collapsed) | 250ms |
| Mobile bottom nav | Instant (already visible) | — | — | — |
| Right panel (detail view) | Slide from right | Slide to right | 400px (overlay on mobile) | 300ms |
| Search overlay | Fade + scale | Fade + scale | Full-screen | 200ms |

---

## 4. Micro-interactions

### 4.1 Button Interactions

```typescript
// Button press states — consistent across ALL button variants
const buttonVariants = {
  rest: { scale: 1 },
  hover: { scale: 1.02, transition: { duration: 0.1, ease: 'easeOut' } },
  tap: { scale: 0.96, transition: { duration: 0.08, ease: 'easeOut' } },
  disabled: { opacity: 0.5, scale: 1 },
};

// Primary button — additional glow effect on hover
const primaryVariants = {
  ...buttonVariants,
  hover: {
    scale: 1.02,
    boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)',
    transition: { duration: 0.15 },
  },
};
```

### 4.2 Card Interactions

```typescript
// Dashboard cards, task cards, module cards
const cardVariants = {
  rest: {
    scale: 1,
    boxShadow: '0 0 0 rgba(99, 102, 241, 0)',
    borderColor: 'rgba(30, 41, 59, 1)',
  },
  hover: {
    scale: 1.01,
    y: -2,
    boxShadow: '0 4px 20px rgba(99, 102, 241, 0.15), 0 0 0 1px rgba(99, 102, 241, 0.2)',
    borderColor: 'rgba(99, 102, 241, 0.3)',
    transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] },
  },
  tap: {
    scale: 0.99,
    transition: { duration: 0.1 },
  },
};
```

### 4.3 Toggle & Switch

```typescript
const toggleVariants = {
  off: { x: 0, backgroundColor: '#334155' },
  on: {
    x: 20,
    backgroundColor: '#6366F1',
    transition: { type: 'spring', stiffness: 500, damping: 30 },
  },
};

const toggleTrack = {
  off: { backgroundColor: '#334155' },
  on: {
    backgroundColor: 'rgba(99, 102, 241, 0.3)',
    transition: { duration: 0.15 },
  },
};
```

### 4.4 Checkbox & Radio

```typescript
const checkboxVariants = {
  unchecked: { scale: 0, opacity: 0 },
  checked: {
    scale: 1,
    opacity: 1,
    transition: { type: 'spring', stiffness: 400, damping: 25 },
  },
};
```

### 4.5 Form Validation

```typescript
// Input error shake — 3 oscillations, fast
const shakeAnimation = {
  x: [0, -4, 4, -4, 4, 0],
  transition: { duration: 0.3, ease: 'easeInOut' },
};

// Success pulse on surrounding field
const successPulse = {
  scale: [1, 1.02, 1],
  borderColor: ['#334155', '#00FFA3', '#334155'],
  transition: { duration: 0.4 },
};
```

### 4.6 Dropdown & Select

```typescript
const dropdownVariants = {
  closed: {
    opacity: 0,
    y: -8,
    scale: 0.98,
    transition: { duration: 0.12, ease: 'easeIn' },
  },
  open: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.18, ease: 'easeOut' },
  },
};
```

### 4.7 Tooltip

```typescript
const tooltipVariants = {
  hidden: { opacity: 0, y: 4, scale: 0.96 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.12, ease: 'easeOut', delay: 0.3 },
  },
};
// Tooltips have a 300ms delay before appearing to prevent flicker
// on fast mouse movements
```

---

## 5. Loading & Progress States

### 5.1 Skeleton Screens

```typescript
// Skeleton uses a pulse-glow animation with accent-primary
const skeletonVariants = {
  initial: { opacity: 0.6 },
  animate: {
    opacity: [0.6, 0.9, 0.6],
    transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
  },
};

// Skeleton layout mirrors the content it replaces
// Task list: 5 skeleton rows, each 72px tall with title/date placeholders
// Dashboard grid: Skeleton cards matching the grid layout
// Chat: Skeleton message bubbles, alternating left/right
```

| Content Type | Skeleton Pattern | Elements |
|---|---|---|
| Task list | 5 rows, 72px each | Title bar (60% width), date bar (30% width), priority dot |
| Dashboard | 4 cards in 2×2 grid | Header bar, metric circle, 2 data lines |
| Habit grid | 7×12 grid cells | 84 cells, 32×32px each, with pulse delay stagger |
| Chat message | 3 alternating bubbles | Avatar circle, name bar, message body (40-70% width) |
| Data table | 8 rows × 6 columns | Varying column widths matching content |
| Briefing page | Full-page skeleton | Title, 3 section headers, paragraph blocks (80% → 60% → 90% width) |

### 5.2 Glow Pulse Animation (Decorative)

```css
/* Background glow used on cards and decorative elements during loading */
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 8px rgba(99, 102, 241, 0.05); }
  50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.15); }
}

.glow-pulse {
  animation: glow-pulse 3s ease-in-out infinite;
}
```

### 5.3 AI Generation Loading

```typescript
// While ARIA generates content (briefing, review, analysis)
const aiGenerationVariants = {
  active: {
    opacity: [0.7, 1, 0.7],
    scale: [1, 1.01, 1],
    transition: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
  },
};

// Progress steps shown during generation:
// 1. "Gathering your data..." (2s)
// 2. "Analyzing patterns..." (2-5s)
// 3. "Generating insights..." (2-5s)
// 4. "Formatting your briefing..." (1-2s)
// Each step has a smooth progress bar with accent-primary gradient
```

### 5.4 Progress Indicators

| Type | Visual | Animation | Usage |
|---|---|---|---|
| **Linear determinate** | Gradient bar, 4px height | Width transitions smoothly (`transition: width 300ms ease-out`) | Form progress, file upload |
| **Linear indeterminate** | Gradient bar with moving highlight | Highlight sweeps L→R over 1.5s, repeats | AI generation, sync |
| **Circular determinate** | Ring with stroke-dashoffset | Rotates with arc growth | Task completion %, quiz score |
| **Circular indeterminate** | Spinning ring with gradient | Continuous 360° rotation, 1s/rev | Loading button, page load |
| **Dot steps** | 3-5 dots, accent-primary | Sequential scale + opacity, staggered 200ms | Wizard/multi-step forms |
| **Skeleton pulse** | Background shimmer | `background-position` slide, 1.5s cycle | Content placeholders |

### 5.5 Page Load Sequence

```typescript
// Page load animation sequence (total: 500ms max)
// 1. Skeleton appears immediately (0ms) — gives user instant feedback
// 2. API response received — skeleton fades out (200ms)
// 3. Content fades in with stagger (300ms total)

const pageLoadSequence = {
  skeleton: { opacity: [0, 1], transition: { duration: 0.1 } },
  content: {
    opacity: [0, 1],
    y: [8, 0],
    transition: { duration: 0.25, delay: 0.05, ease: 'easeOut' },
  },
};
```

---

## 6. Notification & Feedback Animations

### 6.1 Toast / Snackbar

```typescript
// Toast — slides from top-right, auto-dismisses after 4s
const toastVariants = {
  hidden: { opacity: 0, x: 50, scale: 0.95 },
  visible: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 300, damping: 25 },
  },
  exit: {
    opacity: 0,
    x: 50,
    scale: 0.95,
    transition: { duration: 0.15, ease: 'easeIn' },
  },
};

// Snackbar — slides from bottom-center (mobile) or bottom-left (desktop)
const snackbarVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 350, damping: 28 },
  },
  exit: {
    opacity: 0,
    y: 20,
    transition: { duration: 0.15 },
  },
};
```

### 6.2 Modal / Dialog

```typescript
// Modal — scale + fade with backdrop
const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 0.6, transition: { duration: 0.15 } },
  exit: { opacity: 0, transition: { duration: 0.1 } },
};

const modalVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 400, damping: 30 },
  },
  exit: {
    opacity: 0,
    scale: 0.97,
    y: -10,
    transition: { duration: 0.15, ease: 'easeIn' },
  },
};
```

### 6.3 Dropdown / Popover / Menu

```typescript
// Positioning-aware: grows from the trigger element's attachment point
const popoverVariants = {
  hidden: { opacity: 0, scale: 0.96, y: -4 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.15, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    scale: 0.96,
    y: -4,
    transition: { duration: 0.1, ease: 'easeIn' },
  },
};
```

### 6.4 Celebration Effects

```typescript
// Used for: habit streak milestones, goal completion, 100 tasks completed
// Confetti particles — 50-80 small squares, neon accent colors
// Central burst — expanding ring from completion point
// Banner text — scale in with spring, then settle

const celebrationBanner = {
  hidden: { scale: 0, opacity: 0, rotate: -5 },
  visible: {
    scale: 1,
    opacity: 1,
    rotate: 0,
    transition: { type: 'spring', stiffness: 200, damping: 12 },
  },
};

// Confetti particle
const confettiParticle = (i: number) => ({
  hidden: { opacity: 0, y: 0, x: 0, rotate: 0 },
  visible: {
    opacity: [0, 1, 1, 0],
    y: [-20 - Math.random() * 200],
    x: [-40 + Math.random() * 80],
    rotate: [0, 360 * (Math.random() > 0.5 ? 1 : -1)],
    transition: {
      duration: 1 + Math.random() * 1.5,
      delay: i * 0.02,
      ease: 'easeOut',
    },
  },
});
```

---

## 7. List & Feed Animations

### 7.1 Staggered Reveals

```typescript
// Container — orchestrates the stagger
const listContainerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.05,  // 50ms between each child
      delayChildren: 0.1,     // 100ms initial delay before stagger begins
    },
  },
};

// Child item — individual entry animation
const listItemVariants = {
  hidden: { opacity: 0, y: 12, scale: 0.98 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.25, ease: [0.4, 0, 0.2, 1] },
  },
};
```

### 7.2 Item Add Animation

```typescript
// When a new item is added to a list (e.g., new task created)
const itemAddVariants = {
  initial: { height: 0, opacity: 0, scaleY: 0 },
  animate: {
    height: 'auto',
    opacity: 1,
    scaleY: 1,
    transition: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }, // spring-like
  },
};
```

### 7.3 Item Remove/Archive Animation

```typescript
// When an item is removed — collapses and fades out
const itemRemoveVariants = {
  exit: {
    opacity: 0,
    height: 0,
    marginBottom: 0,
    paddingTop: 0,
    paddingBottom: 0,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};
```

### 7.4 Reorder Animation

```typescript
// Drag-to-reorder in task list / habit list
// Uses Framer Motion's Reorder component internally

const reorderItem = {
  whileDrag: {
    scale: 1.03,
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
    zIndex: 100,
    cursor: 'grabbing',
    transition: { duration: 0.1 },
  },
  whileHover: { cursor: 'grab' },
};
```

### 7.5 Empty State Transition

```typescript
// When list transitions from empty → has items (or vice versa)
const emptyStateVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: { duration: 0.15, ease: 'easeIn' },
  },
};
```

---

## 8. Gesture-Based Animations

### 8.1 Mobile Swipe Actions

```typescript
// Task item swipe-to-complete
// Swipe right: reveals green checkmark, completes on >40% threshold
// Swipe left: reveals delete/archive, performs action on >60% threshold

const swipeableItem = {
  whileDrag: { scale: 1.02 },
  drag: 'x',
  dragConstraints: { left: -100, right: 100 },
  dragElastic: 0.2,
  onDragEnd: (_, info) => {
    if (info.offset.x > 100) completeTask();
    if (info.offset.x < -100) archiveTask();
  },
};

// Action hint icons revealed during swipe
const hintIconVariants = (direction: 'left' | 'right', progress: number) => ({
  opacity: progress,
  scale: 0.5 + progress * 0.5,
  x: direction === 'right' ? -20 + progress * 20 : 20 - progress * 20,
});
```

### 8.2 Pull-to-Refresh

```typescript
// Pull-to-refresh for lists (tasks, habits, opportunities)
const pullToRefresh = {
  refreshThreshold: 80,  // px — triggers refresh
  maxPullDistance: 120,  // px — limit
  spinnerVariants: {
    idle: { rotate: 0 },
    pulling: (progress: number) => ({
      rotate: progress * 180,
      opacity: Math.min(progress, 1),
    }),
    refreshing: {
      rotate: 360,
      transition: { duration: 1, repeat: Infinity, ease: 'linear' },
    },
  },
};
```

### 8.3 Bottom Sheet

```typescript
// Mobile bottom sheet (for filters, task details, quick actions)
const sheetVariants = {
  hidden: { y: '100%' },
  visible: {
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 30 },
  },
  exit: {
    y: '100%',
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

// Drag handle at top of sheet
const sheetDrag = {
  drag: 'y',
  dragConstraints: { top: 0, bottom: 0 },
  dragElastic: { top: 0, bottom: 0.5 },
  onDragEnd: (_, info) => {
    if (info.offset.y > 100) closeSheet();
  },
};
```

### 8.4 Long-Press Context Menu

```typescript
// Long press (500ms) on items reveals context menu
const longPressVariants = {
  pressed: {
    scale: 0.97,
    backgroundColor: 'rgba(99, 102, 241, 0.08)',
    transition: { duration: 0.1 },
  },
};
```

---

## 9. Data Visualization Animations

### 9.1 Chart Entry Animations

```typescript
// Bar/column charts: bars grow from bottom with stagger
const barVariants = {
  hidden: { scaleY: 0, transformOrigin: 'bottom' },
  visible: (i: number) => ({
    scaleY: 1,
    transition: {
      duration: 0.4,
      delay: i * 0.03,
      ease: [0.4, 0, 0.2, 1],
    },
  }),
};

// Line charts: path drawn from left to right
const linePathVariants = {
  hidden: { pathLength: 0 },
  visible: {
    pathLength: 1,
    transition: { duration: 0.8, ease: 'easeInOut' },
  },
};

// Pie/donut charts: arc rotates into place
const arcVariants = {
  hidden: { rotate: -90, opacity: 0 },
  visible: (i: number) => ({
    rotate: 0,
    opacity: 1,
    transition: {
      duration: 0.5,
      delay: i * 0.05,
      ease: [0.4, 0, 0.2, 1],
    },
  }),
};
```

### 9.2 Stat Counter Animation

```typescript
// Animated number counting up/down
// Uses Framer Motion's useMotionValue + useTransform
const countVariants = {
  initial: { value: 0 },
  animate: { value: targetValue, transition: { duration: 0.8, ease: 'easeOut' } },
};
```

### 9.3 Streak Calendar Animation

```typescript
// Habit streak days: cells fill with neon gradient, staggered by row
const streakCellVariants = {
  hidden: { scale: 0, opacity: 0, backgroundColor: '#13151A' },
  visible: (i: number) => ({
    scale: 1,
    opacity: 1,
    backgroundColor: '#00FFA3',
    transition: {
      duration: 0.3,
      delay: i * 0.02,
      ease: [0.4, 0, 0.2, 1],
    },
  }),
  missed: { backgroundColor: '#EF4444', scale: [1, 1.1, 1] },
};
```

---

## 10. Performance Budget

### 10.1 Motion Performance Targets

| Metric | Target | Enforcement |
|---|---|---|
| JS execution per animation frame | ≤ 5ms | Performance profiling in CI |
| Frame rate | 60fps (16.7ms per frame) | DevTools FPS meter, `requestAnimationFrame` checks |
| Animation init latency | ≤ 50ms from interaction to first frame | Interaction readiness checks |
| Layout thrashing events | 0 per animation sequence | Layout boundary checks in review |
| GPU memory for animations | < 50MB | Memory profiling |
| CSS `will-change` declarations | < 10 per page | Lint rule to flag overuse |

### 10.2 Optimization Rules

| Rule | Rationale | Implementation |
|---|---|---|
| Animate only `opacity` and `transform` | These are composited on GPU; no layout/paint triggers | Lint rule: no `width`, `height`, `top`, `left` in `style` props for animations |
| Prefer CSS animations for decorative loops | No JavaScript overhead for continuous animations | Glow pulse, shimmer: CSS `@keyframes`. Springs, stagger: Framer Motion |
| Use `will-change` sparingly | Overuse consumes GPU memory | Only on actively animating elements; remove after animation completes |
| Avoid animating large node trees | Not applicable | Split large lists into virtualized windows, animate visible viewport only |
| Batch DOM reads/writes | Prevents layout thrashing | Use Framer Motion's batched updates; avoid manual `getBoundingClientRect` during animations |
| Use `transform` for position changes | No layout recalculations | Instead of `left: X`, use `translateX(X)` |

### 10.3 Motion Provider (Production Architecture)

See **MotionArchitecture.md §6** for the full implementation. The production `MotionProvider` wraps `MotionConfig` with:

1. **Device tier detection** — `navigator.deviceMemory` + `hardwareConcurrency`
2. **OS preference + device tier resolution** — combines both into `Full` / `Reduced` / `Minimal` / `Accessibility`
3. **Context-based API** — `useReducedMotionContext()` and `useMotionContext()` available to all components
4. **No `features` array** — Framer Motion's tree-shaking exports `motion` features by default

```typescript
// Simplified reference — see MotionArchitecture.md §6 for complete code
import { MotionConfig } from 'framer-motion';

function MotionProvider({ children }) {
  // ... tier detection, preference resolution ...
  return (
    <MotionConfig reducedMotion={prefersReduced ? 'always' : 'never'}>
      {children}
    </MotionConfig>
  );
}
```

### 10.4 Device Performance Tiers

| Tier | Devices | Animation Complexity | Notes |
|---|---|---|---|
| **Full** | Desktop (M1+, modern GPUs) | All animations, springs, glows, confetti, parallax | No limits |
| **Reduced** | Mid-range mobile, older desktop | No glow, no parallax, linear transitions instead of springs | `@media (prefers-reduced-motion: no-preference)` + battery check |
| **Minimal** | Budget mobile, low-end devices | Crossfade only, no decorative, 200ms max | `navigator.hardwareConcurrency < 4` or low battery |
| **Accessibility** | User preference / assistive technology | 0ms transitions, instant state changes, no decorative | `prefers-reduced-motion: reduce` |

---

## 11. Framer Motion Implementation Patterns

### 11.1 Standard AnimatedComponent Wrapper

```typescript
// Reusable animated wrapper for consistent entry animations
import { motion, type Variants } from 'framer-motion';

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.25, ease: [0.4, 0, 0.2, 1] },
  },
};

function AnimatedSection({ children, className }: Props) {
  return (
    <motion.section
      variants={fadeUp}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {children}
    </motion.section>
  );
}
```

### 11.2 Preset Animation Variants (Conceptual Reference)

> **The definitive preset library lives in `animation-presets.ts` defined by MotionArchitecture.md §4 (V1-V35).**  
> The examples below are conceptual — always import from the centralized preset module, not from this doc.

```typescript
// Import from centralized presets (MotionArchitecture.md §4)
import { fadeUp, fadeOut, buttonPress, cardHover, staggerContainer, staggerItem } from '@/packages/ui/animation-presets';
```

### 11.3 AnimatePresence Patterns

```typescript
// Route transitions (layout level)
<AnimatePresence mode="wait">
  <motion.div key={pathname} { ...fadeUp }>
    <Component />
  </motion.div>
</AnimatePresence>

// List add/remove
<AnimatePresence>
  {items.map(item => (
    <motion.div
      key={item.id}
      layout
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
    >
      <ItemComponent data={item} />
    </motion.div>
  ))}
</AnimatePresence>

// Modal
<AnimatePresence>
  {isOpen && (
    <motion.div key="modal-backdrop" { ...backdropVariants }>
      <motion.div key="modal-content" { ...modalVariants }>
        {children}
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

### 11.4 Shared Layout Animations (LayoutGroup)

```typescript
// Use layout animations when content reflows (filtering, sorting, collapsing)
// Wrap in LayoutGroup to coordinate multiple layout animations

import { LayoutGroup, motion } from 'framer-motion';

<LayoutGroup id="task-list">
  {filteredTasks.map(task => (
    <motion.div key={task.id} layout transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}>
      <TaskCard task={task} />
    </motion.div>
  ))}
</LayoutGroup>
```

### 11.5 Path / SVG Animations

```typescript
// Logo reveal, chart lines, decorative SVG paths
<motion.path
  d="M 10 80 Q 95 10 180 80"
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 1.5, ease: 'easeInOut' }}
/>
```

---

## 12. Reduced Motion & Fallback Strategy

### 12.1 System-Level Detection

> **Production implementation:** Use `useReducedMotionContext()` from `MotionProvider` (MotionArchitecture.md §6)  
> which combines OS preference + device tier detection. The Framer Motion `useReducedMotion()` hook below is  
> available but our custom context provides richer tier information (`Full`/`Reduced`/`Minimal`/`Accessibility`).

```typescript
// Production: use MotionProvider context (MotionArchitecture.md §6)
import { useReducedMotionContext } from '@/packages/ui/MotionProvider';
const isReduced = useReducedMotionContext();

// Development / fallback: Framer Motion hook
import { useReducedMotion } from 'framer-motion';
const shouldReduceMotion = useReducedMotion();
```

### 12.2 Application Motion Settings

| Setting | Effect on Animations | Code |
|---|---|---|
| **Full** (default) | All animations enabled | No restrictions |
| **Reduced** | No decorative animations. Micro-interactions: 50% duration. Page transitions: crossfade only (200ms). No stagger. No parallax. No glow. | `(prefers-reduced-motion: reduce)` + user setting override |
| **Minimal** | No animations except: loading spinners (required for function), progress bars. All state changes instant. | User explicitly chooses this in Settings > Accessibility |

### 12.3 Animation Replacement Map

| Animation | Full | Reduced | Minimal |
|---|---|---|---|
| Page transition | Fade + slide, 300ms | Crossfade, 200ms | Instant |
| Staggered list | 50ms stagger, y: 12 | No stagger, opacity fade, 150ms | Instant |
| Card hover | Scale 1.01, y: -2, glow | No motion | No motion |
| Button press | Scale 0.96, 80ms | Opacity 0.8, 50ms | Instant |
| Toggle switch | Spring animation, 300ms | Opacity crossfade, 150ms | Instant state |
| Toast slide-in | Spring from right, 300ms | Fade in, 200ms | Instant |
| Modal | Spring scale + fade, 250ms | Fade only, 150ms | Instant |
| Glow pulse | 3s infinite loop | No animation | No animation |
| Confetti | 1.5s celebration | No celebration | No celebration |
| Skeleton pulse | 1.5s shimmer | Static skeleton (no pulse) | Static skeleton (no pulse) |
| Progress bar | Smooth width transition | Smooth width transition | Smooth width transition |
| Loading spinner | 1s rotation loop | 1s rotation loop | Static icon |

### 12.4 Testing Reduced Motion

```typescript
// DevTools: simulate reduced motion
// Chrome: Rendering > Emulate CSS media feature prefers-reduced-motion
// Firefox: about:config > ui.prefersReducedMotion = 1

// Cypress test for reduced motion
cy.visit('/', {
  onBeforeLoad(win) {
    cy.stub(win, 'matchMedia')
      .withArgs('(prefers-reduced-motion: reduce)')
      .returns({ matches: true });
  },
});
// Verify no animation-related layout shifts
// Verify all functionality is preserved
```

---

## 13. Motion Dev Tools & Debugging

### 13.1 Development Tools

> For the complete audit script and CI checks, see **MotionArchitecture.md §13** (Motion Dev Tooling).

| Tool | Use Case | Setup |
|---|---|---|
| **Framer Motion DevTools** | Visualize animation variants, timeline, FPS | Chrome extension |
| **Chrome Performance tab** | Frame rate analysis, JS cost of animations | DevTools > Performance |
| **Chrome Rendering tab** | Paint flashing, layer borders, FPS meter | DevTools > Rendering |
| **React DevTools Profiler** | Component render cost during animations | DevTools > Profiler |
| **Motion Audit Script** | Detect hardcoded durations, missing presets, missing reduced-motion | `node scripts/audit-motion.mjs` |

### 13.2 Debugging Commands

```typescript
// Enable Framer Motion debug logging
window.__MOTION_DEV_TOOLS__ = true;

// Profile a specific animation
console.profile('TaskListEnter');
// Trigger animation
console.profileEnd();

// Check if element is composited
// DevTools > Rendering > Layer borders
// Composited layers show orange/blue borders
```

### 13.3 Common Animation Issues

| Issue | Symptom | Cause | Fix |
|---|---|---|---|
| Janky animation | Visible stutter, dropped frames | Animating `width`/`height`/`top`/`left` | Switch to `scaleX`/`scaleY`/`translateX`/`translateY` |
| Element flashes at start | `opacity: 1` before animation starts | Missing `initial` prop | Add `initial={{ opacity: 0 }}` |
| Animation on wrong element | Motion applied to parent instead of child | Incorrect variant targeting | Verify `variants` prop on correct element |
| Infinite loop | Component re-renders forever | Animation triggers state update → re-render → animation | Use `useMemo` for variants, remove animation triggers from dependency arrays |
| Layout shift after animation | Content jumps when animation ends | No `layout` prop on animated element | Add `layout` prop or specify final dimensions |
| Reduced motion not working | Animations still play | `useReducedMotion()` not implemented in component | Add hook and conditionally return static variants |

### 13.4 Performance Profiling Checklist

```markdown
- [ ] All animations use `opacity` and `transform` only
- [ ] No layout thrashing (batched read/write operations)
- [ ] GPU compositing confirmed (DevTools layer borders)
- [ ] JS execution per frame ≤ 5ms
- [ ] No `will-change` on non-animating elements
- [ ] Reduced motion degrades gracefully
- [ ] Animations don't re-trigger on parent re-render
- [ ] Virtualized lists don't animate off-screen items
- [ ] Mobile battery impact considered (no continuous animations when not visible)
- [ ] IntersectionObserver pauses animations when element is off-screen
```

### 13.5 Animation Documentation Pattern

```typescript
// Every animated component should document its motion behavior:
/**
 * @motion
 * - Entry: fadeUp, 250ms, staggered if in list context
 * - Hover: scale 1.01 + y -2 + glow shadow, 200ms
 * - Tap: scale 0.99, 100ms
 * - Exit: fadeOut, 150ms
 * - Reduced motion: all animations replaced with instant transitions
 * - Layout: uses layout animation for position changes
 */
```

---

## Appendix A: Motion System Cheat Sheet

| What | Pattern | Duration | Easing |
|---|---|---|---|
| Button press | scale → 0.96 | 80ms | ease-out-fast |
| Card hover | scale 1.01, y -2 | 200ms | ease-in-out |
| Modal entry | scale 0.95 → 1 + fade | 250ms | spring |
| Toast in | x: 50 → 0 + fade | 300ms | spring |
| Page change | y: 12 → 0 + fade | 250ms | ease-in-out |
| List stagger | 50ms delay per item | 250ms/item | ease-in-out |
| Toggle on | spring x: 0 → 20 | 300ms | spring |
| Skeleton pulse | opacity 0.6 → 0.9 | 1.5s loop | ease-in-out |
| Glow pulse | box-shadow intensity | 3s loop | ease-in-out |
| Streak fill | scale 0 → 1 | 300ms | ease-in-out |
| Error shake | x oscillate ±4 | 300ms | ease-in-out |
| Celebration | spring scale + confetti | 1-2s | spring |

---

> **Maintenance:** This document is updated per release cycle. New animated components must reference animation variants from the presets library. Deviations require motion design review.
>
> **Related documents:** `docs/design/Accessibility.md` (reduced motion), `docs/design/10_DesignSystem.md` (component tokens), `docs/design/Branding.md` (brand motion personality).
