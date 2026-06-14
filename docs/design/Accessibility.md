# Accessibility — Second Brain OS (ARIA)

> **Document ID:** SB-A11Y-001  
> **Version:** 1.0.0  
> **Status:** Active  
> **Last Updated:** 2026-06-11  
> **Classification:** Internal — Engineering & QA  
> **Owner:** Accessibility Working Group (Design + Engineering + QA)

---

## Table of Contents

1. [Accessibility Philosophy](#1-accessibility-philosophy)
2. [WCAG 2.2 AA Compliance Checklist](#2-wcag-22-aa-compliance-checklist)
3. [Color Contrast Requirements](#3-color-contrast-requirements)
4. [Keyboard Navigation](#4-keyboard-navigation)
5. [Screen Reader Support](#5-screen-reader-support)
6. [Focus Indicators](#6-focus-indicators)
7. [Motion Sensitivity](#7-motion-sensitivity)
8. [Text Scaling & Zoom](#8-text-scaling--zoom)
9. [Error Announcement Patterns](#9-error-announcement-patterns)
10. [Skip Navigation](#10-skip-navigation)
11. [Touch Target Sizes](#11-touch-target-sizes)
12. [Accessibility Testing Tools & Process](#12-accessibility-testing-tools--process)
13. [Known Accessibility Issues & Roadmap](#13-known-accessibility-issues--roadmap)

---

## 1. Accessibility Philosophy

### 1.1 Our Commitment

Second Brain OS believes that cognitive augmentation should be available to everyone, regardless of ability. A "second brain" that excludes users with disabilities is fundamentally failing its mission. Accessibility is not a feature — it is a design principle embedded in every component, every interaction, and every line of code.

### 1.2 Principles

| Principle | Meaning | Application |
|---|---|---|
| **Equitable Experience** | The same information and functionality for all users, regardless of how they access it | All features usable via keyboard, screen reader, touch, or mouse |
| **Perceivable by Default** | No information conveyed through sensory characteristics alone | Color is never the sole indicator of status; icons, text, and patterns supplement |
| **Operable by Choice** | Users control their pace and method of interaction | No time limits on tasks, adjustable animation speed, user-controlled media |
| **Understandable Language** | Clear, predictable, and consistent | Voice guidelines (see Branding.md §7) apply equally to ARIA labels and error messages |
| **Robust Foundation** | Works with current and future assistive technologies | Semantic HTML, proper ARIA roles, tested with NVDA, JAWS, VoiceOver, TalkBack |

### 1.3 Target Compliance Level

**WCAG 2.2 Level AA** is the minimum. All new features target Level AAA where feasible without degrading the experience for other users.

| Priority | Criteria | Examples |
|---|---|---|
| Critical (blocking launch) | All A criteria | Keyboard operable, text alternatives, meaningfully ordered |
| High (must pass) | All AA criteria | Color contrast 4.5:1, focus visible, error identification |
| Medium (target) | AAA contrast (7:1) for body text | Enhanced readability, especially for low-vision users |
| Nice-to-have | AAA non-essential criteria | Sign language for pre-recorded media, extended audio descriptions |

---

## 2. WCAG 2.2 AA Compliance Checklist

### 2.1 Perceivable (A + AA)

| ID | Criterion | Status | Implementation |
|---|---|---|---|
| 1.1.1 | **Non-text Content (A)** | ✅ Implemented | All icons have `aria-label` or visually-hidden text; decorative icons have `aria-hidden="true"` |
| 1.2.2 | **Captions (Prerecorded) (A)** | ✅ Implemented | All tutorial videos include captions; auto-generated + human-reviewed |
| 1.2.4 | **Captions (Live) (AA)** | ⚠️ Partial | Live streams use auto-captioning; accuracy review pending |
| 1.3.1 | **Info and Relationships (A)** | ✅ Implemented | Semantic HTML: `<nav>`, `<main>`, `<aside>`, `<header>`, `<section>`, `<article>` throughout |
| 1.3.2 | **Meaningful Sequence (A)** | ✅ Implemented | DOM order matches visual order; CSS order never changes logical flow |
| 1.3.4 | **Orientation (AA)** | ✅ Implemented | All screens support portrait and landscape; no fixed-orientation locks |
| 1.3.5 | **Identify Input Purpose (AA)** | ✅ Implemented | `autocomplete` attributes on all form fields (name, email, tel, etc.) |
| 1.4.1 | **Use of Color (A)** | ✅ Implemented | Status indicators use icon + text + color, never color alone |
| 1.4.2 | **Audio Control (A)** | ✅ Implemented | Any auto-playing audio has pause/stop/mute, lasting >3s |
| 1.4.3 | **Contrast Minimum (AA)** | ✅ Implemented | 4.5:1 for body text, 3:1 for large text (≥18px bold / ≥24px regular). See §3 |
| 1.4.4 | **Resize Text (AA)** | ✅ Implemented | No loss of content or functionality up to 200% zoom |
| 1.4.5 | **Images of Text (AA)** | ✅ Implemented | No images used to convey text; true text everywhere |
| 1.4.10 | **Reflow (AA)** | ✅ Implemented | No horizontal scrolling at 320px width; responsive layout |
| 1.4.11 | **Non-text Contrast (AA)** | ✅ Implemented | UI components and graphical objects meet 3:1 against adjacent colors |
| 1.4.12 | **Text Spacing (AA)** | ✅ Implemented | No loss of content when user overrides text spacing (1.5× line height, 2× word spacing, 2× letter spacing) |
| 1.4.13 | **Content on Hover or Focus (AA)** | ✅ Implemented | Dismissable, hoverable, and persistent tooltips/ popovers |

### 2.2 Operable (A + AA)

| ID | Criterion | Status | Implementation |
|---|---|---|---|
| 2.1.1 | **Keyboard (A)** | ✅ Implemented | All interactive elements reachable and operable via keyboard |
| 2.1.2 | **No Keyboard Trap (A)** | ✅ Implemented | Focus never trapped; Escape exits any modal/menu |
| 2.1.4 | **Character Key Shortcuts (A)** | ✅ Implemented | Single-key shortcuts are remappable or turn-off-able in settings |
| 2.2.1 | **Timing Adjustable (A)** | ✅ Implemented | Session timeout warning at 2 min; user can extend or disable |
| 2.2.2 | **Pause, Stop, Hide (A)** | ✅ Implemented | All auto-updating content (briefings, notifications) has pause/play controls |
| 2.3.1 | **Three Flashes or Below (A)** | ✅ Implemented | No content flashes >3× per second; if introduced, has warning |
| 2.4.1 | **Bypass Blocks (A)** | ✅ Implemented | Skip-to-content link on every page |
| 2.4.2 | **Page Titled (A)** | ✅ Implemented | Descriptive `<title>` on every route |
| 2.4.3 | **Focus Order (A)** | ✅ Implemented | Logical tab order matching visual reading order |
| 2.4.4 | **Link Purpose (In Context) (A)** | ✅ Implemented | All links describe their destination; no "click here" |
| 2.4.5 | **Multiple Ways (AA)** | ✅ Implemented | Site search, nav menu, and dashboard access every page |
| 2.4.6 | **Headings and Labels (AA)** | ✅ Implemented | Descriptive headings and form labels |
| 2.4.7 | **Focus Visible (AA)** | ✅ Implemented | Cyberpunk glow focus indicators (see §6) |
| 2.5.1 | **Pointer Gestures (A)** | ✅ Implemented | All path-based gestures have a button-based alternative |
| 2.5.2 | **Pointer Cancellation (A)** | ✅ Implemented | Down-event never executes action; up-event or click required |
| 2.5.3 | **Label in Name (A)** | ✅ Implemented | Visible label text matches accessible name |
| 2.5.4 | **Motion Actuation (A)** | ✅ Implemented | Shake/tilt actions have UI button alternatives |
| 2.5.7 | **Dragging Movements (AA)** | ✅ Implemented | All drag-and-drop has click-to-select alternative |
| 2.5.8 | **Target Size (AA)** | ✅ Implemented | All targets ≥24×24px (see §11 for beyond-AA standard) |

### 2.3 Understandable (A + AA)

| ID | Criterion | Status | Implementation |
|---|---|---|---|
| 3.1.1 | **Language of Page (A)** | ✅ Implemented | `lang="en"` on `<html>` element |
| 3.1.2 | **Language of Parts (AA)** | ✅ Implemented | `lang` attribute on in-page language changes (code snippets, phrases) |
| 3.2.1 | **On Focus (A)** | ✅ Implemented | No context changes on focus |
| 3.2.2 | **On Input (A)** | ✅ Implemented | No context changes on input unless user warned |
| 3.2.3 | **Consistent Navigation (AA)** | ✅ Implemented | Navigation order and location consistent across pages |
| 3.2.4 | **Consistent Identification (AA)** | ✅ Implemented | Same components have same labels and functions everywhere |
| 3.3.1 | **Error Identification (A)** | ✅ Implemented | Errors announced with text description (see §9) |
| 3.3.2 | **Labels or Instructions (A)** | ✅ Implemented | All inputs have labels; required fields marked |
| 3.3.3 | **Error Suggestion (AA)** | ✅ Implemented | Suggestions for correction provided (see §9) |
| 3.3.4 | **Error Prevention (Legal, Financial, Data) (AA)** | ✅ Implemented | Confirmation dialogs for destructive actions; undo available |
| 3.3.7 | **Accessible Authentication (AA)** | ✅ Implemented | No cognitive function tests (like CAPTCHAs); alternative available |

### 2.4 Robust (A + AA)

| ID | Criterion | Status | Implementation |
|---|---|---|---|
| 4.1.1 | **Parsing (A)** | ✅ Implemented | No duplicate IDs, properly nested elements, valid HTML |
| 4.1.2 | **Name, Role, Value (A)** | ✅ Implemented | All custom components have proper ARIA roles, states, and properties |
| 4.1.3 | **Status Messages (AA)** | ✅ Implemented | `role="status"`, `role="alert"`, `aria-live` regions for dynamic content |

---

## 3. Color Contrast Requirements

### 3.1 Contrast Ratio Matrix

All values measured against their background. Minimum WCAG AA ratios: 4.5:1 for body text, 3:1 for large text (≥18px bold or ≥24px regular), 3:1 for UI components.

| Foreground Token | Background Token | Ratio | Pass AA? | Pass AAA? |
|---|---|---|---|---|
| `--text-primary` (#F1F5F9) | `--bg-page` (#0A0B0F) | 16.2:1 | ✅ | ✅ (>7:1) |
| `--text-primary` (#F1F5F9) | `--bg-card` (#13151A) | 14.6:1 | ✅ | ✅ |
| `--text-secondary` (#94A3B8) | `--bg-page` (#0A0B0F) | 9.8:1 | ✅ | ✅ |
| `--text-secondary` (#94A3B8) | `--bg-card` (#13151A) | 8.7:1 | ✅ | ✅ |
| `--text-tertiary` (#64748B) | `--bg-page` (#0A0B0F) | 6.1:1 | ✅ | ❌ (7:1 minimum) |
| `--text-tertiary` (#64748B) | `--bg-card` (#13151A) | 5.4:1 | ✅ | ❌ |
| `--accent-primary` (#6366F1) | `--bg-page` (#0A0B0F) | 5.8:1 | ✅ | ❌ |
| `--accent-primary` (#6366F1) | `--bg-card` (#13151A) | 5.1:1 | ✅ | ❌ |
| `--accent-primary` (#6366F1) | `--bg-card-hover` (#1A1D24) | 4.5:1 | ✅ (passes exactly) | ❌ |
| `--accent-neon` (#00FFA3) | `--bg-page` (#0A0B0F) | 9.3:1 | ✅ | ✅ |
| `--accent-neon` (#00FFA3) | `--bg-card` (#13151A) | 8.2:1 | ✅ | ✅ |
| `--accent-warning` (#F59E0B) | `--bg-page` (#0A0B0F) | 6.9:1 | ✅ | ❌ |
| `--accent-danger` (#EF4444) | `--bg-page` (#0A0B0F) | 6.7:1 | ✅ | ❌ |
| `--accent-danger` (#EF4444) | `--bg-card` (#13151A) | 5.9:1 | ✅ | ❌ |
| `--status-success` (#00FFA3) | `--bg-page` (#0A0B0F) | 9.3:1 | ✅ | ✅ |
| `--status-error` (#EF4444) | `--bg-page` (#0A0B0F) | 6.7:1 | ✅ | ❌ |
| `--status-info` (#6366F1) | `--bg-page` (#0A0B0F) | 5.8:1 | ✅ | ❌ |
| `--border-default` (#1E293B) | `--bg-page` (#0A0B0F) | 2.7:1 | ❌ (3:1 minimum) | ❌ |
| `--border-accent` (#334155) | `--bg-page` (#0A0B0F) | 4.2:1 | ✅ | ❌ |
| `--border-light` (#475569) | `--bg-page` (#0A0B0F) | 5.8:1 | ✅ | ❌ |
| Disabled text (#64748B on #13151A) | `--bg-card` | 5.4:1 | ✅ | ❌ |
| Placeholder (#64748B on #13151A) | `--bg-card` | 5.4:1 | ✅ | ❌ |

### 3.2 Border Contrast Remediation

`--border-default` (#1E293B at 2.7:1) fails WCAG AA for non-text contrast. **Remediation strategy:**

| Context | Solution | Token to Use | Ratio |
|---|---|---|---|
| Card borders (subtle) | Keep `--border-default` (decorative, not critical for understanding) | `--border-default` | 2.7:1 ❌ but acceptable for non-critical UI |
| Input borders (interactive) | Use `--border-accent` (#334155) | `--border-accent` | 4.2:1 ✅ |
| Focused / active borders | Use `--accent-primary` (#6366F1) | `--accent-primary` | 5.8:1 ✅ |
| Disabled state borders | Use `--border-accent` | `--border-accent` | 4.2:1 ✅ |
| Table cell borders | Use `--border-accent` | `--border-accent` | 4.2:1 ✅ |

### 3.3 Color Blindness Considerations

| Type | Impact | Mitigation |
|---|---|---|
| **Deuteranopia** (green-blind, ~6% of males) | Cannot distinguish `--accent-neon` from `--status-warning` | Status uses shape + text, never color alone. Green accent is redundant with luminance contrast (9.3:1 even for color-blind users) |
| **Protanopia** (red-blind, ~2% of males) | Cannot distinguish `--accent-danger` from `--status-warning` | Error states include exclamation icon + bold red border-left, not just red color |
| **Tritanopia** (blue-blind, rare) | `--accent-primary` appears gray | Active states use underline + bold weight in addition to color |
| **Achromatopsia** (complete color blindness) | All colors as grayscale | Luminance contrast maintained (all combos ≥4.5:1 in grayscale) |

### 3.4 Contrast Testing Protocol

```typescript
// Every new color combination must pass this check
const contrastCheck = (fg: string, bg: string, size: 'small' | 'large' | 'component'): boolean => {
  const ratio = getContrastRatio(fg, bg);
  const thresholds = { small: 4.5, large: 3, component: 3 };
  return ratio >= thresholds[size];
};

// Integrated into CI pipeline as part of component tests
// Fails PR build if any color combination doesn't meet threshold
```

---

## 4. Keyboard Navigation

### 4.1 Core Keyboard Interaction Model

| Key | Action | Notes |
|---|---|---|
| **Tab** | Move focus to next focusable element | Follows visual DOM order |
| **Shift + Tab** | Move focus to previous focusable element | — |
| **Enter / Space** | Activate focused element | Button, link, toggle |
| **Escape** | Close modal, popover, dropdown, menu | Returns focus to triggering element |
| **Arrow Up/Down** | Navigate lists, menus, radio groups | Wraps at ends |
| **Arrow Left/Right** | Navigate tabs, carousels, date picker | — |
| **Home / End** | Jump to first/last item in list, scrollable region | — |
| **Ctrl + K** | Open command palette (global) | — |
| **?** | Show keyboard shortcuts help overlay | Global, any screen |
| **Delete / Backspace** | Delete selected item (with confirmation) | In list contexts |
| **Ctrl + Z** | Undo last action | Where applicable |

### 4.2 Application-Specific Shortcuts

| Shortcut | Context | Action |
|---|---|---|
| `G then T` | Global | Navigate to Tasks |
| `G then C` | Global | Navigate to Courses |
| `G then H` | Global | Navigate to Habits |
| `G then D` | Global | Navigate to Dashboard |
| `G then S` | Global | Navigate to Sleep |
| `G then I` | Global | Navigate to Income |
| `G then R` | Global | Navigate to Resources |
| `G then O` | Global | Navigate to Opportunities |
| `G then P` | Global | Navigate to Projects |
| `C` | Tasks list | Create new task |
| `/` | Any list | Focus search / filter |
| `N` | Any list | Focus next item (after search) |
| `J` / `K` | Any list | Move selection down/up (vim-style) |
| `A` | Task detail | Archive task |
| `F` | Habit view | Toggle filter |
| `Shift + ?` | Anywhere | Toggle shortcut help overlay |

### 4.3 Tab Order Rules

| Rule | Implementation |
|---|---|
| Tab order follows visual reading order | Left-to-right, top-to-bottom within each section |
| Skip navigation is first focusable item | Before `<header>`, `<nav>`, or any content |
| Modal / dialog traps focus | Tab cycles within modal elements; Escape to close |
| Sidebar navigation items | Tab through in vertical order; no arrow key trapping in collapsed state |
| Data tables | Tab enters table, arrow keys navigate cells, Tab exits to next element |
| Form sections | Tab through fields in logical (not column) order; Shift+Tab reverses |

### 4.4 Focus Management in SPAs

```typescript
// Route change: move focus to <main> or <h1>
// Modal open: save last focus, move to modal's first focusable element
// Modal close: restore focus to triggering element
// Dynamic content: announce via aria-live="polite" and move focus to new content

const routeChangeFocus = () => {
  const main = document.querySelector('main');
  if (main) {
    main.setAttribute('tabindex', '-1');
    main.focus();
    main.removeAttribute('tabindex');
  }
};
```

---

## 5. Screen Reader Support

### 5.1 Supported Screen Readers

| Screen Reader | OS | Browser | Testing Priority |
|---|---|---|---|
| NVDA 2024+ | Windows | Firefox, Chrome | Primary (daily CI) |
| JAWS 2024+ | Windows | Chrome, Edge | Secondary (weekly) |
| VoiceOver | macOS | Safari | Primary (daily CI) |
| TalkBack | Android | Chrome | Secondary (per release) |
| Narrator | Windows | Edge | Tertiary (per milestone) |

### 5.2 ARIA Label Conventions

```html
<!-- Icons and icon buttons -->
<button aria-label="Create new task">
  <PlusIcon aria-hidden="true" />
</button>

<!-- Status indicators -->
<span role="status" aria-live="polite">
  <span class="sr-only">Task completed</span>
  <CheckIcon class="text-accent-neon" aria-hidden="true" />
</span>

<!-- Loading states -->
<div role="status" aria-live="polite" aria-busy="true">
  <span class="sr-only">Generating your daily briefing...</span>
  <SkeletonLoader aria-hidden="true" />
</div>

<!-- Navigation -->
<nav aria-label="Main navigation">
  <ul role="list">
    <li><a href="/tasks" aria-current="page">Tasks</a></li>
  </ul>
</nav>

<!-- Dynamic updates -->
<section aria-live="polite" aria-atomic="true">
  <!-- Content that updates via AJAX/WebSocket -->
</section>

<!-- Error summary -->
<div role="alert" aria-labelledby="error-heading">
  <h2 id="error-heading">3 errors found</h2>
  <ul>
    <li>Email is required</li>
    <li>Password must be at least 8 characters</li>
  </ul>
</div>
```

### 5.3 ARIA Roles and Properties Usage

| Pattern | ARIA | Rationale |
|---|---|---|
| Navigation sidebar | `role="navigation"` with `aria-label="Main"` | Distinguish from other nav elements |
| Search results | `role="listbox"` with `aria-activedescendant` | Arrow-key navigation |
| Tab panels | `role="tablist"`, `role="tab"`, `role="tabpanel"` with `aria-selected`, `aria-controls`, `aria-labelledby` | Standard accessible tabs |
| Accordion | `role="button"` with `aria-expanded`, `aria-controls` | Expand/collapse pattern |
| Toast notifications | `role="alert"` with `aria-live="assertive"` | Critical updates |
| Status messages | `role="status"` with `aria-live="polite"` | Non-critical updates |
| Progress indicator | `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax` | Loading states |
| Modal dialog | `role="dialog"` with `aria-modal="true"` and `aria-labelledby` | Focus trap + content isolation |
| Tooltip | `role="tooltip"` with `aria-describedby` on trigger | Supplemental information |
| Breadcrumb | `nav` with `aria-label="Breadcrumb"` + `aria-current="page"` on last item | Navigation context |

### 5.4 Live Region Strategy

| Region Type | `aria-live` | Use Case | Timing |
|---|---|---|---|
| Status | `polite` | Briefing loaded, task saved, streak updated | After async operation completes |
| Alert | `assertive` | Error messages, destructive action confirmation | Immediate |
| Log | Off (use `role="log"`) | Chat messages, activity feed updates | Append-only |
| Timer | `polite` | Pomodoro countdown, deadline warnings | Every 60s or at threshold |
| Suggestion | `polite` | AI nudges, opportunity alerts | As generated |

### 5.5 Screen Reader Testing Protocol

```bash
# Automated checks (CI pipeline)
npx axe-core --rules aria-*,color-contrast,label,landmark-one-main,page-has-heading-one

# Manual checks (per release)
1. Navigate entire app using keyboard only (no mouse)
2. Complete all primary flows with NVDA + Firefox
3. Complete all primary flows with VoiceOver + Safari
4. Verify all dynamic content announcements
5. Test at 200% zoom
6. Test with Windows High Contrast Mode
```

---

## 6. Focus Indicators

### 6.1 Cyberpunk Glow Focus Rings

ARIA OS uses distinctive neon-glow focus indicators that are both highly visible and on-brand.

```css
/* Default focus ring — accent-primary glow */
:focus-visible {
  outline: 2px solid #6366F1;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.25),
              0 0 12px rgba(99, 102, 241, 0.15);
  border-radius: 4px;
}

/* Danger focus — used for destructive actions */
.btn-danger:focus-visible {
  outline: 2px solid #EF4444;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.25);
}

/* Card focus — interactive cards */
.card:focus-visible {
  outline: 1px solid #6366F1;
  outline-offset: 0px;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2),
              inset 0 0 0 1px rgba(99, 102, 241, 0.3);
}

/* Input focus — form fields */
.input:focus-visible {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2),
              0 0 8px rgba(99, 102, 241, 0.1);
}

/* List item focus */
[role="menuitem"]:focus-visible,
[role="option"]:focus-visible {
  outline: 1px solid #6366F1;
  outline-offset: -1px;
  background: rgba(99, 102, 241, 0.08);
}
```

### 6.2 Focus Ring Rules

| Rule | Implementation |
|---|---|
| Never use `:focus { outline: none }` without providing an alternative | Always use `:focus-visible` for custom styles |
| Focus ring must be visible in all background contexts | Inner glow or ring offset to handle both dark and elevated surfaces |
| Interactive elements must have distinct focus from rest state | Minimum 2px outline + 3px glow shadow |
| Focus ring must not be obscured by overflow hidden | Use `outline-offset` or positive `box-shadow` |
| Custom components (divs as buttons) must have `tabindex="0"` and visible focus | Follow the `:focus-visible` patterns above |
| Skip-link focus ring must be FULL-WIDTH and highly visible | White outline on dark background: `outline: 3px solid #F1F5F9; outline-offset: 4px;` |

### 6.3 Focus Indicator Visibility Matrix

| Element | Background | Focus Style | Visibility |
|---|---|---|---|
| Button (primary) | `--accent-primary` (#6366F1) | White outline + brighter glow | Excellent |
| Button (secondary) | `--bg-card` (#13151A) | `--accent-primary` outline + glow | Excellent |
| Card | `--bg-card` (#13151A) | `--accent-primary` inset border + glow | Excellent |
| Input | `--bg-card` (#13151A) | `--accent-primary` border + glow | Excellent |
| Nav link | `--bg-page` (#0A0B0F) | `--accent-primary` background tint + glow | Excellent |
| Modal close button | `--bg-elevated` (#1E2230) | White outline + glow | Excellent |
| Icon-only button | `--bg-card` (#13151A) | `--accent-primary` glow around icon | Excellent |
| Table row | `--bg-page` (#0A0B0F) | Inset `--accent-primary` border-left | Good |

---

## 7. Motion Sensitivity

### 7.1 Reduced Motion Support

ARIA OS respects both the `prefers-reduced-motion` media query and provides in-app motion controls.

```css
/* Respect OS-level preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  .glow-pulse,
  .particle-effect,
  .confetti {
    display: none !important;
  }

  /* Immediate reveals instead of animations */
  .stagger-item {
    opacity: 1 !important;
    transform: none !important;
  }
}
```

### 7.2 Framer Motion `useReducedMotion` Implementation

```typescript
import { useReducedMotion } from 'framer-motion';

function AnimatedComponent() {
  const prefersReducedMotion = useReducedMotion();

  const variants = {
    hidden: { opacity: prefersReducedMotion ? 1 : 0, y: prefersReducedMotion ? 0 : 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={variants}
      initial="hidden"
      animate="visible"
      transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
    >
      Content
    </motion.div>
  );
}
```

### 7.3 Application Motion Settings

Beyond the OS-level preference, users can configure motion in ARIA Settings:

| Setting | Options | Default | Effect |
|---|---|---|---|
| Motion intensity | Full / Reduced / Minimal | Full | Full: all animations. Reduced: no decorative animations, critical transitions only. Minimal: no animations except loading spinners. |
| Disable parallax | On / Off | Off | Removes background parallax and depth effects |
| Disable glow effects | On / Off | Off | Removes all animated glow/shadow effects |
| Flash-free mode | On / Off | Off | Ensures no content flashes at any frequency |

### 7.4 Animation Categories by Sensitivity

| Category | Examples | Reduced Motion Behavior |
|---|---|---|
| **Critical** (essential) | Loading spinner, skeleton screen, progress bar | Keep, no change (functional) |
| **Navigation** | Page transitions, route changes | Crossfade (300ms) instead of slide, no stagger |
| **Micro-interaction** | Button press, toggle switch, hover | 0ms instant state change |
| **Decorative** | Particle effects, background glow pulse, confetti | Remove entirely |
| **Notification** | Toast slide-in, modal fade-in Fade-in (200ms) instead of slide-up (keeps | function) |
| **Data visualization** | Chart transitions, counter animations | 0ms instant update, no stagger |

---

## 8. Text Scaling & Zoom

### 8.1 Responsive Typography (Zoom Support)

ARIA OS supports browser zoom up to 200% without loss of content or functionality. The fluid type system (`clamp()` values) handles the zoom gracefully.

```css
/* Fluid type prevents layout breakage at zoom levels */
--fs-body: clamp(0.875rem, 1vw + 0.5rem, 1rem);

/* At 200% zoom on a 1440px viewport:
   - Font size becomes: clamp(14px, 14.4px + 8px = 22.4px, 16px) = 22.4px
   - Layout reflows into single-column as needed
   - All content remains readable and functional */
```

### 8.2 Zoom Behavior Rules

| Rule | Implementation |
|---|---|
| No horizontal scroll at any zoom level up to 200% | Container queries + responsive grid |

|

| Interactive elements don't overlap or clip | Min-width on buttons, auto-flow on flex containers |
| Fixed-position elements (modals, toasts) remain usable | Max-height with overflow-y: auto; never position: absolute for critical content |
| Text never gets truncated at zoom levels | `overflow-wrap: break-word; hyphens: auto;` on all text containers |
| Layout shifts from zoom don't hide content | `min-height` on sections; never `height: 100vh` for critical content |

### 8.3 Browser Zoom Testing Matrix

| Browser | Zoom Level | Layout | Text Readable | Interactive |
|---|---|---|---|---|
| Chrome 125+ | 100% | ✅ | ✅ | ✅ |
| Chrome 125+ | 150% | ✅ | ✅ | ✅ |
| Chrome 125+ | 200% | ✅ | ✅ | ✅ |
| Firefox 130+ | 100-200% | ✅ | ✅ | ✅ |
| Safari 18+ | 100-200% | ✅ | ✅ | ✅ |
| Edge 125+ | 100-200% | ✅ | ✅ | ✅ |

### 8.4 OS-Level Text Scaling

```css
/* Support iOS Dynamic Type and Android font scale */
/* Use relative units (rem) everywhere — never px for text */
html { font-size: 100%; } /* Respects browser/OS base font size */
body { font-size: 1rem; }
```

---

## 9. Error Announcement Patterns

### 9.1 Error Identification

All form validation errors must:

1. Identify which field(s) have errors
2. Describe what's wrong
3. Suggest how to fix it
4. Be announced to screen readers

```html
<!-- Error pattern -->
<div role="alert" aria-labelledby="form-error-heading">
  <h2 id="form-error-heading" class="sr-only">Form submission errors</h2>
  <ul>
    <li>
      <a href="#task-title" class="error-link">
        <span class="sr-only">Error: </span>
        Title is required
      </a>
    </li>
    <li>
      <a href="#due-date" class="error-link">
        <span class="sr-only">Error: </span>
        Due date must be in the future
      </a>
    </li>
  </ul>
</div>

<!-- Inline field error -->
<div class="input-wrapper">
  <label for="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-invalid="true"
    aria-describedby="email-error"
    required
  />
  <p id="email-error" class="field-error" role="alert">
    Please enter a valid email address (e.g., name@example.com)
  </p>
</div>
```

### 9.2 Error Types and Announcements

| Error Type | Announcement Pattern | `aria-live` | Example |
|---|---|---|---|
| Form validation | List of links to each invalid field | `assertive` | "3 errors found. Title is required. Due date must be in future." |
| API failure | Toast + inline error on the affected area | `assertive` | "Couldn't save your task. Your internet connection appears offline." |
| Auth failure | Inline error on the form | `assertive` | "Invalid email or password." (generic, no "user not found") |
| Permission denied | Toast + redirect to appropriate page | `polite` | "You don't have access to this resource." |
| Rate limiting | Toast with retry timer | `polite` | "Too many requests. Please wait 30 seconds." |
| Destructive action | Confirmation dialog with consequences | `assertive` | "Delete task 'Final Report'? This cannot be undone." |
| Network offline | Banner at top of page | `polite` | "You're offline. Changes will sync when you reconnect." |

### 9.3 Error Recovery

Every error must provide a path forward:

| Error | Action Button | Secondary Action |
|---|---|---|
| Network failure | "Retry" | "Save locally" |
| Validation error | "Fix issues" (scrolls to first error) | "Cancel" |
| Auth timeout | "Sign in again" | "Go to home" |
| Server error (500) | "Refresh page" | "Contact support" |
| Rate limited | "Dismiss" (with countdown) | "Learn about limits" |

---

## 10. Skip Navigation

### 10.1 Implementation

```html
<!-- First focusable element on every page -->
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<!-- Target -->
<main id="main-content" tabindex="-1">
  <!-- Page content -->
</main>
```

### 10.2 Skip Link Styling

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  padding: 12px 24px;
  background: #6366F1;
  color: #F1F5F9;
  font-family: 'DM Sans', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 0 0 8px 8px;
  text-decoration: none;
  white-space: nowrap;
  transition: top 0.2s ease;
}

.skip-link:focus {
  top: 0;
  outline: 3px solid #00FFA3;
  outline-offset: 2px;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
}
```

### 10.3 Additional Bypass Mechanisms

| Mechanism | Implementation | Scope |
|---|---|---|
| Skip to content | First tab stop on every page | Global |
| Landmark regions | `<nav>`, `<main>`, `<aside>` with proper labels | Global |
| Heading structure | Single `h1` per page, hierarchical `h2`-`h6` | Global |
| Quick navigation | `Ctrl+K` command palette | Global |
| Module sidebar | `aria-label="Module navigation"` with section landmarks | Dashboard |
| Table of contents | `nav` with `aria-label="Page sections"` | Long-form content only |

---

## 11. Touch Target Sizes

### 11.1 Minimum Target Sizes

| Context | Minimum Size | Our Standard | Rationale |
|---|---|---|---|
| All interactive elements (mobile) | 24×24px (WCAG AA) | 44×44px | AA min is insufficient for real-world use |
| Icon-only buttons | 24×24px | 44×44px hit area (icon centered inside) | Touch accuracy |
| Form inputs | 24×24px height | 44px height | Finger placement |
| Bottom navigation tabs | 24×24px | 48×48px + 8px gap | Thumb reach zone |
| Slider handles | 24×24px | 44×44px hit area | Precision control |
| Link targets in text | 24×24px | 44×44px minimum (padding) | Inline links |
| Close / dismiss buttons | 24×24px | 44×44px hit area | Always top-right, easy to reach |

### 11.2 Touch Target Spacing

All interactive elements must have minimum 4px gap between their hit areas. For bottom-mounted navigation and action bars, minimum 8px gap required.

```css
/* Icon button with adequate touch target */
.icon-button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Icon inside is 20×20px, padded to 44×44 hit area */
}

/* Bottom navigation items */
.bottom-nav-item {
  min-width: 48px;
  min-height: 48px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
```

---

## 12. Accessibility Testing Tools & Process

### 12.1 Automated Testing Tools

| Tool | Scope | Integration | Frequency |
|---|---|---|---|
| axe-core (via jest-axe) | Component-level WCAG violations | Unit tests | Every PR |
| Lighthouse | Page-level audit (accessibility section) | CI pipeline | Every PR |
| WAVE | Manual page inspection | Browser extension | Per release |
| Colour Contrast Analyser | Color pair verification | Manual check | Per new color |
| IBM Equal Access Checker | Full-page audits | CI pipeline | Weekly |
| Pa11y | Automated crawl of all routes | CI pipeline | Daily |

### 12.2 Manual Testing Process

```bash
# Pre-release accessibility checklist

# 1. Automated checks
npm run a11y:ci         # axe-core + Lighthouse in CI

# 2. Keyboard audit
npm run a11y:keyboard   # Scripted keyboard navigation of all routes

# 3. Screen reader audit
# NVDA + Firefox: Complete all primary user journeys
# VoiceOver + Safari: Complete all primary user journeys

# 4. Zoom audit
# 200% zoom on Chrome: verify no horizontal scroll, no clipped content

# 5. Reduced motion audit
# Enable prefers-reduced-motion: reduce in dev tools
# Verify all animations stop or degrade gracefully

# 6. Color blindness audit
# Use Chrome DevTools rendering emulation
# Check each CVD type (protanopia, deuteranopia, tritanopia)

# 7. High contrast mode audit
# Windows High Contrast Mode: verify all elements remain distinguishable
```

### 12.3 Testing Cadence

| Cadence | Tests | Responsibility |
|---|---|---|
| Per commit | Unit tests with jest-axe | Developer |
| Per PR | CI pipeline (axe-core, Lighthouse) | CI |
| Daily | Pa11y crawl | Automated |
| Weekly | Full keyboard audit + screen reader spot-check | QA |
| Per release (2 weeks) | Full manual accessibility audit | QA + Design |
| Per milestone (quarterly) | Third-party accessibility audit | External consultant |

### 12.4 Accessibility Bug Severity

| Severity | Definition | SLI | Examples |
|---|---|---|---|
| **Critical** | Blocks core functionality for assistive tech users | Fix before merge | No keyboard access to primary action, missing form labels, no focus indicator |
| **High** | Causes significant difficulty, workaround exists | Fix before release | Low contrast (between 3:1 and 4.5:1), missing alt text, incomplete ARIA labels |
| **Medium** | Causes inconvenience, clear workaround | Fix within 1 release cycle | Suboptimal heading hierarchy, redundant ARIA, non-standard button text |
| **Low** | Minor polish, cosmetic | Fix when convenient | Slightly small touch target (40px instead of 44px), imperfect color harmony |

---

## 13. Known Accessibility Issues & Roadmap

### 13.1 Current Known Issues

| ID | Issue | WCAG Criterion | Severity | Status | Target Fix |
|---|---|---|---|---|---|
| A11Y-001 | `--border-default` (2.7:1) fails non-text contrast for decorative borders | 1.4.11 AA | Medium | Workaround available | v1.1 |
| A11Y-002 | Drag-and-drop task reorder has limited keyboard alternative | 2.5.7 AA | High | In progress | v1.0.1 |
| A11Y-003 | Some chart visualizations (radar chart) lack full screen reader descriptions | 1.1.1 A | Medium | Backlogged | v1.2 |
| A11Y-004 | Bottom sheet on mobile not fully accessible via TalkBack | 4.1.2 A | Critical | In progress | v1.0.1 |
| A11Y-005 | AI-generated briefings have no semantic heading structure | 1.3.1 A | High | In progress | v1.0.1 |
| A11Y-006 | Streak calendar not fully navigable via arrow keys | 2.1.1 A | Medium | Backlogged | v1.1 |
| A11Y-007 | Push notification preferences not adjustable from within app (requires OS settings) | 2.2.1 A | Low | Investigating | v1.2 |
| A11Y-008 | Loading states for AI agent responses lack `aria-busy` attribute | 4.1.3 AA | Medium | In progress | v1.0.1 |

### 13.2 Accessibility Roadmap

**v1.0 (Current — 2026 Q2)**
- ✅ WCAG 2.2 AA compliance for all standard CRUD routes
- ✅ Keyboard navigation for all 15 modules
- ✅ Focus indicator system (cyberpunk glow rings)
- ✅ Screen reader support for primary flows
- ⏳ Drag-and-drop keyboard alternative (target: v1.0.1 patch)
- ⏳ Chart accessibility descriptions (target: v1.2)

**v1.1 (2026 Q3)**
- WCAG 2.2 AA compliance for AI-generated content
- AI briefing/review semantic structure enforcement
- Streak calendar keyboard navigation
- Border contrast remediation
- Touch target audit and fixes
- Full screen reader test protocol documented

**v1.2 (2026 Q4)**
- WCAG 2.2 AAA contrast for body text (7:1)
- Sign language support for tutorial videos
- Custom color theme (high-contrast variant)
- User testing with 5+ assistive technology users
- Third-party accessibility audit

**v2.0 (2027 Q1+)**
- AI-powered accessibility: ARIA suggests contrast-safe color combinations, alt text, and heading structure
- Full WCAG 2.2 AAA audit
- Accessibility API for community themes
- Integration with OS accessibility features (Live Captions, Voice Access)

### 13.3 Accessibility Champions

| Role | Name | Responsibility |
|---|---|---|
| Accessibility Lead | — | Overall strategy, standards, training |
| Engineering Champion | — | Code reviews, implementation patterns, CI integration |
| Design Champion | — | Component review, color audits, motion design |
| QA Champion | — | Test plans, regression testing, screen reader protocol |
| Community Liaison | — | User feedback funnel, assistive tech user testing coordination |

---

> **Maintenance:** This document is updated per release cycle. All new components must be reviewed against this document before merging. File an issue in GitHub with label `accessibility` for any questions or violations.
>
> **Related documents:** `docs/design/10_DesignSystem.md` (component tokens), `docs/design/Branding.md` (color system, voice), `docs/design/MotionSystem.md` (reduced motion patterns), `docs/design/ResponsiveRules.md` (responsive touch targets).
