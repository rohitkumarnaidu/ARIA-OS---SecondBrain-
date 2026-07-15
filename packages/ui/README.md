# @secondbrain/ui — Shared UI Component Package

**Status:** Scaffold — not yet populated

**Purpose:** Shared React UI components consumed by `apps/web`, `apps/admin`, and future `apps/mobile`.

**Migration Plan:**
- Currently all UI components live in `apps/web/components/ui/`
- Phase 1: Create barrel exports re-exporting from `apps/web/components/ui/`
- Phase 2: Migrate shared components here when admin/mobile apps are created
- Must support: Tree-shaking, TypeScript, Tailwind CSS design tokens

**Design System:** Cyberpunk (#0A0B0F theme, Syne/DM Sans/JetBrains Mono fonts) — see `docs/design/10_DesignSystem.md`
