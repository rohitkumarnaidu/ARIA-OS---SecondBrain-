# ADR-001: Monorepo over Multi-Repo

## Status
Accepted

## Date
2024-06-01

## Context
This project consists of multiple deployable components: a Next.js frontend (`apps/web`), a FastAPI backend (`apps/api`), a scheduler service (`services/scheduler`), AI agent modules (`packages/ai/agents`), and shared packages for config, database schemas, types, and UI components. As a solo developer, managing dependencies across these components is critical. The options were a single monorepo or separate repositories per component.

## Decision
Adopt a monorepo structure with `apps/` for deployable applications and `packages/` for shared libraries. The root `package.json` orchestrates frontend dependencies while Python shared packages live under `packages/`. Root-level `requirements.txt` covers Python deps across all services.

## Consequences

### Positive
- Single `git pull` gets the entire project — no coordination across repos
- Atomic commits can span frontend, backend, and shared packages (e.g., adding a DB column and updating both API and UI in one commit)
- Shared packages (`packages/config/core`, `packages/types`, `packages/shared/utils`) are imported by path, not published — no version bumping or npm/PyPI publishing overhead
- Common tooling config at root (ESLint, Ruff, Black, tsconfig) ensures consistency

### Negative
- Larger `git clone` (~50MB+ with node_modules and Python venvs excluded)
- All CI pipelines trigger on any change, though this is manageable with path filters
- Harder to scale to a large team with conflicting interests (irrelevant for solo developer)

### Neutral
- Requires discipline to keep `apps/` and `packages/` boundaries clean — a package should not depend on an app
- Monorepo tooling (npm workspaces, `pip -e`) is already set up and proven
