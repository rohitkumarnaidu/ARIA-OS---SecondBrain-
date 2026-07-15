## Document Control

| Field | Value |
|---|---|
| Document ID | DSG-WF12-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Part XII â€” Future Expansion

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `InformationArchitecture.md` (module registry pattern), `DesignStrategy.md` (expansion principles), `00_ProjectVision.md` (product roadmap).

---

## 12.1 Module Registration Interface

Every new module must implement the `ModuleRegistration` contract. This ensures the system can discover, mount, and integrate the module without modifying existing code.

### TypeScript Interface

```typescript
interface ModuleRegistration {
  /** Unique identifier (kebab-case) */
  id: string

  /** Human-readable name */
  name: string

  /** Lucide icon component */
  icon: React.ComponentType

  /** Primary route path */
  route: string

  /** Navigation group placement */
  navGroup: 'primary' | 'secondary' | 'tertiary'

  /** Keyboard shortcut (e.g., 'g t' for Tasks) */
  shortcuts?: string[]

  /** Register searchable content types from this module */
  searchScope?: {
    type: string
    fields: string[]
    weight: number
  }

  /** Notification types this module can trigger */
  notificationTypes?: {
    id: string
    priority: 'P0' | 'P1' | 'P2' | 'P3'
    defaultEnabled: boolean
  }[]

  /** Dashboard widgets this module provides */
  widgetSlots?: {
    slot: 'hero' | 'grid' | 'sidebar'
    component: React.ComponentType
    defaultOrder: number
  }[]

  /** Whether this module requires AI to function */
  requiresAI: boolean

  /** Module version (semver) */
  version: string

  /** Optional dependency IDs */
  dependsOn?: string[]
}
```

---

## 12.2 Module Template

Every new module must provide consistency across 9 layers.

### Layer Template

```
Layer                 Location                                 Pattern
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
1. Route              apps/web/app/[module]/page.tsx           'use client'
2. State              apps/web/stores/[module]-store.ts        Zustand (local)
3. Data Model         packages/database/schemas/[module].py    Pydantic BaseModel
4. API                apps/api/app/api/[module].py             CRUD + search + filter
5. Supabase Table     migrations/[timestamp]_[module].sql      RLS enforced
6. AI Agent           packages/ai/agents/[module]_agent.py     Async function
7. Prompt File        prompts/agents/[module]_agent.md         YAML frontmatter
8. Tests              tests/test_[module]*.py                  Happy + error paths
9. Wireframe          docs/design/wireframes/[module].md       Desktop/Tablet/Mobile
```

### New Module Checklist

- [ ] **Route:** No collision with existing routes (check `FrontendRoutingNavigation.md`)
- [ ] **Nav group:** Does not exceed 8 items per group (split if so)
- [ ] **AI:** Provides algorithmic fallback if `requiresAI: false`
- [ ] **Data model:** Uses existing `user_id` isolation pattern
- [ ] **API:** Uses `/api/v1/[module]/` prefix with versioning headers
- [ ] **Widgets:** Registers dashboard widget with default placement
- [ ] **Search:** Registers search scope with weighted fields
- [ ] **Notifications:** Defines notification types with priorities
- [ ] **Tests:** Minimum 80% coverage on new code
- [ ] **Works offline:** Graceful degradation without network

---

## 12.3 Extension Slots

The system provides 6 extension slots that modules can plug into without modifying core code.

### Slot Map

| Slot | What It Provides | Implemented As | Example |
|---|---|---|---|
| **Navigation** | Sidebar / bottom tab entry | Register in `navGroup` | All 15 modules |
| **Dashboard Widget** | Slot in dashboard grid | Register in `widgetSlots` | Briefing card, task count |
| **Search Scope** | Searchable content type | Register in `searchScope` | All modules with content |
| **Notification Type** | Notification trigger + settings | Register in `notificationTypes` | Task reminder, course nudge |
| **Command Palette** | Commands for Cmd+K | Auto from shortcuts | "Go to Tasks", "Add Task" |
| **Settings Section** | Settings page entry | Register in settings registry | Profile, AI, Notifications |

---

## 12.4 Break-Never Contract

The system guarantees that adding a new module will never break existing functionality.

### Commitments

| Commitment | Description |
|---|---|
| **No existing component modification** | Never modify `@/components/ui/*` for a new module |
| **No token removal or rename** | Design tokens are additive only â€” never removed or renamed |
| **No layout shift** | New module adds nav items without rearranging existing ones |
| **No API breaking change** | New endpoints don't modify existing endpoint contracts |
| **No data model migration** | New tables never require changes to existing table schemas |
| **Module can be disabled** | Every module can be toggled off independently in Settings |
| **No global CSS pollution** | Module styles scoped to module's component tree |
| **No bundle size impact** | Modules are lazy-loaded â€” 0kb impact unless visited |

### Migration Path for Breaking Changes

If a breaking change is absolutely necessary:
1. Deprecate old API with `Deprecation: true` + `Sunset` headers
2. Add `/api/v2/[module]/` with new contract
3. Maintain both versions for 6 months minimum
4. Remove v1 only after 0 active users on old version

---

## 12.5 Plugin Architecture (Future)

### Roadmap

| Phase | Timeline | Features |
|---|---|---|
| **Phase 1** | Q4 2026 | Module Registry + Extension Slots (this document) |
| **Phase 2** | Q1 2027 | Plugin SDK: JS sandbox (QuickJS), public API, manifest format |
| **Phase 3** | Q2 2027 | Plugin Marketplace: discover, install, update, permissions |
| **Phase 4** | Q3 2027 | Community: ratings, reviews, verified publisher badges |

### Manifest Format (Future)

```json
{
  "id": "plugin-journal",
  "name": "Journal Plugin",
  "version": "1.0.0",
  "author": "Community Developer",
  "description": "Daily journaling with AI prompts",
  "permissions": ["storage:local", "api:read:tasks", "api:read:goals"],
  "extends": {
    "navigation": { "group": "secondary" },
    "dashboard": { "slot": "grid", "order": 6 },
    "search": { "types": ["journal-entry"] },
    "notifications": { "types": ["journal-reminder"] }
  },
  "entry": "main.js",
  "styles": "styles.css"
}
```

---

## Future Module Candidates

The IA supports these future additions (see `InformationArchitecture.md` for full list):

| Module | Group | Priority | Dependencies |
|---|---|---|---|
| Journal | Secondary | High | None |
| Collections | Secondary | Medium | Resources |
| Templates | Secondary | Low | Goals, Tasks |
| Tags | Cross-cutting | Medium | All modules |
| Calendar | Secondary | High | Tasks, Courses |
| Notes | Secondary | High | Resources |
| Bookmark Manager | Secondary | Medium | Resources |
| Team Workspaces | Collaboration | Future | All modules |
