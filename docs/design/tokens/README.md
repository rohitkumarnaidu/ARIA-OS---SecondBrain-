# ARIA OS Design Token System

## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-TKN-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-23 |
| Classification | Internal -- Design System |
| Target Audience | Developers, Designers, AI Agents |
| Approver | Developer |

---

## 1. Overview

**Design tokens** are the atomic visual primitives that power the ARIA OS cyberpunk design language. They represent a single source of truth for every color, spacing unit, typeface, shadow, and animation duration used across the entire application.

Tokens bridge the gap between design and engineering by storing visual decisions in a platform-agnostic, machine-readable format (`tokens-studio.json`) that feeds directly into:

- **CSS custom properties** in `styles/globals.css`
- **Tailwind CSS configuration** in `tailwind.config.js`
- **Design files** via Token Studio (Figma plugin)
- **Storybook** component documentation

### Why Tokens Matter

- **Consistency**: One value, referenced everywhere -- no drift between design and code
- **Theming**: Dark, Light, and High Contrast themes derived from the same primitive palette
- **Scalability**: New components automatically inherit the visual language
- **Maintainability**: Change a primitive value and the entire system updates

---

## 2. Token Architecture

The ARIA OS token system follows a **three-layer architecture** modelled after the Design Token Community Group (DTCG) standard:

### Layer 1: Primitive Tokens (Raw Values)

The foundational palette -- hues, scales, and unit values with no semantic meaning. These are the building blocks for all other tokens.

```
color.primitive.neutral.500  -->  #64748B
color.primitive.indigo.500  -->  #6366F1
spacing.primitive.4         -->  4px
typography.primitive.syne   -->  "Syne", sans-serif
```

**Source file**: `tokens-studio.json` defines 7 hue families (neutral, indigo, emerald, amber, rose, cyan, slate), each with a 12-step scale (50-950) plus white, black, and transparent.

### Layer 2: Semantic Tokens (Role-Based)

Purpose-built tokens that map primitives to functional roles. These are theme-aware -- each token has a value for dark (default), light, and high-contrast modes.

```
color.semantic.bg.page        -->  #0A0B0F (dark) / #F8FAFC (light)
color.semantic.text.primary   -->  #F0F2F5 (dark) / #0F172A (light)
color.semantic.border.default -->  #2A2E3F (dark) / #CBD5E1 (light)
```

**Convention**: Semantic token names follow the pattern `{property}-{role}` (e.g., `bg-page`, `text-primary`, `border-default`).

### Layer 3: Component Tokens (Scoped)

Highly specific tokens scoped to individual components. These reference semantic tokens and add component-specific overrides.

```
component.btn.primary.bg        -->  var(--accent-primary)
component.card.border-radius    -->  var(--radius-lg)
component.input.bg              -->  var(--background-input)
```

**Convention**: Component tokens follow `{component}-{variant}-{property}` (e.g., `btn-primary-bg`, `card-radius`, `input-border-focus`).

---

## 3. Current Token Inventory

The complete token set is defined in a single JSON file following the DTCG / Token Studio format:

| File | Size | Tokens | Description |
|---|---|---|---|
| `tokens-studio.json` | 623 lines | ~180+ tokens | All primitives, semantic tokens, and component tokens across 3 themes |

**Token categories in the file**:
- `color.primitive` -- 7 hue families x 12 steps + white/black/transparent
- `color.semantic` -- Backgrounds, text, borders, accents, priority colors
- `spacing` (referenced via Tailwind config)
- `typography` (referenced via Tailwind config)
- `shadow` (glow and neon effects)
- `radius` (border radius scale)
- `opacity` (interaction states)
- `animation` (durations and easing curves)

---

## 4. Usage Guide

### In CSS / SCSS

Reference tokens via `var()` CSS custom properties:

```css
.card {
  background: var(--background-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--accent-primary);
  box-shadow: var(--shadow-glow-sm);
}
```

### In Tailwind CSS

Use the semantic Tailwind utility classes mapped to tokens in `tailwind.config.js`:

```html
<div class="bg-background-card text-text-primary border-border-default rounded-lg">
  <h1 class="font-display text-2xl">Dashboard</h1>
  <p class="text-text-secondary">Welcome back.</p>
</div>

<button class="btn btn-primary">Save</button>
```

**Key Tailwind mappings** (from `tailwind.config.js`):
| Utility Class | CSS Variable |
|---|---|
| `bg-background-card` | `var(--background-card)` |
| `bg-background-page` / `bg-background-dark` | `var(--background-dark)` |
| `text-text-primary` | `var(--text-primary)` |
| `text-text-secondary` | `var(--text-secondary)` |
| `border-border-default` | `var(--border)` |
| `accent-primary` / `accent-neon` | `var(--accent-primary)` / `var(--accent-neon)` |

### In Design Files (Figma / Token Studio)

Reference tokens by their semantic name:
- Use `bg/page` for page backgrounds
- Use `text/primary` for body text
- Use `accent/primary` for interactive accents
- Use `border/default` for dividers and outlines

All tokens are synchronised via the Token Studio Figma plugin. Changes to `tokens-studio.json` can be imported directly into design files.

### Golden Rule

**Never use hardcoded hex values in code.** Every colour, spacing unit, shadow, and font family must come from the token system. Arbitrary Tailwind values like `bg-[#123]` are prohibited by project convention (see AGENTS.md Section 5.2).

---

## 5. Color Palette

All colors derive from the primitive palette and are exposed as semantic CSS custom properties:

| CSS Variable | Hex Value | Usage |
|---|---|---|
| `--bg-page` / `--background-dark` | `#0A0B0F` | Page background (dark theme) |
| `--bg-card` / `--background-card` | `#13151A` | Card and surface backgrounds |
| `--bg-card-hover` / `--background-elevated` | `#1A1D24` | Card hover / elevated surface |
| `--accent-primary` | `#6366F1` | Primary actions, links, focus rings |
| `--accent-secondary` | `#818CF8` | Secondary interactive elements |
| `--accent-neon` | `#00FFA3` | Highlight, success states, cyber accents |
| `--accent-warning` | `#F59E0B` | Warning states, medium priority |
| `--accent-danger` / `--accent-error` | `#EF4444` | Errors, destructive actions, urgent priority |
| `--text-primary` | `#F1F5F9` | Primary body text (dark theme) |
| `--text-secondary` | `#94A3B8` | Secondary / muted text |
| `--border-default` | `#1E293B` | Default borders and dividers |
| `--border-accent` | `#334155` | Accent borders, hover states |

### Priority Colors

| Token | Hex Value | Use Case |
|---|---|---|
| `--priority-urgent` | `#EF4444` | Urgent tasks and alerts |
| `--priority-high` | `#F59E0B` | High-priority items |
| `--priority-medium` | `#6366F1` | Medium-priority items |
| `--priority-low` | `#64748B` | Low-priority items |

---

## 6. Typography Scale

| Usage | Font Family | Weights | Sizes |
|---|---|---|---|
| Display / Headings | **Syne** (`font-display`) | 600 (Semibold), 700 (Bold) | 24px-48px (2xl-5xl) |
| Body text | **DM Sans** (`font-body`) | 400 (Normal), 500 (Medium) | 13px-17px (sm-lg) |
| Code / Monospace | **JetBrains Mono** (`font-mono`) | 400 (Normal) | 13px-14px (sm-base) |

### Font Sizes

| Tailwind Class | Size | Line Height | Usage |
|---|---|---|---|
| `text-xs` | 11px | 16px | Labels, metadata |
| `text-sm` | 13px | 18px | Captions, secondary text |
| `text-base` | 15px | 24px | Body text (default) |
| `text-lg` | 17px | 26px | Large body, card subtitles |
| `text-xl` | 19px | 28px | Section headings |
| `text-2xl` | 24px | 32px | Card titles |
| `text-3xl` | 32px | 38px | Page headings |
| `text-4xl` | 42px | 48px | Hero headings |
| `text-5xl` | 56px | 1.1 | Display / landing pages |

---

## 7. Spacing Scale

Based on a **4px base unit**. All spacing tokens are defined in `tailwind.config.js`:

| Tailwind Class | Pixels | Example Usage |
|---|---|---|
| `p-1` / `m-1` | 4px | Tight icon spacing |
| `p-2` / `m-2` | 8px | Button padding, small gaps |
| `p-3` / `m-3` | 12px | Input padding |
| `p-4` / `m-4` | 16px | Card padding (default) |
| `p-5` / `m-5` | 20px | Section spacing |
| `p-6` / `m-6` | 24px | Panel padding |
| `p-8` / `m-8` | 32px | Page margins |
| `p-10` / `m-10` | 40px | Large section gaps |
| `p-12` / `m-12` | 48px | Modal padding |
| `p-16` / `m-16` | 64px | Page gutters |

### Touch Targets

| Token | Value | Usage |
|---|---|---|
| `min-h-touch` | 44px | All interactive elements |
| `min-w-touch` | 44px | Buttons and tap targets |
| `h-input` | 44px | Input field height |

---

## 8. Shadows and Effects

The cyberpunk aesthetic is reinforced through glow and neon shadow tokens:

| Token | Usage |
|---|---|
| `shadow-glow-sm` | Subtle hover glow on cards |
| `shadow-glow` | Default interactive glow |
| `shadow-glow-lg` | Focused / active state glow |
| `shadow-neon-sm` | Subtle neon accent glow |
| `shadow-neon` | Neon accent (primary CTAs) |
| `shadow-cyber-sm` | Cyber grid decorative glow |
| `shadow-cyber` | Strong cyber accent |
| `shadow-focus` | Focus ring (accent-primary) |
| `shadow-focus-error` | Error focus ring |
| `shadow-inner-glow` | Inner glow for depth |

---

## 9. How to Extend

### Adding a New Token

1. **Define the primitive**: Add the raw value to `tokens-studio.json` under the appropriate primitive category (e.g., `color.primitive`).
2. **Create the semantic mapping**: Map the primitive to a role in `color.semantic` with values for all three themes (dark, light, high-contrast).
3. **Expose as CSS variable**: Add the `var()` declaration to `styles/globals.css` in the `:root` block.
4. **Register in Tailwind config**: Add the mapping in `apps/web/tailwind.config.js` under the appropriate `theme.extend` section.
5. **Update documentation**: Document the new token in this file and any relevant Storybook stories.
6. **Bump version**: Update the `version` field in `tokens-studio.json` metadata.

### Adding a New Theme

Each semantic token must provide values for all three themes:

```json
"bg": {
  "page": {
    "dark": "#0A0B0F",
    "light": "#F8FAFC",
    "high-contrast": "#FFFFFF"
  }
}
```

When adding a new theme, audit all existing semantic tokens to ensure complete coverage.

---

## 10. Related Documents

| Document | Location | Description |
|---|---|---|
| Design System Guide | `docs/design/10_DesignSystem.md` | Full design system documentation |
| Design Tokens (JSON) | `docs/design/tokens/tokens-studio.json` | Machine-readable token definitions (623 lines) |
| Tailwind Configuration | `apps/web/tailwind.config.js` | Token-to-Tailwind-utility mappings (318 lines) |
| Global Styles | `apps/web/styles/globals.css` | CSS custom properties and base styles |
| AGENTS.md Section 5 | `AGENTS.md` (lines 347-420) | UI/UX and design system reference for AI agents |
| UI Component Library | `packages/ui/` | Shared React components consuming these tokens |
| Storybook Stories | `apps/web/stories/` | Component documentation with token references |

---

*Maintained by the ARIA OS Design System. All tokens follow the Design Token Community Group (DTCG) format and are synchronised via Token Studio (Figma).*
