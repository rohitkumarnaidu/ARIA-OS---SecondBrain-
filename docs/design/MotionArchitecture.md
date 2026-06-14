# Motion Architecture — Second Brain OS (ARIA)

> **The engineering constitution for every animation in the system.**
> Authored by: Motion Design Director, Principal Product Designer, GSAP Expert, Framer Motion Expert, Creative Technologist, Enterprise UX Architect, Frontend Performance Architect.
> This document is the engineering companion to MotionSystem.md. MotionSystem.md defines *what* to animate; MotionArchitecture.md defines *how to build it*.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-MOTION-ARCH-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal — Engineering & Design |
| Target Audience | Engineering Team, Design Team, AI Agents, Code Reviewers |
| Supersedes | Ad-hoc animation patterns across all 17 page files |
| Companion Docs | MotionSystem.md (design specs), DesignStrategy.md §18 (strategy), Accessibility.md §7 (reduced motion) |

---

## Table of Contents

1. [Executive Architecture Vision](#1-executive-architecture-vision)
2. [Architecture Principles](#2-architecture-principles)
3. [Animation Token Architecture](#3-animation-token-architecture)
4. [Animation Preset Library](#4-animation-preset-library)
5. [Component Animation Contracts](#5-component-animation-contracts)
6. [Global Motion Provider](#6-global-motion-provider)
7. [Page Transition Architecture](#7-page-transition-architecture)
8. [GSAP Integration Architecture](#8-gsap-integration-architecture)
9. [Rive Integration Architecture](#9-rive-integration-architecture)
10. [AI Motion Architecture](#10-ai-motion-architecture)
11. [Motion Performance Architecture](#11-motion-performance-architecture)
12. [Motion Testing Architecture](#12-motion-testing-architecture)
13. [Motion Dev Tooling](#13-motion-dev-tooling)
14. [Implementation Roadmap](#14-implementation-roadmap)
15. [Motion Governance](#15-motion-governance)
16. [Decision Trees](#16-decision-trees)
17. [Library-Specific Rules](#17-library-specific-rules)
18. [Appendix: Quick Reference](#18-appendix-quick-reference)

---

## 1. Executive Architecture Vision

### 1.1 The Gap

MotionSystem.md defines 1159 lines of comprehensive motion design. Zero lines of it exist in production code. Framer Motion is imported on every page, but every page hardcodes its own `initial/animate` values — 17 independent animation systems, none sharing a single variant. CSS custom properties for durations and easings are documented but never defined. `useReducedMotion()` is described as the standard but never used.

**The gap is not in design. The gap is in architecture.**

### 1.2 The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MotionSystem.md (Design)                   │
│         defines WHAT to animate and WHY                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ informs
┌───────────────────────────▼─────────────────────────────────┐
│              MotionArchitecture.md (Engineering)             │
│         defines HOW to build it and WHERE it lives          │
└──────┬──────────────────┬───────────────────┬───────────────┘
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────┐    ┌────────────────┐   ┌───────────────┐
│ tokens.ts│    │animation-     │   │ MotionProvider │
│ (source  │    │presets.ts     │   │ (global root)  │
│  of      │    │ (shared       │   └───────┬───────┘
│  truth)  │    │  variants)    │           │
└────┬─────┘    └───────┬───────┘           │
     │                  │                   │
     ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│                    Component Layer                            │
│  Button  Card  Modal  Input  Sidebar  Toast  Dropdown  etc.  │
│  (each imports presets from animation-presets.ts)            │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Architecture Decisions

| Decision | Rationale | Rule |
|---|---|---|
| **Tokens are the single source of truth** | One `tokens.ts` generates CSS custom properties + TypeScript constants + Tailwind config | AR1 |
| **All variants centralized in presets** | No page-level variant definitions; every animation maps to a named preset | AR2 |
| **FM for UI, GSAP for scroll/timeline, Rive for character/celebration** | Each library for its strength; never two libraries animating the same element | AR3 |
| **MotionProvider at app root** | Global `MotionConfig`, device tier detection, reduced-motion context | AR4 |
| **AI motion is a first-class preset category** | Thinking, streaming, suggestion, agent states share the same variant architecture as UI motion | AR5 |
| **Performance enforced in CI, not reviewed** | Automated budgets catch regressions before they reach PR review | AR6 |

---

## 2. Architecture Principles

### 2.1 The 12 Golden Rules

Every animation in the system MUST conform to these rules. Violations block PR merge.

#### AR1 — One Source of Truth
**All animation parameters live in `tokens.ts`.** No inline duration values, no ad-hoc easing curves, no hardcoded transform values in component files. The single exception is custom-per-animation delays in stagger patterns.

*Violation example:* `transition={{ duration: 0.3 }}` in a page component.
*Compliant:* `transition={{ duration: tokens.duration.normal }}`.

#### AR2 — One Library Per Concern
| Concern | Library | Never Use |
|---|---|---|
| UI state transitions (hover, tap, focus, enter/exit) | Framer Motion | GSAP, CSS |
| Page transitions, route changes | Framer Motion | GSAP |
| Scroll-driven animations (parallax, reveal on scroll) | GSAP ScrollTrigger | Framer Motion `useScroll` |
| Complex timeline sequences (multi-step, sequenced) | GSAP timeline | Framer Motion |
| SVG path morphing, complex shape animations | GSAP MorphSVG | Framer Motion |
| Character / celebratory animations | Rive | Custom confetti |
| Decorative loops (glow pulse, shimmer) | CSS `@keyframes` | FM, GSAP |
| Loading spinners | CSS `@keyframes` | FM, GSAP |

#### AR3 — All Variants Centralized
**No page-level `const variants = {...}` definitions.** Every animation variant is defined in `packages/ui/animation-presets.ts` and imported by name. Components receive variants as props — they do not own them.

#### AR4 — Interruptible By Design
Every animation longer than 80ms must be interruptible. If a user triggers a new action while an animation is playing, the current animation terminates immediately and the new animation begins. Framer Motion handles this natively; GSAP animations must call `gsap.killTweensOf(element)` before starting new ones.

#### AR5 — Reduced Motion Is Not Optional
Every animated component MUST have a reduced-motion equivalent. The `MotionProvider` context provides `isMotionReduced: boolean`. Components must use this to switch to instant or simplified transitions. This is tested in CI.

#### AR6 — Performance Budgets Are Hard Limits
| Metric | Hard Limit | Soft Warning |
|---|---|---|
| FM bundle contribution | 30KB gzip | 25KB |
| GSAP bundle contribution | 25KB gzip (lazy) | 20KB |
| Rive file per asset | 200KB | 150KB |
| JS execution per animation frame | 5ms | 3ms |
| Concurrent animated elements | 12 | 8 |
| `will-change` declarations per page | 8 | 5 |

#### AR7 — No Animations On Layout Properties
**Never animate `width`, `height`, `top`, `left`, `margin`, or `padding`.** Use `scaleX`/`scaleY` for size changes, `translateX`/`translateY` for position changes, and `transformOrigin` to control the anchor point. Violation of this rule is a hard block.

#### AR8 — Exit Animations Are Faster Than Entry
Entry animations use ease-out (deceleration). Exit animations use ease-in (acceleration). Exit duration is 60-70% of entry duration. This makes the system feel responsive — users never wait for something to leave.

#### AR9 — Stagger Total Never Exceeds 500ms
The cumulative stagger delay for any group of elements must not exceed 500ms. This means: if stagger delay per item is 50ms, the maximum items staggered is 10. For lists with 20+ items, use `stagger-fast` (30ms) or apply stagger only to the first visible viewport items.

#### AR10 — Motion Belongs In Components, Not Pages
Animation code lives at two levels:
1. **Presets** (`packages/ui/animation-presets.ts`) — shared variant definitions
2. **Components** (`packages/ui/*.tsx`) — components apply presets via props

Pages import components. Pages do NOT import `framer-motion` directly. If a page needs a custom animation, the pattern is extracted into a new component or preset — never defined inline.

#### AR11 — AI Motion Is Not Decorative
AI motion patterns (thinking, streaming, suggestion) serve a functional purpose: they communicate system state. Every AI motion must answer "is the system working?" and "what stage is it in?" within 500ms of observation. If the animation does not communicate state, it is decorative and must be removed.

#### AR12 — Animation Cleanup On Unmount
Every animated component must cancel all running animations on unmount. Framer Motion handles this automatically. GSAP must call `ctx.revert()` or `kill()`. Rive must call `reset()`. CSS animations stop automatically when the element is removed from DOM.

---

## 3. Animation Token Architecture

### 3.1 Token Distribution Model

```
┌─────────────────────┐
│    tokens.ts         │ ← Single source of truth (TypeScript)
│ (packages/ui/)       │
└────┬──────┬──────┬──┘
     │      │      │
     ▼      ▼      ▼
┌────────┐ ┌──────────┐ ┌──────────────────────┐
│ CSS    │ │ Tailwind │ │ TypeScript constants  │
│ Custom │ │ Config   │ │ (for runtime calc.)   │
│ Props  │ │ (extend) │ │                      │
└────────┘ └──────────┘ └──────────────────────┘
```

### 3.2 Token Categories (7 Categories, 40+ Tokens)

#### 3.2.1 Duration Tokens

| Token Name | Value | MotionSystem.md Ref | Usage |
|---|---|---|---|
| `duration.instant` | 0ms | §2.1 | State changes, reduced motion fallback |
| `duration.fast` | 80ms | §2.1 | Button press, tap feedback, hover transitions |
| `duration.normal` | 150ms | §2.1 | Toggles, checkboxes, dropdown opens |
| `duration.slow` | 250ms | §2.1 | Card hover, list item entry, tooltip |
| `duration.nav` | 300ms | §2.1 | Page transitions, sidebar open/close |
| `duration.reveal` | 400ms | §2.1 | Content reveals, modal entrances |
| `duration.decorative` | 3000ms | §2.1 | Glow pulses, ambient loops |
| `duration.celebration` | 1000ms | §2.1 | Confetti, streak milestones |

#### 3.2.2 Easing Tokens

| Token Name | cubic-bezier() | MotionSystem.md Ref | Usage |
|---|---|---|---|
| `easing.out` | (0.0, 0.0, 0.2, 1) | §2.2 | Entries, micro-interactions |
| `easing.in` | (0.4, 0.0, 1.0, 1) | §2.2 | Exits, dismissals |
| `easing.inOut` | (0.4, 0.0, 0.2, 1) | §2.2 | Most UI transitions |
| `easing.spring` | (0.34, 1.56, 0.64, 1) | §2.2 | Celebrations, playful elements |
| `easing.linear` | (0.0, 0.0, 1.0, 1) | §2.2 | Progress bars, spinners |
| `easing.emphasis` | (0.2, 0.0, 0.0, 1) | §2.2 | Important content arrival |
| `easing.gsapOut` | "power2.out" | GSAP | GSAP timeline entries |
| `easing.gsapIn` | "power2.in" | GSAP | GSAP timeline exits |

#### 3.2.3 Stagger Tokens

| Token Name | Value | Usage |
|---|---|---|
| `stagger.fast` | 30ms | Dense lists (20+ items) |
| `stagger.normal` | 50ms | Standard lists (5-20 items) |
| `stagger.slow` | 80ms | Sparse content (<5 items) |
| `stagger.card` | 100ms | Card grids, dashboard tiles |
| `stagger.maxTotal` | 500ms | Maximum cumulative stagger |

#### 3.2.4 Scale Tokens

| Token Name | Value | Usage |
|---|---|---|
| `scale.press` | 0.96 | Button/touchable press |
| `scale.hover` | 1.02 | Card hover, button hover |
| `scale.hoverIcon` | 1.05 | Icon-only button hover |
| `scale.activeTab` | 1.04 | Active navigation tab |
| `scale.modalBg` | 0.95 | Modal background on entry |

#### 3.2.5 Opacity Tokens

| Token Name | Value | Usage |
|---|---|---|
| `opacity.hidden` | 0 | Hidden state |
| `opacity.subtle` | 0.5 | Disabled elements, hints |
| `opacity.overlay` | 0.6 | Modal/drawer backdrops |
| `opacity.visible` | 1 | Fully visible |

#### 3.2.6 Glow Tokens

| Token Name | Value | Usage |
|---|---|---|
| `glow.primary` | `0 0 20px rgba(99,102,241,0.3)` | Primary button, active element |
| `glow.neon` | `0 0 15px rgba(0,255,163,0.25)` | Success, premium |
| `glow.cyber` | `0 0 12px rgba(255,51,102,0.3)` | Urgent, priority |
| `glow.hover` | `0 0 10px rgba(99,102,241,0.15)` | Hover state |
| `glow.ai` | `0 0 18px rgba(99,102,241,0.25)` | AI processing state |

#### 3.2.7 Z-Motion Tokens

| Token Name | Value | Usage |
|---|---|---|
| `z.page` | 0 | Base page content |
| `z.elevated` | 10 | Cards, toolbars |
| `z.sticky` | 20 | Sticky headers, navbar |
| `z.overlay` | 30 | Dropdowns, popovers |
| `z.modal` | 40 | Modals, drawers |
| `z.toast` | 50 | Toasts, notifications |
| `z.tooltip` | 60 | Tooltips |

### 3.3 File: `packages/ui/tokens.ts`

```typescript
// === MOTION TOKENS — Single Source of Truth ===
// Every animation parameter in the system derives from this file.
// Do NOT add inline duration/easing values in component files.

export const tokens = {
  duration: {
    instant: 0,
    fast: 80,
    normal: 150,
    slow: 250,
    nav: 300,
    reveal: 400,
    decorative: 3000,
    celebration: 1000,
  } as const,

  easing: {
    out: [0.0, 0.0, 0.2, 1] as const,
    in: [0.4, 0.0, 1.0, 1] as const,
    inOut: [0.4, 0.0, 0.2, 1] as const,
    spring: [0.34, 1.56, 0.64, 1] as const,
    linear: [0.0, 0.0, 1.0, 1] as const,
    emphasis: [0.2, 0.0, 0.0, 1] as const,
    gsapOut: 'power2.out' as const,
    gsapIn: 'power2.in' as const,
  } as const,

  stagger: {
    fast: 30,
    normal: 50,
    slow: 80,
    card: 100,
    maxTotal: 500,
  } as const,

  scale: {
    press: 0.96,
    hover: 1.02,
    hoverIcon: 1.05,
    activeTab: 1.04,
    modalBg: 0.95,
  } as const,

  opacity: {
    hidden: 0,
    subtle: 0.5,
    overlay: 0.6,
    visible: 1,
  } as const,

  glow: {
    primary: '0 0 20px rgba(99,102,241,0.3)',
    neon: '0 0 15px rgba(0,255,163,0.25)',
    cyber: '0 0 12px rgba(255,51,102,0.3)',
    hover: '0 0 10px rgba(99,102,241,0.15)',
    ai: '0 0 18px rgba(99,102,241,0.25)',
  } as const,

  z: {
    page: 0,
    elevated: 10,
    sticky: 20,
    overlay: 30,
    modal: 40,
    toast: 50,
    tooltip: 60,
  } as const,
} as const;

export type DurationToken = keyof typeof tokens.duration;
export type EasingToken = keyof typeof tokens.easing;
export type StaggerToken = keyof typeof tokens.stagger;
export type ScaleToken = keyof typeof tokens.scale;
export type OpacityToken = keyof typeof tokens.opacity;
```

### 3.4 Token Naming Rule

**TR1 — Token names use `.` (dot) notation in TypeScript, `--` (double dash) in CSS, and follow this hierarchy:**

```
category.variant
  Example: duration.fast → --duration-fast
  Example: easing.inOut → --easing-in-out
  Example: scale.press → --scale-press
```

**TR2 — Every token in `tokens.ts` MUST have a corresponding CSS custom property.** Generated automatically by the build process from `tokens.ts`. CSS custom properties are used for Tailwind config and component-level CSS animations.

**TR3 — Tokens are READ-ONLY at runtime.** No component should mutate a token value. If a component needs a custom value, define it as a component-scoped constant, not a token override.

### 3.5 Token Usage Rules

| Rule | Description |
|---|---|
| TUR1 | No numeric duration value appears in any `tsx` or `css` file outside of `tokens.ts` |
| TUR2 | No `cubic-bezier()` value appears in any `tsx` file outside of `tokens.ts` |
| TUR3 | All components reference tokens via the preset library, not directly |
| TUR4 | CSS `@keyframes` in `globals.css` reference `var(--duration-*)` for animation duration |
| TUR5 | New tokens require approval from Motion Design Director and must be added to all 3 distribution formats (TS, CSS, Tailwind) in the same PR |

---

## 4. Animation Preset Library

### 4.1 Preset Architecture

The preset library (`packages/ui/animation-presets.ts`) is the single registry of all Framer Motion variants in the system. Every component imports presets from here. No page-level variant definitions.

### 4.2 File: `packages/ui/animation-presets.ts`

```typescript
import { type Variants, type Transition } from 'framer-motion';
import { tokens } from './tokens';

// === Shared Transition Builders ===

const transition = (
  duration: number,
  ease: readonly number[] | string,
  delay = 0
): Transition => ({ duration: duration / 1000, ease: ease as any, delay });

const spring = (stiffness: number, damping: number, delay = 0): Transition => ({
  type: 'spring',
  stiffness,
  damping,
  delay,
});

// === ENTRY PRESETS (V1–V8) ===

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: transition(tokens.duration.normal, tokens.easing.out) },
};

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transition(tokens.duration.slow, tokens.easing.inOut),
  },
};

export const fadeDown: Variants = {
  hidden: { opacity: 0, y: -12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transition(tokens.duration.slow, tokens.easing.inOut),
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transition(tokens.duration.normal, tokens.easing.out),
  },
};

export const slideRight: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: transition(tokens.duration.slow, tokens.easing.inOut),
  },
};

export const slideLeft: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: transition(tokens.duration.slow, tokens.easing.inOut),
  },
};

export const heroReveal: Variants = {
  hidden: { opacity: 0, y: 30, scale: 0.98 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: transition(tokens.duration.reveal, tokens.easing.emphasis),
  },
};

export const scaleSpringIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: spring(400, 30),
  },
};

// === EXIT PRESETS (V9–V12) ===

export const fadeOut: Variants = {
  hidden: { opacity: 1 },
  visible: { opacity: 0, transition: transition(tokens.duration.fast, tokens.easing.in) },
};

export const scaleOut: Variants = {
  hidden: { opacity: 1, scale: 1 },
  visible: {
    opacity: 0,
    scale: 0.96,
    transition: transition(tokens.duration.fast, tokens.easing.in),
  },
};

export const slideOutRight: Variants = {
  hidden: { opacity: 1, x: 0 },
  visible: {
    opacity: 0,
    x: 20,
    transition: transition(tokens.duration.fast, tokens.easing.in),
  },
};

export const collapseOut: Variants = {
  hidden: { opacity: 1, height: 'auto' },
  visible: {
    opacity: 0,
    height: 0,
    transition: transition(tokens.duration.normal, tokens.easing.in),
  },
};

// === STAGGER PRESETS (V13–V15) ===

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: tokens.stagger.normal / 1000,
      delayChildren: 0.05,
    },
  },
};

export const staggerFast: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: tokens.stagger.fast / 1000,
      delayChildren: 0.05,
    },
  },
};

export const staggerCard: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: tokens.stagger.card / 1000,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transition(tokens.duration.slow, tokens.easing.inOut),
  },
};

// === INTERACTION PRESETS (V16–V19) ===

export const buttonPress = {
  whileHover: { scale: tokens.scale.hover, transition: { duration: tokens.duration.fast / 1000 } },
  whileTap: { scale: tokens.scale.press, transition: { duration: tokens.duration.fast / 1000 } },
};

export const cardHover = {
  whileHover: {
    scale: tokens.scale.hover,
    y: -2,
    boxShadow: tokens.glow.hover,
    transition: { duration: tokens.duration.slow / 1000 },
  },
  whileTap: {
    scale: tokens.scale.press,
    transition: { duration: tokens.duration.fast / 1000 },
  },
};

export const iconButtonHover = {
  whileHover: {
    scale: tokens.scale.hoverIcon,
    transition: { duration: tokens.duration.fast / 1000 },
  },
  whileTap: {
    scale: tokens.scale.press,
    transition: { duration: tokens.duration.fast / 1000 },
  },
};

export const navTabActive = {
  whileHover: { scale: tokens.scale.activeTab },
  whileTap: { scale: tokens.scale.press },
};

// === OVERLAY PRESETS (V20–V22) ===

export const backdropFade: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: tokens.opacity.overlay, transition: transition(tokens.duration.normal, tokens.easing.out) },
  exit: { opacity: 0, transition: transition(tokens.duration.fast, tokens.easing.in) },
};

export const modalEnter: Variants = {
  hidden: { opacity: 0, scale: tokens.scale.modalBg, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: spring(400, 30),
  },
  exit: {
    opacity: 0,
    scale: 0.97,
    y: -10,
    transition: transition(tokens.duration.fast, tokens.easing.in),
  },
};

export const toastEnter: Variants = {
  hidden: { opacity: 0, x: 50, scale: 0.95 },
  visible: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: spring(300, 25),
  },
  exit: {
    opacity: 0,
    x: 50,
    scale: 0.95,
    transition: transition(tokens.duration.fast, tokens.easing.in),
  },
};

// === FEEDBACK PRESETS (V23–V26) ===

export const shakeError: Variants = {
  hidden: { x: 0 },
  visible: {
    x: [0, -4, 4, -4, 4, 0],
    transition: { duration: tokens.duration.slow / 1000, ease: tokens.easing.inOut as any },
  },
};

export const successPulse: Variants = {
  hidden: { scale: 1, borderColor: '#334155' },
  visible: {
    scale: [1, 1.02, 1],
    borderColor: ['#334155', '#00FFA3', '#334155'],
    transition: { duration: tokens.duration.reveal / 1000 },
  },
};

export const skeletonPulse: Variants = {
  hidden: { opacity: 0.6 },
  visible: {
    opacity: [0.6, 0.9, 0.6],
    transition: { duration: tokens.duration.decorative / 1000 / 2, repeat: Infinity, ease: tokens.easing.inOut as any },
  },
};

export const celebrationBanner: Variants = {
  hidden: { scale: 0, opacity: 0, rotate: -5 },
  visible: {
    scale: 1,
    opacity: 1,
    rotate: 0,
    transition: spring(200, 12),
  },
};

// === LAYOUT PRESET (V27) ===

export const layoutTransition: Transition = {
  duration: tokens.duration.slow / 1000,
  ease: tokens.easing.inOut as any,
};

// === AI PRESETS (V28–V35) — See Section 10 for full definitions ===

export const aiThinking: Variants = { /* defined in AI Motion section */ };
export const aiStreaming: Variants = { /* defined in AI Motion section */ };
export const aiSuggestion: Variants = { /* defined in AI Motion section */ };
export const aiAgentSpawn: Variants = { /* defined in AI Motion section */ };
export const aiAgentActive: Variants = { /* defined in AI Motion section */ };
export const aiAgentProcessing: Variants = { /* defined in AI Motion section */ };
export const aiAgentComplete: Variants = { /* defined in AI Motion section */ };
export const aiRecommendation: Variants = { /* defined in AI Motion section */ };
```

### 4.3 Preset Naming Convention

**PN1 — Preset names use camelCase and describe the visual behavior, not the component that uses them.**

| ✅ Correct | ❌ Incorrect |
|---|---|
| `fadeUp` | `pageSectionEnter` |
| `cardHover` | `dashboardCardInteraction` |
| `scaleSpringIn` | `modalAppearanceAnimation` |
| `toastEnter` | `notificationSlideIn` |

**PN2 — Preset categories are prefixed in comments but not in variable names:**
- Entry: `fadeIn`, `fadeUp`, `scaleIn`, `slideRight`, `heroReveal`, `scaleSpringIn`
- Exit: `fadeOut`, `scaleOut`, `slideOutRight`, `collapseOut`
- Stagger: `staggerContainer`, `staggerFast`, `staggerCard`, `staggerItem`
- Interaction: `buttonPress`, `cardHover`, `iconButtonHover`, `navTabActive`
- Overlay: `backdropFade`, `modalEnter`, `toastEnter`
- Feedback: `shakeError`, `successPulse`, `skeletonPulse`, `celebrationBanner`

**PN3 — Every preset has a version number (V1–V35+) in comments.** When updating a preset, increment the minor version. When removing a preset, note the deprecation in the comment.

### 4.4 Preset Usage Rule

**PUR1 — Components apply presets via `variants` prop. They never define variants internally.**

```typescript
// ✅ CORRECT: Component imports preset
import { buttonPress } from '@/packages/ui/animation-presets';

export function Button({ children }: Props) {
  return (
    <motion.button
      variants={buttonPress}
      whileHover="whileHover"
      whileTap="whileTap"
    >
      {children}
    </motion.button>
  );
}
```

```typescript
// ❌ INCORRECT: Component defines its own variants
export function Button({ children }: Props) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, transition: { duration: 0.1 } }}
      whileTap={{ scale: 0.96, transition: { duration: 0.08 } }}
    >
      {children}
    </motion.button>
  );
}
```

**PUR2 — If a component needs a variant that doesn't exist, create the variant in `animation-presets.ts`.** Do not create component-scoped variants. If the variant is truly component-specific (used in 1 place), add it with a `@internal` JSDoc tag and a note explaining why it shouldn't be shared.

**PUR3 — Stagger presets are applied via container/child pattern:**

```typescript
import { staggerContainer, staggerItem } from '@/packages/ui/animation-presets';

function TaskList() {
  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      {tasks.map(task => (
        <motion.div key={task.id} variants={staggerItem}>
          <TaskCard task={task} />
        </motion.div>
      ))}
    </motion.div>
  );
}
```

---

## 5. Component Animation Contracts

### 5.1 Contract Architecture

Every interactive component in the design system has a defined "animation contract" — a spec that maps component states to animation presets. This contract lives in the component's JSDoc block and is enforced during code review.

### 5.2 Component Contracts

#### Button

```typescript
/**
 * @motion
 * - Presets: buttonPress
 * - State transitions:
 *   - idle → hover: whileHover (100ms, scale 1.02)
 *   - hover → idle: revert (100ms, scale 1.0)
 *   - idle → active/tap: whileTap (80ms, scale 0.96)
 *   - active → idle: revert (80ms, scale 1.0)
 *   - enabled → disabled: opacity shift (150ms)
 * - Reduced motion: no scale changes, opacity only
 * - Layout: no layout animations
 * - Loading variant: <motion.button> shows spinner, scales to 1 immediately
 */
export function Button({ variant = 'primary', loading, disabled, children }: ButtonProps) {
  const shouldReduceMotion = useReducedMotionContext();

  return (
    <motion.button
      variants={shouldReduceMotion ? undefined : buttonPress}
      whileHover={shouldReduceMotion ? undefined : 'whileHover'}
      whileTap={shouldReduceMotion ? undefined : 'whileTap'}
      animate={{ opacity: disabled ? 0.5 : 1 }}
      transition={{ duration: 0.15 }}
    >
      {loading && <Spinner />}
      {children}
    </motion.button>
  );
}
```

#### Card

```typescript
/**
 * @motion
 * - Presets: cardHover (interactive cards), staggerItem (in grids)
 * - State transitions:
 *   - idle → hover: whileHover (200ms, scale 1.01, y -2, glow)
 *   - idle → tap: whileTap (100ms, scale 0.99)
 * - Entry: via staggerItem when inside staggerContainer
 * - Exit: collapseOut when removed from list
 * - Reduced motion: no scale/glow, static card
 * - Interactive cards only; display cards have no hover animation
 */
```

#### Modal

```typescript
/**
 * @motion
 * - Presets: backdropFade (backdrop), modalEnter (content)
 * - AnimatePresence wraps both backdrop and content
 * - Entry sequence: backdrop fade (150ms) → content scale spring (250ms)
 * - Exit sequence: content scale out (150ms) → backdrop fade (100ms)
 * - Trigger: isOpen boolean prop
 * - Reduced motion: instant opacity toggle, no scale
 * - Backdrop click dismisses with exit animation
 */
```

#### Input

```typescript
/**
 * @motion
 * - Presets: shakeError (validation error), successPulse (valid input)
 * - State transitions:
 *   - idle → error: shakeError (300ms, 3 oscillations)
 *   - error → idle: reset (150ms, border color transition)
 *   - idle → valid: successPulse (400ms, green border flash)
 * - Focus state: border color transition (CSS, not FM)
 * - Reduced motion: no shake, instant border color change
 * - Layout: no layout animations
 */
```

#### Sidebar

```typescript
/**
 * @motion
 * - Presets: slideRight (desktop sidebar), none (mobile bottom nav)
 * - State transitions:
 *   - collapsed → expanded: slideRight (300ms, x: -240 → 0)
 *   - expanded → collapsed: slideLeft (250ms, x: 0 → -240)
 * - Entry: on mount, slide from left (300ms)
 * - Reduced motion: instant width change
 * - Mobile: bottom nav has no animation (always visible)
 * - Layout: uses Framer Motion layout prop for content reflow
 */
```

#### Toast

```typescript
/**
 * @motion
 * - Presets: toastEnter
 * - AnimatePresence wraps toast container
 * - State transitions:
 *   - hidden → visible: toastEnter (spring, 300ms)
 *   - visible → exit: toastEnter.exit (150ms)
 * - Auto-dismiss: AnimatePresence onTimeout (4s)
 * - Stack: multiple toasts stack with y offset animation
 * - Reduced motion: instant appear/disappear
 * - Exit animation plays before component unmounts
 */
```

#### Dropdown / Select

```typescript
/**
 * @motion
 * - Presets: scaleIn (content), fadeIn (backdrop)
 * - State transitions:
 *   - closed → open: scaleIn (180ms)
 *   - open → closed: scaleOut (120ms)
 * - Positioning-aware: animates from trigger element
 * - Reduced motion: instant toggle
 * - AnimatePresence for exit
 */
```

#### Tab

```typescript
/**
 * @motion
 * - Presets: navTabActive, layoutTransition
 * - State transitions:
 *   - idle → active: navTabActive.hover (100ms)
 *   - active indicator: layoutTransition (300ms, smooth underline slide)
 * - Content transition: crossfade (200ms)
 * - Reduced motion: no scale, instant indicator
 * - Layout group: LayoutGroup coordinates tab indicator + content
 */
```

### 5.3 Contract Enforcement Rules

| Rule | Description |
|---|---|
| CER1 | Every new component must have a `@motion` JSDoc block in its contract format |
| CER2 | Components must import presets, not inline variants |
| CER3 | Components must check `useReducedMotionContext()` and disable motion when true |
| CER4 | Interactive components must define `whileHover`, `whileTap`, or `whileFocus` |
| CER5 | Components that open/close (modal, toast, dropdown) must use `AnimatePresence` |
| CER6 | `layout` prop is only used on components inside a `LayoutGroup` |

---

## 6. Global Motion Provider

### 6.1 Provider Architecture

```
<App>
  <MotionProvider>     ← Wraps entire app
    <MotionConfig>     ← Framer Motion global config
      {children}
    </MotionConfig>
  </MotionProvider>
</App>
```

### 6.2 File: `packages/ui/MotionProvider.tsx`

```typescript
'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { MotionConfig } from 'framer-motion';

// === Device Performance Tiers ===

export type MotionTier = 'full' | 'reduced' | 'minimal';

interface MotionContextValue {
  tier: MotionTier;
  isMotionReduced: boolean;
  prefersReducedMotion: boolean;
  deviceTier: 'high' | 'medium' | 'low';
}

const MotionContext = createContext<MotionContextValue>({
  tier: 'full',
  isMotionReduced: false,
  prefersReducedMotion: false,
  deviceTier: 'high',
});

export function useMotionContext(): MotionContextValue {
  return useContext(MotionContext);
}

export function useReducedMotionContext(): boolean {
  return useContext(MotionContext).isMotionReduced;
}

// === Device Tier Detection ===

function detectDeviceTier(): 'high' | 'medium' | 'low' {
  if (typeof window === 'undefined') return 'high';

  const memory = (navigator as any).deviceMemory;
  const cores = navigator.hardwareConcurrency;

  if (memory >= 8 && cores >= 8) return 'high';
  if (memory >= 4 && cores >= 4) return 'medium';
  return 'low';
}

// === Motion Tier Resolution ===

function resolveMotionTier(
  osPref: boolean,
  deviceTier: 'high' | 'medium' | 'low'
): MotionTier {
  if (osPref) return 'minimal';
  if (deviceTier === 'low') return 'reduced';
  return 'full';
}

// === MotionProvider Component ===

export function MotionProvider({ children }: { children: React.ReactNode }) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [deviceTier, setDeviceTier] = useState<'high' | 'medium' | 'low'>('high');

  useEffect(() => {
    setDeviceTier(detectDeviceTier());

    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mq.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  const tier = resolveMotionTier(prefersReducedMotion, deviceTier);
  const isMotionReduced = tier !== 'full';

  return (
    <MotionContext.Provider value={{ tier, isMotionReduced, prefersReducedMotion, deviceTier }}>
      <MotionConfig
        reducedMotion={prefersReducedMotion ? 'always' : 'never'}
        transition={{ duration: 0.2 }}
      >
        {children}
      </MotionConfig>
    </MotionContext.Provider>
  );
}
```

### 6.3 Provider Integration Rules

| Rule | Description |
|---|---|
| PIR1 | `MotionProvider` MUST be at the app root, wrapping all pages |
| PIR2 | `useReducedMotionContext()` is used in every animated component, not `useReducedMotion()` from Framer Motion directly (to ensure the context is available in tests) |
| PIR3 | Device tier is detected once on mount and cached — it does not change at runtime |
| PIR4 | The provider exposes `tier` for components to conditionally render complex animations (e.g., confetti only on `full` tier) |
| PIR5 | `MotionConfig reducedMotion` is set to `"always"` when OS preference is detected, `"never"` otherwise. This is Framer Motion's native hook, not a manual override |

### 6.4 Context Usage in Components

```typescript
// In any animated component:
function TaskCard() {
  const { isMotionReduced, tier } = useMotionContext();

  return (
    <motion.div
      initial={isMotionReduced ? undefined : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={isMotionReduced ? { duration: 0 } : { duration: 0.25 }}
      whileHover={isMotionReduced ? undefined : { scale: 1.01, y: -2 }}
    >
      {tier === 'full' && <GlowEffect />}
      <CardContent />
    </motion.div>
  );
}
```

---

## 7. Page Transition Architecture

### 7.1 Route Change Architecture

```
User clicks link
    │
    ▼
Start exit animation (old page) ─── 200ms
    │
    ▼
AnimatePresence mode="wait"
    │
    ▼
Start enter animation (new page) ─── 250ms
    │
    ▼
Page is interactive
```

### 7.2 File: `app/layout.tsx` (Page Transition Wrapper)

```typescript
'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { fadeUp, fadeOut } from '@/packages/ui/animation-presets';
import { useReducedMotionContext } from '@/packages/ui/MotionProvider';

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isReduced = useReducedMotionContext();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        variants={isReduced ? undefined : fadeUp}
        initial="hidden"
        animate="visible"
        exit={isReduced ? undefined : 'hidden'}
        transition={{ duration: isReduced ? 0 : undefined }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

### 7.3 Transition Types by Navigation Context

| Navigation Action | Entry | Exit | Duration | Preset |
|---|---|---|---|---|
| **Sidebar link click** | fadeUp (y: 12 → 0) | fadeOut (opacity: 1 → 0) | 250ms | `fadeUp` / `fadeOut` |
| **Tab switch** | Crossfade (opacity 0 → 1) | Crossfade (opacity 1 → 0) | 200ms | `fadeIn` / `fadeOut` |
| **Back/forward browser** | slideRight (x: -30 → 0) | slideRight (x: 0 → 30) | 300ms | `slideRight` / `slideOutRight` |
| **Deep link (external)** | scaleIn (0.98 → 1) + fade | Instant | 300ms | `scaleIn` |
| **Cmd+K navigate** | Instant | Instant | 0ms | None |
| **Modal route** | scaleSpringIn | scaleOut | 250ms | `scaleSpringIn` / `scaleOut` |

### 7.4 Page Transition Rules

| Rule | Description |
|---|---|
| PTR1 | Page transitions are handled at the layout level, not individual pages |
| PTR2 | `AnimatePresence mode="wait"` ensures exit completes before enter begins |
| PTR3 | The `key` prop on the animated wrapper MUST be the pathname to trigger re-animation |
| PTR4 | Cmd+K navigation uses 0ms transitions — it's a power user action that must be instant |
| PTR5 | Browser back/forward navigation uses slideRight (content slides in from left) to reinforce spatial awareness |
| PTR6 | Tab switches within the same page use crossfade (200ms), not full page transitions |
| PTR7 | Reduced motion: all page transitions become instant (0ms), even crossfade |

### 7.5 Sidebar Navigation Motion

| Element | Open | Close | Width Change | Duration |
|---|---|---|---|---|
| Desktop sidebar expanded | slideRight (x: -240 → 0) | slideRight (x: 0 → -240) | 240px → 64px (collapsed) | 250ms |
| Desktop sidebar collapsed | slideRight (x: -64 → 0) | slideRight (x: 0 → -64) | 64px → 240px (expanded) | 250ms |
| Mobile nav bottom sheet | slideRight (y: 100% → 0) | slideRight (y: 0 → 100%) | Full width | 250ms |
| Right detail panel | slideLeft (x: 400 → 0) | slideLeft (x: 0 → 400) | 400px overlay | 300ms |

**SBR1 — Sidebar width change uses `layout` prop on the sidebar container with `layoutTransition` preset.** Main content area uses `layout="position"` to reflow around the sidebar without animating its own width.

**SBR2 — Mobile sidebar is a bottom sheet, not a slide-from-left.** This follows platform convention and avoids gesture conflicts with system back-swipe.

---

## 8. GSAP Integration Architecture

### 8.1 When to Use GSAP

GSAP is reserved for animation types that Framer Motion handles poorly or cannot handle at all.

| Use Case | GSAP Feature | Why Not FM |
|---|---|---|
| Scroll-driven animations | ScrollTrigger | FM `useScroll` has limited control over scrubbing and pinning |
| Complex timeline sequences | GSAP Timeline | FM sequencing requires nested callbacks; GSAP timelines are declarative |
| SVG morphing | MorphSVGPlugin | FM cannot morph SVG path data |
| Text splitting + animation | SplitText | FM has no text-splitting utilities |
| Marquee / infinite scroll | GSAP with `repeat: -1` | FM loops require manual keyframes |
| Physics-based motion | GSAP Physics | FM springs are simpler but less configurable |

### 8.2 Import Strategy

```typescript
// GSAP is NEVER in the main bundle.
// It is dynamically imported ONLY when the animation type requires it.

async function initScrollAnimations() {
  const gsap = (await import('gsap')).gsap;
  const { ScrollTrigger } = await import('gsap/ScrollTrigger');
  gsap.registerPlugin(ScrollTrigger);

  gsap.from('.reveal-section', {
    scrollTrigger: '.reveal-section',
    y: 60,
    opacity: 0,
    duration: 0.8,
    ease: 'power2.out',
  });
}
```

### 8.3 GSAP Usage Rules

| Rule | Description |
|---|---|
| GUR1 | GSAP is dynamically imported — never a static import. Bundle size contribution: 25KB gzip max |
| GUR2 | Every GSAP animation must be wrapped in a `useEffect` cleanup that calls `ctx.revert()` |
| GUR3 | GSAP must never animate the same element that Framer Motion is animating. Use `data-gsap` attribute selectors to isolate GSAP targets |
| GUR4 | ScrollTrigger animations must use `scrub: 1` minimum to prevent scroll jank. No `scrub: 0` (instant scrub) |
| GUR5 | GSAP timeline durations must reference `tokens.duration.*` — no hardcoded duration values |
| GUR6 | On reduced motion, GSAP ScrollTrigger animations resolve immediately: `ScrollTrigger.refresh()` with all animations at progress 1 |

### 8.4 GSAP Integration Pattern

```typescript
'use client';

import { useEffect, useRef } from 'react';
import { useReducedMotionContext } from '@/packages/ui/MotionProvider';

export function ScrollRevealSection({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const isReduced = useReducedMotionContext();

  useEffect(() => {
    if (isReduced) return; // No GSAP animation on reduced motion

    let ctx: gsap.Context;

    (async () => {
      const gsap = (await import('gsap')).gsap;
      const { ScrollTrigger } = await import('gsap/ScrollTrigger');
      gsap.registerPlugin(ScrollTrigger);

      ctx = gsap.context(() => {
        gsap.from(ref.current?.querySelectorAll('.reveal-item'), {
          scrollTrigger: {
            trigger: ref.current,
            start: 'top 80%',
            end: 'bottom 20%',
            scrub: 1,
          },
          y: 40,
          opacity: 0,
          stagger: 0.1,
          duration: 0.6,
          ease: 'power2.out',
        });
      }, ref);
    })();

    return () => {
      ctx?.revert();
    };
  }, [isReduced]);

  return <div ref={ref}>{children}</div>;
}
```

### 8.5 GSAP Animation Registration

All GSAP animations in the codebase must be registered in a central manifest:

```typescript
// packages/ui/gsap-registry.ts
// Every GSAP animation in the system is registered here for audit and cleanup.

export const gsapAnimations = {
  scrollReveal: {
    file: 'components/ScrollRevealSection.tsx',
    purpose: 'Fade up sections on scroll',
    duration: 0.6,
    plugin: 'ScrollTrigger',
  },
  heroParallax: {
    file: 'components/HeroSection.tsx',
    purpose: 'Parallax background on hero',
    duration: 1.0,
    plugin: 'ScrollTrigger',
  },
  // Every GSAP animation must be added here
} as const;
```

---

## 9. Rive Integration Architecture

### 9.1 When to Use Rive

Rive is reserved for highly complex, multi-state visual animations that cannot be achieved with Framer Motion or GSAP.

| Use Case | Why Rive | Alternatives |
|---|---|---|
| Character animation (ARIA mascot) | State machine with multiple animation layers | Lottie, but Rive files are 60% smaller |
| Celebratory effects (streak, milestone) | Particle systems + state transitions | Custom confetti (FM), but Rive is more performant |
| Onboarding illustrations | Interactive state machines | Lottie, but Rive supports state triggers |
| Complex loading animations | Multi-layered animations with blending | CSS, but Rive enables complex shapes |

### 9.2 Asset Pipeline

```
Rive editor (.riv)
    │
    ▼
Export optimized .riv file  ← Max 200KB per file
    │
    ▼
Place in /public/rive/
    │
    ▼
Import via @rive-app/react-canvas
```

### 9.3 Rive Usage Rules

| Rule | Description |
|---|---|
| RUR1 | Rive files must not exceed 200KB each. Files exceeding this must be optimized (reduce artboard size, limit states, compress meshes) |
| RUR2 | Rive is loaded via dynamic import — never a static import. The `@rive-app/react-canvas` bundle only loads when a Rive animation is mounted |
| RUR3 | Every Rive animation must have a static fallback (static image or CSS animation) that renders when reduced motion is active |
| RUR4 | Rive state machines must use `stateMachine` input, not animation play/stop. This ensures predictable state transitions |
| RUR5 | Rive canvases must have explicit `width` and `height` attributes to prevent layout shift during loading |
| RUR6 | Only one Rive animation can be active on screen at a time. Multiple simultaneous Rive instances degrade performance |

### 9.4 Rive Integration Pattern

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useReducedMotionContext } from '@/packages/ui/MotionProvider';

export function CelebrationAnimation({ trigger }: { trigger: boolean }) {
  const [RiveComponent, setRiveComponent] = useState<React.ComponentType<any> | null>(null);
  const isReduced = useReducedMotionContext();

  useEffect(() => {
    if (isReduced) return; // No Rive animation on reduced motion

    (async () => {
      const { Rive } = await import('@rive-app/react-canvas');
      // Rive component is loaded only when needed
    })();
  }, [isReduced]);

  if (isReduced) {
    return <div className="static-celebration-fallback" />;
  }

  if (!trigger) return null;

  return (
    <div className="rive-container" style={{ width: 300, height: 300 }}>
      <rive-canvas
        src="/rive/celebration.riv"
        stateMachine="main"
        autoplay
      />
    </div>
  );
}
```

### 9.5 Rive Asset Inventory

Every Rive file in the project must be documented:

| File | Size | States | Purpose | Fallback |
|---|---|---|---|---|
| `/public/rive/celebration.riv` | 180KB | idle, burst, settle | Streak milestone celebration | Static SVG badge |
| `/public/rive/loading-orb.riv` | 45KB | idle, active, complete | Full-page loading indicator | CSS spinner |
| `/public/rive/aria-character.riv` | 195KB | idle, thinking, speaking, listening | AI assistant avatar | Static SVG avatar |

---

## 10. AI Motion Architecture

### 10.1 AI Motion Philosophy

**AI motion is system communication, not decoration.** Every AI motion pattern must answer one of these questions within 500ms:

1. "Is the system working?" (Thinking/Loading)
2. "What stage is it in?" (Processing → Complete)
3. "What should I do?" (Suggestion/Recommendation)
4. "What just happened?" (Agent state change)

### 10.2 AI Motion Presets (V28–V35)

All AI motion presets are defined in `packages/ui/animation-presets.ts` alongside UI presets. They follow the same architecture and are consumed by the same components.

#### V28 — aiThinking (Thinking Indicator)

```typescript
// Communicates "the AI is processing your request"
// Visual: pulsing glow ring + subtle scale oscillation
// Duration: 1s cycle, continuous while thinking
// Trigger: user sends message / AI begins processing

export const aiThinking: Variants = {
  idle: { opacity: 0.6, scale: 1 },
  active: {
    opacity: [0.6, 1, 0.6],
    scale: [1, 1.02, 1],
    boxShadow: [
      tokens.glow.hover,
      tokens.glow.ai,
      tokens.glow.hover,
    ],
    transition: {
      duration: tokens.duration.decorative / 1000 / 3,
      repeat: Infinity,
      ease: tokens.easing.inOut as any,
    },
  },
};
```

**Thinking dots** (staggered bounce for "..." indicator):

```typescript
export const thinkingDots = {
  container: {
    initial: {},
    animate: {
      transition: { staggerChildren: 0.15, repeat: Infinity, repeatDelay: 0.3 },
    },
  },
  dot: {
    initial: { y: 0, opacity: 0.3 },
    animate: {
      y: [0, -6, 0],
      opacity: [0.3, 1, 0.3],
      transition: { duration: 0.6, ease: tokens.easing.out as any },
    },
  },
};
```

#### V29 — aiStreaming (Text Streaming)

```typescript
// Communicates "content is arriving in real-time"
// Visual: each token/word appears with a brief fade-up
// Duration: 30-50ms per character, 80-120ms per word
// Trigger: AI generates response tokens

export const aiStreaming: Variants = {
  hidden: { opacity: 0, y: 4, filter: 'blur(2px)' },
  visible: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: { duration: 0.15, ease: tokens.easing.out as any },
  },
};

// Streaming cursor (blinking underscore)
export const aiStreamingCursor = {
  initial: { opacity: 1 },
  animate: {
    opacity: [1, 0, 1],
    transition: { duration: 0.6, repeat: Infinity, ease: tokens.easing.linear as any },
  },
};
```

#### V30 — aiSuggestion (Suggestion Appearance)

```typescript
// Communicates "the AI has a suggestion for you"
// Visual: ghost text fades in below input, subtle accent glow
// Duration: 400ms total
// Trigger: AI detects opportunity to suggest

export const aiSuggestion: Variants = {
  hidden: { opacity: 0, y: -4, height: 0 },
  visible: {
    opacity: 1,
    y: 0,
    height: 'auto',
    transition: {
      duration: tokens.duration.reveal / 1000,
      ease: tokens.easing.inOut as any,
    },
  },
  exit: {
    opacity: 0,
    y: 4,
    height: 0,
    transition: { duration: tokens.duration.normal / 1000, ease: tokens.easing.in as any },
  },
};
```

#### V31 — aiRecommendation (Recommendation Card)

```typescript
// Communicates "here is something you might want to act on"
// Visual: card slides in from right with glow, settles to position
// Duration: 450ms spring
// Trigger: AI identifies a recommendation

export const aiRecommendation: Variants = {
  hidden: { opacity: 0, x: 40, scale: 0.95, boxShadow: '0 0 0px rgba(99,102,241,0)' },
  visible: {
    opacity: 1,
    x: 0,
    scale: 1,
    boxShadow: tokens.glow.ai,
    transition: {
      type: 'spring',
      stiffness: 250,
      damping: 22,
      mass: 0.8,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    scale: 0.97,
    transition: { duration: tokens.duration.fast / 1000, ease: tokens.easing.in as any },
  },
  hover: {
    boxShadow: tokens.glow.primary,
    transition: { duration: tokens.duration.normal / 1000 },
  },
};
```

#### V32 — aiAgentSpawn (Agent Entrance)

```typescript
// Communicates "an AI agent is now active"
// Visual: agent icon spawns from trigger point (scale 0→1 with glow burst)
// Duration: 300ms spring
// Trigger: user invokes an AI agent

export const aiAgentSpawn: Variants = {
  hidden: { opacity: 0, scale: 0, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 350,
      damping: 20,
      mass: 0.6,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    y: -10,
    transition: { duration: tokens.duration.fast / 1000, ease: tokens.easing.in as any },
  },
};

// Spawn burst ring (expanding ring from agent spawn point)
export const aiAgentBurst: Variants = {
  hidden: { scale: 0, opacity: 0.6 },
  visible: {
    scale: 3,
    opacity: 0,
    transition: { duration: 0.5, ease: tokens.easing.out as any },
  },
};
```

#### V33 — aiAgentActive (Agent Idle State)

```typescript
// Communicates "the agent is ready and listening"
// Visual: subtle ambient pulse on agent icon
// Duration: 2s cycle, continuous while agent is active
// Trigger: agent has spawned and is ready

export const aiAgentActive: Variants = {
  idle: { opacity: 1, scale: 1, boxShadow: tokens.glow.hover },
  listening: {
    opacity: [1, 0.8, 1],
    scale: [1, 1.03, 1],
    boxShadow: [tokens.glow.hover, tokens.glow.ai, tokens.glow.hover],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: tokens.easing.inOut as any,
    },
  },
};
```

#### V34 — aiAgentProcessing (Agent Working State)

```typescript
// Communicates "the agent is processing your request"
// Visual: gradient sweep across agent icon / speed lines
// Duration: 1.5s cycle
// Trigger: agent begins processing

export const aiAgentProcessing: Variants = {
  idle: { opacity: 1 },
  active: {
    opacity: [0.7, 1, 0.7],
    rotate: [0, 5, -5, 0],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: tokens.easing.inOut as any,
    },
  },
};

// Processing speed lines (GSAP for this — too complex for FM)
// See: packages/components/ai/ProcessingSpeedLines.tsx
```

#### V35 — aiAgentComplete (Agent Finished State)

```typescript
// Communicates "the agent has finished"
// Visual: checkmark draw animation + brief success glow, then settles
// Duration: 400ms
// Trigger: agent completes processing

export const aiAgentComplete: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: { duration: 0.4, ease: tokens.easing.out as any },
  },
};

// Completion glow burst (expanding and fading accent ring)
export const aiCompleteBurst: Variants = {
  hidden: { scale: 0.5, opacity: 0.5, boxShadow: tokens.glow.neon },
  visible: {
    scale: 2.5,
    opacity: 0,
    transition: { duration: 0.6, ease: tokens.easing.out as any },
  },
};
```

### 10.3 AI Motion State Machine

```
                    ┌──────────┐
                    │  Idle    │
                    └────┬─────┘
                         │ User sends input
                         ▼
                    ┌──────────┐
              ┌────→│ Thinking │←────┐
              │     │ (V28)    │     │
              │     └────┬─────┘     │
              │          │           │
              │          ▼           │
              │     ┌──────────┐     │
              │     │Streaming │     │ Agent fallback
              │     │ (V29)    │─────┤
              │     └────┬─────┘     │
              │          │           │
              │          ▼           │
              │     ┌──────────┐     │
              │     │ Complete │     │
              │     │ (V35)    │─────┘
              │     └────┬─────┘
              │          │
              │     ┌──────────┐
              └─────│   Idle   │
                    └──────────┘
```

**Agent-specific flow:**

```
Agent invoked
    │
    ▼
[Spawn] ─→ [Active/Listening] ─→ [Processing] ─→ [Complete] ─→ [Exit]
  V32          V33                    V34              V35         V32 exit
```

### 10.4 AI Motion Rules

| Rule | Description |
|---|---|
| AIR1 | AI thinking animation must activate within 100ms of user input. If the AI responds faster than 300ms, skip the thinking animation entirely |
| AIR2 | Streaming text uses 30-50ms per character. At this rate, a 500-character response appears in 2.5 seconds max |
| AIR3 | Recommendation cards always enter from the right (future direction) and exit to the left (past direction) |
| AIR4 | Agent processing animation must loop exactly 3 times maximum. If processing takes longer than 4.5 seconds, show a determinate progress bar instead |
| AIR5 | On reduced motion, all AI animations become instant state toggles. No thinking pulse, no streaming reveal — show content immediately when available |
| AIR6 | AI motion is always interruptible. If the user sends a new message while AI is responding, the current animation terminates immediately |

---

## 11. Motion Performance Architecture

### 11.1 Bundle Budgets

| Library | Gzip Size | Load Strategy | When Loaded |
|---|---|---|---|
| Framer Motion | 30KB | Static import (main bundle) | App bootstrap |
| GSAP core | 17KB | Dynamic import (lazy) | On first GSAP animation mount |
| GSAP ScrollTrigger | 8KB | Dynamic import (lazy) | On first ScrollTrigger mount |
| GSAP MorphSVG | 5KB | Dynamic import (lazy) | On first SVG morph |
| @rive-app/react-canvas | 35KB | Dynamic import (lazy) | On first Rive mount |
| Total (FM only) | 30KB | — | — |
| Total (all libraries) | 95KB | — | Only when features demand it |

### 11.2 Runtime Budgets

| Metric | Hard Limit | Warning | Measurement |
|---|---|---|---|
| JS execution per animation frame | 5ms | 3ms | `performance.now()` in `requestAnimationFrame` |
| Concurrent animated elements | 12 | 8 | Framer Motion DevTools |
| Concurrent GSAP tweens | 20 | 12 | GSAP `getTweensOf()` |
| `will-change` declarations per page | 8 | 5 | CSS audit script |
| GPU memory for animations | 50MB | 30MB | Chrome Task Manager |
| Animation init latency | 50ms | 30ms | Interaction readiness |
| Layout thrashing events | 0 | 0 | Layout boundary checks |

### 11.3 Animation Performance Rules

| Rule | Description |
|---|---|
| APR1 | Only animate `opacity` and `transform`. Never animate `width`, `height`, `top`, `left`, `margin`, or `padding` |
| APR2 | Use CSS `@keyframes` for decorative loops (glow pulse, shimmer). No JavaScript runtime cost for infinite loops |
| APR3 | Use `will-change` sparingly — set on the animating element before the animation starts, remove after it settles. Never set `will-change` on more than 8 elements per page |
| APR4 | Virtualized lists (100+ items) must not animate off-screen items. Only animate items within the visible viewport + 1 buffer row |
| APR5 | IntersectionObserver pauses decorative animations when the element is off-screen. Resume on re-entry |
| APR6 | Battery-sensitive: continuous animations (glow pulse, ambient) pause when the page is backgrounded. Use `document.visibilitychange` |
| APR7 | SVG animations with Framer Motion must use `motion.path` with `pathLength`, not CSS `stroke-dashoffset` |
| APR8 | GSAP ScrollTrigger animations must use `scrub: 1` minimum. `scrub: 0` causes scroll jank |

### 11.4 Device Performance Tier System

| Tier | Target Devices | Animations Enabled | Complexity Level |
|---|---|---|---|
| **Full** | Desktop (M1+, 8GB+ RAM, modern GPU) | All animations, springs, glows, confetti, parallax, Rive | Unlimited |
| **Reduced** | Mid-range mobile, older desktop (4-8GB RAM, integrated GPU) | No glow effects, no parallax, linear transitions instead of springs, no Rive, no GSAP scroll-triggered reveals | 60% of Full |
| **Minimal** | Budget mobile, low-end devices (<4GB RAM, <4 cores) | Crossfade only (200ms max), no decorative animations, no stagger, no hover effects, all state changes via instant transforms | 20% of Full |
| **Accessibility** | User preference / assistive technology | 0ms transitions, instant state changes, no decorative animations, no parallax, no stagger, no hover, loading spinners replaced with static indicators | 0% of Full (functional only) |

**Tier Detection:**

```typescript
function getDeviceTier(): 'full' | 'reduced' | 'minimal' {
  const mem = (navigator as any).deviceMemory; // undefined if not supported
  const cores = navigator.hardwareConcurrency;

  if (!mem && !cores) return 'full'; // Desktop fallback (no device memory API)
  if ((mem ?? 8) >= 8 && cores >= 8) return 'full';
  if ((mem ?? 4) >= 4 && cores >= 4) return 'reduced';
  return 'minimal';
}
```

### 11.5 Performance CI Checks

Every PR is checked for:

| Check | Method | Failure Action |
|---|---|---|
| No ad-hoc animation values | Lint rule: no `transition={{` with numeric values outside presets | Block PR |
| Bundle size | `size-limit` config for FM (30KB), GSAP (lazy), Rive (lazy) | Warning at 90%, Block at 100% |
| `will-change` count | CSS audit script counts `will-change` declarations per page | Warning >5, Block >8 |
| No layout-animating properties | Lint rule: no `width`/`height`/`top`/`left` inside `motion.*` components | Block PR |
| Reduced motion paths | Test: verify all animated components have reduced-motion equivalent | Block PR if missing |

---

## 12. Motion Testing Architecture

### 12.1 Testing Philosophy

**Animations are behavior, not decoration.** They must be tested like any other behavior — not ignored in test environments.

### 12.2 Test Categories

| Test Type | What It Verifies | Tool | Priority |
|---|---|---|---|
| **Unit** | Animation variants are applied correctly, transitions fire | Jest + Testing Library | P0 |
| **Integration** | AnimatePresence exit/enter sequences, layout animations | Jest + Testing Library | P1 |
| **Visual regression** | Animation frames match expected appearance | Chromatic / Percy | P1 |
| **Accessibility** | Reduced motion paths, no flashing, no unannounced motion | Jest + axe-core | P0 |
| **Performance** | Bundle sizes, frame rates, will-change counts | Lighthouse CI + size-limit | P1 |

### 12.3 Unit Testing Pattern

```typescript
import { render } from '@testing-library/react';
import { MotionConfig } from 'framer-motion';
import { Button } from './Button';

describe('Button motion', () => {
  it('renders without animation in reduced motion mode', () => {
    const { container } = render(
      <MotionConfig reducedMotion="always">
        <Button>Click me</Button>
      </MotionConfig>
    );

    // In reduced motion mode, no motion props are applied
    expect(container.querySelector('[style]')).toBeNull();
  });

  it('applies motion variants in normal mode', () => {
    const { container } = render(
      <MotionConfig reducedMotion="never">
        <Button>Click me</Button>
      </MotionConfig>
    );

    // Component has motion attributes
    const button = container.querySelector('button');
    expect(button).toHaveAttribute('style');
  });

  it('disables animation when loading', () => {
    const { container } = render(
      <Button loading>Click me</Button>
    );

    expect(container.querySelector('[data-loading]')).toBeTruthy();
  });
});
```

### 12.4 Animation Testing Rules

| Rule | Description |
|---|---|
| ATR1 | Test wrappers use `<MotionConfig reducedMotion="always">` to disable real animations in unit tests |
| ATR2 | Test that exit animations fire by wrapping in `<AnimatePresence>` and toggling mount state |
| ATR3 | Verify `useReducedMotionContext()` is correctly consumed by checking class name toggles |
| ATR4 | Visual regression tests capture enter animation settled state (500ms delay) |
| ATR5 | Test AI streaming by asserting character-by-character DOM updates at expected intervals |
| ATR6 | Test reduced motion by asserting `opacity: 1` and `transform: none` on elements |

### 12.5 Reduced Motion Test Matrix

| Component | Full Motion | Reduced Motion | Test File |
|---|---|---|---|
| Button | whileHover scale 1.02, whileTap scale 0.96 | No scale, instant opacity | `Button.test.tsx` |
| Card | hover y -2 + glow, entry stagger | Static entry, no hover | `Card.test.tsx` |
| Modal | spring scale + fade entry | Instant opacity toggle | `Modal.test.tsx` |
| Toast | spring slide from right | Instant appear | `Toast.test.tsx` |
| Sidebar | slide from left 300ms | Instant width change | `Sidebar.test.tsx` |
| AI Thinking | pulse glow + scale oscillation | Static indicator | `AIThinking.test.tsx` |
| AI Streaming | character-by-character reveal | Full content immediately | `AIStreaming.test.tsx` |

---

## 13. Motion Dev Tooling

### 13.1 Development Tools

| Tool | Use Case | Setup |
|---|---|---|
| **Framer Motion DevTools** | Visualize animation variants, FPS timeline, layout animations | Chrome extension |
| **GSAP DevTools** | Debug GSAP timelines, ScrollTrigger markers | Include `gsap-trial` with DevTools |
| **Chrome Performance tab** | Frame rate analysis, JS cost of animations | DevTools > Performance |
| **Chrome Rendering tab** | Paint flashing, layer borders, FPS meter | DevTools > Rendering |
| **React DevTools Profiler** | Component render cost during animations | DevTools > Profiler |
| **Motion Audit Script** | Checks for ad-hoc variants, missing presets, inline durations | `node scripts/audit-motion.mjs` |

### 13.2 Motion Audit Script

Create `scripts/audit-motion.mjs`:

```javascript
// Motion Architecture Audit Script
// Checks every .tsx file for:
// 1. Hardcoded transition values (duration, ease)
// 2. Inline variants (not imported from presets)
// 3. framer-motion imports in page files
// 4. Missing AnimatePresence for conditional renders
// 5. Missing reduced-motion checks

const fs = require('fs');
const path = require('path');

const APP_DIR = './apps/web/app';
const RESULTS = [];

function auditFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  // Check 1: Hardcoded duration values
  if (content.match(/duration:\s*\d+(\.\d+)?/)) {
    RESULTS.push({ file: filePath, issue: 'Hardcoded duration value', severity: 'error' });
  }

  // Check 2: framer-motion import in page files (not components)
  if (filePath.includes('/app/') && !filePath.includes('/components/')) {
    if (content.includes("from 'framer-motion'")) {
      RESULTS.push({ file: filePath, issue: 'Direct framer-motion import in page', severity: 'warn' });
    }
  }

  // Check 3: Missing reduced-motion context
  if (content.includes('whileHover') || content.includes('whileTap')) {
    if (!content.includes('useReducedMotionContext') && !content.includes('useReducedMotion')) {
      RESULTS.push({ file: filePath, issue: 'Interactive animation without reduced motion check', severity: 'error' });
    }
  }

  // Check 4: Hardcoded cubic-bezier
  if (content.match(/cubic-bezier\([^)]+\)/)) {
    RESULTS.push({ file: filePath, issue: 'Hardcoded cubic-bezier value', severity: 'warn' });
  }
}

// Walk the directory and audit
function walkDir(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory() && !file.startsWith('_') && !file.startsWith('.')) {
      walkDir(fullPath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      auditFile(fullPath);
    }
  }
}

walkDir(APP_DIR);

// Report
if (RESULTS.length === 0) {
  console.log('✅ Motion Audit: Clean — no violations found');
} else {
  console.log(`🔍 Motion Audit: ${RESULTS.length} issues found`);
  for (const r of RESULTS) {
    console.log(`  [${r.severity.toUpperCase()}] ${r.file}: ${r.issue}`);
  }
}
```

### 13.3 Dev Tooling Rules

| Rule | Description |
|---|---|
| DTR1 | Framer Motion DevTools Chrome extension is required for all frontend developers |
| DTR2 | Motion audit script runs as a pre-commit hook (`npx tsx scripts/audit-motion.mjs`) |
| DTR3 | GSAP DevTools markers (`ScrollTrigger.debug = true`) are allowed in development only — stripped from production builds |
| DTR4 | The debug overlay (`__MOTION_DEV_TOOLS__ = true`) is toggled via URL param `?motion-debug` |
| DTR5 | Animation performance is profiled in every PR that touches motion code. PR description must include "Motion Impact: [none/low/medium/high]" |

---

## 14. Implementation Roadmap

### 14.1 Phase Overview

```
Phase 1 ─── Phase 2 ─── Phase 3 ─── Phase 4 ─── Phase 5 ─── Phase 6 ─── Phase 7
  Tokens     Presets     Components  Per-page    AI Motion   GSAP+Rive   Testing
   + CSS      + Provider  contracts   transitions  patterns    integration + CI
```

### 14.2 Phase Details

#### Phase 1 — Token Implementation (Sprint 1)

| Task | Output | Depends On |
|---|---|---|
| Create `packages/ui/tokens.ts` | All 40+ motion tokens | None |
| Generate CSS custom properties from tokens | `--duration-*`, `--easing-*`, `--stagger-*`, etc. in `globals.css` | `tokens.ts` |
| Update `tailwind.config.js` extend section | Tailwind utilities for animation | CSS custom properties |
| Create `packages/ui/MotionProvider.tsx` | Provider with device tier detection + reduced-motion context | None |
| Validate: audit script against all page files | Baseline report of current violations | Audit script |

#### Phase 2 — Animation Preset Library (Sprint 2)

| Task | Output | Depends On |
|---|---|---|
| Create `packages/ui/animation-presets.ts` | V1–V35+ variant definitions | Phase 1 tokens |
| Define all entry, exit, stagger, interaction, overlay, feedback presets | Complete preset library | None |
| Define AI motion presets (V28–V35) | AI motion patterns | None |
| Write tests for all presets | `animation-presets.test.ts` | Preset library |
| Integrate `MotionProvider` into app root `layout.tsx` | Global motion context | Phase 1 provider |

#### Phase 3 — Component Integration (Sprint 3)

| Task | Output | Depends On |
|---|---|---|
| Refactor `<Button>` to use `buttonPress` preset | Updated `Button.tsx` | Phase 2 presets |
| Refactor `<Card>` to use `cardHover` + `staggerItem` | Updated `Card.tsx` | Phase 2 presets |
| Refactor `<Modal>` to use `modalEnter` + `backdropFade` | Updated `Modal.tsx` | Phase 2 presets |
| Refactor `<Toast>` to use `toastEnter` | Updated toast component | Phase 2 presets |
| Refactor `<Sidebar>` to use `slideRight` | Updated `Sidebar.tsx` | Phase 2 presets |
| Refactor `<Input>` to use `shakeError` + `successPulse` | Updated `Input.tsx` | Phase 2 presets |
| Add `@motion` JSDoc contracts to all 7 components | Documentation | Component refactoring |
| Write component motion tests | `Button.test.tsx`, etc. | Component refactoring |

#### Phase 4 — Page Transitions (Sprint 4)

| Task | Output | Depends On |
|---|---|---|
| Create `<PageTransition>` wrapper | Layout-level `AnimatePresence` | Phase 2 presets |
| Configure transition types by navigation context | Sidebar, tab, back/forward, deep link, Cmd+K | PageTransition wrapper |
| Add `LayoutGroup` for content reflow animations | Smooth filter/sort transitions | None |
| Remove ad-hoc page-level animation code | Clean 17 page files | Phase 3 components |
| Verify: audit script shows zero violations | Clean audit | Page cleanup |

#### Phase 5 — AI Motion Patterns (Sprint 5)

| Task | Output | Depends On |
|---|---|---|
| Build `<AIThinkingIndicator>` component | Thinking pulse + dots | Phase 2 AI presets |
| Build `<AIStreamingText>` component | Character-by-character reveal | Phase 2 AI presets |
| Build `<AISuggestion>` component | Suggestion fade-in | Phase 2 AI presets |
| Build `<AIRecommendationCard>` component | Recommendation slide-in | Phase 2 AI presets |
| Build `<AIAgentAvatar>` component | Agent state machine | Phase 2 AI presets |
| Wire AI components into chat system | Functional AI motion | AI component library |
| Write AI motion tests | All AI component tests | AI component library |

#### Phase 6 — GSAP + Rive Integration (Sprint 6)

| Task | Output | Depends On |
|---|---|---|
| Add GSAP dynamic import utility | `useGSAP` hook with cleanup | None |
| Build `<ScrollRevealSection>` | GSAP ScrollTrigger fade-up | GSAP hook |
| Build `<HeroParallax>` | GSAP scroll-driven parallax | GSAP hook |
| Build `<CelebrationEffect>` (Rive) | Rive celebration integration | Rive setup |
| Build `<AIAvatar>` (Rive) | Rive character animation | Rive setup |
| Build `<RiveLoading>` | Rive loading indicator | Rive setup |
| Register all GSAP animations in gsap-registry | Registry manifest | GSAP components |
| Write GSAP + Rive tests | Integration tests | Components |

#### Phase 7 — Testing + Performance CI (Sprint 7)

| Task | Output | Depends On |
|---|---|---|
| Set up `size-limit` config for animation bundles | Bundle budget enforcement | All phases |
| Add reduced-motion integration tests to CI | `prefers-reduced-motion` test suite | Phase 3 components |
| Add motion audit script to pre-commit hook | Pre-commit enforcement | Audit script |
| Add performance profiling to PR template | Motion Impact section | None |
| Run full test suite, fix regressions | Green CI pipeline | All phases |

### 14.3 Dependency Map

```
Phase 1 (Tokens)
    │
    ▼
Phase 2 (Presets + Provider)
    │                   │
    ├───────────────────┤
    ▼                   ▼
Phase 3 (Components)   Phase 5 (AI Motion)
    │                   │
    ▼                   │
Phase 4 (Pages)        │
    │                   │
    ├───────────────────┤
    ▼
Phase 6 (GSAP+Rive)
    │
    ▼
Phase 7 (Testing+CI)
```

---

## 15. Motion Governance

### 15.1 PR Review Checklist

Every PR containing animation code MUST pass this checklist before merging:

| # | Check | Applies To |
|---|---|---|
| 1 | All animation parameters use tokens from `tokens.ts` | All files |
| 2 | All variants are imported from `animation-presets.ts` | All files |
| 3 | Component has `@motion` JSDoc block | New/existing components |
| 4 | Reduced motion path exists and is tested | All animated components |
| 5 | No `width`, `height`, `top`, `left` in `motion.*` style props | All files |
| 6 | `will-change` count per page ≤ 8 | All pages |
| 7 | Stagger total ≤ 500ms | Staggered lists |
| 8 | AnimatePresence wraps all conditional renders | Modals, toasts, dropdowns |
| 9 | Dynamic import for GSAP, static import for FM | Library imports |
| 10 | GSAP animation cleanup in `useEffect` return | GSAP files |
| 11 | Rive file ≤ 200KB | Rive files |
| 12 | Rive has static fallback | Rive components |
| 13 | AI motion interrupts on new user input | AI components |
| 14 | No framer-motion imports in page files | `app/` directory |
| 15 | Audit script passes (zero violations) | All files |

### 15.2 Lint Rules

Configure ESLint to enforce:

```json
{
  "rules": {
    // No framer-motion imports in page files
    "no-restricted-imports": ["error", {
      "paths": [{
        "name": "framer-motion",
        "importNames": ["motion", "AnimatePresence", "useReducedMotion"],
        "message": "Import from @/packages/ui/animation-presets instead. Pages should not use framer-motion directly."
      }]
    }],

    // No hardcoded transition values
    "no-restricted-syntax": ["warn", {
      "selector": "JSXAttribute[name.name='transition'] > JSXExpressionContainer > ObjectExpression > Property[key.name='duration']",
      "message": "Use tokens.duration.* instead of hardcoded duration values."
    }],

    // No AnimatePresence without key
    "no-restricted-syntax": ["error", {
      "selector": "JSXElement[openingElement.name.name='AnimatePresence'] > JSXElement[openingElement.attributes.length=0]",
      "message": "AnimatePresence children must have a unique key prop."
    }]
  }
}
```

### 15.3 Deprecation Process

When an animation preset or pattern is deprecated:

1. Mark the preset with `@deprecated` JSDoc and version note
2. Keep the preset for 2 versions (backward compatibility)
3. Run audit script to identify all usages
4. Migrate usages to new preset
5. Remove deprecated preset in version +2

```typescript
/**
 * @deprecated Use `fadeUp` instead (v2.0.0)
 * Will be removed in v4.0.0
 */
export const oldFadeUp: Variants = { ... };
```

### 15.4 Governance Rules

| Rule | Description |
|---|---|
| GR1 | Motion Design Director must approve new presets before merge |
| GR2 | Component animation contracts are reviewed as part of the component spec review |
| GR3 | Monthly motion audit: run audit script, report violations, track remediation |
| GR4 | Quarterly motion performance review: bundle sizes, frame rates, device tier distribution |
| GR5 | Animation-related bug reports are tagged `motion` and triaged at P1 or higher |
| GR6 | Every release notes include a "Motion Changes" section |

---

## 16. Decision Trees

### 16.1 Library Selection Decision Tree

```
"Which animation library should I use?"

Do I need to animate...
│
├── A UI state change? (hover, tap, enter, exit, open, close)
│   → Framer Motion
│   └── Is it a decorative loop? (glow, shimmer, ambient)
│       → CSS @keyframes
│
├── A scroll-driven effect? (parallax, reveal, pin)
│   → GSAP ScrollTrigger (dynamic import)
│
├── A complex timeline? (multi-step sequence, SVG morph)
│   → GSAP timeline (dynamic import)
│
├── A character animation? (ARIA mascot, complex loading)
│   → Rive (dynamic import)
│
├── A celebratory burst? (confetti, streak milestone)
│   → Rive (preferred) or Framer Motion (simple bursts)
│
├── A data-driven update? (chart entry, counter, progress)
│   → Framer Motion (layout animations, useMotionValue)
│
└── A streaming text reveal? (AI response)
    → Framer Motion (staggered children, not GSAP)
```

### 16.2 Preset Selection Decision Tree

```
"Which entry preset should I use?"

How important is the content?
│
├── Hero / Primary (critical information)
│   → heroReveal (400ms, emphasis easing, y: 30)
│
├── Important (section headers, key metrics)
│   → fadeUp (250ms, y: 12)
│
├── Standard (cards, list items, content blocks)
│   → staggerItem (inside staggerContainer or staggerCard)
│
├── Supporting (metadata, secondary info)
│   → fadeIn (150ms, no y movement)
│
└── Modal/overlay content
    → scaleSpringIn (250ms, spring)
```

### 16.3 AI Motion Selection Decision Tree

```
"Which AI motion pattern should I use?"

What is the system doing?
│
├── Processing user input
│   → aiThinking (V28) — pulsing glow + dots
│   └── Will response be >300ms?
│       → Yes: Show thinking animation immediately
│       → No: Skip, show response directly
│
├── Generating a response
│   → aiStreaming (V29) — character-by-character reveal
│
├── Offering a suggestion
│   → aiSuggestion (V30) — ghost text fade-in
│
├── Recommending an action
│   → aiRecommendation (V31) — slide-in card with glow
│
├── Spawning an AI agent
│   → aiAgentSpawn (V32) — scale 0→1 + burst ring
│   └── Agent is now active
│       → aiAgentActive (V33) — ambient pulse
│       └── Agent is processing
│           → aiAgentProcessing (V34) — speed lines/oscillation
│           └── Agent is done
│               → aiAgentComplete (V35) — checkmark draw + glow burst
│
└── Done
    → Settle to idle state
```

### 16.4 Component Animation Decision Tree

```
"Does my interactive component need a @motion contract?"

Does the component...
│
├── Have visual states? (hover, active, disabled, focus)
│   → Yes: Define interaction presets (whileHover, whileTap)
│
├── Open/close? (modal, toast, dropdown, sidebar)
│   → Yes: Define entry/exit presets + AnimatePresence
│
├── Reorder or filter? (task list, sortable table)
│   → Yes: LayoutGroup + layoutTransition
│
├── Show/hide content? (accordion, expandable card)
│   → Yes: height/opacity transition with AnimatePresence
│
├── Display in a list/grid? (card, task row)
│   → Yes: staggerContainer + staggerItem
│
└── None of the above (static display component)?
    → No motion contract needed
```

---

## 17. Library-Specific Rules

### 17.1 Framer Motion Rules

| Rule | Description |
|---|---|
| FMR1 | `motion.div` is the default animated element. Only use `motion.span`, `motion.button`, etc. when the HTML element semantics matter |
| FMR2 | `AnimatePresence mode="wait"` for page transitions, `mode="popLayout"` for list mutations |
| FMR3 | `layoutId` is required on elements within `LayoutGroup` that animate between positions |
| FMR4 | `useReducedMotionContext()` from `MotionProvider` is preferred over Framer Motion's `useReducedMotion()` to ensure consistency in tests |
| FMR5 | Spring transitions use stiffness 300-500, damping 25-35 for UI elements. Lower stiffness = looser spring |
| FMR6 | `onAnimationComplete` is used for sequencing, not nested timeouts |
| FMR7 | `initial={false}` is set on components that mount already in their visible state (prevents initial animation) |

### 17.2 GSAP Rules

| Rule | Description |
|---|---|
| GSR1 | Every GSAP animation must be wrapped in `gsap.context()` for automatic cleanup |
| GSR2 | ScrollTrigger `markers: true` is allowed in development only; stripped via `process.env.NODE_ENV === 'production'` |
| GSR3 | GSAP animations must use `data-gsap` attribute selectors, never class or ID selectors (to avoid conflicts with FM) |
| GSR4 | SVG morph animations use MorphSVGPlugin with `shapeIndex` for predictable morphing |
| GSR5 | Timeline animations use `position: '<'` or `position: '-=0.2'` for overlap, not absolute delays |
| GSR6 | `gsap.matchMedia()` is used for responsive GSAP animations (different behavior on mobile vs desktop) |

### 17.3 Rive Rules

| Rule | Description |
|---|---|
| RR1 | Rive state machine inputs are the primary control mechanism. Animation play/stop is secondary |
| RR2 | Rive canvases must have explicit `width` and `height` set to prevent layout shift |
| RR3 | Rive files are optimized with `--compress` flag before commit |
| RR4 | Rive animations pause when the document is hidden (`document.hidden`) |
| RR5 | Every Rive component renders a static SVG fallback when JS is disabled or reduced motion is active |

---

## 18. Appendix: Quick Reference

### 18.1 Duration Reference

| Token | ms | Used For |
|---|---|---|
| `duration.instant` | 0 | Reduced motion fallback, state snaps |
| `duration.fast` | 80 | Button press, tap feedback |
| `duration.normal` | 150 | Toggles, checkboxes, dropdown open |
| `duration.slow` | 250 | Card hover, list item, tooltip |
| `duration.nav` | 300 | Page transitions, sidebar |
| `duration.reveal` | 400 | Content reveal, modal entry |
| `duration.decorative` | 3000 | Glow pulse, ambient loop |
| `duration.celebration` | 1000 | Confetti, milestone burst |

### 18.2 Preset Quick Reference

| ID | Preset | Type | Duration | Key Property |
|---|---|---|---|---|
| V1 | `fadeIn` | Entry | 150ms | opacity 0→1 |
| V2 | `fadeUp` | Entry | 250ms | opacity 0→1, y 12→0 |
| V3 | `fadeDown` | Entry | 250ms | opacity 0→1, y -12→0 |
| V4 | `scaleIn` | Entry | 150ms | opacity 0→1, scale 0.96→1 |
| V5 | `slideRight` | Entry | 250ms | opacity 0→1, x -20→0 |
| V6 | `slideLeft` | Entry | 250ms | opacity 0→1, x 20→0 |
| V7 | `heroReveal` | Entry | 400ms | opacity 0→1, y 30→0, scale 0.98→1 |
| V8 | `scaleSpringIn` | Entry | 250ms | spring(400, 30), scale 0.9→1 |
| V9 | `fadeOut` | Exit | 80ms | opacity 1→0 |
| V10 | `scaleOut` | Exit | 80ms | opacity 1→0, scale 1→0.96 |
| V11 | `slideOutRight` | Exit | 80ms | opacity 1→0, x 0→20 |
| V12 | `collapseOut` | Exit | 150ms | opacity 1→0, height auto→0 |
| V13 | `staggerContainer` | Stagger | 50ms/item | staggerChildren: 0.05 |
| V14 | `staggerFast` | Stagger | 30ms/item | staggerChildren: 0.03 |
| V15 | `staggerCard` | Stagger | 100ms/item | staggerChildren: 0.1 |
| V16 | `buttonPress` | Interaction | 80-100ms | hover scale 1.02, tap scale 0.96 |
| V17 | `cardHover` | Interaction | 200ms | scale 1.01, y -2, glow |
| V18 | `iconButtonHover` | Interaction | 80-100ms | hover scale 1.05, tap scale 0.96 |
| V19 | `navTabActive` | Interaction | 100ms | hover scale 1.04, tap scale 0.96 |
| V20 | `backdropFade` | Overlay | 150ms | opacity 0→0.6 |
| V21 | `modalEnter` | Overlay | 250ms | spring(400, 30), scale 0.95→1 |
| V22 | `toastEnter` | Overlay | 300ms | spring(300, 25), x 50→0 |
| V23 | `shakeError` | Feedback | 300ms | x oscillation ±4px |
| V24 | `successPulse` | Feedback | 400ms | scale pulse, border flash |
| V25 | `skeletonPulse` | Feedback | 1.5s loop | opacity 0.6⇄0.9 |
| V26 | `celebrationBanner` | Feedback | 1s | spring(200, 12), scale 0→1 |
| V27 | `layoutTransition` | Layout | 250ms | ease inOut |
| V28 | `aiThinking` | AI | 1s loop | opacity/scale pulse, glow |
| V29 | `aiStreaming` | AI | 150ms/word | opacity 0→1, y 4→0, blur 2→0 |
| V30 | `aiSuggestion` | AI | 400ms | opacity 0→1, y -4→0, height 0→auto |
| V31 | `aiRecommendation` | AI | 450ms | spring(250, 22), x 40→0, scale 0.95→1 |
| V32 | `aiAgentSpawn` | AI | 300ms | spring(350, 20), scale 0→1 |
| V33 | `aiAgentActive` | AI | 2s loop | ambient pulse, glow |
| V34 | `aiAgentProcessing` | AI | 1.5s loop | opacity/rotate oscillation |
| V35 | `aiAgentComplete` | AI | 400ms | pathLength 0→1, glow burst |

### 18.3 Library Import Rules

| Library | Import Style | Import Path | Bundle |
|---|---|---|---|
| Framer Motion | Static | `from 'framer-motion'` | Main bundle (30KB) |
| GSAP | Dynamic | `await import('gsap')` | Lazy (17KB) |
| GSAP ScrollTrigger | Dynamic | `await import('gsap/ScrollTrigger')` | Lazy (8KB) |
| GSAP MorphSVG | Dynamic | `await import('gsap/MorphSVGPlugin')` | Lazy (5KB) |
| @rive-app/react-canvas | Dynamic | `await import('@rive-app/react-canvas')` | Lazy (35KB) |

### 18.4 File Reference

| File | Purpose | Created In |
|---|---|---|
| `packages/ui/tokens.ts` | Animation token definitions | Phase 1 |
| `packages/ui/MotionProvider.tsx` | Global motion context provider | Phase 1 |
| `packages/ui/animation-presets.ts` | Shared Framer Motion variants (V1–V35) | Phase 2 |
| `packages/ui/gsap-registry.ts` | GSAP animation manifest | Phase 6 |
| `apps/web/app/layout.tsx` | PageTransition wrapper integration | Phase 4 |
| `scripts/audit-motion.mjs` | Motion architecture audit script | Phase 1 |
| `.eslintrc.json` (motion rules) | ESLint rules for animation enforcement | Phase 7 |

### 18.5 Common Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|---|---|---|
| `transition={{ duration: 0.3 }}` in a page file | Hardcoded value, not using token | Use `tokens.duration.slow` |
| `const variants = {...}` in a component | Duplicate variant definition | Import from `animation-presets.ts` |
| AnimatePresence without `mode` | Default behavior may cause visual glitches | Specify `mode="wait"` or `mode="popLayout"` |
| `whileHover` on touch-only elements | Touch devices don't hover, animation never triggers | Use `whileTap` for touch, `whileHover` as enhancement |
| `width`/`height` animation | Triggers layout recalculations, causes jank | Use `scaleX`/`scaleY` or `clip-path` |
| `useEffect` for sequencing | Fragile, not interruptible | Use Framer Motion `onAnimationComplete` or GSAP timeline |
| GSAP in same element as FM | Two libraries fighting for the same properties | Use `data-gsap` attribute selectors to isolate targets |
| Rive without size attributes | Causes Cumulative Layout Shift (CLS) | Always set explicit `width` and `height` |

---

> **Maintenance:** This document is updated per release cycle. New animated components must reference presets from `animation-presets.ts`. Deviations require Motion Architecture review.
>
> **Related documents:** `docs/design/MotionSystem.md` (design specs), `docs/design/DesignStrategy.md` §18 (strategy), `docs/design/Accessibility.md` §7 (reduced motion), `docs/design/10_DesignSystem.md` (component tokens).
