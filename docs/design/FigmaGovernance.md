# Figma Governance â€” Second Brain OS (ARIA)

> **The design-to-code constitution for Antigravity (design system), Stitch (component library), and every Figma file across the Second Brain OS ecosystem.**
>
> Authored by: Principal Design Systems Director, Figma Architect, Enterprise UI Governance Lead, Frontend Architect, Accessibility Specialist.
>
> This document is the single source of truth for Figma workspace structure, token management, component naming, auto layout rules, variant governance, design reviews, version control, and developer handoff. Every Figma file in the organization must conform to these standards.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-FIG-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal â€” Design & Engineering |
| Target Audience | Design Team, Engineering Team, AI Agents, Design System Contributors, Design Reviewers |
| Companion Docs | Design.md (design blueprint), DesignStrategy.md (strategic foundation), DesignSystemResearch.md (token research), MotionArchitecture.md (motion engineering), 35_DesignTokens.md (token reference), 10_DesignSystem.md (component catalog), FrontendAccessibilityGuide.md (a11y) |

---

## Table of Contents

**Part I â€” Governance & Structure**
1. [Executive Governance Strategy](#1-executive-governance-strategy)
2. [Figma Workspace Structure](#2-figma-workspace-structure)
3. [Naming Convention Standards](#3-naming-convention-standards)

**Part II â€” Layout & Grid**
4. [Auto Layout Standards](#4-auto-layout-standards)
5. [Grid Standards](#5-grid-standards)

**Part III â€” Tokens & Components**
6. [Design Token Governance](#6-design-token-governance)
7. [Component Governance](#7-component-governance)
8. [Variant Governance](#8-variant-governance)

**Part IV â€” Quality & Compliance**
9. [Accessibility Governance](#9-accessibility-governance)
10. [Asset Governance](#10-asset-governance)

**Part V â€” Process & Future**
11. [Documentation Standards](#11-documentation-standards)
12. [Design Review Process](#12-design-review-process)
13. [Version Control Process](#13-version-control-process)
14. [Release Process](#14-release-process)
15. [Future Expansion Rules](#15-future-expansion-rules)

---

```mermaid
%%
init: {
  'theme': 'base',
  'themeVariables': {
    'background': '#0A0B0F',
    'primaryColor': '#13151A',
    'primaryBorderColor': '#6366F1',
    'primaryTextColor': '#F1F5F9',
    'lineColor': '#818CF8',
    'secondaryColor': '#1A1D24',
    'tertiaryColor': '#00FFA3',
    'fontFamily': 'DM Sans',
    'fontSize': '14px'
  }
}
%%
graph LR
  subgraph Design["ðŸ–Œï¸ Design Layer"]
    F[Figma Design System<br/>Antigravity] --> T[Design Tokens<br/>Colors, Spacing, Typography]
  end

  subgraph Code["ðŸ’» Code Layer"]
    T --> S[Stitch Component Library<br/>React + Tailwind]
    S --> P[Page Composition<br/>Next.js Pages]
  end

  subgraph Review["âœ… Review Layer"]
    P --> DR[Design Review<br/>Accessibility + Visual]
    DR --> PR[Pull Request Review<br/>Code + Token Compliance]
  end

  subgraph Deploy["ðŸš€ Deploy Layer"]
    PR --> CI[CI/CD Pipeline<br/>Build + Test + Lint]
    CI --> D[Production Deploy<br/>Vercel + Railway]
  end

  D -.->|Feedback Loop| F

  style Design fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Code fill:#13151A,stroke:#6366F1,color:#F1F5F9
  style Review fill:#13151A,stroke:#00FFA3,color:#F1F5F9
  style Deploy fill:#13151A,stroke:#00FFA3,color:#F1F5F9
```

---

# Part I â€” Governance & Structure

---

## 1. Executive Governance Strategy

### 1.1 Governance Model

Second Brain OS uses a **Centralized Library + Federated Consumption** governance model:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    DESIGN SYSTEM COUNCIL                          â”‚
â”‚          Principal Design Director + Figma Architect              â”‚
â”‚              + Frontend Architect + A11y Specialist               â”‚
â”‚         Approves: breaking changes, new components, tokens,       â”‚
â”‚                   naming conventions, accessibility standards     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â–¼                â–¼                â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Antigravity     â”‚ â”‚  Stitch       â”‚ â”‚  Module Teams   â”‚
â”‚  (Design System) â”‚ â”‚  (Components)  â”‚ â”‚  (Consumers)    â”‚
â”‚                  â”‚ â”‚               â”‚ â”‚                 â”‚
â”‚  Library owner   â”‚ â”‚  Code owner   â”‚ â”‚  Use libraries  â”‚
â”‚  Creates tokens,  â”‚ â”‚  Implements   â”‚ â”‚  via Tokens     â”‚
â”‚  foundations,    â”‚ â”‚  components   â”‚ â”‚  Studio + npm   â”‚
â”‚  component specs  â”‚ â”‚  from specs   â”‚ â”‚                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 1.2 Governance Levels

| Level | Scope | Authority | Review Cadence |
|---|---|---|---|
| **L1 â€” Strategic** | Cross-system decisions: token architecture, naming conventions, accessibility policy | Design System Council (DSG Council) | Quarterly |
| **L2 â€” Tactical** | Component additions, variant changes, deprecations, minor token additions | Design Systems Lead + Figma Architect | Bi-weekly (sprint-aligned) |
| **L3 â€” Operational** | Bug fixes, style alignment, asset updates, documentation improvements | Individual designers (self-service with checklist) | Continuous / daily standup |

### 1.3 Decision Rights Matrix

| Decision | Propose | Review | Approve | Inform |
|---|---|---|---|---|
| New color token | DSG Council | A11y Specialist | DSG Council | All teams |
| New component | Design Lead | Figma Architect + FE Architect | DSG Council | Module teams |
| Variant addition | Component owner | Design Lead + FE Lead | Design Systems Lead | â€” |
| Breaking change | Any | DSG Council | DSG Council | All teams + changelog |
| Token value change | Design Systems Lead | A11y Specialist | Design Systems Lead | All teams |
| Deprecation | Component owner | Design Systems Lead | DSG Council | All teams + migration guide |
| Naming change | Figma Architect | DSG Council | DSG Council | All teams |
| Access grant | Team lead | Workspace admin | Figma Architect | â€” |

### 1.4 Quality Gates

Every component must pass these gates before reaching Stable status:

| Gate | Requirement | Verification |
|---|---|---|
| **G1 â€” Token Audit** | No hardcoded values; every fill, stroke, effect, and text style uses a token | Manual + Plugin scan |
| **G2 â€” Auto Layout** | Auto Layout enabled on all frames; responsive constraints per breakpoint | Manual inspection |
| **G3 â€” Variant Coverage** | All required states (default, hover, active, focus, disabled, loading, error) exist | Checklist verification |
| **G4 â€” A11y Scan** | Color contrast â‰¥ 4.5:1 (AA), touch targets â‰¥ 44px, focus indicators visible | a11y plugin |
| **G5 â€” Handoff Ready** | Dev Mode annotations, inspect layer naming, export settings, component description | Design Lead review |
| **G6 â€” Coded Match** | Dev Handoff includes comparison screenshot; code parity approved by FE engineer | Pair review |

### 1.5 AI Agent Roles in Figma Governance

| Role | Responsibility | Tools |
|---|---|---|
| **Token Auditor** | Scan files for hardcoded values, validate token usage, report drift | Figma Plugin API, GitHub Actions |
| **Variant Checker** | Verify all required states exist per component, flag missing variants | Figma REST API |
| **A11y Scanner** | Check contrast ratios, touch target sizes, focus indicator visibility | a11y plugins + custom scripts |
| **Handoff Generator** | Auto-generate Dev Mode descriptions, export settings, code snippets | Tokens Studio + Figma API |
| **Release Bot** | Manage library publishing, version bumps, changelog generation | GitHub Actions + Figma API |

### 1.6 Governance Enforcement

| Mechanism | Frequency | Tool |
|---|---|---|
| Automated token audit scan | Every commit (CI) | Figma Plugin API + GitHub Actions |
| Component variant completeness check | Weekly | Figma REST API |
| Accessibility compliance scan | Per release | axe-core + a11y Figma plugin |
| Style drift report (design vs. code) | Bi-weekly | Tokens Studio diff + custom script |
| Library publish compliance check | Per publish | Figma Library API |
| Design review checklist | Per component review | Figma Comments + Notion |

---

## 2. Figma Workspace Structure

### 2.1 Organization Hierarchy

```
Second Brain OS (Organization)
â”‚
â”œâ”€â”€ Antigravity (Team)                    # Design system team
â”‚   â”œâ”€â”€ Design Tokens (Project)
â”‚   â”‚   â”œâ”€â”€ Tokens.json                   # Tokens Studio source
â”‚   â”‚   â”œâ”€â”€ Token Documentation           # Figma file with token visualization
â”‚   â”‚   â””â”€â”€ Theme Swatches                # Dark / Light / High Contrast swatch files
â”‚   â”‚
â”‚   â”œâ”€â”€ Foundations (Project)
â”‚   â”‚   â”œâ”€â”€ 01_Color                      # Color system: primitives, semantic aliases, charts
â”‚   â”‚   â”œâ”€â”€ 02_Typography                 # Font families, type scale, text styles
â”‚   â”‚   â”œâ”€â”€ 03_Spacing                    # 4px base grid, spacing scale, layout patterns
â”‚   â”‚   â”œâ”€â”€ 04_Iconography               # Icon grid, lucide library, custom icons
â”‚   â”‚   â”œâ”€â”€ 05_Elevation                 # Shadows, z-index, depth system
â”‚   â”‚   â”œâ”€â”€ 06_Motion                    # Duration, easing, animation presets
â”‚   â”‚   â””â”€â”€ 07_Grid                      # Grid templates, breakpoints, responsive rules
â”‚   â”‚
â”‚   â”œâ”€â”€ Antigravity Library (Project)    # SHARED LIBRARY â€” published to all teams
â”‚   â”‚   â”œâ”€â”€ Atoms                        # Button, Input, Card, Badge, Tooltip, etc.
â”‚   â”‚   â”œâ”€â”€ Molecules                    # FormField, InputGroup, SearchBar, TabBar, etc.
â”‚   â”‚   â”œâ”€â”€ Organisms                    # Sidebar, Navbar, DataTable, KanbanBoard, etc.
â”‚   â”‚   â”œâ”€â”€ Patterns                     # Empty states, loading skeletons, error pages
â”‚   â”‚   â””â”€â”€ Templates                    # Page-level layout shells (dashboard, modal, etc.)
â”‚   â”‚
â”‚   â””â”€â”€ Sandbox (Project)                # Experimental / WIP components
â”‚       â”œâ”€â”€ Proposals                    # Component proposals with specs
â”‚       â”œâ”€â”€ In_Review                    # Components under DSG review
â”‚       â””â”€â”€ Archive                      # Deprecated or rejected experiments
â”‚
â”œâ”€â”€ Stitch (Team)                         # Component engineering team
â”‚   â”œâ”€â”€ Component Specs (Project)         # Handoff files for each component
â”‚   â”‚   â”œâ”€â”€ Atoms_Specs                  # 1:1 with Antigravity Atoms
â”‚   â”‚   â”œâ”€â”€ Molecules_Specs              # 1:1 with Antigravity Molecules
â”‚   â”‚   â””â”€â”€ Organisms_Specs              # 1:1 with Antigravity Organisms
â”‚   â”‚
â”‚   â”œâ”€â”€ Component Audit (Project)        # Design vs. code comparison
â”‚   â”‚   â”œâ”€â”€ Implemented                    # Green â€” coded match verified
â”‚   â”‚   â”œâ”€â”€ In_Progress                    # Yellow â€” in active development
â”‚   â”‚   â””â”€â”€ Gap                            # Red â€” no code equivalent
â”‚   â”‚
â”‚   â””â”€â”€ Migration (Project)              # Breaking change migration planning
â”‚       â”œâ”€â”€ Current â†’ Target              # Side-by-side comparison
â”‚       â””â”€â”€ Migration Guide               # Step-by-step update instructions
â”‚
â”œâ”€â”€ Modules (Team)                         # Feature teams (consumers)
â”‚   â”œâ”€â”€ 01_Application_Shell             # Sidebar, Navbar, responsive shell
â”‚   â”œâ”€â”€ 02_Dashboard                     # Dashboard page, KPI strip, bento grid
â”‚   â”œâ”€â”€ 03_Tasks_Courses                 # Task list, course grid, kanban
â”‚   â”œâ”€â”€ 04_Goals_Habits                  # Goals with roadmap, habit calendar
â”‚   â”œâ”€â”€ 05_Ideas_Projects                # Idea pipeline, project phases
â”‚   â”œâ”€â”€ 06_Sleep_Income_Time             # Sleep tracker, income log, pomodoro
â”‚   â”œâ”€â”€ 07_Resources_Opportunities       # Resource library, radar view
â”‚   â”œâ”€â”€ 08_Chat_Automation_Youtube       # AI chat, cron triggers, video library
â”‚   â””â”€â”€ 09_Academics                     # Academic module, semester view
â”‚
â””â”€â”€ Design Ops (Team)                      # Design operations
    â”œâ”€â”€ Design Review (Project)            # Review files, feedback, annotations
    â”œâ”€â”€ Design Sprint (Project)            # Current sprint design work
    â”œâ”€â”€ Assets (Project)                   # Shared imagery, illustrations, video
    â””â”€â”€ Archive (Project)                  # Historical design files
```

### 2.2 Library Linking Topology

```
Antigravity Library (Published)
â”‚
â”œâ”€â”€ Enables â†’ Modules (all 9 project files)
â”‚   â””â”€â”€ Module files use components from the published library
â”‚       (never detach instances in module files)
â”‚
â”œâ”€â”€ Enables â†’ Stitch Component Specs
â”‚   â””â”€â”€ Spec files reference library components when showing expected behavior
â”‚
â”œâ”€â”€ Enables â†’ Antigravity Sandbox
â”‚   â””â”€â”€ Proposals draft new components using existing library primitives
â”‚
â””â”€â”€ Depends on â†’ Tokens Studio JSON
    â””â”€â”€ All components reference tokens from the Tokens Studio source
```

### 2.3 File Structure Standards

Each Figma file MUST follow this page structure:

```
Page 1: Cover / Changelog
Page 2: Component Index (overview grid of all components in file)
Page 3: [Component Name] â€” Overview
Page 4: [Component Name] â€” States / Variants
Page 5: [Component Name] â€” Specs (auto layout, sizing, spacing)
Page 6: [Component Name] â€” Do / Don't
Page N: [Next Component] â€” ...
Final Page: Dev Handoff
```

### 2.4 Page Naming Convention

| Suffix | Purpose | When to Use |
|---|---|---|
| `Cover / Changelog` | Version history, file metadata, change log | Every file â€” MUST be page 1 |
| `Index` | Component overview grid with names and thumbnails | Every library file |
| `â€” Overview` | Component specification: anatomy, tokens, behavior | Per component |
| `â€” States` | State machine matrix: default, hover, active, focus, disabled, loading, error, empty | Per component with states |
| `â€” Variants` | Variant matrix: sizes, styles, themes, breakpoints | Per component with variants |
| `â€” Specs` | Auto layout, padding, gap, sizing, responsive rules | Per component |
| `â€” Do / Don't` | Usage guidance, anti-patterns, context rules | Per component |
| `â€” Dev Handoff` | Export settings, code snippets, implementation notes | Per component |

---

## 3. Naming Convention Standards

### 3.1 Universal Naming Rules

| Construct | Convention | Example | Rule |
|---|---|---|---|
| Pages | PascalCase | `Button â€” States` | Page names in file navigator |
| Frames | kebab-case + purpose suffix | `button-default`, `input-group-horizontal` | No PascalCase for frames |
| Components | PascalCase | `Button`, `InputField`, `DataTable` | Published component names |
| Variant Properties | camelCase | `size`, `variantStyle`, `hasIcon` | Property names in component set |
| Variant Values | kebab-case | `primary`, `md`, `with-icon` | Value strings in component set |
| Boolean Variants | `is` prefix | `isDisabled`, `isLoading`, `isSelected` | Boolean properties start with `is` |
| Tokens (Primitives) | kebab-case, category prefix | `color-blue-500`, `spacing-4`, `radius-lg` | Token Studio primitives |
| Tokens (Semantic) | kebab-case, purpose-based | `color-bg-card`, `color-text-primary`, `shadow-elevation-2` | Token Studio semantic |
| Styles | `.` prefix + kebab-case | `.btn-primary`, `.card-interactive` | Figma text/fill styles |
| Variables | `$` prefix + kebab-case | `$color-accent-primary`, `$spacing-page-margin` | Figma variables |
| Icons | snake_case | `check_circle`, `alert_triangle`, `plus` | lucide-react naming |
| Assets | kebab-case + context | `empty-state-tasks`, `onboarding-step-01` | Illustration / image files |
| Components (instance) | PascalCase, no prefix | `Button`, `Card`, `Sidebar` | No vendor prefix |

### 3.2 Frame Naming Patterns

Every frame MUST include a suffix that describes its purpose:

| Suffix | Purpose | Example |
|---|---|---|
| `-container` | Wrapper/parent frame | `dashboard-container` |
| `-group` | Grouped elements (no auto layout) | `icon-group` |
| `-stack` | Vertical auto layout | `form-stack` |
| `-row` | Horizontal auto layout | `button-row` |
| `-grid` | Grid layout | `card-grid` |
| `-content` | Dynamic/content area | `modal-content` |
| `-wrapper` | Absolute-positioned wrapper | `tooltip-wrapper` |
| `-item` | Individual item in a list | `list-item` |
| `-cell` | Table/grid cell | `table-cell` |
| `-header` | Section/component header | `card-header` |
| `-footer` | Section/component footer | `modal-footer` |
| `-slot` | Component slot / placeholder | `header-slot` |
| `-overlay` | Overlay/modal backdrop | `modal-overlay` |
| `-icon` | Icon layer | `status-icon` |
| `-label` | Text label | `input-label` |

### 3.3 Component Naming Hierarchy

```
[Domain]-[Component]-[Variant]-[State]
```

| Level | Convention | Example |
|---|---|---|
| **Domain** | Optional â€” only for module-specific components | `TaskCard`, `HabitCalendar` |
| **Component** | PascalCase, noun | `Button`, `InputField`, `DataTable` |
| **Variant** | camelCase property, kebab-case value | size=md, variantStyle=primary |
| **State** | camelCase property, kebab-case value | state=hover, state=disabled |

Full example component set properties:
- Property 1: `type` = `primary | secondary | ghost | danger`
- Property 2: `size` = `sm | md | lg`
- Property 3: `state` = `default | hover | active | focus | disabled`

### 3.4 Layer Naming in Components

All layers within a component MUST be named using the pattern:

```
[ComponentPart] [Descriptor]
```

| Layer | Name | Reason |
|---|---|---|
| Background fill | `Container` | The component's outermost shape |
| Text label | `Label` | Primary text content |
| Text description | `Description` | Secondary text content |
| Icon | `Icon` | Icon element |
| Icon (trailing) | `Icon Trailing` | Trailing/right-side icon |
| Input field | `Input` | Text input area |
| Placeholder text | `Placeholder` | Input placeholder |
| Error message | `Error` | Validation error text |
| Optional indicator | `Optional` | "(Optional)" label |
| Required indicator | `Required` | "*" indicator |
| Counter | `Counter` | Character count |
| Dropdown chevron | `Chevron` | Select dropdown indicator |
| Close button | `Close` | Modal/dismiss close button |
| Action button | `Action` | CTA within component |
| Avatar image | `Avatar` | User avatar |
| Badge dot | `Badge` | Notification/status badge |
| Progress fill | `Progress` | Progress bar fill |

### 3.5 Naming Anti-Patterns

| âŒ Anti-Pattern | Why | âœ… Correct |
|---|---|---|
| `Rectangle 1`, `Rectangle 2` | Auto-generated, meaningless | `Container`, `Background` |
| `Frame 2394` | No semantic meaning | `card-container` |
| `Button Copy 2` | Version-based, fragile | `Button` (use variants) |
| `#FF3366` fill on layer | Hardcoded value | `$color-accent-cyber` |
| `antigravity-button` | Vendor prefix not needed | `Button` |
| `btn-primary` | BEM class name in design | `Button` (type=primary) |
| `Desktop/Button/State` | Slash naming in single layer | Use component sets |

---

# Part II â€” Layout & Grid

---

## 4. Auto Layout Standards

### 4.1 Universal Auto Layout Rules

**Every component frame MUST use Auto Layout.** Exceptions require Design Systems Lead approval.

| Rule | Specification | Enforcement |
|---|---|---|
| **AL1** | All component root frames use Auto Layout | Automated scan |
| **AL2** | All nested containers use Auto Layout | Automated scan |
| **AL3** | No absolute positioning inside components | Review gate G2 |
| **AL4** | All spacing references tokens only | Review gate G1 |
| **AL5** | Every frame has explicit padding, gap, and sizing | Checklist |

### 4.2 Spacing Scale (4px Base)

| Token | Value | Tailwind | Usage |
|---|---|---|---|
| `spacing-0` | 0px | `gap-0` `p-0` | No spacing |
| `spacing-0\.5` | 2px | `gap-0.5` `p-0.5` | Micro spacing, icon gaps |
| `spacing-1` | 4px | `gap-1` `p-1` | Small inline gaps |
| `spacing-1\.5` | 6px | `gap-1.5` `p-1.5` | Tight icon+text |
| `spacing-2` | 8px | `gap-2` `p-2` | Default stack gap |
| `spacing-3` | 12px | `gap-3` `p-3` | Inline element gap |
| `spacing-4` | 16px | `gap-4` `p-4` | Card padding default |
| `spacing-5` | 20px | `gap-5` `p-5` | Section spacing |
| `spacing-6` | 24px | `gap-6` `p-6` | Modal padding, column gap |
| `spacing-7` | 28px | `gap-7` `p-7` | Card grid gaps |
| `spacing-8` | 32px | `gap-8` `p-8` | Section spacing large |
| `spacing-10` | 40px | `gap-10` `p-10` | Page margins desktop |
| `spacing-12` | 48px | `gap-12` `p-12` | Page margins wide |
| `spacing-16` | 64px | `gap-16` `p-16` | Hero/section spacing |
| `spacing-20` | 80px | `gap-20` `p-20` | Major section breaks |

### 4.3 Padding Rules by Component Type

| Component Type | Default Padding | Tight | Loose |
|---|---|---|---|
| **Card** | `spacing-5` (20px) | `spacing-4` (16px) | `spacing-6` (24px) |
| **Modal** | `spacing-6` (24px) | `spacing-5` (20px) | `spacing-8` (32px) |
| **Button** | Horizontal: `spacing-4` (16px), Vertical: `spacing-2` (8px) | `spacing-3` / `spacing-1.5` | `spacing-5` / `spacing-3` |
| **Input** | Horizontal: `spacing-3` (12px), Vertical: `spacing-2` (8px) | `spacing-2` / `spacing-1.5` | `spacing-4` / `spacing-3` |
| **Table cell** | `spacing-3` (12px) | `spacing-2` (8px) | `spacing-4` (16px) |
| **Badge** | Horizontal: `spacing-2` (8px), Vertical: `spacing-0.5` (2px) | â€” | â€” |
| **Tooltip** | `spacing-2` (8px) | â€” | â€” |
| **Dropdown item** | Horizontal: `spacing-3` (12px), Vertical: `spacing-2` (8px) | â€” | â€” |
| **Section** | `spacing-6` (24px) | `spacing-4` (16px) | `spacing-8` (32px) |

### 4.4 Gap Rules

| Context | Stack (Vertical) | Inline (Horizontal) | Grid |
|---|---|---|---|
| **Component internals** | `spacing-2` (8px) | `spacing-2` (8px) | `spacing-4` (16px) |
| **Form stack** | `spacing-5` (20px) | `spacing-3` (12px) | â€” |
| **Card grid** | `spacing-6` (24px) | `spacing-6` (24px) | `spacing-6` (24px) |
| **List items** | `spacing-2` (8px) | â€” | â€” |
| **Icon + text** | â€” | `spacing-2` (8px) | â€” |
| **Button group** | `spacing-3` (12px) | `spacing-3` (12px) | â€” |
| **Modal sections** | `spacing-6` (24px) | â€” | â€” |
| **KPI strip** | â€” | `spacing-6` (24px) | â€” |
| **Navigation items** | `spacing-1` (4px) | â€” | â€” |

### 4.5 Alignment Rules by Component Type

| Component | Horizontal Alignment | Vertical Alignment | Text Alignment |
|---|---|---|---|
| **Button** | Center | Center | Center |
| **Input** | Left | Center | Left |
| **Card** | Left | Top | Left |
| **Card â€” interactive** | Left | Top | Left |
| **Modal** | Left | Top | Left |
| **Badge** | Center | Center | Center |
| **Tooltip** | Left | Center | Left |
| **Table header** | Left (per column) | Center | Left |
| **Table cell** | Left (per column) | Center | Left |
| **Dropdown menu** | Left | Center | Left |
| **Tab** | Center | Center | Center |
| **Checkbox / Radio** | Left | Center | Left |
| **Toggle** | Left | Center | Left |
| **KPI metric** | Left | Center | Left |
| **StatCard** | Center | Center | Center |

### 4.6 Sizing Strategy

| Sizing Mode | Rule | Example Components |
|---|---|---|
| **Hug** | Content determines width and height | Badge, Tooltip, Icon |
| **Fill** | Fills parent container width | Input, Button (in form), Card (in grid) |
| **Fixed** | Explicit pixel width | Sidebar (240px), Icon (20x20px) |
| **Min/Max** | Responsive range | Card (min 280px, max 1fr) |

**Default sizing per component type:**

| Component | Width | Height | Notes |
|---|---|---|---|
| Button | Hug (min 44px) | Fixed 44px | lg: 52px, sm: 36px |
| Input | Fill | Fixed 44px | Textarea: hug height |
| Card | Fill container | Hug | Min height on interactive cards |
| Badge | Hug | Fixed 22px | sm: 20px, lg: 26px |
| Modal sm | Fixed 400px | Hug | Max 90vh |
| Modal md | Fixed 520px | Hug | Max 90vh |
| Modal lg | Fixed 680px | Hug | Max 90vh |
| Modal full | Fill | Fill | With padding |
| Sidebar | Fixed 240px | Fill | Collapsed: 64px |
| Navbar | Fill | Fixed 64px | Mobile: 56px |
| Icon | Fixed 20px | Fixed 20px | sm: 16px, lg: 24px, xl: 32px |
| Avatar | Fixed 40px | Fixed 40px | sm: 32px, lg: 48px |
| Thumbnail | Fixed 80px | Fixed 80px | Video: 16:9 |

### 4.7 Responsive Constraints

Every component must define resize behavior for all three breakpoints:

| Component | Mobile (<768px) | Tablet (768-1023px) | Desktop (â‰¥1024px) |
|---|---|---|---|
| Button | Fill container | Hug | Hug |
| Card | Fill, stacked | Fill, 2-col | Fill, 3-col |
| Input | Fill | Fill | Fill (max 480px) |
| Sidebar | Hidden (drawer) | Collapsed (64px) | Expanded (240px) |
| Navbar | 56px height, compact | 56px height, compact | 64px height, full |
| Modal | Full screen inset | Centered, 90vw max | Centered, fixed width |
| Badge | Left edge | Left edge | Inline |
| Table | Card list transform | Responsive columns | Full table |
| Grid | 1 column | 2 columns | 3-4 columns |

### 4.8 Auto Layout Property Reference

| Property | Setting | When |
|---|---|---|
| **Layout mode** | Vertical | Default stack direction |
| | Horizontal | Button rows, inline groups |
| | Wrap | Badge groups, tag lists |
| **Padding** | Per token (spacing-*) | Every container |
| **Item spacing** | Per token (spacing-*) | Between children |
| **Counter axis** | Auto | Default |
| | Hug | When content should determine cross-axis size |
| | Fixed | When explicit height/width needed |
| **Alignment** | Min | Left/top alignment |
| | Center | Centered content |
| | Max | Right/bottom alignment |
| | Space between | Distributed space |
| **Sizing** | Hug | Content-driven |
| | Fill | Parent-driven |
| | Fixed | Explicit |
| **Overflow** | Visible | Default |
| | Hidden | For image crops, card clipping |
| | Scroll | For scrollable content areas |

---

## 5. Grid Standards

### 5.1 Breakpoint System

| Breakpoint | Token | Min Width | Device | Columns | Gutter | Margin |
|---|---|---|---|---|---|---|
| **Mobile** | `bp-mobile` | 320px | Phones (portrait) | 4 | 16px | 16px |
| **Tablet** | `bp-tablet` | 768px | Tablets, large phones | 8 | 24px | 24px |
| **Desktop** | `bp-desktop` | 1024px | Laptops, desktops | 12 | 24px | 32px |
| **Ultra Wide** | `bp-wide` | 1440px | Large monitors | 12 | 32px | Auto (centered) |

**Rules:**
- Content max-width is 1440px. Beyond 1440px, content is centered with equal margins.
- Backgrounds (page color, grid patterns) extend full-width regardless of viewport.
- All breakpoints are min-width (mobile-first). Use only `min-width` media queries.

### 5.2 Desktop Grid (12-Column)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Margin (32px)                                                   â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Gutter (24px)                                              â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”                    â”‚  â”‚
â”‚  â”‚  â”‚ 1â”‚ 2â”‚ 3â”‚ 4â”‚ 5â”‚ 6â”‚ 7â”‚ 8â”‚ 9â”‚10â”‚11â”‚12â”‚                    â”‚  â”‚
â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚                    â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”˜                    â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Column span patterns (Desktop):**

| Span | Usage | Example |
|---|---|---|
| 12-col | Full width page sections | Page headers, KPI strips, notification bars |
| 8-col + 4-col | Main content + sidebar | Task list + filters, course grid + detail |
| 6-col + 6-col | Split layout | Editor + preview, form + help sidebar |
| 4-col Ã— 3 | Three-column grid | Card grids, stat cards |
| 3-col Ã— 4 | Four-column grid | Dense card layouts, metrics |
| 2-col Ã— 6 | Six-column grid | Compact stats, badge groups |

### 5.3 Tablet Grid (8-Column)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Margin (24px)                                   â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Gutter (24px)                             â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”               â”‚  â”‚
â”‚  â”‚  â”‚ 1â”‚ 2â”‚ 3â”‚ 4â”‚ 5â”‚ 6â”‚ 7â”‚ 8â”‚               â”‚  â”‚
â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚  â”‚               â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”˜               â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Column span patterns (Tablet):**

| Span | Usage | Example |
|---|---|---|
| 8-col | Full width | Page headers, forms, tables |
| 6-col + 2-col | Main + sidebar (collapsed) | Dashboard with secondary panel |
| 4-col Ã— 2 | Two-column grid | Card grids, stat pairs |
| 2-col Ã— 4 | Four-column compact | Dense stat grids |

### 5.4 Mobile Grid (4-Column)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Margin (16px)               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Gutter (16px)         â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”¬â”€â”€â”¬â”€â”€â”¬â”€â”€â”        â”‚  â”‚
â”‚  â”‚  â”‚ 1â”‚ 2â”‚ 3â”‚ 4â”‚        â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”´â”€â”€â”´â”€â”€â”´â”€â”€â”˜        â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Column span patterns (Mobile):**

| Span | Usage | Example |
|---|---|---|
| 4-col | Full width | Single column stacks, forms, detail views |
| 2-col Ã— 2 | Two-column compact | Stat pairs, small cards |
| 3-col + 1-col | Content + narrow sidebar | Filter controls |

### 5.5 Grid Transformation Rules

| Element | Desktop (12-col) | Tablet (8-col) | Mobile (4-col) |
|---|---|---|---|
| Card grid | `auto-fill, minmax(300px, 1fr)` | `auto-fill, minmax(240px, 1fr)` | Single column |
| KPI strip | 4 columns, inline | 4 columns, wrap | 2 columns, wrap |
| Sidebar | 240px expanded | 64px collapsed | Drawer (hidden) |
| Data table | Full table, all columns | Collapsed columns | Card list transform |
| Analytics panel | Multi-panel bento | 2-column grid | Single column stack |
| Modal | Fixed width, centered | 90vw, centered | Fullscreen inset |
| Form layout | 2-column inline | Single column | Single column |
| Button group | Horizontal row | Horizontal (wrap) | Full-width stacked |

### 5.6 Dashboard Bento Grid

Dashboard and analytics screens use a **CSS Grid auto-fill bento** system rather than a fixed column grid:

```
Desktop (â‰¥1024px):       Tablet (768-1023px):     Mobile (<768px):
â”Œâ”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KPI   â”‚ KPI   â”‚ KPI  â”‚   â”‚ KPI       â”‚ KPI       â”‚   â”‚ KPI           â”‚
â”‚ strip â”‚ strip â”‚ stripâ”‚   â”‚ strip s  â”‚ strip s  â”‚   â”‚ strip s      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Card  â”‚ Card  â”‚ Card â”‚   â”‚ Card 1     â”‚ Card 2   â”‚   â”‚ Card 1        â”‚
â”‚ 1     â”‚ 2     â”‚ 3    â”‚   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”œâ”€â”€â”€â”€â”€â”€â”´â”€â”€â”¬â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”¤   â”‚ Card 3    â”‚ Card 4    â”‚   â”‚ Card 2        â”‚
â”‚ Insight  â”‚ Activity â”‚   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ panel    â”‚ heatmap  â”‚   â”‚ Insight panel (full) â”‚   â”‚ Card 3        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AI suggestions (full) â”‚   â”‚ Activity heatmap     â”‚   â”‚ Card 4        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
                                                    â”‚ Insight panel â”‚
                                                    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
                                                    â”‚ Activity      â”‚
                                                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 5.7 Liquid Layout Rules

| Rule | Description |
|---|---|
| **LK1** | Content area fills available width, never exceeds 1440px |
| **LK2** | Backgrounds extend full viewport width regardless of content max-width |
| **LK3** | Sidebar width is fixed (240px expanded, 64px collapsed) â€” does not scale |
| **LK4** | Cards in a grid use `minmax(280px, 1fr)` â€” never fixed card widths |
| **LK5** | Cards stretch to fill their column, never leave gaps at row bottoms |
| **LK6** | Bento grid cards can span 1Ã—1, 2Ã—1, 1Ã—2, or 2Ã—2 using CSS grid placement |
| **LK7** | No horizontal scroll at any breakpoint â€” content must reflow |
| **LK8** | Tables >12 columns on desktop collapse lower-priority columns on tablet |

---

# Part III â€” Tokens & Components

---

## 6. Design Token Governance

### 6.1 Token Architecture â€” 3-Tier System

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  TIER 1: PRIMITIVE TOKENS                                        â”‚
â”‚  Raw values â€” color hex, font size px, spacing px, radius px    â”‚
â”‚  Named by category + index (e.g., color-blue-500, spacing-4)     â”‚
â”‚  One source of truth â€” never override in lower tiers              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  TIER 2: SEMANTIC TOKENS                                         â”‚
â”‚  Abstract purpose â€” references primitive tokens                  â”‚
â”‚  Named by purpose (e.g., color-bg-card, color-text-primary)       â”‚
â”‚  Theme-aware â€” dark/light/high-contrast map to different          â”‚
â”‚  primitive values                                                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  TIER 3: COMPONENT TOKENS                                        â”‚
â”‚  Component-scoped â€” references semantic tokens                   â”‚
â”‚  Named by component + part + property (e.g., button-bg-primary)   â”‚
â”‚  Component-level overrides only when necessary for brand-specificâ”‚
â”‚  values that deviate from the semantic system                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 6.2 Token Categories

| Category | Primitives | Semantic | Component | Tokens Studio Group |
|---|---|---|---|---|
| **Color** | `color-{hue}-{scale}` | `color-{purpose}-{role}` | `{component}-{part}-{property}` | `color/` |
| **Typography** | `font-{family}`, `size-{scale}`, `weight-{name}` | `text-{usage}`, `font-{role}` | `{component}-text-{part}` | `typography/` |
| **Spacing** | `spacing-{index}` | `space-{usage}` | `{component}-padding-{part}` | `spacing/` |
| **Border Radius** | `radius-{name}` | `radius-{usage}` | `{component}-radius-{part}` | `border-radius/` |
| **Shadow** | `shadow-{name}` | `elevation-{level}` | `{component}-shadow-{part}` | `box-shadow/` |
| **Motion** | `duration-{name}`, `easing-{name}` | `motion-{usage}` | `{component}-motion-{part}` | `motion/` |
| **Breakpoint** | `bp-{device}` | â€” | â€” | `breakpoint/` |
| **Z-Index** | `z-{layer}` | `z-{usage}` | â€” | `z-index/` |
| **Opacity** | `opacity-{value}` | `opacity-{usage}` | â€” | `opacity/` |

### 6.3 Color Token System

#### 6.3.1 Primitive Color Tokens (Palette)

| Hue Family | Token Pattern | Values (Scale) | Usage |
|---|---|---|---|
| **Neutral** | `color-neutral-{50..950}` | 12 values: #F8FAFC â†’ #0F172A | Backgrounds, text, borders |
| **Indigo** | `color-indigo-{50..950}` | 12 values: #EEF2FF â†’ #1E1B4B | Primary accent |
| **Emerald** | `color-emerald-{50..950}` | 12 values: #ECFDF5 â†’ #022C22 | Success / secondary accent |
| **Amber** | `color-amber-{50..950}` | 12 values: #FFFBEB â†’ #451A03 | Warning |
| **Rose** | `color-rose-{50..950}` | 12 values: #FFF1F2 â†’ #4C0519 | Error / danger |
| **Cyan** | `color-cyan-{50..950}` | 12 values: #ECFEFF â†’ #164E63 | Info / neon accent |
| **Slate** | `color-slate-{50..950}` | 12 values: #F8FAFC â†’ #020617 | Data viz, secondary text |

**Scale semantics:**
- `50` â†’ Lightest (backgrounds, hover highlights)
- `100` â†’ Surface fills
- `200` â†’ Subtle borders
- `300` â†’ Default borders
- `400` â†’ Muted text, disabled
- `500` â†’ Base color (primary brand)
- `600` â†’ Hover states
- `700` â†’ Active states
- `800` â†’ Pressed states
- `900` â†’ Darkest backgrounds
- `950` â†’ Deepest (near black)

#### 6.3.2 Semantic Color Tokens

| Token | Dark Theme | Light Theme | High Contrast | Purpose |
|---|---|---|---|---|
| `color-bg-page` | `neutral-950` | `neutral-50` | `neutral-0` | Page background |
| `color-bg-card` | `neutral-900` | `neutral-100` | `neutral-0` | Card, sidebar, navbar |
| `color-bg-elevated` | `neutral-800` | `neutral-0` | `neutral-0` | Dropdowns, hovered items |
| `color-bg-input` | `neutral-950` | `neutral-100` | `neutral-0` | Input backgrounds |
| `color-border-default` | `neutral-700` | `neutral-300` | `neutral-600` | Default borders |
| `color-border-focus` | `indigo-500` | `indigo-500` | `indigo-700` | Focus rings |
| `color-border-error` | `rose-500` | `rose-500` | `rose-700` | Error borders |
| `color-text-primary` | `neutral-100` | `neutral-900` | `neutral-0` | Headings, body |
| `color-text-secondary` | `neutral-400` | `neutral-500` | `neutral-200` | Subtext, metadata |
| `color-text-tertiary` | `neutral-500` | `neutral-400` | `neutral-300` | Placeholders, muted |
| `color-text-disabled` | `neutral-600` | `neutral-300` | `neutral-400` | Disabled text |
| `color-text-inverse` | `neutral-900` | `neutral-100` | `neutral-0` | On accent backgrounds |
| `color-accent-primary` | `indigo-500` | `indigo-500` | `indigo-600` | Actions, links, active |
| `color-accent-primary-hover` | `indigo-400` | `indigo-600` | `indigo-500` | Primary button hover |
| `color-accent-secondary` | `emerald-500` | `emerald-500` | `emerald-600` | Success indicators |
| `color-accent-warning` | `amber-500` | `amber-500` | `amber-600` | Warning states |
| `color-accent-error` | `rose-500` | `rose-500` | `rose-600` | Error states |
| `color-accent-info` | `cyan-500` | `cyan-500` | `cyan-600` | Info badges |
| `color-accent-neon` | `emerald-400` | `emerald-500` | `emerald-400` | Decorative highlights |
| `color-accent-cyber` | `rose-400` | `rose-500` | `rose-400` | Urgent indicators |
| `color-priority-urgent` | `rose-500` | `rose-600` | `rose-600` | Priority level â€” urgent |
| `color-priority-high` | `amber-500` | `amber-600` | `amber-600` | Priority level â€” high |
| `color-priority-medium` | `amber-400` | `amber-500` | `amber-500` | Priority level â€” medium |
| `color-priority-low` | `emerald-400` | `emerald-500` | `emerald-500` | Priority level â€” low |
| `color-glass-light` | `neutral-0 / 3%` | `neutral-900 / 3%` | â€” | Subtle glass |
| `color-glass-medium` | `neutral-0 / 8%` | `neutral-900 / 8%` | â€” | Card glass |
| `color-glass-heavy` | `neutral-0 / 15%` | `neutral-900 / 15%` | â€” | Highlighted glass |
| `color-surface-primary` | `neutral-0` | `neutral-900` | `neutral-0` | Inverted surfaces |
| `color-surface-secondary` | `neutral-100` | `neutral-800` | `neutral-0` | Secondary surfaces |

#### 6.3.3 Data Visualization Color Sequence

| Series | Token | Dark Theme | Light Theme |
|---|---|---|---|
| Series 1 | `color-chart-1` | `indigo-400` | `indigo-600` |
| Series 2 | `color-chart-2` | `emerald-400` | `emerald-600` |
| Series 3 | `color-chart-3` | `amber-400` | `amber-600` |
| Series 4 | `color-chart-4` | `rose-400` | `rose-600` |
| Series 5 | `color-chart-5` | `cyan-400` | `cyan-600` |
| Series 6 | `color-chart-6` | `violet-400` | `violet-600` |
| Series 7 | `color-chart-7` | `orange-400` | `orange-600` |
| Series 8 | `color-chart-8` | `teal-400` | `teal-600` |

### 6.4 Typography Token System

#### 6.4.1 Font Family Tokens

| Token | Font | Weight Available | CSS |
|---|---|---|---|
| `font-display` | Syne | 400, 500, 600, 700, 800 | Headings, display text |
| `font-body` | DM Sans | 400, 500, 600, 700 | Body text, labels |
| `font-mono` | JetBrains Mono | 400, 500, 700 | Code, numbers, data grids |

#### 6.4.2 Type Scale

| Token | Size | Line Height | Tailwind | Usage |
|---|---|---|---|---|
| `size-xs` | 11px | 16px | `text-xs` | Captions, timestamps, badges |
| `size-sm` | 13px | 18px | `text-sm` | Metadata, secondary text |
| `size-base` | 15px | 22px | `text-base` | Body text, input values |
| `size-lg` | 17px | 26px | `text-lg` | Card titles, form labels |
| `size-xl` | 19px | 28px | `text-xl` | Section headings |
| `size-2xl` | 24px | 32px | `text-2xl` | Page headings (H2) |
| `size-3xl` | 32px | 40px | `text-3xl` | Page titles (H1) |
| `size-4xl` | 42px | 50px | `text-4xl` | Hero titles |
| `size-5xl` | 56px | 66px | `text-5xl` | Display / landing |

#### 6.4.3 Font Weight Tokens

| Token | Numeric | CSS |
|---|---|---|
| `weight-normal` | 400 | `font-normal` |
| `weight-medium` | 500 | `font-medium` |
| `weight-semibold` | 600 | `font-semibold` |
| `weight-bold` | 700 | `font-bold` |
| `weight-extrabold` | 800 | `font-extrabold` |

#### 6.4.4 Semantic Typography Tokens

| Token | Size | Weight | Family | Usage |
|---|---|---|---|---|
| `text-display-hero` | `5xl` | 800 | display | Landing page hero |
| `text-display-page-title` | `4xl` | 700 | display | Page title (H1) |
| `text-heading-section` | `2xl` | 700 | display | Section heading (H2) |
| `text-heading-card` | `xl` | 600 | display | Card title (H3) |
| `text-heading-modal` | `xl` | 600 | display | Modal title |
| `text-body` | `base` | 400 | body | Paragraph body |
| `text-body-large` | `lg` | 400 | body | Large body / card content |
| `text-body-small` | `sm` | 400 | body | Secondary body |
| `text-label` | `sm` | 500 | body | Form labels |
| `text-label-large` | `base` | 500 | body | Large form labels |
| `text-caption` | `xs` | 400 | body | Captions, timestamps |
| `text-overline` | `xs` | 600 | body | Uppercase overline labels |
| `text-button` | `sm` | 600 | body | Button labels |
| `text-button-large` | `base` | 600 | body | Large button labels |
| `text-link` | `base` | 500 | body | Inline links |
| `text-input` | `base` | 400 | body | Input field values |
| `text-placeholder` | `base` | 400 | body | Placeholder text |
| `text-data-value` | `2xl` | 700 | mono | KPI metric values |
| `text-data-label` | `sm` | 500 | body | KPI metric labels |
| `text-code` | `sm` | 400 | mono | Code snippets |
| `text-table-header` | `sm` | 600 | body | Table column headers |
| `text-table-cell` | `sm` | 400 | body | Table cell content |
| `text-badge` | `xs` | 600 | body | Badge labels |
| `text-tooltip` | `xs` | 400 | body | Tooltip content |

### 6.5 Spacing Token System

| Token | Value | Rem | Tailwind | Usage |
|---|---|---|---|---|
| `spacing-0` | 0px | 0rem | `gap-0` / `p-0` | No spacing |
| `spacing-0\.5` | 2px | 0.125rem | `gap-0.5` / `p-0.5` | Micro gaps |
| `spacing-1` | 4px | 0.25rem | `gap-1` / `p-1` | Base unit |
| `spacing-1\.5` | 6px | 0.375rem | `gap-1.5` / `p-1.5` | Tight icon+text |
| `spacing-2` | 8px | 0.5rem | `gap-2` / `p-2` | Default inline gap |
| `spacing-2\.5` | 10px | 0.625rem | `gap-2.5` / `p-2.5` | Button internal |
| `spacing-3` | 12px | 0.75rem | `gap-3` / `p-3` | Relaxed inline |
| `spacing-3\.5` | 14px | 0.875rem | `gap-3.5` / `p-3.5` | Form spacing |
| `spacing-4` | 16px | 1rem | `gap-4` / `p-4` | Card padding |
| `spacing-5` | 20px | 1.25rem | `gap-5` / `p-5` | Section spacing |
| `spacing-6` | 24px | 1.5rem | `gap-6` / `p-6` | Modal padding |
| `spacing-7` | 28px | 1.75rem | `gap-7` / `p-7` | Card grid |
| `spacing-8` | 32px | 2rem | `gap-8` / `p-8` | Large section |
| `spacing-9` | 36px | 2.25rem | `gap-9` / `p-9` | Form sections |
| `spacing-10` | 40px | 2.5rem | `gap-10` / `p-10` | Page margin desktop |
| `spacing-11` | 44px | 2.75rem | `gap-11` / `p-11` | Touch target min |
| `spacing-12` | 48px | 3rem | `gap-12` / `p-12` | Page margin wide |
| `spacing-14` | 56px | 3.5rem | `gap-14` / `p-14` | Hero bottom |
| `spacing-16` | 64px | 4rem | `gap-16` / `p-16` | Major sections |
| `spacing-20` | 80px | 5rem | `gap-20` / `p-20` | Page section breaks |
| `spacing-24` | 96px | 6rem | `gap-24` / `p-24` | Hero sections |
| `spacing-28` | 112px | 7rem | `gap-28` / `p-28` | Landing page |

### 6.6 Border Radius Token System

| Token | Value | Tailwind | Usage |
|---|---|---|---|
| `radius-none` | 0px | `rounded-none` | Sharp containers |
| `radius-sm` | 4px | `rounded-sm` | Input fields, small elements |
| `radius-md` | 8px | `rounded-md` | Default button radius |
| `radius-lg` | 12px | `rounded-lg` | Cards, modals |
| `radius-xl` | 16px | `rounded-xl` | Large cards, panels |
| `radius-2xl` | 20px | `rounded-2xl` | Modals, dialogs |
| `radius-3xl` | 28px | `rounded-3xl` | Feature cards, hero |
| `radius-full` | 9999px | `rounded-full` | Badges, avatars, pills |

**Semantic radius tokens:**

| Semantic Token | Value | Usage |
|---|---|---|
| `radius-button` | `radius-md` (8px) | All buttons |
| `radius-card` | `radius-lg` (12px) | Cards, sidebar, navbar |
| `radius-modal` | `radius-2xl` (20px) | Modals, dialogs |
| `radius-input` | `radius-sm` (4px) | Input fields, textareas |
| `radius-badge` | `radius-full` | Badges, tags, chips |
| `radius-tooltip` | `radius-sm` (4px) | Tooltip containers |
| `radius-dropdown` | `radius-md` (8px) | Dropdown menus |
| `radius-avatar` | `radius-full` | Avatars, thumbnails |

### 6.7 Shadow & Elevation Token System

| Token | Value | Elevation | Usage |
|---|---|---|---|
| `shadow-none` | none | None | Flat surfaces |
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.15)` | 1 (base) | Cards (default) |
| `shadow-md` | `0 4px 12px rgba(0,0,0,0.18)` | 2 (raised) | Dropdowns, elevated cards |
| `shadow-lg` | `0 8px 24px rgba(0,0,0,0.22)` | 3 (overlay) | Modals, dialogs |
| `shadow-xl` | `0 12px 40px rgba(0,0,0,0.26)` | 4 (top) | Tooltips, popovers |
| `shadow-2xl` | `0 20px 60px rgba(0,0,0,0.30)` | 5 (peak) | Command palette, high-priority overlays |
| `shadow-glow-sm` | `0 0 20px rgba(99,102,241,0.15)` | â€” | Subtle accent glow |
| `shadow-glow` | `0 0 30px rgba(99,102,241,0.25)` | â€” | Accent glow (interactive) |
| `shadow-glow-lg` | `0 0 50px rgba(99,102,241,0.35)` | â€” | Strong accent glow |
| `shadow-neon-sm` | `0 0 15px rgba(0,255,163,0.2)` | â€” | Success/neon glow |
| `shadow-neon` | `0 0 25px rgba(0,255,163,0.3)` | â€” | Strong neon glow |
| `shadow-cyber-sm` | `0 0 15px rgba(255,51,102,0.2)` | â€” | Urgent/cyber glow |
| `shadow-cyber` | `0 0 25px rgba(255,51,102,0.3)` | â€” | Strong cyber glow |
| `shadow-focus` | `0 0 0 2px rgba(99,102,241,0.8)` | â€” | Focus ring |
| `shadow-focus-error` | `0 0 0 2px rgba(239,68,68,0.8)` | â€” | Error focus ring |
| `shadow-inner` | `inset 0 1px 0 rgba(255,255,255,0.05)` | â€” | Inner edge highlight |

### 6.8 Motion Token System

#### 6.8.1 Duration Tokens

| Token | Value | Usage |
|---|---|---|
| `duration-instant` | 0ms | No motion (instant) |
| `duration-fast` | 100ms | Micro-interactions, hover states, button press |
| `duration-normal` | 200ms | Default transitions, state changes |
| `duration-slow` | 300ms | Panel slides, modal entry |
| `duration-slide` | 400ms | Page transitions, sidebar expand |
| `duration-complex` | 500ms | Compound animations, staggered reveals |
| `duration-hero` | 800ms | Hero animations, celebration effects |

#### 6.8.2 Easing Tokens

| Token | Value (cubic-bezier) | Usage |
|---|---|---|
| `easing-default` | `0.4, 0, 0.2, 1` | Standard UI motion (Material-inspired) |
| `easing-enter` | `0.05, 0.7, 0.1, 1.0` | Elements entering â€” decelerate (ease-out) |
| `easing-exit` | `0.4, 0.0, 1.0, 1.0` | Elements leaving â€” accelerate (ease-in) |
| `easing-spring` | Spring(180, 15) | Overshoot effects â€” buttons, bouncy cards |
| `easing-emphasis` | `0.2, 0, 0, 1` | Expressive motion â€” hero, celebrations |
| `easing-sharp` | `0.4, 0, 0.6, 1` | Reactive feedback â€” press, dismiss |

#### 6.8.3 Stagger Tokens

| Token | Value | Usage |
|---|---|---|
| `stagger-fast` | 30ms | Lists >20 items, data table rows |
| `stagger-normal` | 50ms | Card grids, dashboard tiles |
| `stagger-slow` | 80ms | Page sections, form fields |
| `stagger-hero` | 120ms | Landing page reveals |

**Rule:** Maximum cumulative stagger delay must not exceed 500ms. For lists with >10 items, use `stagger-fast`.

### 6.9 Breakpoint Token System

| Token | Value | Device | Content Columns | Sidebar State |
|---|---|---|---|---|
| `bp-mobile` | 320px | Phones (portrait) | 4-col | Hidden |
| `bp-mobile-wide` | 375px | Large phones | 4-col | Hidden |
| `bp-tablet` | 768px | Tablets | 8-col | Collapsed (64px) |
| `bp-tablet-landscape` | 1024px | Tablet landscape | 8-col | Collapsed (64px) |
| `bp-desktop` | 1200px | Laptops | 12-col | Expanded (240px) |
| `bp-wide` | 1440px | Large monitors | 12-col max-width | Expanded (240px) |
| `bp-ultra-wide` | 1600px+ | Ultra-wide | 12-col centered | Expanded (240px) |

### 6.10 Z-Index Token System

| Token | Value | Usage |
|---|---|---|
| `z-base` | 0 | Default layer |
| `z-dropdown` | 1000 | Dropdown menus, autocomplete |
| `z-sticky` | 1020 | Sticky headers, navbar |
| `z-navbar` | 1030 | Fixed navbar |
| `z-modal-backdrop` | 1040 | Modal dim/overlay |
| `z-modal` | 1050 | Modal dialogs |
| `z-popover` | 1060 | Popovers, tooltips |
| `z-toast` | 1070 | Toast notifications |
| `z-command-palette` | 1080 | Command palette (Cmd+K) |
| `z-tooltip` | 1090 | Tooltips (highest) |

### 6.11 Opacity Token System

| Token | Value | Usage |
|---|---|---|
| `opacity-0` | 0% | Hidden |
| `opacity-subtle` | 8% | Glass backgrounds |
| `opacity-light` | 15% | Secondary glass layers |
| `opacity-medium` | 40% | Disabled elements |
| `opacity-heavy` | 60% | Muted elements |
| `opacity-strong` | 80% | Dimmed elements |
| `opacity-full` | 100% | Fully visible |

### 6.12 Tokens Studio Configuration

#### 6.12.1 Token Structure (JSON)

All tokens are managed in **Tokens Studio for Figma** with the following JSON structure:

```json
{
  "color": {
    "bg": {
      "page": { "value": "{color.neutral.950}", "type": "color" },
      "card": { "value": "{color.neutral.900}", "type": "color" },
      "elevated": { "value": "{color.neutral.800}", "type": "color" },
      "input": { "value": "{color.neutral.950}", "type": "color" }
    },
    "text": {
      "primary": { "value": "{color.neutral.100}", "type": "color" },
      "secondary": { "value": "{color.neutral.400}", "type": "color" },
      "tertiary": { "value": "{color.neutral.500}", "type": "color" }
    }
  },
  "spacing": {
    "4": { "value": "16", "type": "dimension" },
    "5": { "value": "20", "type": "dimension" }
  },
  "border-radius": {
    "card": { "value": "{radius.lg}", "type": "borderRadius" }
  },
  "box-shadow": {
    "card": { "value": "{shadow.md}", "type": "boxShadow" }
  },
  "typography": {
    "heading": {
      "card": {
        "value": {
          "fontFamily": "{font.display}",
          "fontSize": "{size.xl}",
          "fontWeight": "{weight.bold}",
          "lineHeight": "26px"
        },
        "type": "typography"
      }
    }
  },
  "opacity": {
    "icon": { "value": "80%", "type": "opacity" }
  }
}
```

#### 6.12.2 Theme Structure

```json
{
  "Dark": {
    "color": {
      "bg": { "page": { "value": "{color.neutral.950}" } },
      "text": { "primary": { "value": "{color.neutral.100}" } }
    }
  },
  "Light": {
    "color": {
      "bg": { "page": { "value": "{color.neutral.50}" } },
      "text": { "primary": { "value": "{color.neutral.900}" } }
    }
  },
  "High Contrast": {
    "color": {
      "bg": { "page": { "value": "{color.neutral.0}" } },
      "text": { "primary": { "value": "{color.neutral.0}" } }
    }
  }
}
```

#### 6.12.3 Variable Mapping

Every Figma variable references its Tokens Studio source token:

| Figma Variable | Source Token | Type | Theme Support |
|---|---|---|---|
| `$bg-page` | `color.bg.page` | Color | Dark / Light / HC |
| `$text-primary` | `color.text.primary` | Color | Dark / Light / HC |
| `$spacing-card` | `spacing.4` | Number | Single value |
| `$radius-card` | `border-radius.card` | Number | Single value |
| `$shadow-card` | `box-shadow.card` | Shadow | Single value |
| `$font-heading` | `typography.heading.card` | Text | Single value |
| `$opacity-icon` | `opacity.icon` | Number | Single value |

#### 6.12.4 Sync Workflow

```
Tokens Studio (Figma)
  â”‚
  â”œâ”€â”€ Export â†’ tokens.json
  â”‚
  â”œâ”€â”€ Push â†’ GitHub (sb-design-tokens repo)
  â”‚   â”œâ”€â”€ tokens.json
  â”‚   â”œâ”€â”€ themes/dark.json
  â”‚   â”œâ”€â”€ themes/light.json
  â”‚   â”œâ”€â”€ themes/high-contrast.json
  â”‚   â””â”€â”€ $metadata.json
  â”‚
  â”œâ”€â”€ GitHub Action â†’ Build:
  â”‚   â”œâ”€â”€ apps/web/tailwind.config.js (theme extension)
  â”‚   â”œâ”€â”€ apps/web/app/globals.css (CSS custom properties)
  â”‚   â””â”€â”€ packages/types/tokens.ts (TypeScript constants)
  â”‚
  â””â”€â”€ Pull â†’ Tokens Studio pulls from GitHub
      (Designers get latest tokens from main branch)
```

### 6.13 Token Anti-Patterns

| âŒ Anti-Pattern | Why | âœ… Correct |
|---|---|---|
| `color-blue-500` used directly in component | Loses theme support | `$bg-card` or `$text-primary` |
| Same value typed in 5 places | Drift risk | Single token reference |
| Token named by presentation (`color-dark-gray`) | Doesn't describe purpose | `color-text-secondary` |
| Hardcoded `16px` in Auto Layout | Consistency loss | `$spacing-4` variable |
| Opacity on a layer instead of token | Inconsistent transparency | `$opacity-medium` variable |
| Theme-specific colors in component tokens | Mixes concerns | Theme maps to semantic, semantic to component |
| `--color-primary` in CSS | Ambiguous meaning | `--color-accent-primary` |

---

## 7. Component Governance

### 7.1 Atomic Design Hierarchy

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  PAGES (18)                                                       â”‚
â”‚  Dashboard, Tasks, Courses, Goals, Habits, Sleep, Income,         â”‚
â”‚  Projects, Ideas, Resources, Opportunities, Time, Chat,           â”‚
â”‚  Automation, Youtube, Academics, Login, Root                      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ORGANISMS (11)                                                    â”‚
â”‚  Sidebar, Navbar, DataTable, KanbanBoard, RoadmapCanvas,          â”‚
â”‚  Heatmap, MessageList, CommandPalette, Calendar, ActivityFeed,    â”‚
â”‚  FloatingActionButton                                             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  MOLECULES (15)                                                    â”‚
â”‚  FormField, InputGroup, ButtonGroup, TabBar, Pagination,          â”‚
â”‚  Breadcrumbs, SearchBar, DropdownMenu, ToastNotification,         â”‚
â”‚  ModalHeader, ModalFooter, ProgressWithLabel, StatCard,           â”‚
â”‚  CardHeader, CardFooter                                           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  ATOMS (14)                                                        â”‚
â”‚  Button, Card, Input, Textarea, Select, Checkbox, Radio, Toggle,  â”‚
â”‚  Badge, Tooltip, Avatar, Spinner, Progress, Skeleton, Divider,    â”‚
â”‚  Tag                                                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 7.2 Component Implementation Status

| Component | Atomic Level | Figma Status | Code Status | Priority | Notes |
|---|---|---|---|---|---|
| Button | Atom | âœ… Complete | âœ… Implemented | â€” | Two competing code implementations |
| Card | Atom | âœ… Complete | âœ… Implemented | â€” | Code missing variant prop |
| Input | Atom | âœ… Complete | âœ… Implemented | â€” | Two competing code implementations |
| Textarea | Atom | ðŸ”² Planned | âŒ Missing | P1 | Essential for forms |
| Select | Atom | âœ… Complete | âœ… Implemented | â€” | Only in UI.tsx |
| Checkbox | Atom | ðŸ”² Planned | âŒ Missing | P0 | Used in task filters |
| Radio | Atom | ðŸ”² Planned | âŒ Missing | P2 | Low current usage |
| Toggle | Atom | ðŸ”² Planned | âŒ Missing | P2 | Low current usage |
| Badge | Atom | ðŸ”² Planned | âŒ Missing | P1 | CSS class exists, no component |
| Tooltip | Atom | ðŸ”² Planned | âŒ Missing | P1 | Required for truncation |
| Avatar | Atom | ðŸ”² Planned | âŒ Missing | P2 | Inline in Navbar currently |
| Spinner | Atom | ðŸ”² Planned | âŒ Missing | P1 | CSS class exists, no component |
| Progress | Atom | ðŸ”² Planned | âŒ Missing | P1 | CSS class exists, no component |
| Skeleton | Atom | âœ… Complete | âœ… Implemented | â€” | In UI.tsx |
| Divider | Atom | ðŸ”² Planned | âŒ Missing | P2 | `<hr>` used inline |
| Tag | Atom | ðŸ”² Planned | âŒ Missing | P2 | Low current usage |
| FormField | Molecule | ðŸ”² Planned | âŒ Missing | P0 | Critical for forms |
| InputGroup | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Needed for search + icon |
| ButtonGroup | Molecule | ðŸ”² Planned | âŒ Missing | P2 | Currently inline |
| TabBar | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Inline filters exist |
| Pagination | Molecule | ðŸ”² Planned | âŒ Missing | P2 | No pagination yet |
| Breadcrumbs | Molecule | ðŸ”² Planned | âŒ Missing | P2 | Not needed yet |
| SearchBar | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Inline in Navbar |
| DropdownMenu | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Inline in Navbar |
| ToastNotification | Molecule | ðŸ”² Planned | âŒ Missing | P1 | react-hot-toast used |
| ModalHeader | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Inline in Modal usage |
| ModalFooter | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Inline in Modal usage |
| ProgressWithLabel | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Not implemented |
| StatCard | Molecule | ðŸ”² Planned | âŒ Missing | P1 | Not implemented |
| CardHeader | Molecule | âœ… Complete | âœ… Implemented | â€” | In Card.tsx |
| CardTitle | Molecule | âœ… Complete | âœ… Implemented | â€” | In Card.tsx |
| CardFooter | Molecule | ðŸ”² Planned | âŒ Missing | P2 | Not implemented |
| Sidebar | Organism | âœ… Complete | âœ… Implemented | â€” | Self-contained |
| Navbar | Organism | âœ… Complete | âœ… Implemented | â€” | Self-contained |
| DataTable | Organism | ðŸ”² Planned | âŒ Missing | P0 | Required for tables |
| KanbanBoard | Organism | ðŸ”² Planned | âŒ Missing | P1 | Task board view |
| RoadmapCanvas | Organism | ðŸ”² Planned | âœ… Partial | P2 | React Flow edition |
| Heatmap | Organism | ðŸ”² Planned | âŒ Missing | P2 | Dashboard enhancement |
| MessageList | Organism | ðŸ”² Planned | âŒ Missing | P1 | Chat module |
| CommandPalette | Organism | ðŸ”² Planned | âŒ Missing | P1 | Cmd+K search |
| Calendar | Organism | ðŸ”² Planned | âŒ Missing | P2 | Course schedule |
| ActivityFeed | Organism | ðŸ”² Planned | âŒ Missing | P2 | Analytics |
| FloatingActionButton | Organism | ðŸ”² Planned | âŒ Missing | P2 | Quick capture |
| OfflineBanner | Organism | âœ… Complete | âœ… Implemented | â€” | Special-purpose |
| ThreeBackground | Special | âœ… Complete | âœ… Implemented | â€” | Login page only |

### 7.3 Component Maturity Model

| Stage | Label | Criteria | Figma Status | Code Status | Governance |
|---|---|---|---|---|---|
| **0 â€” Planned** | `plnd` | Spec document approved, no design work | Not started | Not started | Proposal in Sandbox |
| **1 â€” Alpha** | `alpha` | Core interaction designed, primary state only | Design in Sandbox | Proof of concept | Internal testing only |
| **2 â€” Beta** | `beta` | All states designed, token-clean, reviewed | In Antigravity Library | Feature branch | Limited consumption |
| **3 â€” Stable** | `stable` | All variants, responsive, accessibility-verified, coded match | Published library component | Main branch | Full consumption allowed |
| **4 â€” Deprecated** | `depr` | Replacement exists, migration guide published | Moved to Archive | Migration warning | No new usage |

### 7.4 Component Specification Template

Every component in Figma MUST have a spec page following this template:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  COMPONENT SPEC: [Component Name]                                â”‚
â”‚  Status: [stable | beta | alpha | planned]                      â”‚
â”‚  Version: [semver]                                              â”‚
â”‚  Last Updated: [date]                                           â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ DESCRIPTION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  One-paragraph description of what this component does      â”‚  â”‚
â”‚  â”‚  and when to use it.                                       â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ ANATOMY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  [Layer diagram with numbered parts]                      â”‚  â”‚
â”‚  â”‚  1. Container â€” $bg-elevated, $radius-card, $shadow-sm    â”‚  â”‚
â”‚  â”‚  2. Label â€” $text-label, $font-body                       â”‚  â”‚
â”‚  â”‚  3. Icon â€” 20Ã—20, $opacity-icon                          â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ PROPS TABLE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  | Prop | Type | Default | Values | Description |        â”‚  â”‚
â”‚  â”‚  |------|------|---------|--------|-------------|        â”‚  â”‚
â”‚  â”‚  | variant | variant | primary | primary/secondary/... |  â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ STATES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  [Matrix of required states with screenshots]             â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ TOKENS USED â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  $bg-elevated, $text-primary, $radius-md, $spacing-3    â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ CODE REFERENCE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Stitch component: apps/web/components/[Name].tsx        â”‚  â”‚
â”‚  â”‚  Radix primitive: @radix-ui/react-[primitive]            â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€ ACCESSIBILITY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  WCAG criteria met, keyboard interactions, aria patterns  â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 7.5 Component Gap Action Plan

| Priority | Component | Action | Target Sprint | Assignee |
|---|---|---|---|---|
| P0 | FormField | Design + spec â†’ code | Sprint 1 | DSG + Stitch |
| P0 | DataTable | Research + design â†’ spec â†’ code | Sprint 2-3 | DSG + Stitch |
| P0 | Checkbox | Quick design â†’ code | Sprint 1 | Stitch |
| P1 | Textarea, Badge, Tooltip, Spinner, Progress | Design batch | Sprint 1-2 | DSG |
| P1 | SearchBar, DropdownMenu, TabBar, ToastNotification | Convert inline code to components | Sprint 2 | Stitch |
| P1 | CommandPalette, MessageList, KanbanBoard | Design â†’ spec â†’ code | Sprint 3-4 | Full team |
| P2 | Radio, Toggle, Avatar, Divider, Tag, Calendar, Heatmap | Research first | Sprint 4+ | DSG |

---

## 8. Variant Governance

### 8.1 Component Variant Architecture

Every component with multiple visual forms uses **Figma Component Sets** with named properties. The property naming follows a strict hierarchy:

```
Component Set Properties:
  Property 1: type / variant / kind (visual distinction)
  Property 2: size / scale / density (dimensional distinction)
  Property 3: state (interaction state)
  Property 4: is[Boolean] (feature toggles)
  Property 5: mode / theme (context alternation)
```

### 8.2 Component Variant Matrix

| Component | Property 1 | Property 2 | Property 3 | Property 4 | Property 5 | Total Variants |
|---|---|---|---|---|---|---|
| **Button** | type: `primary`, `secondary`, `ghost`, `danger` | size: `sm`, `md`, `lg` | state: `default`, `hover`, `active`, `focus`, `disabled`, `loading` | isIconOnly | â€” | 4 Ã— 3 Ã— 6 Ã— 2 = 144 |
| **Input** | type: `text`, `password`, `email`, `search`, `number` | size: `sm`, `md`, `lg` | state: `default`, `hover`, `focus`, `error`, `disabled`, `readOnly` | | â€” | 5 Ã— 3 Ã— 6 = 90 |
| **Card** | variant: `default`, `interactive`, `highlighted`, `compact`, `glass`, `bento` | padding: `sm`, `md`, `lg` | state: `default`, `hover` (interactive only) | â€” | â€” | 6 Ã— 3 + 1 hover = 19 |
| **Badge** | variant: `primary`, `success`, `warning`, `error`, `info`, `neutral` | size: `sm`, `md`, `lg` | â€” | isDot, isRemovable | â€” | 6 Ã— 3 Ã— 2 Ã— 2 = 72 |
| **Modal** | size: `sm`, `md`, `lg`, `xl`, `full` | â€” | state: `open`, `closed` | â€” | â€” | 5 Ã— 2 = 10 |
| **Tooltip** | position: `top`, `bottom`, `left`, `right` | â€” | state: `hidden`, `visible` | â€” | â€” | 4 Ã— 2 = 8 |
| **Toggle** | size: `sm`, `md` | â€” | state: `off`, `on`, `disabled-off`, `disabled-on` | isLabeled | â€” | 2 Ã— 4 Ã— 2 = 16 |
| **Checkbox** | size: `sm`, `md` | â€” | state: `unchecked`, `checked`, `indeterminate`, `disabled-unchecked`, `disabled-checked`, `error` | isLabeled | â€” | 2 Ã— 6 Ã— 2 = 24 |
| **Select** | size: `sm`, `md`, `lg` | â€” | state: `default`, `hover`, `focus`, `error`, `disabled`, `open` | â€” | â€” | 3 Ã— 6 = 18 |
| **TabBar** | variant: `underline`, `pill`, `enclosed` | size: `sm`, `md` | state: `default`, `hover`, `active`, `focus` | â€” | â€” | 3 Ã— 2 Ã— 4 = 24 |
| **DropdownMenu** | size: `sm`, `md` | â€” | state: `closed`, `open` | isDangerItem | â€” | 2 Ã— 2 Ã— 2 = 8 |

### 8.3 State Variant Requirements

Every interactive component MUST implement these states:

| State | Visual Change | Token Changes | Required |
|---|---|---|---|
| **Default** | Base appearance | â€” | âœ… Required |
| **Hover** | Background lighten, border accent, cursor | `bg-elevated`, `border-focus` | âœ… Required (interactive) |
| **Active / Pressed** | Scale down (0.97), background darker | `bg-elevated-dark`, scale transform | âœ… Required (interactive) |
| **Focus** | Focus ring (2px outline offset 2px) | `shadow-focus`, `border-focus` | âœ… Required (keyboard) |
| **Disabled** | Reduced opacity, no events | `opacity-medium`, `text-disabled` | âœ… Required |
| **Loading** | Spinner replaces icon/text, no interaction | Pulse animation, pointer-events none | âš ï¸ Conditional |
| **Error** | Red border, error icon, error message | `border-error`, `text-error` | âš ï¸ Conditional (inputs) |
| **Empty** | Placeholder content, muted text | `text-tertiary` | âš ï¸ Conditional (data) |
| **Read Only** | No border, no interaction, static | Text-only with muted bg | âš ï¸ Conditional (inputs) |
| **Selected** | Highlighted background, accent border | `bg-accent-primary / 10%` | âš ï¸ Conditional (lists) |

### 8.4 Theme Variants

Every component MUST support **Dark** theme. **Light** and **High Contrast** are secondary targets.

| Theme | Target | Timeline | Enforcement |
|---|---|---|---|
| **Dark** | All components â€” Stable | v1.0 | Required for all states |
| **Light** | Atoms + Molecules â€” Stable; Organisms â€” Beta | v1.1 | Token swap only |
| **High Contrast** | All atoms â€” Beta | v1.2 | Manual a11y review |
| **Custom (Accent)** | Tokens only â€” no component variants | v1.0 | Accent color token swap |

**Theme implementation approach:**
- Themes use token-level switching only â€” no component variant duplication for theme
- Dark remains the default theme; components are designed dark-first
- Light theme derived by changing semantic token values (same component structure)
- High Contrast theme uses increased contrast ratios with solid borders instead of glass

### 8.5 Responsive Variants

Components that change structure across breakpoints use **breakpoint variants**:

| Component | Mobile | Tablet | Desktop | Variant Strategy |
|---|---|---|---|---|
| **Sidebar** | Hidden (drawer) | Collapsed (64px) | Expanded (240px) | 3 variants in component set |
| **Navbar** | Compact (56px) | Compact (56px) | Full (64px) | 2 variants |
| **Modal** | Full screen inset | Centered (90vw) | Centered (fixed) | 3 variants |
| **Button in forms** | Fill width | Fill width | Hug | Use auto layout fill |
| **Card grid** | Single column | 2 columns | 3 columns | Use auto-fill grid |

### 8.6 Variant Property Naming Reference

| Property Name | Type | Example Values | Used By |
|---|---|---|---|
| `type` | Text | `primary`, `secondary`, `ghost`, `danger` | Button, Badge |
| `variant` | Text | `default`, `interactive`, `highlighted` | Card |
| `variantStyle` | Text | `underline`, `pill`, `enclosed` | TabBar |
| `size` | Text | `sm`, `md`, `lg` | Button, Input, Badge, Select |
| `state` | Text | `default`, `hover`, `active`, `focus`, `disabled` | All interactive |
| `position` | Text | `top`, `bottom`, `left`, `right` | Tooltip, Popover |
| `isDisabled` | Boolean | `true`, `false` | All interactive |
| `isLoading` | Boolean | `true`, `false` | Button, Select |
| `isSelected` | Boolean | `true`, `false` | Tab, DropdownItem |
| `isRemovable` | Boolean | `true`, `false` | Badge, Tag |
| `isIconOnly` | Boolean | `true`, `false` | Button |
| `isLabeled` | Boolean | `true`, `false` | Checkbox, Toggle |
| `hasError` | Boolean | `true`, `false` | Input, Select |
| `isReadOnly` | Boolean | `true`, `false` | Input, Textarea |
| `isOpen` | Boolean | `true`, `false` | Dropdown, Modal |

### 8.7 Variant Optimization Rules

| Rule | Description |
|---|---|
| **V1** | Maximum 6 properties per component set. Beyond 6, split into sub-components. |
| **V2** | Boolean properties must use `is` prefix. Avoid swapped boolean names (use `isDisabled`, never `isEnabled`). |
| **V3** | Properties are ordered by importance: type â†’ size â†’ state â†’ boolean modifiers. |
| **V4** | Property values are kebab-case text, never numbers or abbreviations. |
| **V5** | If two components share >70% of their variant matrix, consider merging. |
| **V6** | No component variant should exceed 200 instances. Split into logical sub-components if needed. |
| **V7** | Disabled states are created via boolean override, not as separate component variants â€” unless the disabled visual differs structurally (not just opacity). |

---

# Part IV â€” Quality & Compliance

---

## 9. Accessibility Governance

### 9.1 Compliance Target

| Standard | Target | Verification Method | Timeline |
|---|---|---|---|
| WCAG 2.2 Level AA | All components â€” Stable | Manual audit + axe-core scan | v1.0 |
| WCAG 2.2 Level AAA | High Contrast theme tokens | Color contrast ratio check | v1.2 |
| Section 508 | All components â€” Beta | VPAT documentation | v1.1 |
| EN 301 549 | All components â€” Beta | EU accessibility conformity | v1.2 |

### 9.2 Color Contrast Requirements

| Token Category | Dark Theme | Light Theme | High Contrast | WCAG Level |
|---|---|---|---|---|
| `text-primary` on `bg-page` | â‰¥ 13.5:1 | â‰¥ 14.5:1 | â‰¥ 15:1 | AAA |
| `text-primary` on `bg-card` | â‰¥ 12.5:1 | â‰¥ 13.5:1 | â‰¥ 15:1 | AAA |
| `text-secondary` on `bg-page` | â‰¥ 7.0:1 | â‰¥ 7.5:1 | â‰¥ 10:1 | AAA |
| `text-secondary` on `bg-card` | â‰¥ 6.5:1 | â‰¥ 7.0:1 | â‰¥ 10:1 | AA |
| `accent-primary` on `bg-page` | â‰¥ 6.0:1 | â‰¥ 6.8:1 | â‰¥ 7.5:1 | AA |
| `accent-primary` on `bg-card` | â‰¥ 5.5:1 | â‰¥ 6.2:1 | â‰¥ 7.5:1 | AA |
| `text-error` on `bg-page` | â‰¥ 5.5:1 | â‰¥ 6.0:1 | â‰¥ 7.0:1 | AA |
| `accent-neon` on `bg-page` | â‰¥ 4.5:1 | â‰¥ 4.8:1 | â‰¥ 7.0:1 | AA (large text) |
| Disabled text on any bg | â‰¥ 3.0:1 | â‰¥ 3.0:1 | â‰¥ 4.5:1 | AA (non-text) |

**Token contrast verification protocol:**
1. Every new color token submission must include contrast ratio against all four surface backgrounds (page, card, elevated, input)
2. If any contrast falls below 3.0:1, the token can only be used for decorative purposes (not information-bearing)
3. Auto-generated report in CI compares every semantic token against every background token
4. High Contrast theme must pass all ratios at â‰¥ 7:1 for text, â‰¥ 4.5:1 for non-text

### 9.3 Touch Target Requirements

| Context | Minimum Target Size | Applied Token | Verification |
|---|---|---|---|
| All interactive elements | 44 Ã— 44px | `spacing-11` (44px) | Automated layout scan |
| Mobile (<768px) | 44 Ã— 44px | `min-h-touch`, `min-w-touch` | Responsive checker |
| Tablet (768-1023px) | 44 Ã— 44px | `min-h-touch`, `min-w-touch` | Responsive checker |
| Desktop (â‰¥1024px) | 44 Ã— 36px | `min-h-button` | Manual review |
| Icon buttons | 44 Ã— 44px | `w-11 h-11` | Automated |
| Inline links | 44 Ã— 24px (min height) | `py-2` | Manual (focus area) |
| Form controls | 44 Ã— 44px | `min-h-input` | Automated |
| Bottom nav (mobile) | 56 Ã— 44px | `h-14` | Responsive checker |
| Slider / handles | 44 Ã— 44px | `w-11 h-11` | Manual review |

**Touch target rule:** No interactive element may have a tappable area smaller than 44Ã—44 CSS pixels. If the visual element is smaller, expand the hit area via `::before` pseudo-element or transparent padding.

### 9.4 Keyboard Navigation Requirements

| Interaction | Pattern | WCAG Criterion | Verification |
|---|---|---|---|
| Tab order | Logical DOM order â€” follows visual layout | 2.4.3 Focus Order | Manual + tab test |
| Focus indicator | 2px ring, offset 2px, never removed | 2.4.7 Focus Visible | CSS audit |
| Skip link | First focusable element on page | 2.4.1 Bypass Blocks | Manual |
| Escape | Closes dropdowns, modals, popovers | â€” | Integration test |
| Enter / Space | Activates buttons, links, toggles | â€” | Automation |
| Arrow keys | Within listboxes, tab bars, tree views | â€” | Integration test |
| Tab (within modal) | Traps focus in open modal | 1.4.11 Focus Trap | Automated |
| Cmd+K | Opens command palette | â€” | Manual |
| Esc (modal) | Closes modal without confirmation | â€” | Integration test |
| Arrow (dropdown) | Navigates dropdown options | â€” | Integration test |

**Focus management rules:**

| Rule | Description |
|---|---|
| **FK1** | Every interactive element must have a visible focus ring â€” never use `outline: none` without a replacement |
| **FK2** | Focus ring color: `$color-border-focus` (indigo 500) â€” consistent across all components |
| **FK3** | Focus ring width: 2px, offset: 2px, style: `outline-offset: 2px` |
| **FK4** | `:focus-visible` for keyboard-initiated focus â€” separate from `:focus` for mouse clicks |
| **FK5** | Modal opens: focus first focusable element. Modal closes: return focus to trigger element |
| **FK6** | Custom interactive elements (not native HTML) must use `tabindex="0"`, `role`, and keyboard event handlers |
| **FK7** | Never tab to disabled elements (`tabindex="-1"`) |

### 9.5 Reduced Motion Requirements

Every animated component MUST respect operating system reduced motion preferences. Components must provide a static alternative for every animation.

#### Animation â†’ Static Replacement Table

| Animation | Motion Variant | Reduced Motion Replacement |
|---|---|---|
| Entry fade-in | `opacity 0â†’1, translateY: 20pxâ†’0` | `opacity 1` (instant appear) |
| Exit fade-out | `opacity 1â†’0` | `opacity 0` (instant disappear) |
| Stagger entrance | Items appear with 50ms delay each | All items appear simultaneously |
| Scale press | `scale: 1â†’0.97` | No scale change |
| Slide (sidebar) | `translateX: -240â†’0, 250ms` | Instant position change |
| Slide (modal) | `translateY: 20â†’0, 200ms` | Instant appear |
| Parallax | Background moves slower than foreground | No parallax â€” static background |
| Pulse glow | Box-shadow oscillates | Static shadow (no animation) |
| Floating (decorative) | `translateY` oscillates -10px to 10px | No float â€” fixed position |
| Scanline overlay | `translateY` animates | Static overlay image |
| Progress fill | Width animates from 0% to target | Instant width change |
| Character (Rive) | Full animation | Static poster frame |

**Implementation requirements:**

```typescript
// Every animated component MUST check reduced motion context:
import { useReducedMotion } from 'motion/react'

function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion()

  const variants = shouldReduceMotion
    ? { initial: { opacity: 1 }, animate: { opacity: 1 } }
    : { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 } }

  return <motion.div variants={variants} />
}
```

### 9.6 Screen Reader Requirements

| Component | ARIA Role | ARIA Properties | Keyboard Navigation |
|---|---|---|---|
| Button | `button` or native `<button>` | `aria-label` if icon-only, `aria-disabled` when disabled | Enter/Space to activate |
| Input | No role needed (native input) | `aria-invalid` when error, `aria-describedby` for helper/error text | Tab to focus, type |
| Checkbox | No role needed (native checkbox) or `role="checkbox"` | `aria-checked`, `aria-disabled`, `aria-labelledby` | Space to toggle |
| Radio | `role="radiogroup"` on group, `role="radio"` on items | `aria-checked`, `aria-labelledby` | Arrow keys to navigate |
| Toggle | `role="switch"` | `aria-checked`, `aria-labelledby` | Space to toggle |
| Select / Dropdown | `role="combobox"` | `aria-expanded`, `aria-controls`, `aria-activedescendant` | Enter to open, arrow to navigate, Enter to select, Escape to close |
| Listbox | `role="listbox"` | `aria-multiselectable` (if applicable) | Arrow keys |
| Option | `role="option"` | `aria-selected` | â€” |
| Modal | `role="dialog"` or `role="alertdialog"` | `aria-modal="true"`, `aria-labelledby` (title), `aria-describedby` (description) | Tab trap, Escape to close |
| Tab | `role="tab"` on tab, `role="tabpanel"` on panel | `aria-selected`, `aria-controls`, `aria-labelledby` | Arrow keys to switch tabs |
| Tooltip | `role="tooltip"` | `aria-describedby` on trigger element | Hover or focus to show, Escape to dismiss |
| Alert / Toast | `role="alert"` | `aria-live="polite"` or `"assertive"` | Auto-dismiss, focus if persistent |
| Progress bar | `role="progressbar"` | `aria-valuenow`, `aria-valuemin`, `aria-valuemax` | â€” |
| Badge | No role (decorative) | `aria-label` if meaningful | â€” |
| Avatar | No role (decorative) or `role="img"` | `aria-label` for user name | â€” |
| Skeleton | `role="status"` or `aria-hidden="true"` | `aria-label="Loading..."` | â€” |
| Navigation | `role="navigation"` or `<nav>` | `aria-label="Main navigation"` | Tab through items |

### 9.7 Accessibility Review Checklist

Every component review must verify:

```
[ ] Color contrast â‰¥ 4.5:1 for all text (AA)
[ ] Color contrast â‰¥ 3.0:1 for non-text elements (AA)
[ ] Focus indicator visible on all interactive elements
[ ] Touch targets â‰¥ 44Ã—44px
[ ] All interactive elements keyboard-accessible
[ ] Modal focus trap works correctly
[ ] Reduced motion respected
[ ] ARIA roles and properties correct
[ ] Screen reader test: all content announced correctly
[ ] Error messages associated with inputs via aria-describedby
[ ] Icon-only elements have aria-label
[ ] Images have alt-text or aria-hidden
[ ] Color not the only differentiator (icon + label + color)
[ ] Dark theme contrast verified
[ ] Light theme contrast verified (if applicable)
```

---

## 10. Asset Governance

### 10.1 Icon Governance

| Rule | Specification |
|---|---|
| **IS1** | **Library:** lucide-react only. No duplicative icon sets. No custom SVG icons unless lucide has no equivalent. |
| **IS2** | **Naming:** lucide naming convention (snake_case). New custom icons follow same convention. |
| **IS3** | **Grid:** Icons sit on a transparent 24Ã—24px grid. 16px and 20px variant grids also supported. |
| **IS4** | **Sizing in components:** sm = 16Ã—16, md = 20Ã—20 (default), lg = 24Ã—24, xl = 32Ã—32. |
| **IS5** | **Stroke width:** lucide default (2px). Do not change stroke width. |
| **IS6** | **Color:** Icons inherit color from adjacent text. Use icon color only to communicate meaning (status, state, interaction). |
| **IS7** | **Color rule:** A standalone colored icon (without text) must be self-explanatory contextually. |
| **IS8** | **Decorative icons:** Set `aria-hidden="true"` on all decorative icons. |
| **IS9** | **Meaningful icons:** Provide `aria-label` on interactive icons without visible labels. |
| **IS10** | **No ambiguous icons:** Every icon must be paired with text or used in a context where its meaning is unmistakable. |

**Icon sizing matrix:**

| Context | Size | Token |
|---|---|---|
| Inline with text (body) | 16Ã—16 | `size-sm` |
| Button / list item | 20Ã—20 | `size-md` |
| Navbar icons | 20Ã—20 | `size-md` |
| Sidebar icons | 20Ã—20 | `size-md` |
| Feature / empty states | 48Ã—64 (icon + container) | Custom |
| Hero / landing | 64Ã—64+ | Custom |
| Data viz / chart markers | 12Ã—12 | Custom dot |
| Badge dot | 8Ã—8 | Custom dot |

### 10.2 Illustration Governance

| Tier | Usage | Style | File Format |
|---|---|---|---|
| **Tier 1 â€” Empty States** | Shown when module has no data (e.g., "No tasks yet") | Cyberpunk-themed illustrations with neon accents, dark backgrounds, 3D isometric elements | `.svg` (vectors) |
| **Tier 2 â€” Onboarding** | Tutorial steps, feature introductions, first-time user flows | Character-driven scenes with product UI shown in-context | `.svg` (vectors) |
| **Tier 3 â€” Decorative** | Landing page hero, login page background, brand moments | Abstract cyberpunk tech patterns, grid lines, particle systems | CSS / Three.js (runtime) |

**Illustration rules:**
| Rule | Description |
|---|---|
| **IL1** | All empty state illustrations must include a 48-64px clear space around the focal element |
| **IL2** | Color palette for illustrations must derive from the token system â€” no standalone colors |
| **IL3** | Empty state illustrations must have `role="img"` and `aria-label` describing the visual |
| **IL4** | Decorative Tier 3 illustrations must have `aria-hidden="true"` |
| **IL5** | All SVGs must be optimized (no editor metadata, no unused groups, path-simplified) |

### 10.3 Animation Governance

| Format | Usage | Tool | Output |
|---|---|---|---|
| **Framer Motion variants** | UI micro-interactions, entrance/exit, state transitions | Framer Motion / motion react | React code |
| **Lottie JSON** | Loading animations, progress indicators | LottieFiles / After Effects | `.json` |
| **Rive (.riv)** | Celebratory animations (confetti), character animations, complex timeline | Rive | `.riv` + runtime |
| **CSS animations** | Subtle ambient effects (pulse, glow, float) | Tailwind keyframes | CSS utilities |

**Animation rules:**
| Rule | Description |
|---|---|
| **AN1** | No animation violates reduced motion preferences â€” every animation has a static fallback |
| **AN2** | Framer Motion for UI animations only. GSAP for scroll-driven animation. Rive for complex character/celebration. Never two libraries animating the same element. |
| **AN3** | Maximum cumulative stagger delay: 500ms |
| **AN4** | Entry duration â‰¤ 300ms. Exit duration â‰¤ 200ms. |
| **AN5** | No animation of `width`, `height`, `top`, `left`, `margin`, or `padding` â€” use transforms only |
| **AN6** | All animation values reference motion tokens â€” no hardcoded durations or easings |

### 10.4 Image Governance

| Rule | Description |
|---|---|
| **IMG1** | All user-uploaded images must have a fallback background color matching the container |
| **IMG2** | Avatar images use aspect ratio 1:1 (square) with `rounded-full` |
| **IMG3** | Thumbnail images use aspect ratio 16:9, with fallback placeholder |
| **IMG4** | All `<img>` tags must include `alt` text â€” empty `alt=""` for decorative images |
| **IMG5** | Image loading: use `loading="lazy"` for below-fold images, `loading="eager"` for hero images |
| **IMG6** | Image performance: maximum asset size 200KB before compression |
| **IMG7** | Image format: SVG for illustrations, WebP for photos (with PNG fallback for older browsers) |

---

# Part V â€” Process & Future

---

## 11. Documentation Standards

### 11.1 Component Documentation Template

Every Figma component MUST have a corresponding spec page with the following sections:

```
â”Œâ”€ COMPONENT NAME â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Status: [Stable / Beta / Alpha / Deprecated]              â”‚
â”‚  Version: 1.0.0                                            â”‚
â”‚  Library: Antigravity / Stitch / Modules                   â”‚
â”‚  Design Lead: [Name]                                       â”‚
â”‚  Engineer Lead: [Name]                                     â”‚
â”‚  Last Updated: 2026-06-11                                  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  1. DESCRIPTION                                            â”‚
â”‚  One paragraph. What it does. When to use it. When not to. â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  2. ANATOMY                                               â”‚
â”‚  Labeled diagram with numbered parts                       â”‚
â”‚  1. Container â€” bg-elevated, radius-card, shadow-sm        â”‚
â”‚  2. Label â€” $font-label, $text-primary, $spacing-2         â”‚
â”‚  3. Icon â€” 20Ã—20, $opacity-icon                           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  3. PROPS TABLE                                           â”‚
â”‚  | Prop | Type | Required | Default | Values |             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  4. STATES MATRIX                                         â”‚
â”‚  4Ã—4 grid: rows = states, cols = variants                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  5. AUTO LAYOUT SPEC                                      â”‚
â”‚  Padding: $spacing-4 / Gap: $spacing-2 / Direction: H     â”‚
â”‚  Sizing: width=FILL, height=HUG                           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  6. ACCESSIBILITY                                         â”‚
â”‚  WCAG criteria met. ARIA pattern. Keyboard nav.           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  7. DO / DON'T                                            â”‚
â”‚  3+ visual examples of correct and incorrect usage        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  8. CODE REFERENCE                                        â”‚
â”‚  Stitch: components/ui/Button.tsx                         â”‚
â”‚  Radix: @radix-ui/react-slot                             â”‚
â”‚  Package export: @secondbrain/ui/button                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 11.2 Usage Documentation

Every component must document:

| Section | Content | Format |
|---|---|---|
| **When to use** | The specific scenarios this component is designed for | Bullet list |
| **When not to use** | Anti-patterns, alternatives | Bullet list |
| **Do / Don't examples** | 3+ visual examples showing correct and incorrect usage | Figma frames with labels |
| **Content guidelines** | Character limits, label conventions, tone of voice | Text + examples |
| **Related components** | Cross-reference to alternative or complementary components | Link list |
| **AI interaction** | How the component behaves when populated by AI | Notes in Dev Mode |
| **Edge cases** | Empty state, loading, error, overflow, long content | Figma frames |

### 11.3 Engineering Documentation

Each component spec in Figma must include engineering handoff data:

```
â”Œâ”€ DEV HANDOFF â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  IMPORTS:                                                  â”‚
â”‚  import { Button } from '@/components/ui/button'           â”‚
â”‚  import { cva } from 'class-variance-authority'            â”‚
â”‚                                                            â”‚
â”‚  PROPS:                                                    â”‚
â”‚  interface ButtonProps extends React.ButtonHTMLAttributes  â”‚
â”‚    variant: 'primary' | 'secondary' | 'ghost' | 'danger'   â”‚
â”‚    size: 'sm' | 'md' | 'lg'                                â”‚
â”‚    isLoading?: boolean                                      â”‚
â”‚    isIconOnly?: boolean                                     â”‚
â”‚                                                            â”‚
â”‚  VARIANT DEFINITION:                                       â”‚
â”‚  const buttonVariants = cva({                               â”‚
â”‚    base: 'inline-flex items-center justify-center ...',    â”‚
â”‚    variants: {                                             â”‚
â”‚      variant: {                                            â”‚
â”‚        primary: 'bg-accent-primary text-white ...',       â”‚
â”‚        secondary: 'bg-background-elevated ...',           â”‚
â”‚        ghost: 'bg-transparent ...',                       â”‚
â”‚        danger: 'bg-accent-error text-white ...',           â”‚
â”‚      },                                                    â”‚
â”‚      size: {                                               â”‚
â”‚        sm: 'h-9 px-3 text-sm',                            â”‚
â”‚        md: 'h-11 px-4 text-sm',                           â”‚
â”‚        lg: 'h-13 px-5 text-base',                         â”‚
â”‚      },                                                    â”‚
â”‚    },                                                      â”‚
â”‚    defaultVariants: { variant: 'primary', size: 'md' },   â”‚
â”‚  })                                                        â”‚
â”‚                                                            â”‚
â”‚  TOKENS:                                                   â”‚
â”‚  Â· bg-accent-primary â†’ $color-accent-primary              â”‚
â”‚  Â· text-white â†’ $color-text-inverse                        â”‚
â”‚  Â· h-11 â†’ $spacing-button-height                           â”‚
â”‚                                                            â”‚
â”‚  ANATOMY â†’ CSS:                                            â”‚
â”‚  Container â†’ `<button className={buttonVariants(...)}>`    â”‚
â”‚  Icon â†’ `<Icon size={size === 'sm' ? 16 : 20} />`         â”‚
â”‚  Label â†’ `<span>{children}</span>`                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 12. Design Review Process

### 12.1 Review Stages

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ SELF-     â”‚ â†’  â”‚ PEER     â”‚ â†’  â”‚ DESIGN   â”‚ â†’  â”‚ DESIGN   â”‚
â”‚ REVIEW    â”‚    â”‚ REVIEW   â”‚    â”‚ LEAD     â”‚    â”‚ DIRECTOR â”‚
â”‚           â”‚    â”‚           â”‚    â”‚ REVIEW   â”‚    â”‚ REVIEW   â”‚
â”‚ Author    â”‚    â”‚ 1-2 peersâ”‚    â”‚ DSG Lead â”‚    â”‚ (major   â”‚
â”‚ only      â”‚    â”‚           â”‚    â”‚ only     â”‚    â”‚ changes) â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â”‚               â”‚               â”‚               â”‚
     â–¼               â–¼               â–¼               â–¼
  10 min          30 min          30 min          45 min
  Pre-check       Feedback        Approval        Strategic signoff
```

### 12.2 Self-Review Checklist (Stage 1)

Before submitting for peer review, every designer must verify:

```
[ ] Component uses Auto Layout on all frames
[ ] No hardcoded values â€” every fill, stroke, effect, and text style references a token
[ ] Component set properties correctly named (type/size/state/is*)
[ ] All required states exist (default, hover, active, focus, disabled)
[ ] Variant matrix is complete â€” no missing combinations
[ ] Naming follows Section 3 conventions
[ ] Layer names are semantic (not "Rectangle 1", "Frame 2394")
[ ] Export settings configured (SVG for icons, PNG for images)
[ ] Dev Mode annotations added
[ ] Reduced motion alternative considered
[ ] Color contrast passes WCAG AA at minimum
[ ] Touch targets â‰¥ 44Ã—44px
[ ] Keyboard interaction pattern documented
[ ] Component description written (purpose, when to use, when not to)
```

### 12.3 Peer Review Checklist (Stage 2)

| Category | Check | Pass/Fail |
|---|---|---|
| **Governance** | Naming convention followed | / |
| **Governance** | Token usage verified (zero hardcoded values) | / |
| **Governance** | Auto Layout compliance | / |
| **Accessibility** | Focus indicators visible | / |
| **Accessibility** | Color contrast â‰¥ 4.5:1 | / |
| **Accessibility** | Touch targets â‰¥ 44px | / |
| **Variants** | All required states present | / |
| **Variants** | No unnecessary variant explosion | / |
| **Responsive** | Mobile + tablet behavior defined | / |
| **Consistency** | Matches existing component patterns | / |
| **Documentation** | Dev Mode annotations complete | / |
| **Usage** | Do/Dont examples clear | / |

### 12.4 Design Lead Review (Stage 3)

Triggers:
- New component addition
- Breaking variant change
- Token value modification
- Deprecation proposal

Approval authority: Design Systems Lead. Escalation to Design Director for cross-system impact.

### 12.5 Design Director Review (Stage 4)

Triggers:
- New design system direction or principle
- New token category
- Major visual language revision
- Component that changes brand perception

### 12.6 Review Cadence

| Review Type | Frequency | Participants | Duration | Output |
|---|---|---|---|---|
| Daily design sync | Daily (15 min) | Design team | 15 min | Standup, blockers, pairing |
| Component review | Per component | DSG Lead + designer | 30 min | Approval / revision list |
| Design crit | Weekly | All designers + FE lead | 60 min | Feedback on WIP |
| Token audit | Bi-weekly | DSG Council | 30 min | Token drift report |
| System review | Monthly | DSG Council + FE architects | 60 min | Library health check |
| Milestone review | Per sprint | Product + design + eng | 90 min | Ship/no-ship decision |

### 12.7 Handoff Requirements

Before handoff to engineering:

| Requirement | Detail | Verified By |
|---|---|---|
| Dev Mode enabled | All layers have inspectable properties | Design Lead |
| Export settings | Icons set to SVG, images to PNG 2x | Designer |
| Component description | Purpose, usage, code snippet | Designer |
| Token mapping | Every token linked to Tokens Studio source | Automated |
| Spec annotations | Spacing, sizing, padding labeled | Designer |
| Code reference | Component file path, import path | Engineer review |
| Responsive behavior | Breakpoint previews attached | Designer |

---

## 13. Version Control Process

### 13.1 Version Schema

All Figma library components and tokens follow **Semantic Versioning**:

```
MAJOR.MINOR.PATCH

MAJOR: Breaking change â€” existing components require migration
  - Removing a component property
  - Changing token values that affect existing usage
  - Renaming exported components
  - Changing component anatomy (required children)
  - Changing default variant values

MINOR: Non-breaking addition
  - New component variant (size, style, state)
  - New component in library
  - New token addition (non-breaking)
  - New theme support

PATCH: Backward-compatible fix
  - Token value tweak (no visual regression expected)
  - Bug fix (alignment, spacing correction)
  - Documentation update
  - Missing state addition
```

### 13.2 Figma Version Management

| Action | Version Bump | Process |
|---|---|---|
| Fix token value | PATCH | Quick publish â€” no review needed |
| Add component variant | PATCH / MINOR | Auto-review by design lead |
| Add new component | MINOR | Full review cycle (Stage 2-3) |
| Change existing component prop | MINOR | Full review cycle (Stage 2-3) |
| Remove component prop | MAJOR | Full review cycle (Stage 2-4) + migration guide |
| Rename component | MAJOR | Full review + migration guide + codemod |
| Change token system structure | MAJOR | DSG Council approval + migration plan |
| Deprecate component | MAJOR | Full review + archive + migration guide |

### 13.3 Branch Strategy in Figma

```
main (Published)       â† Always stable. Published to all consumers.
  â”‚
  â”œâ”€â”€ develop          â† Work in progress. Staged components.
  â”‚                      Designers merge feature branches here.
  â”‚
  â”œâ”€â”€ feat/component-name  â† Individual component work
  â”‚
  â”œâ”€â”€ fix/token-value       â† Token fixes
  â”‚
  â”œâ”€â”€ release/v{major}.{minor}  â† Release candidates
  â”‚
  â””â”€â”€ archive/v{prev}     â† Previous versions (read-only)
```

### 13.4 Change Log Requirements

Every library version publish MUST include a changelog entry:

```
## [1.3.0] â€” 2026-06-11

### Added
- Button: new `outline` variant (#42)
- Card: `interactive` variant with hover state (#45)
- Tooltip: first stable release (#38)

### Changed
- Input: error state border color from rose-400 to rose-500 (#44)
- Badge: reduced padding from 12px to 8px (#47)

### Fixed
- Modal: Escape key now correctly closes on mobile (#41)
- Button: loading state now preserves original width (#39)

### Deprecated
- Legacy UI.tsx component variants (Button, Input) â€” use canonical Button.tsx and Input.tsx

### Migration Notes
- Button `outline` variant: no migration needed (new feature)
- Input error border: visual change only, no code migration required
```

### 13.5 Version Archive Rules

| Rule | Description |
|---|---|
| **VC1** | Every MAJOR version creates an archive branch: `archive/v{major}.{minor}` |
| **VC2** | Archive branches are read-only â€” no edits permitted |
| **VC3** | Current version + 2 previous minor versions are kept for reference |
| **VC4** | Archive migration guide must be linked from current component documentation |
| **VC5** | Breaking changes must include a codemod script for automated migration |

---

## 14. Release Process

### 14.1 Release Cadence

| Release Type | Frequency | Scope | Review Level |
|---|---|---|---|
| **Patch release** | As needed (daily) | Bug fixes, token tweaks, docs | Stage 1-2 |
| **Minor release** | Bi-weekly (sprint-aligned) | New components, variants, states | Stage 1-3 |
| **Major release** | Quarterly | Breaking changes, system redesign | Stage 1-4 + DSG Council |

### 14.2 Release Checklist

```
[ ] All new components pass quality gates G1-G6
[ ] All modified components re-verified
[ ] Changelog updated with all changes
[ ] Migration guide written for breaking changes
[ ] Token audit passes â€” zero hardcoded values
[ ] Accessibility scan â€” zero violations
[ ] Component coverage completeness verified
[ ] All variants rendered correctly
[ ] Responsive behavior verified at 3 breakpoints
[ ] Dark theme verified (primary)
[ ] Codemod ready for breaking changes (if applicable)
[ ] Engineering team notified of release
[ ] Release notes drafted
```

### 14.3 Publishing Workflow

```
1. Feature Complete
   â”œâ”€â”€ All components in develop branch
   â”œâ”€â”€ All docs written
   â””â”€â”€ Self-review passed

2. Peer Review
   â”œâ”€â”€ 1-2 design peers review
   â”œâ”€â”€ Feedback incorporated
   â””â”€â”€ Review checklist signed off

3. DSG Lead Review
   â”œâ”€â”€ Design Systems Lead approval
   â”œâ”€â”€ A11y specialist consult (if new tokens)
   â””â”€â”€ Token audit scan

4. Release Candidate
   â”œâ”€â”€ Create release/v{major}.{minor} branch
   â”œâ”€â”€ Run all automated checks
   â””â”€â”€ Fix any regressions

5. Engineering Preview
   â”œâ”€â”€ FE engineer reviews spec
   â”œâ”€â”€ Code parity check
   â””â”€â”€ Handoff complete

6. Publish
   â”œâ”€â”€ Publish library to Figma
   â”œâ”€â”€ Tag version in GitHub
   â”œâ”€â”€ Send release notes to team
   â””â”€â”€ Archive previous major version (if applicable)
```

### 14.4 Breaking Change Policy

| Criteria | Mitigation |
|---|---|
| Component prop removed | 1 sprint deprecation warning + codemod |
| Token value changes | Documented in changelog with visual diff |
| Component renamed | Old name aliased for 1 sprint |
| Default variant changed | Migration guide + before/after comparison |
| Library restructuring | Migration guide + codemod + 2 sprint overlap |

**Breaking change communication:**
1. 2 weeks before: DSG Council announcement + migration timeline
2. 1 week before: Migration guide published + codemod available
3. Day of release: Release notes + team notification
4. 1 week after: Office hours for migration support

### 14.5 Team Communication

| Event | Channel | Template |
|---|---|---|
| Release scheduled | Slack #design-systems | "Antigravity v{X.Y.Z} releasing {date}. Changes: [...]" |
| Release published | Slack #general + #engineering | "Antigravity v{X.Y.Z} now live. Changelog: [link]" |
| Breaking change | Slack #design-systems + email | "Breaking change: [summary]. Migration by: [date]" |
| Patch / hotfix | Slack #design-systems | "Hotfix v{X.Y.Z+1} published for [issue]" |
| Deprecation warning | Component documentation + Slack | "[Component] deprecated in v{X.Y}. Use [alternative] instead." |

---

## 15. Future Expansion Rules

### 15.1 Adding New Components

| Gate | Requirement |
|---|---|
| **C1** | Use case validated: component solves a problem that existing components cannot |
| **C2** | Frequency justification: component used in 3+ module screens or 2+ user flows |
| **C3** | Atomic placement: component fits into the existing atomic hierarchy without creating a new level |
| **C4** | Token compliance: component uses only existing tokens â€” no new primitive tokens introduced |
| **C5** | Accessibility designed-in: WCAG AA target from day one, not retrofitted |
| **C6** | Spec complete: component spec template fully populated before any design work |

### 15.2 Adding New Tokens

| Gate | Requirement |
|---|---|
| **T1** | Justification: existing tokens cannot express the required value through combination |
| **T2** | Contrast verification: new color token passes contrast against all 4 surface backgrounds |
| **T3** | Category mapping: token fits into one of the 9 token categories (no new categories) |
| **T4** | Theme generation: dark, light, and high-contrast values calculated for all new color tokens |
| **T5** | Primitive-first: create primitive tokens first, then semantic aliases, then component tokens |
| **T6** | Limit: no more than 5 new tokens per release cycle without DSG Council approval |

### 15.3 Adding New Breakpoints

| Gate | Requirement |
|---|---|
| **B1** | Usage data confirms users are accessing the application at the target breakpoint |
| **B2** | Backward compatibility: existing components must not break at the new breakpoint |
| **B3** | Variant strategy: responsive variant strategy documented before breakpoint addition |
| **B4** | Testing: all 20+ components verified at new breakpoint before release |

### 15.4 Adding New Themes

| Gate | Requirement |
|---|---|
| **H1** | Token-only approach: themes must be implementable by changing semantic token values â€” no component variant changes |
| **H2** | Accent derivation formula documented: `color-accent-primary` derived from hue shift on base palette |
| **H3** | Contrast auto-generated: all new theme tokens pass WCAG AA auto-check |
| **H4** | Accent customization: 12 preset accent colors (v1), custom hue picker (v2+) |
| **H5** | 3-tier target: Primitive â†’ Semantic â†’ Component â€” dark always first, other themes derived |

### 15.5 Scaling Rules for 100+ â†’ 1,000+ Components

| Threshold | Action |
|---|---|
| **100 components** | Split Antigravity Library into sub-libraries by atomic level (Atoms.ml, Molecules.ml, Organisms.ml) |
| **200 components** | Add domain-specific libraries (Analytics.ml, AI.ml, Data.ml) |
| **500 components** | Implement Figma variable scoping per library |
| **1,000 components** | Create design system portal (Zeroheight / Supernova) with full search, cross-reference, and usage analytics |

### 15.6 RTL Readiness

| Requirement | Timeline |
|---|---|
| All spacing uses logical CSS properties (`margin-inline-start`, `padding-inline-end`) | From day one |
| Icons mirror horizontally in RTL context | v1.0 |
| Layout direction tokens added for RTL | v1.0 (defined, not implemented) |
| Component auto layout direction is token-based (not hardcoded LTR) | v1.1 |
| Full RTL component audit | v1.2 |

### 15.7 Dynamic Color (Future)

| Phase | Feature | Timeline |
|---|---|---|
| **Phase 1** | 12 preset accent colors | v1.0 |
| **Phase 2** | Custom hue color picker | v1.1 |
| **Phase 3** | Wallpaper-based dynamic color extraction | v2.0 |
| **Phase 4** | Brand themes (per-domain coloring) | v2.0+ |

### 15.8 AI Component Pattern Library Expansion

As AI features grow, the following component patterns must be added to the system:

| Pattern | Priority | Description |
|---|---|---|
| **Ghost Hint** | P1 | AI suggestion shown as ghosted text in input fields |
| **Streaming Text** | P1 | Text that appears character-by-character with cursor indicator |
| **Thinking Indicator** | P1 | Animated indicator showing AI is processing |
| **Agent Status Badge** | P1 | "Thinking" / "Ready" / "Error" badge for AI agents |
| **Suggestion Card** | P2 | AI-generated suggestion with accept/dismiss actions |
| **Confidence Meter** | P2 | Visual confidence bar for AI predictions |
| **Contextual Help** | P2 | AI-generated help text shown inline on hover |
| **Summary Block** | P2 | AI-generated summary with expand/collapse |
| **AI Command Input** | P2 | Natural language input with command autocomplete |
| **Agent Activity Feed** | P3 | Real-time feed of what AI agents are doing |

---

## Appendix A: Quick Reference Card

### Naming Reference

| Construct | Convention | Example |
|---|---|---|
| Pages | PascalCase | `Button â€” States` |
| Frames | kebab-case + suffix | `button-container` |
| Components | PascalCase | `Button`, `InputField` |
| Variant properties | camelCase | `size`, `variantStyle` |
| Variant values | kebab-case | `primary`, `md` |
| Boolean variants | `is` prefix | `isDisabled` |
| Primitives tokens | kebab-case, category prefix | `color-blue-500` |
| Semantic tokens | kebab-case, purpose-based | `color-bg-card` |
| Figma variables | `$` prefix | `$color-accent-primary` |
| Icons | snake_case | `check_circle` |

### Auto Layout Defaults

| Component | Direction | Padding | Gap | Width | Height |
|---|---|---|---|---|---|
| Button | Horizontal | 16Ã—8px | 8px | Hug | 44px |
| Input | Vertical | 12Ã—8px | 4px | Fill | 44px |
| Card | Vertical | 20px | 12px | Fill | Hug |
| Badge | Horizontal | 8Ã—2px | 4px | Hug | 22px |
| Modal | Vertical | 24px | 24px | Fixed | Hug |

### Token Categories (9)

`color` | `typography` | `spacing` | `border-radius` | `box-shadow` | `motion` | `breakpoint` | `z-index` | `opacity`

### Accessibility Minimums

- **Contrast:** 4.5:1 text / 3.0:1 non-text (AA)
- **Touch target:** 44Ã—44px below 1024px
- **Focus:** 2px offset 2px, indigo (#6366F1)
- **Motion:** Every animation has a static fallback
- **Reduced motion:** All animations respect `prefers-reduced-motion`

---

## Appendix B: Figma Plugin Requirements

| Plugin | Purpose | Required For |
|---|---|---|
| **Tokens Studio** | Token management, theme switching, sync | All designers |
| **A11y â€” Contrast Checker** | WCAG contrast verification | All designers (pre-publish) |
| **A11y â€” Focus Order** | Tab order verification | Component reviewers |
| **Iconify** | lucide-react icon browser | All designers |
| **Similary** | Component similarity detection | Library health checks |
| **Design Lint** | Auto-layout, token, naming audit | Pre-publish automation |
| **Export to Code** | Code snippet generation | Handoff |
| **Batch Styler** | Bulk token application | Token migrations |
| **Find / Replace** | Bulk property changes | Token migrations |
| **Version History** | Built-in Figma revisions | All files |

---

## Appendix C: File Health Scorecard

| Metric | Target | Measurement |
|---|---|---|
| Token usage coverage | 100% of fills/effects use tokens | Design Lint scan |
| Auto layer coverage | 100% of component frames | Manual + plugin |
| Naming compliance | 100% of layers named semantically | Design Lint scan |
| Variant completeness | 100% of required states present | Manual audit |
| Contrast compliance | 100% pass WCAG AA | A11y plugin scan |
| Component description coverage | 100% of published components | Figma API |
| Dev Mode annotation coverage | 100% of interactive components | Manual audit |
| Changelog completeness | Every version has entry | Release checklist |
| Component â†” Code parity | 90%+ match (visual diff) | Bi-weekly audit |
| Library usage (module adoption) | 95%+ of module instances use library | Figma API |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Principal Design Systems Director | Initial Figma governance document |
