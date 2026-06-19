# Part XI — Responsive Behavior

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `ResponsiveRules.md` (breakpoint definitions, layout reflow), wireframes (7 parts, all show 3 breakpoints), `FrontendArchitecture.md` (responsive shell architecture).

---

## 11.1 Desktop Behavior (≥ 1024px)

| Aspect | Specification |
|---|---|
| **Layout** | Sidebar (240px) + Content (flex) + optional Context Panel (320px) |
| **Density** | Comfortable: padding 24px, gap 16px |
| **Interactions** | Hover states, right-click context menus, drag-and-drop, keyboard shortcuts |
| **Navigation** | Persistent sidebar with icon + label, breadcrumbs in TopBar |
| **Typography** | H1: 32px, H2: 24px, H3: 20px, Body: 16px, Small: 14px |
| **Modals** | Centered dialog (max 600px width) with backdrop blur |
| **Slide-over** | Right panel at 50% width |
| **Multi-column** | 2-3 column grid layouts, split-pane list/detail |
| **Search** | Full overlay with grouped results in columns |
| **Settings** | Sidebar (240px) + content (flex) |

---

## 11.2 Tablet Behavior (640px - 1023px)

| Aspect | Specification |
|---|---|
| **Layout** | Collapsed sidebar (64px icons only) + Content (flex) |
| **Density** | Compact: padding 16px, gap 12px |
| **Interactions** | Tap targets ≥ 44px, swipe gestures, long-press for context menu |
| **Navigation** | Hamburger toggle for sidebar, bottom tab bar (5 items) on the way |
| **Typography** | H1: 24px, H2: 20px, H3: 18px, Body: 15px, Small: 13px |
| **Modals** | Slide-up sheet at 70% height |
| **Slide-over** | Right panel at 70% width (or full-width on < 768px) |
| **Multi-column** | 2-column grid, single-column on < 768px |
| **Search** | Slide-over panel at 70% width |
| **Settings** | Tabs instead of sidebar |

### Tablet-Specific Patterns

| Pattern | Desktop | Tablet |
|---|---|---|
| Sidebar | Always visible, 240px | Collapsed 64px, expand on hamburger |
| Data tables | Full columns | Horizontally scrollable, hide less important columns |
| Card grids | 3 columns | 2 columns |
| Detail view | Split: list + detail | Stacked: list → tap → detail |
| Dashboard widgets | 2-3 per row | 1-2 per row |
| Command palette | Full overlay | Full overlay (same) |
| Notifications | Dropdown from bell | Bottom sheet from bell |

---

## 11.3 Mobile Behavior (320px - 639px)

| Aspect | Specification |
|---|---|
| **Layout** | Full-width (12px padding), no sidebar |
| **Density** | Tight: padding 12px, gap 8px |
| **Interactions** | Swipe gestures (left = delete, right = complete), tap, long-press |
| **Navigation** | Bottom tab bar (5 items: Dashboard, Tasks, Chat, Search, More) |
| **Typography** | H1: 20px, H2: 18px, H3: 16px, Body: 14px, Small: 12px |
| **Modals** | Full-screen sheet with back/dismiss button |
| **Slide-over** | Full-screen (effectively a page) |
| **Multi-column** | Single column always |
| **Search** | Full-screen overlay with back button |
| **Settings** | Accordion list instead of sidebar or tabs |

### Mobile-Specific Patterns

| Pattern | Desktop | Mobile |
|---|---|---|
| Sidebar | 240px left | Full-screen drawer from left |
| Top Bar | 64px with search + actions | 48px with back + title + menu |
| Bottom Nav | None | 5 fixed tabs at bottom |
| Modals | Centered dialog | Full-screen sheet |
| Toast | Top-right | Bottom (above bottom nav) |
| Context menu | Right-click | Long-press → bottom sheet |
| Multi-select | Checkbox + toolbar | Swipe → action bar |
| Pull to refresh | Not needed | Pull down to refresh content |
| Floating action | Button in header | Bottom-right FAB, 56px |

---

## 11.4 Navigation Adaptation

| Element | Desktop | Tablet | Mobile |
|---|---|---|---|
| Sidebar Nav | 240px, icon + label | 64px, icon only (expandable) | Full-screen drawer (hamburger) |
| Top Bar | 64px, logo + search + actions | 56px, hamburger + title + bell | 48px, back + title + menu |
| Bottom Nav | Hidden | Hidden (or visible on PWA) | 5 tabs, always visible |
| Breadcrumb | Full path | Last 2 levels | Hidden (back button only) |
| Quick Capture | Cmd+K shortcut | Cmd+K / gesture | Swipe from bottom / gesture |
| Notification Bell | Top bar, dropdown | Top bar, dropdown | Notification tab in bottom nav |

---

## 11.5 Layout Adaptation

| Component | Desktop | Tablet | Mobile |
|---|---|---|---|
| Dashboard | 3-column bento grid | 2-column grid | 1-column stack |
| Task List | Full list with detail split | List with slide-over | Full list → tap → full detail |
| Kanban Board | 4-5 columns side-by-side | 2-3 columns (horizontal scroll) | Single column with stage tabs |
| Calendar | Month grid with events | Month grid (compact) | Agenda list |
| Chart | Full with tooltips | Full (touch tooltips) | Simplified, no interactive |
| Forms | Inline errors side-by-side | Stacked layout | Stacked, full-width inputs |
| Data Table | All columns | Key columns + scroll | Key fields only → card list |

---

## 11.6 Interaction Adaptation

| Interaction | Desktop | Tablet | Mobile |
|---|---|---|---|
| Click / Tap | Click (mouse) | Tap (finger) | Tap (finger) |
| Right-click / Long-press | Right-click menu | Long-press menu | Long-press → action sheet |
| Hover | Tooltips, previews | None (use tap) | None |
| Drag & Drop | Mouse drag | Touch drag | Touch drag (with haptic) |
| Swipe | N/A | Swipe for actions | Swipe for actions (primary) |
| Scroll | Mouse wheel, scrollbar | Touch scroll | Touch scroll |
| Keyboard shortcuts | Full support (50+) | Limited (Cmd+K) | None |
| Multi-select | Shift/Ctrl + click | Tap select mode | Swipe → select mode |

---

## 11.7 Typography Adaptation

| Token | Desktop | Tablet | Mobile |
|---|---|---|---|
| `font-size-4xl` (H1) | 32px / 2rem | 24px / 1.5rem | 20px / 1.25rem |
| `font-size-3xl` (H2) | 24px / 1.5rem | 20px / 1.25rem | 18px / 1.125rem |
| `font-size-2xl` (H3) | 20px / 1.25rem | 18px / 1.125rem | 16px / 1rem |
| `font-size-base` (Body) | 16px / 1rem | 15px / 0.9375rem | 14px / 0.875rem |
| `font-size-sm` (Small) | 14px / 0.875rem | 13px / 0.8125rem | 12px / 0.75rem |
| `font-size-xs` (Caption) | 12px / 0.75rem | 11px / 0.6875rem | 11px / 0.6875rem |
| Line Height | 1.5 | 1.5 | 1.4 |
| Button Padding | 12px 24px | 12px 20px | 10px 16px |
| Card Padding | 24px | 16px | 12px |

Typography uses `clamp()` for fluid scaling between breakpoints.

---

## 11.8 Accessibility Adaptation

| Requirement | Desktop | Tablet | Mobile |
|---|---|---|---|
| Touch Targets | ≥ 32px (mouse) | ≥ 44px | ≥ 44px |
| Focus Indicators | Keyboard focus ring | Tap highlight | Tap highlight |
| Screen Reader | Full ARIA labels | Full ARIA labels | Full ARIA labels |
| Reduced Motion | Respect `prefers-reduced-motion` | Same | Same |
| High Contrast | Support forced colors | Same | Same |
| Keyboard Navigation | Full tab order | Not primary input | Not primary input |
| Font Scaling | Support 200% browser zoom | Same | Same |
| Voice Control | Support OS voice control | Same | Same |

### Accessible Color Contrast

All text meets WCAG 2.1 AA minimum:
- **Normal text (< 18px)**: 4.5:1 minimum contrast ratio
- **Large text (≥ 18px bold / ≥ 24px)**: 3:1 minimum contrast ratio
- **UI components**: 3:1 minimum contrast ratio
- **Disabled states**: 50% opacity (no contrast requirement)

### Focus Management

| Component | Focus Behavior |
|---|---|
| Modals | Trap focus within modal, restore on close |
| Slide-over | Move focus to panel header, close on Escape |
| Toast | Announce via aria-live="polite", no focus change |
| Skeleton | aria-busy="true" on container, remove when loaded |
| Error messages | Move focus to first error field |
| Navigation | aria-current="page" on active link |
