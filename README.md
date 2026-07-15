## Document Control

| Field | Value |
|---|---|
| Document ID | LEG-README-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Second Brain OS (ARIA OS)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.11-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-2582%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/Coverage-95.56%25-success)]()

A personal AI productivity system that replaces 12+ tools with one intelligent platform. Purpose-built for BTech CSE students, open-source, and **Rs. 0 forever**.

---

## Demo

> _Screenshot coming soon. Run `make dev-web` + `make dev-api` to see the live dashboard._

---

## Key Features

| Module | What It Does | AI Agent |
|---|---|---|
| **Dashboard & Briefing** | Daily AI-generated morning briefing with top 3 priorities | A09 â€” Briefing Agent |
| **Task Manager** | Smart tasks with auto-reschedule, zero-miss policy | A01 â€” Task Agent |
| **Course Tracker** | Udemy/Coursera/NPTEL/YouTube â€” all in one place | A14 â€” Nudge Agent |
| **YouTube Vault** | One-tap save, AI summaries, 60-day expiry | â€” |
| **Idea Vault** | Capture â†’ score â†’ validate â†’ build pipeline | â€” |
| **Opportunity Radar** | Daily scan: internships, hackathons, fellowships, freelance | A06 â€” Opportunity Agent |
| **Income Tracker** | All income streams, effective hourly rate | â€” |
| **Project Tracker** | Kanban phases, GitHub integration, blocker logging | â€” |
| **Time Tracker** | Pomodoro, deep work detection, focus analytics | â€” |
| **Habit Engine** | Custom habits, streaks, goal-linked consistency | A14 â€” Nudge Agent |
| **Sleep Monitor** | Logs, quality scoring, wind-down messages | A13 â€” Sleep Agent |
| **Academic Planner** | Semesters, CGPA, at-risk alerts | â€” |
| **Resource Library** | Auto-tagging, semantic search, browser extension | A03 â€” Learning Agent |
| **Goal & Roadmap** | Drag-and-drop milestones, skill progression | A08 â€” Roadmap Agent |
| **Weekly Review** | AI-generated narrative of your week | A10 â€” Weekly Review Agent |
| **ARIA Chat** | Context-aware AI assistant with persistent memory | A00 â€” ARIA Orchestrator |

---

## Architecture

```
apps/api/          â† FastAPI backend (29 routers, /api/v1/)
apps/web/          â† Next.js 14 PWA (cyberpunk design system)
packages/ai/       â† 10 AI agents + PromptLoader + LLM client
packages/config/   â† FastAPI config, Supabase, JWT auth
packages/database/ â† Pydantic schemas (all 18+ tables)
packages/shared/   â† Cache, rate limiter, audit, security utilities
services/scheduler/â† 7 cron jobs (APScheduler)
prompts/           â† 14 AI prompt templates (YAML frontmatter)
tests/             â† 2,582+ passing tests, 95.56% coverage
```

**AI Resilience:** Circuit breakers, exponential backoff, provider failover (Ollama â†’ Claude â†’ OpenAI), algorithmic fallback for every AI feature.

---

## Tech Stack

**Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand, Framer Motion, React Flow, Recharts, shadcn/ui

**Backend:** FastAPI, Python 3.10, Supabase (PostgreSQL + Auth + Realtime), APScheduler, Ruff, Black, Pytest

**AI:** Ollama (Mistral 7B â€” local), Claude API (fallback), PromptLoader with 14 prompt files, 10 specialized agents

**Infrastructure:** Docker Compose, Vercel (web), Railway (API), GitHub Actions (7 CI jobs), Pre-commit hooks

---

## Quick Start

```bash
# 1. Clone + install
git clone <repo-url>
cd "ARIA OS - SecondBrain"
make install

# 2. Configure environment
cp .env.example .env.local  # Edit with Supabase credentials

# 3. Validate setup
make validate-prompts
make test

# 4. Start development
make dev-api   # Terminal 1 â€” http://localhost:8000
make dev-web   # Terminal 2 â€” http://localhost:3000
```

**Detailed guide:** [`docs/quickstart.md`](docs/quickstart.md) â€” get running in under 10 minutes.

---

## Documentation

| Category | Location |
|---|---|
| Quick-Start Guide | [`docs/quickstart.md`](docs/quickstart.md) |
| Full Developer Onboarding | [`docs/operations/44_DeveloperOnboarding.md`](docs/operations/44_DeveloperOnboarding.md) |
| Master Reference (AGENTS.md) | [`AGENTS.md`](AGENTS.md) |
| Project Vision | [`docs/product/00_ProjectVision.md`](docs/product/00_ProjectVision.md) |
| Product Requirements (PRD) | [`docs/product/02_PRD.md`](docs/product/02_PRD.md) |
| Business Requirements (BRD) | [`docs/product/03_BRD.md`](docs/product/03_BRD.md) |
| Architecture Docs | [`docs/engineering/`](docs/engineering/) |
| API Reference | [`docs/engineering/17_API.md`](docs/engineering/17_API.md) |
| AI Agent Spec | [`docs/ai/20_Agent.md`](docs/ai/20_Agent.md) |
| Design System | [`docs/design/10_DesignSystem.md`](docs/design/10_DesignSystem.md) |
| Documentation Index | [`docs/DOCUMENTATION_INDEX.md`](docs/DOCUMENTATION_INDEX.md) |

---

## Commands Cheat Sheet

```bash
make help              # List all targets
make dev-api           # Start backend
make dev-web           # Start frontend
make lint              # Run all linters
make test              # Run all Python tests
make test-coverage     # Tests + HTML coverage report
make validate-prompts  # Validate prompt frontmatter
make pre-commit        # Full pre-commit check
make docker-up         # Start Docker services
```

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines, and [`docs/governance/documentation-ownership.md`](docs/governance/documentation-ownership.md) for documentation ownership.

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- All contributions welcome: bug reports, feature requests, PRs, documentation improvements

**CI pipeline** (7 jobs): Frontend â†’ Backend â†’ Prompts â†’ Docker â†’ Security â†’ Lighthouse â†’ Pentest. All must pass before merge.

---

## License

[MIT](LICENSE) â€” free to use, modify, and distribute. Built for students, by a student.

---

## Stats

| Metric | Value |
|---|---|
| Python files | 184 |
| TypeScript files | 748 |
| Documentation files | 270 |
| Passing tests | 2,582+ |
| Code coverage | 95.56% |
| AI agents | 10 |
| API endpoints | ~80 under /api/v1/ |
| Architecture Decision Records | 15 |
| Storybook stories | 380 |
| E2E specs | 21 |
