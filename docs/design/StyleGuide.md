# Style Guide — Second Brain OS (ARIA OS) — Updated

## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-STY-001 |
| Version | 2.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Design Philosophy

**Bold and distinctive cyberpunk aesthetics.** Every visual element should feel intentional and distinctive. This is not a generic AI product — it is a developer's personal OS with attitude.

### Core Principles
1. **Dark first:** #0A0B0F base, light mode deferred to post-GA
2. **Neon accents:** Indigo (#6366F1) primary, green (#00FFA3) for success
3. **Developer-centric:** Code aesthetics, monospace fonts, grid backgrounds
4. **Motion with purpose:** Framer Motion for page transitions, micro-interactions
5. **Glass depth:** backdrop-filter: blur() for overlays, cards

---

## 2. Design Tokens

### Color System

```css
/* Background */
--bg-page: #0A0B0F;
--bg-card: #13151A;
--bg-card-hover: #1A1D24;
--bg-input: #1A1D24;
--bg-tooltip: #1E293B;

/* Accent */
--accent-primary: #6366F1;
--accent-secondary: #818CF8;
--accent-neon: #00FFA3;
--accent-warning: #F59E0B;
--accent-danger: #EF4444;

/* Text */
--text-primary: #F1F5F9;
--text-secondary: #94A3B8;
--text-muted: #64748B;

/* Border */
--border-default: #1E293B;
--border-accent: #334155;
--border-hover: #475569;

/* Status */
--status-pending: #F59E0B;
--status-in-progress: #6366F1;
--status-completed: #00FFA3;
--status-cancelled: #EF4444;

/* Shadow */
--shadow-glow-primary: 0 0 20px rgba(99, 102, 241, 0.15);
--shadow-glow-neon: 0 0 20px rgba(0, 255, 163, 0.15);
--shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
```

### Typography Scale

```css
/* Font Families */
--font-display: 'Syne', sans-serif;
--font-body: 'DM Sans', sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Font Sizes */
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 32px;
--text-4xl: 40px;
--text-5xl: 48px;

/* Font Weights */
--weight-regular: 400;
--weight-medium: 500;
--weight-semibold: 600;
--weight-bold: 700;
```

### Spacing System (4px base)

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 9999px;
```

---

## 3. Component Guidelines

### Buttons

```html
<button class="btn btn-primary">Primary</button>
<!-- Indigo (#6366F1) bg, white text, glow shadow on hover -->

<button class="btn btn-secondary">Secondary</button>
<!-- Border only, transparent bg, indigo border -->

<button class="btn btn-ghost">Ghost</button>
<!-- No bg, no border, text only, subtle hover -->

<button class="btn btn-danger">Danger</button>
<!-- Red (#EF4444) bg, white text -->

<button class="btn btn-sm">Small</button>
<button class="btn btn-lg">Large</button>
```

### Cards

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
    <span class="card-badge">Status</span>
  </div>
  <div class="card-content">
    <!-- Content -->
  </div>
  <div class="card-footer">
    <!-- Actions -->
  </div>
</div>
```

### Inputs

```html
<input class="input" placeholder="Placeholder" />
<textarea class="input input-textarea" rows="3"></textarea>
<select class="input input-select">
  <option>Option 1</option>
</select>
```

---

## 4. Layout Patterns

### Page Structure
```
┌─────────────────────────────────────┐
│  Navbar (sticky, blurred bg)        │
├──────┬──────────────────────────────┤
│      │                              │
│ Side │   Main Content Area          │
│ bar  │   (max-width: 1200px)        │
│      │                              │
│ 240px│  - Section headers (text-    │
│      │    gradient for main titles) │
│      │  - Cards in bento-box grids  │
│      │  - Agent activity feed       │
│      │                              │
├──────┴──────────────────────────────┤
│  Footer (minimal, copyright)        │
└─────────────────────────────────────┘
```

### Responsive Breakpoints
| Breakpoint | Width | Layout |
|---|---|---|
| Mobile | < 640px | Single column, sidebar hidden |
| Tablet | 640-1024px | 2-column, collapsible sidebar |
| Desktop | > 1024px | Full layout with sidebar |

---

## 5. Motion Guidelines

| Element | Animation | Duration | Easing |
|---|---|---|---|
| Page load | Staggered fade-in (children) | 300ms | ease-out |
| Card hover | Scale up 1.02 + glow | 200ms | ease-in-out |
| Modal | Fade + scale backdrop | 250ms | ease-out |
| Button press | Scale down 0.97 | 100ms | ease-in |
| Sidebar toggle | Slide horizontal | 200ms | ease-in-out |
| Notification | Slide down + fade | 300ms | ease-out |

```tsx
// Framer Motion examples
<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
  <Card>
    <motion.h2 className="text-gradient">Section Title</motion.h2>
    <AnimatePresence>
      {items.map((item, i) => (
        <motion.div key={item.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
          <ItemCard {...item} />
        </motion.div>
      ))}
    </AnimatePresence>
  </Card>
</motion.div>
```

---

## 6. Accessibility Standards

| Requirement | Standard | Enforcement |
|---|---|---|
| Color contrast | WCAG AA (4.5:1 text) | lint-a11y.ts |
| Keyboard navigation | All interactive elements | Manual check |
| Focus indicators | Visible outline | CSS `:focus-visible` |
| ARIA labels | All icon buttons | ESLint jsx-a11y |
| Reduced motion | `prefers-reduced-motion` | CSS media query |
| Screen reader | Semantic HTML, headings | axe DevTools |

---

## 7. Writing Style

| Element | Style | Example |
|---|---|---|
| Buttons | Title Case | "Save Changes" |
| Headings | Title Case | "Task Management" |
| Labels | Sentence case | "Task title" |
| Error messages | Complete sentence | "Could not load tasks. Please try again." |
| Toast notifications | Action + Result | "Task created successfully" |
| AI responses | First person, direct | "I noticed you have 3 overdue tasks..." |

**Tone:** Direct, helpful, developer-friendly. No emojis. No marketing fluff.

---

## 8. File Organization

```
components/
├── ui/           # Primitive components (Button, Card, Input, Modal)
│   ├── button.tsx
│   ├── card.tsx
│   └── modal.tsx
├── features/     # Feature-specific components
│   ├── task-card.tsx
│   ├── habit-calendar.tsx
│   └── sleep-chart.tsx
└── layout/
    ├── navbar.tsx
    ├── sidebar.tsx
    └── footer.tsx
```

---

## 9. References

| Document | Location |
|---|---|
| Design System | `docs/design/10_DesignSystem.md` |
| Design Tokens | `docs/design/35_DesignTokens.md` |
| UI/UX Guidelines | `docs/design/08_UIUX.md` |
| Tailwind Config | `apps/web/tailwind.config.js` |
| Global CSS | `apps/web/styles/globals.css` |
