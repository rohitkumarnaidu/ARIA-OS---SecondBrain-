# Component Specification â€” Second Brain OS (ARIA)

> **Document ID:DSG-CSP-001 SB-COMP-SPEC-001  
> **Version:** 1.0.0  
> **Status:** Active  
> **Last Updated:** 2026-06-18  
> **Classification:** Internal â€” Engineering & Design  
> **Owner:** Design Engineering Team

---

## Table of Contents

1. [Component Inventory](#1-component-inventory)
2. [Component Standards](#2-component-standards)
3. [Anatomy Patterns](#3-anatomy-patterns)
4. [State Coverage](#4-state-coverage)
5. [Accessibility Matrix](#5-accessibility-matrix)
6. [Responsive Behavior](#6-responsive-behavior)
7. [Testing Requirements](#7-testing-requirements)
8. [Performance Budgets](#8-performance-budgets)

---

## 1. Component Inventory

| # | Component | Type | States | Dependencies | Storybook |
|---|---|---|---|---|---|
| 1 | `Button` | Action | default, hover, active, disabled, loading, icon-only | `@/components/ui/Button` | âœ… |
| 2 | `Input` | Form | default, focus, filled, error, disabled, readonly | `@/components/ui/Input` | âœ… |
| 3 | `Card` | Layout | default, hover, selected | `@/components/ui/Card` | âœ… |
| 4 | `Badge` | Display | default, dot, count | `@/components/ui/Badge` | âœ… |
| 5 | `Skeleton` | Feedback | pulse, wave, shimmer | `@/components/ui/Skeleton` | â€” |
| 6 | `Spinner` | Feedback | sm, md, lg, with-label | `@/components/ui/Spinner` | â€” |
| 7 | `EmptyCanvas` | Empty | default, action, illustration | `@/components/ui/EmptyCanvas` | â€” |
| 8 | `ErrorState` | Feedback | default, retry, redirect | `@/components/ui/ErrorState` | â€” |
| 9 | `LoadingScreen` | Feedback | default, progress, determinate | `@/components/ui/LoadingScreen` | â€” |
| 10 | `PageHeader` | Layout | default, back-button, actions | `@/components/ui/PageHeader` | â€” |
| 11 | `Dialog` | Overlay | closed, open, confirm | `@/components/ui/Dialog` | â€” |
| 12 | `Sheet` | Overlay | closed, open, positions: left/right/bottom | `@/components/ui/Sheet` | â€” |
| 13 | `Drawer` | Overlay | closed, open, size: sm/md/lg/full | `@/components/ui/Drawer` | â€” |
| 14 | `Popover` | Overlay | closed, open, positions: top/bottom/left/right | `@/components/ui/Popover` | â€” |
| 15 | `Tooltip` | Overlay | hidden, visible, delay: fast/slow | `@/components/ui/Tooltip` | â€” |
| 16 | `Select` | Form | default, focus, open, selected, error, disabled | `@/components/ui/Select` | â€” |
| 17 | `Switch` | Form | off, on, disabled | `@/components/ui/Switch` | â€” |
| 18 | `Tabs` | Navigation | inactive, active, hover, underline | `@/components/ui/Tabs` | â€” |
| 19 | `DropdownMenu` | Overlay | closed, open, item-hover, item-selected | `@/components/ui/DropdownMenu` | â€” |
| 20 | `BentoGrid` | Layout | default, populated, empty | `@/components/ui/BentoGrid` | â€” |
| 21 | `ProgressRing` | Feedback | determinate, indeterminate, value range | `@/components/ui/ProgressRing` | â€” |
| 22 | `ActivityHeatmap` | Display | daily, weekly, monthly, empty, loading | `@/components/ui/ActivityHeatmap` | â€” |
| 23 | `Timeline` | Display | default, active, completed, upcoming | `@/components/ui/Timeline` | â€” |
| 24 | `ChartContainer` | Layout | loading, empty, data, error | `@/components/ui/ChartContainer` | â€” |
| 25 | `Modal` | Overlay | closed, open, size: sm/md/lg/fullscreen | `@/components/ui/Modal` | â€” |
| 26 | `EmptyState` | Empty | default, action, illustration, search | `@/components/ui/EmptyState` | â€” |
| 27 | `Avatar` | Display | image, initials, fallback, status-dot | `@/components/ui/Avatar` | â€” |
| 28 | `Command` | Navigation | closed, open, empty, results, loading | `@/components/ui/Command` | â€” |
| 29 | `DataTable` | Data | empty, loading, populated, sorted, filtered, paginated | `@/components/ui/DataTable` | â€” |
| 30 | `Pagination` | Navigation | first, prev, page, next, last, ellipsis, disabled | `@/components/ui/Pagination` | â€” |
| 31 | `Slider` | Form | default, hover, dragging, disabled | `@/components/ui/Slider` | â€” |
| 32 | `Textarea` | Form | default, focus, filled, error, disabled, char-count | `@/components/ui/Textarea` | â€” |
| 33 | `Toggle` | Form | off, on, disabled, size: sm/md/lg | `@/components/ui/Toggle` | â€” |
| 34 | `Toolbar` | Navigation | default, grouped, overflow | `@/components/ui/Toolbar` | â€” |
| 35 | `TreeView` | Navigation | collapsed, expanded, selected, disabled, nested | `@/components/ui/TreeView` | â€” |
| 36 | `Calendar` | Display | default, selected, today, disabled, min/max | `@/components/ui/Calendar` | â€” |
| 37 | `Combobox` | Form | closed, open, empty, selected, search, async | `@/components/ui/Combobox` | â€” |
| 38 | `FileUpload` | Form | empty, dragging, files, error, max-files | `@/components/ui/FileUpload` | â€” |
| 39 | `DatePicker` | Form | closed, open, selected, range | `@/components/ui/DatePicker` | â€” |
| 40 | `FormField` | Form | default, error, disabled, with-helper | `@/components/ui/Form` | â€” |
| 41 | `MultiSelect` | Form | closed, open, selected, search, max | `@/components/ui/MultiSelect` | â€” |
| 42 | `AIDock` | AI | idle, open, thinking, streaming, error | `@/components/ai/AIDock` | â€” |
| 43 | `ThinkingIndicator` | AI | idle, thinking, complete, error, cancelled | `@/components/ai/ThinkingIndicator` | â€” |
| 44 | `AIInsightCard` | AI | recommendation, insight, alert | `@/components/ai/AIInsightCard` | â€” |
| 45 | `AIUndo` | AI | visible, expired, dismissed | `@/components/ai/AIUndo` | â€” |
| 46 | `StreamingText` | AI | idle, streaming, complete | `@/components/ai/StreamingText` | â€” |
| 47 | `GhostHint` | AI | idle, visible, dismissed | `@/components/ai/GhostHint` | â€” |
| 48 | `SuggestionChips` | AI | default, selected, hover | `@/components/ai/SuggestionChips` | â€” |
| 49 | `ConfidenceBadge` | AI | low, medium, high, unknown | `@/components/ai/ConfidenceBadge` | â€” |

---

## 2. Component Standards

Every component MUST comply with the following standards:

### 2.1 File Structure
```
ComponentName.tsx       # Component implementation
ComponentName.stories.tsx  # Storybook stories (for core components)
index.ts                # Barrel export from components/ui/
```

### 2.2 Code Requirements
- `'use client'` directive at the top
- Named function export (no default exports)
- `displayName` assigned to all components
- Full TypeScript interfaces exported alongside component
- Framer Motion for animations (when applicable)
- CSS variables for all colors (`var(--token)`)
- `cn()` utility from `@/components/ui/utils` for class merging
- `data-testid` attributes on interactive elements

### 2.3 Props Conventions
| Pattern | Rule | Example |
|---|---|---|
| `className` | Last prop, optional string | `className?: string` |
| Children | Explicit `ReactNode` type | `children?: ReactNode` |
| Event handlers | `on{Event}` naming | `onChange`, `onClick` |
| Size variants | `sm \| md \| lg` | `size?: 'sm' \| 'md' \| 'lg'` |
| Disabled state | `disabled?: boolean` | All form controls |
| Loading state | `isLoading?: boolean` | When async data needed |

### 2.4 Styling Rules
- NO inline `style` objects with static values â€” use Tailwind + variables
- NO `any` in type definitions â€” use `unknown` + type guards
- NO `var()`, `let` â€” always `const`
- ALL colors via design tokens: `var(--accent-primary)`, `var(--text-primary)`, etc.
- ALL spacing via Tailwind classes: `gap-2`, `p-4`, `m-2`
- ALL transitions: `transition-all duration-200`

---

## 3. Anatomy Patterns

### 3.1 Form Control Anatomy
```tsx
<FormField>
  <FormLabel />       // Label with optional required indicator
  <FormControl />     // Input/Select/Textarea/etc.
  <FormMessage />     // Error state
  <FormDescription /> // Helper text
</FormField>
```

### 3.2 Card Anatomy
```tsx
<Card>
  <CardHeader />      // Title + description
  <CardContent />     // Body content
  <CardFooter />      // Actions
</Card>
```

### 3.3 Overlay Anatomy
```tsx
<Overlay>             // Backdrop
  <Content>           // Dialog/Sheet/Drawer
    <Header />        // Title + close button
    <Body />          // Main content
    <Footer />        // Action buttons
  </Content>
</Overlay>
```

### 3.4 AI Component Anatomy
```tsx
<AIDock>
  <ThinkingIndicator />   // State indicator
  <StreamingText />       // Animated text output
  <SuggestionChips />     // Quick action chips
  <ConfidenceBadge />     // Confidence indicator (optional)
</AIDock>
```

---

## 4. State Coverage

Every component MUST implement these states where applicable:

| State Category | States | Examples |
|---|---|---|
| **Default** | Initial render state | Button in normal state |
| **Hover** | Mouse over interactive element | Button hover, Card hover |
| **Focus** | Keyboard focus | Input focus, Button focus-visible |
| **Active** | Mouse down/pressed | Button pressed, Toggle on |
| **Disabled** | Non-interactive | Input disabled, Button disabled |
| **Loading** | Async operation in progress | Button loading, Table loading |
| **Empty** | No data to display | Empty table, empty list |
| **Error** | Failed operation | Form validation, API error |
| **Success** | Completed operation | Form submitted, saved |

---

## 5. Accessibility Matrix

| Requirement | Standard | Verification |
|---|---|---|
| Keyboard navigation | All interactive elements reachable via Tab | Tab through flow |
| Focus indicators | `focus-visible:ring-2` on all interactive | Visual inspection |
| ARIA labels | `aria-label` on icon-only buttons | axe-core |
| ARIA roles | `role` attributes per component type | axe-core |
| ARIA states | `aria-expanded`, `aria-selected`, etc. | axe-core |
| Color contrast | WCAG AA minimum (4.5:1 text, 3:1 large) | Lighthouse |
| Reduced motion | `useReducedMotion()` or `prefers-reduced-motion` | CSS media query |
| Touch targets | Minimum 44x44px for all interactive | Lighthouse |
| Screen reader | Meaningful `aria-live` regions for dynamic content | Manual testing |
| Focus trap | Modal/Drawer/Sheet trap focus when open | Manual testing |
| Skip link | First focusable element on page | axe-core |

---

## 6. Responsive Behavior

| Breakpoint | Width | Layout Strategy |
|---|---|---|
| Mobile | < 640px | Single column, stacked |
| Tablet | 640px - 1024px | 2-column grid, condensed nav |
| Desktop | 1024px+ | Full layout, sidebar visible |
| Wide | 1536px+ | Max-width container centered |

### Component Responsive Rules
- **DataTable**: horizontal scroll on mobile, show/hide columns via `columnVisibility`
- **Calendar**: condensed day cells on mobile (smaller font, no events text)
- **Combobox**: full-screen sheet on mobile, dropdown on desktop
- **FileUpload**: reduced drag zone height on mobile
- **TreeView**: full-width touch targets on mobile
- **Toolbar**: overflow menu on mobile (`<Toolbar>` wraps into `DropdownMenu`)

---

## 7. Testing Requirements

| Test Type | Coverage | Tool |
|---|---|---|
| Unit tests | All 49 components â€” 2 variants Ã— 3 states Ã— 2 edge cases minimum | Vitest + Testing Library |
| Accessibility | All components pass axe-core | `jest-axe` + Lighthouse CI |
| Visual regression | Core 28 components in Storybook | Chromatic / Percy |
| Interaction | Form controls, overlays, keyboard nav | Playwright |
| Performance | Render time < 50ms per component | React DevTools profiler |

---

## 8. Performance Budgets

| Metric | Target |
|---|---|
| Component render time | < 50ms (React DevTools profiler) |
| First paint (any component) | < 100ms from page load |
| Animation frame rate | 60fps (no jank) |
| JavaScript bundle contribution | < 5KB gzip per component |
| Re-render frequency | Only on prop/state change (React.memo where beneficial) |
| Memory | No leaks on unmount (verify with `useEffect` cleanup) |
