## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-EPL-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |

# Enterprise Plan â€” Second Brain OS (ARIA OS)

**Version:** 1.0.0  
**Status:** Active  
**Last Updated:** 2026-06-18  
**Target:** Production-ready enterprise MVP

---

## Executive Summary

The codebase has been hardened across **11 dimensions**. All **5 critical** and **7 high-severity** issues from the initial audit are resolved. The remaining work is organized into **3 tiers** below.

**Current health:**
- Build: 0 errors | Lint: 0 warnings | Prompts: 14/14 validated
- 21 stores â†’ 21 services â†’ 28 dashboard routes (all wired)
- 11 AI agents (plus 8 skill sub-agents) with try/except + circuit breaker protection
- 31 backend routers with REST standards (201, 204, pagination)
- 78 catch blocks with proper TypeScript narrowing

---

## Tier 1: Production Hardening (This Week)

### 1.1 Documentation Sync
| Task | Files | Effort |
|---|---|---|
| Update AGENTS.md line counts to match actual prompt files | `AGENTS.md` Â§9.4 | 15 min |
| Bump AGENTS.md version to 5.0.0 reflecting all fixes | `AGENTS.md` header | 5 min |

### 1.2 Backend Polish
| Task | Files | Effort |
|---|---|---|
| Change `created_at`/`updated_at` from `str` to `datetime` in Response schemas | `packages/database/schemas/*.py` (~13 files) | 30 min |
| Fix `auth.py` `datetime.utcnow()` â†’ `datetime.now(datetime.UTC)` | `packages/config/core/auth.py:13,15` | 5 min |
| Fix `logger.py` `datetime.utcnow()` deprecation | `packages/shared/utils/logger.py:24` | 5 min |
| Fix `logger.py` ERROR/WARN logged at INFO level | `packages/shared/utils/logger.py:29` | 5 min |
| Fix `supabase.py` import (`import supabase` â†’ `from supabase import create_client`) | `packages/config/core/supabase.py:1` | 5 min |
| Add empty URL/key guard in supabase client | `packages/config/core/supabase.py:10` | 5 min |

### 1.3 Pre-commit & Dev Tooling
| Task | Files | Effort |
|---|---|---|
| Pin Prettier to stable v3.x (not alpha) | `.pre-commit-config.yaml:99` | 5 min |
| Expand Bandit to scan `apps/api/` + `services/scheduler/` | `.pre-commit-config.yaml:64` | 5 min |
| Remove `apps/web/.env.local` from git tracking, add to `.gitignore` | `.gitignore` | 5 min |

### 1.4 Frontend Type Housekeeping
| Task | Files | Effort |
|---|---|---|
| Remove unused `IdeaStage`, `TimeEntryType`, `GoalMilestone` exports | `apps/web/lib/types/index.ts` | 5 min |
| Remove unused `ProjectStatus`, `ProjectPhase` exports (if unused) | `apps/web/lib/types/index.ts` | 5 min |

**Total Tier 1 effort:** ~1.5 hours

---

## Tier 2: Quality & Monitoring (This Sprint)

### 2.1 Scheduler Upgrade
| Task | Files | Effort |
|---|---|---|
| Replace `print()` with structured logging in all 15 cron jobs | `services/scheduler/crons/*.py` | 1 hour |
| Fix `asyncio.get_event_loop().run_forever()` â†’ `asyncio.run(main())` | `services/scheduler/main.py:94` | 15 min |
| Add scheduler health check endpoint | `services/scheduler/main.py` | 30 min |

### 2.2 Docker Production Profile
| Task | Files | Effort |
|---|---|---|
| Create `docker-compose.prod.yml` with production targets | `docker-compose.prod.yml` | 1 hour |
| Add resource limits (CPU/memory) to all services | `docker-compose.yml` | 30 min |
| Add proper health checks to all compose services | `docker-compose.yml` | 30 min |
| Add Docker build cache to CI workflow | `.github/workflows/ci.yml` | 15 min |

### 2.3 Integration & E2E Tests
| Task | Files | Effort |
|---|---|---|
| Write 1-2 integration tests hitting FastAPI with test Supabase instance | `tests/test_integration.py` | 2 hours |
| Wire Playwright E2E tests into CI pipeline | `.github/workflows/ci.yml` | 1 hour |
| Add coverage artifact upload (Codecov/Coveralls) | `.github/workflows/ci.yml` | 30 min |

### 2.4 LLM Performance
| Task | Files | Effort |
|---|---|---|
| Add semantic caching for repeated LLM queries | `packages/ai/client.py` | 1 hour |
| Add user auth caching (reduce Supabase auth calls) | `packages/config/core/auth.py` | 30 min |

**Total Tier 2 effort:** ~8 hours

---

## Tier 3: Scale & Infrastructure (Next Sprint)

### 3.1 Infrastructure-as-Code
| Task | Files | Effort |
|---|---|---|
| Terraform config for Supabase project provisioning | `infrastructure/terraform/` | 2 hours |
| Terraform config for Vercel project + domain | `infrastructure/terraform/` | 1 hour |
| Terraform config for Railway service deployment | `infrastructure/terraform/` | 1 hour |
| Kubernetes manifests for container orchestration | `infrastructure/k8s/` | 3 hours |

### 3.2 Observability Stack
| Task | Files | Effort |
|---|---|---|
| Integrate Sentry for error tracking (frontend + backend) | `apps/web/sentry.client.config.ts`, `apps/api/main.py` | 1 hour |
| Add structured logging to scheduler cron jobs | `services/scheduler/crons/*.py` | 30 min |
| Set up Logtail/Datadog for log aggregation | config files | 1 hour |
| Create Grafana dashboard for RED metrics | `monitoring/` | 2 hours |

### 3.3 Edge & Bundle Optimization
| Task | Files | Effort |
|---|---|---|
| Configure `next/bundle-analyzer` for bundle CI checks | `apps/web/next.config.js` | 30 min |
| Add ISR for static pages to reduce build time | `apps/web/app/` | 1 hour |
| Set up CDN caching strategy for API responses | `apps/api/main.py` | 1 hour |

### 3.4 Security Hardening
| Task | Files | Effort |
|---|---|---|
| Add rate limiting to individual endpoints (chat: 30/min) | `apps/api/app/api/chat.py` | 15 min |
| Implement API key rotation mechanism | `packages/config/core/auth.py` | 1 hour |
| Add input sanitization for all user-facing prompts | `packages/shared/utils/security.py` | 30 min |
| Set up automated dependency scanning (Trivy in CI) | `.github/workflows/ci.yml` | already done |

**Total Tier 3 effort:** ~15 hours

---

## Effort Summary

| Tier | Hours | Impact |
|---|---|---|
| **Tier 1** â€” Production Hardening | **1.5h** | Fixes all remaining lint/type warnings, doc drift, deprecations |
| **Tier 2** â€” Quality & Monitoring | **8h** | Scheduler reliability, Docker production readiness, test coverage |
| **Tier 3** â€” Scale & Infrastructure | **15h** | IaC, observability, edge optimization, security |
| **Total** | **~24.5h** | Production enterprise MVP |

---

## Current vs Target State

| Metric | Current | Target (after plan) |
|---|---|---|
| Build errors | **0** | 0 |
| Lint warnings | **0** | 0 |
| Prompt validation | **14/14** | 14/14 |
| API REST compliance (201, 204, pagination) | **100%** | 100% |
| AI agent LLM call safety | **100%** | 100% |
| Store wiring coverage | **28/28 routes** | 28/28 routes |
| Type alignmnt (frontend â†” backend) | **100%** | 100% |
| `any` types (high severity) | **0** | 0 |
| `catch(err: any)` | **0** | 0 |
| Docker production build | **broken** (fixed in this session) | âœ… working |
| Frontend CI coverage enforcement | **80% lines** | 80% lines |
| Scheduler coverage | **0% â†’ added** | â‰¥70% |
| Integration tests | **0** | â‰¥2 |
| E2E tests in CI | **7 specs (not wired)** | all 7 running |
| IaC (Terraform/K8s) | **empty** | provisioned |
| Observability | **basic logging** | Sentry + Logtail + Grafana |
| Bundle analysis | **none** | automated CI check |
| Scheduler logging | **print()** | structured JSON |
| Auth caching | **none** | in-memory TTL |
| LLM semantic caching | **none** | TTL cache |

---

## Architecture Decision Log

| ADR | Status | Notes |
|---|---|---|
| ADR-001: Monorepo | âœ… Adopted | Confirmed |
| ADR-002: Supabase | âœ… Adopted | Confirmed |
| ADR-003: Ollama â†’ Claude | âœ… Adopted | Circuit breaker + provider failover in place |
| ADR-004: In-process agents | âœ… Adopted | All 11 agents run as async functions |
| ADR-005: Zustand | âœ… Adopted | 21 stores, 21 services |
| ADR-006: APScheduler | âœ… Adopted | 15 cron jobs running |
| ADR-007: PWA | âœ… Adopted | Service worker + manifest |
| ADR-008: No event bus | âœ… Adopted | Deferred to post-MVP |

---

## Next Actions

1. **Tier 1.1** â€” Update AGENTS.md line counts (5 min)
2. **Tier 1.2** â€” Fix datetime types in backend schemas (30 min)
3. **Tier 1.3** â€” Pin Prettier stable + expand Bandit (10 min)
4. **Tier 1.4** â€” Remove unused type exports (5 min)
5. Begin **Tier 2** scheduler upgrade
