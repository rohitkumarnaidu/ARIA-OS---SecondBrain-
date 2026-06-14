# Design Tokens Reference

> **Source of truth**: `apps/web/tailwind.config.js` (theme extensions) and `apps/web/app/globals.css` (CSS custom properties + utility classes).
>
> These tokens drive every visual decision in ARIA OS. Never introduce hard-coded color, spacing, or typography values; always reference the token.

---

## CSS Custom Properties

Defined in `apps/web/app/globals.css` under `@layer base`:

```css
:root {
  --font-display: var(--font-syne), 'Syne', system-ui, sans-serif;
  --font-body: var(--font-dm-sans), 'DM Sans', system-ui, sans-serif;
  --font-mono: var(--font-jetbrains), 'JetBrains Mono', monospace;
}
```

These are set via Next.js font loader in `app/layout.tsx`:
- `Syne` loaded with `variable: '--font-syne'`, `display: 'swap'`
- `DM_Sans` loaded with `variable: '--font-dm-sans'`, `display: 'swap'`
- `JetBrains_Mono` loaded with `variable: '--font-jetbrains'`, `display: 'swap'`

---

## Color Tokens

### Background Colors

| Token                    | Value    | Tailwind Class          | CSS Variable | Usage                    |
|--------------------------|----------|-------------------------|--------------|--------------------------|
| background               | #0A0B0F  | `bg-background`         | --           | Page background          |
| background-dark          | #050607  | `bg-background-dark`    | --           | Search input, dropdowns  |
| background-card          | #12141C  | `bg-background-card`    | --           | Cards, sidebar, navbar   |
| background-elevated      | #1A1D28  | `bg-background-elevated`| --           | Dropdowns, hovered items |
| background-input         | #0D0F14  | `bg-background-input`   | --           | Input field backgrounds  |

### Surface Colors

| Token           | Value    | Tailwind Class          | Usage                        |
|-----------------|----------|-------------------------|------------------------------|
| surface-primary | #FFFFFF  | `bg-surface-primary`    | Inverted text backgrounds    |
| surface-secondary | #F8FAFC | `bg-surface-secondary` | Light card (future light mode)|
| surface-tertiary| #F1F5F9  | `bg-surface-tertiary`   | Light surfaces (future)      |

### Border Colors

| Token       | Value    | Tailwind Class          | Usage                    |
|-------------|----------|-------------------------|--------------------------|
| border      | #2A2E3F  | `border-border`         | Default component border |
| border-light| #E2E8F0  | `border-border-light`   | Light mode borders       |
| border-focus| #6366F1  | `border-border-focus`   | Focus state border       |
| border-subtle| #1E222E | `border-border-subtle`  | Subtle separators        |

### Text Colors

| Token         | Value    | Tailwind Class          | Usage                     |
|---------------|----------|-------------------------|---------------------------|
| text-primary  | #F0F2F5  | `text-text-primary`     | Headings, body            |
| text-secondary| #8B92A5  | `text-text-secondary`   | Subtext, metadata         |
| text-tertiary | #5A6075  | `text-text-tertiary`    | Placeholders, muted       |
| text-inverse  | #0F172A  | `text-text-inverse`     | Text on light backgrounds |
| text-disabled | #475569  | `text-text-disabled`    | Disabled element text     |

### Accent Colors

| Token             | Value    | Tailwind Class                 | Usage                          |
|-------------------|----------|--------------------------------|--------------------------------|
| accent-primary    | #6366F1  | `text-accent-primary` / `bg-accent-primary` | Actions, links, active |
| primaryHover      | #4F46E5  | `hover:bg-accent-primaryHover` | Primary button hover           |
| accent-secondary  | #10B981  | `text-accent-secondary` / `bg-accent-secondary` | Success indicators |
| secondaryHover    | #059669  | `hover:bg-accent-secondaryHover` | Secondary hover              |
| accent-warning    | #F59E0B  | `text-accent-warning` / `bg-accent-warning` | Warning states      |
| warningHover      | #D97706  | `hover:bg-accent-warningHover` | Warning hover                  |
| accent-error      | #EF4444  | `text-accent-error` / `bg-accent-error` | Error states          |
| errorHover        | #DC2626  | `hover:bg-accent-errorHover`   | Error hover                    |
| accent-info       | #3B82F6  | `text-accent-info` / `bg-accent-info` | Info badges          |
| accent-success    | #22C55E  | `text-accent-success` / `bg-accent-success` | Positive indicators |
| accent-neon       | #00FFA3  | `text-accent-neon` / `bg-accent-neon` | Decorative highlights  |
| accent-cyber      | #FF3366  | `text-accent-cyber` / `bg-accent-cyber` | Urgent indicators   |

### Priority Colors

| Token  | Value    | Tailwind Class                          |
|--------|----------|-----------------------------------------|
| urgent | #FF3366  | `text-priority-urgent` / `bg-priority-urgent` |
| high   | #FF6B35  | `text-priority-high` / `bg-priority-high`     |
| medium | #FFB800  | `text-priority-medium` / `bg-priority-medium` |
| low    | #00FFA3  | `text-priority-low` / `bg-priority-low`       |

### Glass Opacity Colors

| Token  | Value              | Tailwind Class | Usage                   |
|--------|--------------------|----------------|-------------------------|
| light  | rgba(255,255,255,0.03) | `bg-glass-light` | Subtle glass       |
| medium | rgba(255,255,255,0.08) | `bg-glass-medium` | Card glass        |
| heavy  | rgba(255,255,255,0.15) | `bg-glass-heavy` | Highlighted glass |

---

## Typography Tokens

### Font Families

| Token          | Value                  | Tailwind Class   | CSS Variable           |
|----------------|------------------------|------------------|------------------------|
| display        | Syne, system-ui, sans  | `font-display`   | `var(--font-display)`  |
| body           | DM Sans, system-ui, sans | `font-body`    | `var(--font-body)`     |
| mono           | JetBrains Mono, monospace | `font-mono`  | `var(--font-mono)`     |

### Font Size Tokens

| Token | Size  | Line Height | Tailwind Class | Usage              |
|-------|-------|-------------|----------------|--------------------|
| xs    | 11px  | 16px        | `text-xs`      | Labels, badges     |
| sm    | 13px  | 18px        | `text-sm`      | Secondary info     |
| base  | 15px  | 24px        | `text-base`    | Body text          |
| lg    | 17px  | 26px        | `text-lg`      | Subheadings        |
| xl    | 19px  | 28px        | `text-xl`      | Module headings    |
| 2xl   | 24px  | 32px        | `text-2xl`     | Card titles        |
| 3xl   | 32px  | 38px        | `text-3xl`     | Section headers    |
| 4xl   | 42px  | 48px        | `text-4xl`     | Page titles        |
| 5xl   | 56px  | 1.1         | `text-5xl`     | Hero display       |

### Font Weight Tokens

| Token     | Value | Tailwind Class    |
|-----------|-------|-------------------|
| normal    | 400   | `font-normal`     |
| medium    | 500   | `font-medium`     |
| semibold  | 600   | `font-semibold`   |
| bold      | 700   | `font-bold`       |
| extrabold | 800   | `font-extrabold`  |

### Line Height Tokens

| Token   | Value | Tailwind Class    | Usage                  |
|---------|-------|-------------------|------------------------|
| tight   | 1.2   | `leading-tight`   | Headings, display      |
| normal  | 1.5   | `leading-normal`  | Body text              |
| relaxed | 1.7   | `leading-relaxed` | Long-form reading      |

---

## Spacing Tokens

Base unit: 4px. All tokens follow the Tailwind spacing scale.

| Token | Value | Tailwind Class    | Common Usage                    |
|-------|-------|-------------------|---------------------------------|
| 0     | 0px   | `p-0` / `gap-0`  | Remove spacing                  |
| 1     | 4px   | `p-1` / `gap-1`  | Tight inner paddings            |
| 2     | 8px   | `p-2` / `gap-2`  | Stack items, tight separator    |
| 3     | 12px  | `p-3` / `gap-3`  | Input/button inner padding      |
| 4     | 16px  | `p-4` / `gap-4`  | Card padding, list spacing      |
| 5     | 20px  | `p-5` / `gap-5`  | Card content, grid gaps         |
| 6     | 24px  | `p-6` / `gap-6`  | Sections, modal padding         |
| 7     | 28px  | `p-7` / `gap-7`  | Page section gaps               |
| 8     | 32px  | `p-8` / `gap-8`  | Page padding, sidebar padding   |
| 10    | 40px  | `p-10` / `gap-10`| Large section separation        |
| 12    | 48px  | `p-12` / `gap-12`| Page section margins            |
| 16    | 64px  | `p-16` / `gap-16`| Major page sections             |
| 20    | 80px  | `p-20` / `gap-20`| Extra-large page spacing        |

### Min-Height/Min-Width Tokens (Touch Targets)

| Token       | Value | Tailwind Class           | Usage                        |
|-------------|-------|--------------------------|------------------------------|
| touch       | 44px  | `min-h-touch`            | Universal touch target       |
| input       | 44px  | `min-h-input` / `h-input`| Form input height            |
| button      | 44px  | `min-h-button` / `min-w-button` | Button minimum size   |
| button-sm   | 36px  | `min-h-button-sm`        | Small button variant         |

---

## Border Radius Tokens

| Token | Value | Tailwind Class     | Usage                    |
|-------|-------|--------------------|--------------------------|
| none  | 0px   | `rounded-none`     | No rounding              |
| sm    | 4px   | `rounded-sm`       | Minimal rounding         |
| DEFAULT | 8px | `rounded` / `rounded-lg` | Buttons, inputs   |
| md    | 10px  | `rounded-md`       | Badges                   |
| lg    | 12px  | `rounded-lg`       | Cards, modals            |
| xl    | 16px  | `rounded-xl`       | Large cards              |
| 2xl   | 20px  | `rounded-2xl`      | Hero sections            |
| 3xl   | 28px  | `rounded-3xl`      | Extreme rounding         |
| full  | 9999px| `rounded-full`     | Pills, avatars, badges   |

---

## Shadow Tokens

### Glow Shadows (Primary Accent - #6366F1)

| Token    | Value                                      | Tailwind Class       | Usage                    |
|----------|--------------------------------------------|----------------------|--------------------------|
| glow-sm  | `0 0 20px rgba(99, 102, 241, 0.15)`       | `shadow-glow-sm`     | Hover state glow         |
| glow     | `0 0 30px rgba(99, 102, 241, 0.25)`       | `shadow-glow`        | Active state glow        |
| glow-lg  | `0 0 50px rgba(99, 102, 241, 0.35)`       | `shadow-glow-lg`     | Hero/primary CTA glow    |

### Neon Shadows (Success/Neon - #00FFA3)

| Token   | Value                                      | Tailwind Class      | Usage                        |
|---------|--------------------------------------------|---------------------|------------------------------|
| neon-sm | `0 0 15px rgba(0, 255, 163, 0.2)`         | `shadow-neon-sm`    | Low-priority badge glow      |
| neon    | `0 0 25px rgba(0, 255, 163, 0.3)`         | `shadow-neon`       | Success indicator glow       |

### Cyber Shadows (Error/Urgent - #FF3366)

| Token    | Value                                      | Tailwind Class      | Usage                    |
|----------|--------------------------------------------|---------------------|--------------------------|
| cyber-sm | `0 0 15px rgba(255, 51, 102, 0.2)`        | `shadow-cyber-sm`   | Urgent badge glow        |
| cyber    | `0 0 25px rgba(255, 51, 102, 0.3)`        | `shadow-cyber`      | Error state glow         |

### Functional Shadows

| Token       | Value                                      | Tailwind Class        | Usage                  |
|-------------|--------------------------------------------|-----------------------|------------------------|
| focus       | `0 0 0 2px #6366F1`                       | `shadow-focus`        | Focus ring state       |
| focus-error | `0 0 0 2px #EF4444`                       | `shadow-focus-error`  | Error focus ring       |
| inner-glow  | `inset 0 1px 0 0 rgba(255,255,255,0.05)`  | `shadow-inner-glow`   | Card inner highlight   |

### CSS Glow Utility Classes

Defined in `globals.css` `@layer utilities`:

| Class           | Shadow Value                                              |
|-----------------|-----------------------------------------------------------|
| `.glow-primary` | `0 0 20px rgba(99, 102, 241, 0.3), 0 0 60px rgba(99, 102, 241, 0.1)` |
| `.glow-success` | `0 0 20px rgba(0, 255, 163, 0.3), 0 0 60px rgba(0, 255, 163, 0.1)` |
| `.glow-error`   | `0 0 20px rgba(255, 51, 102, 0.3), 0 0 60px rgba(255, 51, 102, 0.1)` |

---

## Animation Tokens

### Duration Tokens

| Token  | Value | Tailwind Class           | Usage                    |
|--------|-------|--------------------------|--------------------------|
| fast   | 150ms | `duration-fast`          | Micro-interactions       |
| DEFAULT| 200ms | `duration`               | Standard transitions     |
| slow   | 300ms | `duration-slow`          | Page transitions         |
| slower | 400ms | `duration-slower`        | Modal enter/exit         |

### Easing Tokens

| Token          | Value                                  | Tailwind Class     |
|----------------|----------------------------------------|--------------------|
| DEFAULT        | `cubic-bezier(0.4, 0, 0.2, 1)`        | `ease-default`     |
| in             | `cubic-bezier(0.4, 0, 1, 1)`          | `ease-in`          |
| out            | `cubic-bezier(0, 0, 0.2, 1)`          | `ease-out`         |
| bounce         | `cubic-bezier(0.68, -0.55, 0.265, 1.55)` | `ease-bounce`   |
| elastic        | `cubic-bezier(0.68, -0.6, 0.32, 1.6)` | `ease-elastic`     |

### Keyframe Animations

```css
@keyframes glow {
  0%   { box-shadow: 0 0 20px rgba(99, 102, 241, 0.15); }
  100% { box-shadow: 0 0 35px rgba(99, 102, 241, 0.35); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-10px); }
}

@keyframes scan {
  0%   { background-position: 0 0; }
  100% { background-position: 0 100%; }
}

@keyframes slideInUp {
  from { transform: translateY(20px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

@keyframes slideInDown {
  from { transform: translateY(-20px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.2); }
  50%      { box-shadow: 0 0 40px rgba(99, 102, 241, 0.4); }
}

@keyframes gradient-shift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

---

## Z-Index Tokens

| Token    | Value | Tailwind Class     | Usage                       |
|----------|-------|--------------------|-----------------------------|
| 0        | 0     | `z-0`              | Base layer                  |
| 10       | 10    | `z-10`             | Page content                |
| 20       | 20    | `z-20`             | Sticky elements             |
| 30       | 30    | `z-30`             | Sticky headers              |
| 40       | 40    | `z-40`             | Fixed navbar/sidebar        |
| 50       | 50    | `z-50`             | Highest page level          |
| dropdown | 1000  | `z-dropdown`       | Dropdowns, popovers         |
| sticky   | 1020  | `z-sticky`         | Sticky section headers      |
| modal    | 1030  | `z-modal`          | Modal backdrops + content   |
| popover  | 1040  | `z-popover`        | Tooltips, popovers          |
| tooltip  | 1050  | `z-tooltip`        | Tooltips (always on top)    |

---

## Background Patterns

| Token        | Tailwind Class   | Description                                      |
|--------------|------------------|--------------------------------------------------|
| grid-pattern | `bg-grid-pattern`| 30px grid lines at 3% opacity accent-primary     |
| scanlines    | `bg-scanlines`   | 2px repeating horizontal lines at 10% black      |
| noise        | `bg-noise`       | SVG fractal noise at 1.5% opacity (via pseudo-element) |
| bg-grid      | `.bg-grid`       | 40px grid lines at 3% opacity accent-primary     |

---

## Responsive Breakpoint Tokens

| Token | Min Width | Tailwind Prefix | Usage                  |
|-------|-----------|-----------------|------------------------|
| xs    | 375px     | `xs:`           | Minimum supported      |
| sm    | 640px     | `sm:`           | Mobile landscape       |
| md    | 768px     | `md:`           | Tablet portrait        |
| lg    | 1024px    | `lg:`           | Tablet landscape       |
| xl    | 1280px    | `xl:`           | Desktop                |
| 2xl   | 1536px    | `2xl:`          | Large desktop          |

---

## Composite Utility Classes

These are defined in `globals.css` `@layer components` and combine multiple tokens:

| Class               | Composition                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `.btn`              | Button base: inline-flex, justify-center, font-medium, rounded-lg, min-h 44px, min-w 44px, focus ring |
| `.btn-primary`      | bg-accent-primary, text-white, glow-sm shadow, inner highlight              |
| `.card`             | bg-background-card, border-border, rounded-xl, p-5, backdrop-blur, gradient overlay |
| `.card-interactive` | card + cursor-pointer, hover lift 2px, hover glow, purple gradient overlay  |
| `.input`            | h-input, px-4, rounded-lg, bg-background-input, border-border, focus-ring   |
| `.glass`            | bg-glass-light, border-glass-medium, backdrop-blur-xl                       |
| `.badge`            | inline-flex, px-2.5 py-1, rounded-md, text-xs, font-medium                  |
| `.spinner`          | animate-spin, rounded-full, border-2, border-accent-primary, border-t-transparent |
| `.progress`         | h-1.5, bg-background-elevated, rounded-full, overflow-hidden                |
| `.progress-bar`     | h-full, rounded-full, gradient fill (indigo -> violet -> neon), duration-500 transition |

### Text Gradient Classes

| Class                | Gradient                                      |
|----------------------|-----------------------------------------------|
| `.text-gradient`     | #F0F2F5 -> #8B92A5 (subtle silver)           |
| `.text-gradient-accent` | #6366F1 -> #00FFA3 (indigo to neon)       |
| `.text-gradient-neon`| #00FFA3 -> #6366F1 -> #FF3366 (tri-color)   |
