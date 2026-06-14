# Technology Stack — Complete Inventory & Decision Framework

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-TECHSTACK-001 |
| **Version** | 2.0.0 |
| **Status** | Active |
| **Last Updated** | 2026-06-11 |
| **Classification** | Internal — Architecture Reference |
| **Owner** | Platform Engineering |

---

## 1. Executive Summary

Second Brain OS is built on **26 open-source and free-tier technologies** organized across 7 functional categories. This document serves as the authoritative reference for every technology in the stack — covering selection rationale, alternatives considered, licensing, cost, maturity, upgrade paths, vendor lock-in assessment, and exit strategies.

**Core Philosophy:** Zero-cost operation for single-user use with a clear migration path to enterprise scale. Every paid alternative has a documented free-tier equivalent that covers the system's current needs. No technology is adopted without a documented exit strategy.

**Stack Highlights:**
- **Frontend:** Next.js 14 (React) + Tailwind CSS + Framer Motion
- **Backend:** FastAPI (Python 3.10) + Supabase PostgreSQL
- **AI:** Ollama (local, default) + Claude API (fallback)
- **DevOps:** Vercel + GitHub Actions
- **Monthly Cost:** $0 (free tiers)
- **Enterprise Scaling Cost:** ~$150–400/month

---

## 2. Technology Categories

| # | Category | Count | Total Monthly Cost |
|---|---|---|---|
| 1 | Frontend | 8 | $0 |
| 2 | Backend | 3 | $0 |
| 3 | Database & Storage | 2 | $0 |
| 4 | AI / ML | 4 | $0 |
| 5 | DevOps & Hosting | 4 | $0 |
| 6 | Testing & Quality | 3 | $0 |
| 7 | Monitoring & Observability | 3 | $0 |
| | **Total** | **27** | **$0** |

---

## 3. Frontend

### 3.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **Next.js** | 14.2.x | App framework, routing, SSR/SSG, PWA | MIT | Mature | Free | Best React meta-framework; built-in SSR, ISR, PWA; massive ecosystem; Vercel integration |
| **React** | 18.3.x | UI component library | MIT | Mature | Free | Industry standard component model; hooks-based; large talent pool |
| **TypeScript** | ^5.4 | Type-safe JavaScript | Apache 2.0 | Mature | Free | Catch errors at compile time; superior DX; self-documenting code |
| **Tailwind CSS** | ^3.4 | Utility-first CSS framework | MIT | Mature | Free | Minimal CSS bundle; consistent design; rapid prototyping; dark mode built-in |
| **Framer Motion** | ^11.0 | Animation library | MIT | Mature | Free | Declarative animations; layout animations; gesture support; SSR compatible |
| **Zustand** | ^4.5 | State management | MIT | Mature | Free | Minimal boilerplate; no providers; TypeScript-first; localStorage persistence built-in |
| **Lucide React** | ^0.300 | Icon library | ISC | Mature | Free | 1000+ consistent icons; tree-shakeable; no runtime overhead |
| **Recharts** | ^2.12 | Charting library | MIT | Mature | Free | Composable React components; SVG-based; responsive; accessible |

### 3.2 Alternatives Considered & Rejected

| Technology | Alternative 1 | Alternative 2 | Decision |
|---|---|---|---|
| **Next.js** | Remix (similar SSR, smaller ecosystem) | Gatsby (static-only, slow builds) | **Next.js** — stronger PWA story, Vercel synergy, larger community |
| **Tailwind CSS** | Chakra UI (component library lock-in) | Styled Components (runtime cost, bundle size) | **Tailwind** — zero runtime, smaller bundles, more flexible |
| **Zustand** | Redux Toolkit (boilerplate, context overhead) | Jotai (atomic, learning curve) | **Zustand** — simplest API, built-in persist, no context issues |
| **Framer Motion** | React Spring (physics-based, less declarative) | CSS Animations (no orchestration) | **Framer Motion** — declarative, SSR, gesture support |
| **Recharts** | Chart.js (canvas-based, less React-native) | D3.js (low-level, high complexity) | **Recharts** — React-first, composable, accessible |

### 3.3 Decision Matrix — Frontend Framework

| Criterion | Weight | Next.js | Remix | Gatsby |
|---|---|---|---|---|
| SSR/SSG Support | 20% | 10 (built-in) | 9 | 10 |
| PWA Support | 15% | 9 (service worker) | 7 | 8 |
| Ecosystem Size | 15% | 10 (largest) | 6 | 7 |
| Vercel Integration | 10% | 10 (native) | 5 | 5 |
| TypeScript DX | 10% | 9 | 8 | 8 |
| Bundle Size | 10% | 8 | 8 | 5 |
| Community / Talent | 10% | 10 | 5 | 5 |
| Learning Curve | 10% | 8 | 5 | 8 |
| **Weighted Score** | **100%** | **9.35** | **6.85** | **7.00** |

### 3.4 Exit Strategy — Frontend

| Technology | Lock-in Risk | Exit Strategy |
|---|---|---|
| **Next.js** | Medium (Vercel-specific features) | Can migrate to any Node.js host; switch to Vite + React Router for full framework independence |
| **Tailwind CSS** | Low | Generated CSS is static; can migrate to vanilla CSS or any post-CSS system |
| **Zustand** | Low | Isolated store modules; replace with Jotai or Redux per module without global refactor |
| **Framer Motion** | Low | Animation definitions in components; can replace with CSS animations gradually |
| **Recharts** | Low | SVG output; can replace with any SVG chart library |

---

## 4. Backend

### 4.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **FastAPI** | 0.110+ | REST API framework | MIT | Mature | Free | Async-native; automatic OpenAPI docs; Pydantic validation; fastest Python framework |
| **Python** | 3.10+ | Runtime language | PSF | Mature | Free | AI/ML ecosystem; scientific computing; readability; massive library support |
| **Uvicorn** | ^0.29 | ASGI server | BSD | Mature | Free | Fastest Python ASGI server; production-ready; HTTP/2 support |
| **Pydantic** | ^2.5 | Data validation & settings | MIT | Mature | Free | Runtime type checking; JSON Schema generation; FastAPI-integrated |

### 4.2 Alternatives Considered & Rejected

| Technology | Alternative 1 | Alternative 2 | Decision |
|---|---|---|---|
| **FastAPI** | Django REST (sync-only, heavy) | Flask (sync-only, no built-in validation) | **FastAPI** — async-native, automatic docs, Pydantic integration |
| **Python 3.10** | Node.js (better for real-time) | Go (better performance) | **Python** — superior AI/ML ecosystem, Ollama integration, faster development velocity |
| **Uvicorn** | Gunicorn (sync workers, older) | Daphne (less maintained) | **Uvicorn** — fastest ASGI, HTTP/1.1 + HTTP/2, built-in WebSocket |

### 4.3 Decision Matrix — Backend Framework

| Criterion | Weight | FastAPI | Django REST | Flask |
|---|---|---|---|---|
| Async Support | 20% | 10 (native) | 3 (limited) | 2 (manual) |
| Auto API Docs | 15% | 10 (OpenAPI built-in) | 5 (drf-spectacular) | 2 (manual) |
| Validation | 15% | 10 (Pydantic) | 6 (DRF serializers) | 3 (manual) |
| AI/ML Integration | 10% | 9 | 7 | 8 |
| Performance | 15% | 9 (async) | 5 (sync) | 5 (sync) |
| Learning Curve | 10% | 8 | 7 | 9 |
| Ecosystem | 10% | 6 | 9 | 8 |
| Production Readiness | 5% | 8 | 9 | 7 |
| **Weighted Score** | **100%** | **8.85** | **6.20** | **5.15** |

### 4.4 Exit Strategy — Backend

| Technology | Lock-in Risk | Exit Strategy |
|---|---|---|
| **FastAPI** | Low (standard ASGI) | Returns standard ASGI app; deployable on any ASGI server; routes are standard Python functions |
| **Pydantic** | Medium (pervasive schema definitions) | Pydantic v2 is widely adopted; schema extraction to JSON Schema enables cross-language migration |
| **Uvicorn** | Low (ASGI standard) | Switch to Daphne, Hypercorn, or any ASGI server |

### 4.5 Vendor Lock-in Assessment

| Technology | Lock-in Mechanism | Mitigation |
|---|---|---|
| **FastAPI** | Dependency injection patterns | Router handlers are pure functions; can be extracted to any framework |
| **Supabase** | PostgreSQL with Supabase extensions | PostgreSQL is standard; migrations to any PostgreSQL host (AWS RDS, Neon, etc.) |
| **Supabase Auth** | Auth schema tied to Supabase | JWT tokens are standard; migrate to Auth0 or Clerk by changing auth provider |

---

## 5. Database & Storage

### 5.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **Supabase PostgreSQL** | 15.x | Primary database — 21 tables | PostgreSQL License (open source) | Mature | Free (500 MB) | Full PostgreSQL; built-in auth; real-time subscriptions; RLS; generous free tier |
| **Supabase Storage** | n/a | File/asset storage | Apache 2.0 | Mature | Free (1 GB) | S3-compatible; RLS integration; CDN delivery |
| **Supabase Realtime** | n/a | WebSocket subscriptions | Apache 2.0 | Mature | Free (50 connections) | PostgreSQL WAL-based; automatic; no custom WebSocket server |

### 5.2 Alternatives Considered & Rejected

| Alternative | Why Rejected |
|---|---|
| **MongoDB Atlas** | No RLS; no real-time; document model unsuitable for relational data (tasks, habits, sleep logs) |
| **Firebase Firestore** | Vendor lock-in to GCP; no PostgreSQL features; expensive at scale; no SQL |
| **Neon Serverless PostgreSQL** | Newer platform; smaller free tier (0.5 GB); no built-in auth or real-time |
| **PlanetScale** | MySQL-based (no PostgreSQL); no real-time; limited free tier |
| **Turso (libSQL)** | Edge-focused; SQLite compatibility issues; immature ecosystem |

### 5.3 Decision Matrix — Database

| Criterion | Weight | Supabase | MongoDB Atlas | Neon |
|---|---|---|---|---|
| SQL Support | 20% | 10 (full PostgreSQL) | 0 | 10 |
| Real-time | 15% | 10 (WAL-based) | 0 | 0 |
| Built-in Auth | 15% | 10 (Google OAuth, JWT) | 0 | 0 |
| RLS/Row Security | 15% | 10 (policy-based) | 0 | 5 |
| Free Tier | 10% | 8 (500 MB DB, 50 MB/day) | 6 (512 MB shared) | 7 (0.5 GB) |
| Performance | 10% | 8 | 7 | 9 |
| Ecosystem | 10% | 9 | 8 | 5 |
| Migration Ease | 5% | 8 (standard PG) | 2 (document model) | 8 (standard PG) |
| **Weighted Score** | **100%** | **9.25** | **2.95** | **5.50** |

### 5.4 Exit Strategy — Database

| Technology | Lock-in Risk | Exit Strategy |
|---|---|---|
| **Supabase PostgreSQL** | Low (standard PostgreSQL) | `pg_dump` → restore to any PostgreSQL host (AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL, Neon) |
| **Supabase Auth** | Medium (custom auth schema) | Extract users and migrate to Auth0, Clerk, or Firebase Auth; JWT tokens are standard |
| **Supabase Realtime** | Medium (WAL-based subscriptions) | Replace with WebSocket server (Socket.IO, native WS) or Supabase Realtime self-hosted |
| **Supabase Storage** | Low (S3-compatible) | Migrate to AWS S3, Cloudflare R2, or GCP Cloud Storage |

### 5.5 Database Migration Path (Enterprise Scale)

| Scale Level | Database Solution | Monthly Cost | Migration Effort |
|---|---|---|---|
| **1 user** (current) | Supabase Free | $0 | None |
| **10–100 users** | Supabase Pro ($25/mo) | $25 | None (same platform) |
| **100–1000 users** | Supabase Team ($599/mo) or AWS RDS | $100–$600 | Low (same PostgreSQL) |
| **1000+ users** | AWS RDS Aurora / Neon Enterprise | $200–$2000 | Low (`pg_dump`/`pg_restore`) |

---

## 6. AI / ML

### 6.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **Ollama** | ^0.3 | Local LLM serving | MIT | Stable | Free | Zero-cost AI; fully private; no data leaves machine; supports 70+ models |
| **Llama 3.1** (Ollama) | 8B | Primary AI: chat, summaries, analysis | Llama 3.1 Community | Mature | Free (local) | State-of-the-art 8B model; runs on consumer hardware; permissive license |
| **Claude API (Anthropic)** | Sonnet 4 | Fallback AI: complex reasoning, vision | Proprietary | Mature | ~$0.015/req | Better at complex tasks; vision capabilities; 200K context window |
| **LangChain** (Python) | ^0.2 | Agent orchestration framework | MIT | Mature | Free | Standardized agent pattern; built-in tool calling; streaming output |

### 6.2 Alternatives Considered & Rejected

| Alternative | Why Rejected |
|---|---|
| **OpenAI GPT-4o** | Higher cost ($0.01/1K in); data privacy concerns; API-dependent |
| **Mistral AI (le Chat)** | Limited fine-tuning; smaller ecosystem |
| **LlamaC++ (llama.cpp)** | More complex setup; no REST API built-in (Ollama provides this) |
| **OpenRouter** | Aggregates multiple APIs but adds latency and cost; no local option |
| **LM Studio** | GUI-focused; programmatic API less mature than Ollama |

### 6.3 Decision Matrix — LLM Provider

| Criterion | Weight | Ollama (Local) | Claude API | OpenAI API |
|---|---|---|---|---|
| Cost | 25% | 10 (free) | 5 ($0.015/req) | 3 ($0.03/req) |
| Privacy | 20% | 10 (fully local) | 3 (API call) | 2 (API call + training opt-out) |
| Quality | 20% | 7 (8B model) | 9 (Sonnet 4) | 9 (GPT-4o) |
| Latency | 15% | 7 (local hardware) | 8 (cloud API) | 8 (cloud API) |
| Context Window | 10% | 5 (8K default) | 10 (200K) | 10 (128K) |
| Availability | 10% | 10 (always available) | 6 (API rate limits) | 6 (API rate limits) |
| **Weighted Score** | **100%** | **8.35** | **6.55** | **5.75** |

### 6.4 AI Fallback Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ User Request │ ──▶ │ Ollama (Default) │ ──▶ │ Response Success │
└─────────────┘     └──────────────────┘     └──────────────────┘
                          │ (timeout/error)
                          ▼
                    ┌──────────────────┐     ┌──────────────────┐
                    │ Claude API (Fallback)│──▶│ Response Success │
                    └──────────────────┘     └──────────────────┘
                          │ (timeout/error)
                          ▼
                    ┌──────────────────┐
                    │ Algorithmic       │
                    │ Fallback          │
                    │ (no AI, rule-based)│
                    └──────────────────┘
```

### 6.5 Exit Strategy — AI

| Technology | Lock-in Risk | Exit Strategy |
|---|---|---|
| **Ollama** | Low (open format) | Switch to any OpenAI-compatible endpoint; Ollama's API matches OpenAI's |
| **Claude API** | Low (standard REST) | Migrate to any LLM provider; abstraction layer via LangChain or custom adapter |
| **LangChain** | Low (modular) | Agents are isolated modules; can be rewritten with plain HTTP calls |

---

## 7. DevOps & Hosting

### 7.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **Vercel** | n/a | Frontend hosting, CDN, serverless functions | Proprietary | Mature | Free (personal) | Native Next.js integration; global CDN; automatic HTTPS; preview deployments |
| **Railway** | n/a | Backend hosting | Proprietary | Growing | Free ($5 credit) | Simple deployment; GitHub integration; automatic SSL |
| **GitHub** | n/a | Code repository, CI/CD, issues | Proprietary | Mature | Free | Industry standard; unlimited private repos; Actions CI/CD; projects |
| **Docker** | ^24 | Containerization | Apache 2.0 | Mature | Free | Consistent environments; CI/CD integration; local dev parity |
| **Docker Compose** | ^2.24 | Local development orchestration | Apache 2.0 | Mature | Free | One-command setup for full stack; service dependencies |

### 7.2 Alternatives Considered & Rejected

| Alternative | Why Rejected |
|---|---|
| **Netlify** | Weaker Next.js support; slower builds; no serverless functions (limited) |
| **Cloudflare Pages** | Limited SSR support; no Next.js middleware; fewer regions |
| **Heroku** | Expensive at scale ($7+/dyno); no longer free tier |
| **GitLab** | More complex; fewer Actions integrations; smaller community |
| **AWS Amplify** | Complex configuration; vendor lock-in; slow builds |

### 7.3 Exit Strategy — DevOps

| Technology | Lock-in Risk | Exit Strategy |
|---|---|---|
| **Vercel** | Medium (Next.js integration) | Next.js builds to static output; deploy anywhere (S3+CloudFront, Netlify, Railway) |
| **Railway** | Low (standard containers) | Docker-compatible; migrate to Fly.io, Railway, or self-hosted |

---

## 8. Testing & Quality

### 8.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **Jest** | ^29 | JavaScript unit testing | MIT | Mature | Free | Most popular JS test framework; mocking built-in; large ecosystem |
| **React Testing Library** | ^14 | Component testing | MIT | Mature | Free | Tests user behavior, not implementation; accessible-first |
| **Pytest** | ^8 | Python unit testing | MIT | Mature | Free | Python's best testing framework; fixtures; plugins; minimal boilerplate |
| **Ruff** | ^0.4 | Python linting | MIT | Mature | Free | 100x faster than Flake8; supports pyproject.toml; auto-fix |
| **Black** | ^24 | Python formatting | MIT | Mature | Free | Uncompromising formatter; zero configuration; consistent output |

### 8.2 Testing Strategy Summary

| Test Category | Tool | Location | Coverage Target |
|---|---|---|---|
| Unit (Frontend) | Jest + RTL | `apps/web/` | >80% |
| Unit (Backend) | Pytest | `apps/api/` | >85% |
| Integration | Pytest + Supabase Local | `tests/` | >70% |
| E2E | Playwright (future) | `e2e/` | >60% (critical paths) |
| Linting | Ruff + ESLint | CI Pipeline | 100% code style |
| Type Checking | TypeScript + mypy | CI Pipeline | 100% type coverage |

---

## 9. Monitoring & Observability

### 9.1 Technology Inventory

| Technology | Version | Purpose | License | Maturity | Cost | Rationale |
|---|---|---|---|---|---|---|
| **Sentry** | ^8 | Error tracking & performance | MIT (SDK) / Proprietary (SaaS) | Mature | Free (5K errors/mo) | Best-in-class error tracking; source maps; performance monitoring |
| **Supabase Logs** | n/a | Database query logging | Apache 2.0 | Mature | Free (included) | PostgreSQL log analysis; query performance; auth events |
| **Vercel Analytics** | n/a | Frontend analytics | Proprietary | Mature | Free (personal) | Speed insights; web vitals; usage tracking |

### 9.2 Alternatives Considered & Rejected

| Alternative | Why Rejected |
|---|---|
| **Datadog** | Expensive ($15+/host/month); overkill for single-user system |
| **New Relic** | Free tier very limited; complex setup |
| **Grafana + Loki** | Requires self-hosting; operational overhead for single user |
| **Logtail** | Better for team workflows; free tier smaller |

### 9.3 Exit Strategy — Monitoring

| Technology | Lock-in Risk | Exit Strategy |
|---|---|---|
| **Sentry** | Low (standard SDK) | Open-source Sentry self-hosting available; export error data via API |
| **Vercel Analytics** | Low | Web Vitals are standard browser APIs; replace with Plausible or Umami |

---

## 10. Technology Radar

### 10.1 Current Radar (Q2 2026)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY RADAR — Q2 2026                    │
├────────────────────┬────────────────────┬───────────────────────┤
│     ADOPT          │      TRIAL         │      ASSESS           │
│  (Proven, use)     │  (Promising, try)  │  (Watch, evaluate)    │
├────────────────────┼────────────────────┼───────────────────────┤
│  Next.js 14        │  Pydantic v2       │  Supabase Edge Fn v2  │
│  Tailwind CSS 3    │  Claude Sonnet 4   │  Playwright E2E       │
│  FastAPI           │  Zustand v4        │  LangChain Agents     │
│  Supabase PG       │  Llama 3.1 8B      │  AI SDK (Vercel)      │
│  Ollama            │  Ruff              │  tRPC                 │
│  Framer Motion     │  Recharts          │  Drizzle ORM          │
│  Sentry            │  Railway           │  BiDirectional        │
│  GitHub Actions     │                    │  (biome)              │
├────────────────────┼────────────────────┼───────────────────────┤
│      HOLD          │  RETIRED           │                       │
│  (Keep, don't      │  (Migrate away)    │                       │
│   upgrade yet)     │                    │                       │
├────────────────────┼────────────────────┼───────────────────────┤
│  React 18          │  (none)            │                       │
│  Python 3.10       │                    │                       │
│  PNPM (keep)       │                    │                       │
│  ESLint (keep)     │                    │                       │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Planned Assessments (Next 6 Months)

| Technology | Quarter | Reason for Assessment |
|---|---|---|
| **Playwright** | Q3 2026 | Replace Jest component tests with E2E; better coverage of user flows |
| **Drizzle ORM** | Q3 2026 | Type-safe PostgreSQL queries; Supabase integration; migration tooling |
| **AI SDK (Vercel)** | Q3 2026 | Unified AI streaming API; React Server Components support |
| **tRPC** | Q4 2026 | End-to-end typesafe APIs; reduce manual API route definitions |
| **Biome** | Q4 2026 | Replace ESLint + Prettier with single tool; performance improvement |

---

## 11. Version Compatibility Matrix

### 11.1 Core Stack Compatibility

```
┌───────────────────────────┬──────────────────────────────────────────────────────┐
│           Tool            │              Compatible Versions                      │
├───────────────────────────┼──────────────────────────────────────────────────────┤
│ Next.js 14                │ React 18.x │ TypeScript 5.x │ Node 18+               │
│ React 18.x                │ TypeScript 5.x │ Zustand 4.x │ Recharts 2.x          │
│ TypeScript 5.x            │ Node 18+ │ React 18.x                                 │
│ Tailwind CSS 3.x          │ PostCSS 8.x │ autoprefixer 10.x                       │
│ FastAPI 0.110+            │ Python 3.10+ │ Pydantic 2.x │ Uvicorn 0.29+           │
│ Pydantic 2.x              │ Python 3.10+ │ FastAPI 0.100+ │ Starlette 0.37+        │
│ Python 3.10               │ FastAPI 0.110+ │ Pydantic 2.x │ Ollama 0.3+            │
│ Supabase JS SDK v2        │ React 18.x │ TypeScript 5.x                          │
│ Sentry SDK v8             │ Next.js 14+ │ React 18.x                             │
└───────────────────────────┴──────────────────────────────────────────────────────┘
```

### 11.2 Version Lock Policy

| Category | Update Policy | Critical Patch | Minor | Major |
|---|---|---|---|---|
| **Runtime (Node, Python)** | Minor pin | Auto | 2-week evaluation | 3-month evaluation |
| **Framework (Next.js, FastAPI)** | Minor pin | 1-week auto | 1-month evaluation | 3-month evaluation |
| **UI (Tailwind, Framer)** | Minor pin | Auto | 2-week evaluation | Within major cycle |
| **Database (Supabase)** | Auto (managed) | Managed by Supabase | Managed | Evaluate breaking changes |
| **AI (Ollama, Claude)** | Major pin | Evaluate | Evaluate | Evaluate per model |

---

## 12. Dependency Update Strategy

### 12.1 Update Cadence

| Frequency | Action | Tooling |
|---|---|---|
| **Daily** | Security vulnerability scan | `npm audit`, `pip audit`, Dependabot |
| **Weekly** | Minor/patch updates | `npm update`, `pip list --outdated` |
| **Monthly** | Major version evaluation | Manual review per dependency |
| **Quarterly** | Full dependency audit | Deprecation check, license review |

### 12.2 Update Process

```
1. Monitor Dependabot / Renovate PRs
2. Read changelog for breaking changes
3. Check compatibility with version matrix
4. Update in development branch
5. Run full test suite (npm test, pytest)
6. Run linting + type checking
7. Manual smoke test of affected features
8. Merge to main → auto-deploy to staging
9. Monitor Sentry for new errors (24h)
10. Promote to production
```

### 12.3 Deprecated Dependency Handling

When a dependency enters deprecation:

1. **Document** the deprecation in this document
2. **Search** for viable alternatives (evaluate 3+ options)
3. **Create** migration plan with timeline
4. **Implement** migration in feature branch
5. **Run** parallel old/new during transition
6. **Remove** old dependency after verification period

---

## 13. Security Patching Process

### 13.1 Vulnerability Severity Triage

| Severity | Response Time | Action |
|---|---|---|
| **Critical** (CVSS 9-10) | < 24 hours | Immediately patch; hotfix branch; deploy same day |
| **High** (CVSS 7-8.9) | < 72 hours | Patch within 3 days; schedule deployment |
| **Medium** (CVSS 4-6.9) | < 2 weeks | Patch within next sprint |
| **Low** (CVSS 0-3.9) | < 1 month | Include in next routine update |

### 13.2 Patching Tools

| Tool | Purpose | Schedule |
|---|---|---|
| **Dependabot** | Automated dependency PRs | Daily |
| **npm audit** | JS vulnerability scan | Pre-commit |
| `pip audit` | Python vulnerability scan | Pre-commit |
| **Snyk** (optional) | Advanced vulnerability analysis | Weekly |
| **Manual review** | Critical dependency changelogs | Per release |

### 13.3 Security Patch Deployment

```
Critical Vulnerability Found
        │
        ▼
1. Assess impact on our codebase
        │
        ▼
2. If exploitable: create hotfix branch
        │
        ▼
3. Apply minimum patch (pin version)
        │
        ▼
4. Verify tests pass (CI bypass allowed)
        │
        ▼
5. Deploy hotfix (Vercel + Railway)
        │
        ▼
6. Monitor Sentry for regressions (2h)
        │
        ▼
7. Backport patch to main branch
        │
        ▼
8. Update AGENTS.md if API changed
```

---

## 14. Tech Debt Tracking

### 14.1 Known Tech Debt Items

| ID | Description | Type | Impact | Estimated Effort | Owner | Target Resolution |
|---|---|---|---|---|---|---|
| TD-001 | Migration to Pydantic v2 models | Upgrade | Medium | 2 days | Backend | Q3 2026 |
| TD-002 | Replace `any` types in shared/types | Type Safety | Medium | 1 day | Frontend | Q3 2026 |
| TD-003 | Add integration tests for all 53 endpoints | Testing | High | 5 days | Full Stack | Q4 2026 |
| TD-004 | Implement caching layer for Supabase queries | Performance | Medium | 3 days | Backend | Q4 2026 |
| TD-005 | Remove deprecated ESLint rules | Housekeeping | Low | 0.5 day | Frontend | Q3 2026 |
| TD-006 | Standardize error response format across all endpoints | Consistency | Medium | 2 days | Backend | Q3 2026 |

### 14.2 Tech Debt Prevention

| Practice | Description |
|---|---|
| **Code Reviews** | Every PR reviewed; check for tech debt introduction |
| **TypeScript strict** | `strict: true` in tsconfig; no `any` allowed |
| **Ruff linting** | All Python code must pass `ruff check` |
| **Prompt validation** | All prompt files validated in CI |
| **Test requirements** | New features must include tests |
| **Documentation** | New endpoints, agents, prompts must be documented |

---

## 15. Cost Analysis

### 15.1 Current Cost (Single User)

| Service | Monthly Cost | Annual Cost | Free Limit Utilization |
|---|---|---|---|
| Vercel | $0 | $0 | ~2% of 100 GB bandwidth |
| Supabase | $0 | $0 | ~10% of 500 MB database |
| Ollama | $0 | $0 | 100% free (local) |
| Claude API | $0 | $0 | ~$0.10 credit consumed |
| Sentry | $0 | $0 | <1% of 5K errors |
| Resend | $0 | $0 | ~3% of 3K emails |
| GitHub | $0 | $0 | 0% of unlimited |
| **Total** | **$0** | **$0** | |

### 15.2 Projected Cost at Scale

| User Count | Monthly Cost | Bottleneck | Upgrade Needed |
|---|---|---|---|
| 1 (current) | $0 | None | None |
| 10 | $25 | Supabase 500MB → use | Supabase Pro ($25) |
| 50 | $50 | Vercel bandwidth | Vercel Pro ($20) + Supabase Pro ($25) |
| 100 | $225 | AI cost (Claude) | Ollama for all + Claude Pro ($20) |
| 500 | $650 | Database (~5GB) | Supabase Team ($599) + Vercel Pro ($20) |
| 1000 | $1200 | Multiple | Enterprise hosting |

### 15.3 Cost Optimization Strategies

| Strategy | Savings | Implementation |
|---|---|---|
| Default to Ollama for all AI | ~$50/user/month at scale | `USE_LOCAL_AI=true` default |
| Batch AI requests | ~30% fewer API calls | Queue non-urgent AI tasks |
| Cache Supabase queries | ~50% fewer reads | In-memory TTL cache (already implemented) |
| Purge old data | ~20% storage savings | Auto-archive/delete policies |
| Code splitting | ~30% smaller bundles | Dynamic imports (already implemented) |

---

## 16. Dependency Graph

```
                           ┌───────────────────┐
                           │   User's Browser   │
                           │  (Next.js SSR'd)   │
                           └────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌────────────┐  ┌────────────┐  ┌────────────┐
            │  Supabase   │  │   Ollama   │  │   Claude   │
            │ PostgreSQL  │  │  (Local)   │  │   (Cloud)  │
            │  + Realtime │  │  Mistral   │  │  Sonnet 4  │
            └────────────┘  └────────────┘  └────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                            ┌────────────────┐
                            │  FastAPI (API)  │
                            │   + Agents      │
                            └────────────────┘
                                    │
                                    ▼
                            ┌────────────────┐
                            │    Scheduler    │
                            │  (APScheduler)  │
                            └────────────────┘
```

---

## 17. Upgrade Paths & Deprecation Timeline

### 17.1 Planned Upgrades

| Technology | Current | Target | Timeline | Reason | Breaking Changes |
|---|---|---|---|---|---|
| React | 18.x | 19.x | Q4 2026 | New compiler, concurrent features | Minimal (RSC-related) |
| Next.js | 14.x | 15.x | Q3 2026 | TurboPack, server actions GA | Major (app router stable) |
| Python | 3.10 | 3.12 | Q3 2026 | Performance, typing improvements | Minimal |
| Tailwind CSS | 3.x | 4.x | Q3 2026 | Faster build, CSS-first config | Major (configuration) |
| Pydantic | 1.x | 2.x | Completed | 2x faster, better validation | Breaking (completed) |

### 17.2 Deprecation Timeline

| Technology | Deprecation Date | Replacement | Migration Priority |
|---|---|---|---|
| Pydantic v1 | Q1 2026 (completed) | Pydantic v2 | High (completed) |
| Node 18 | EOL Oct 2025 | Node 20 | Medium |
| React 17 patterns | No timeline | React 18 patterns | Low |
| ESLint (current set) | Q4 2026 | Biome | Low |

---

## 18. License Compliance

### 18.1 License Inventory

| License | Count | Examples | Compliance Notes |
|---|---|---|---|
| MIT | 14 | Next.js, React, Tailwind, Zustand, FastAPI | No restrictions |
| Apache 2.0 | 5 | TypeScript, Docker, Supabase SDK, Pydantic | Patent grant required |
| BSD | 2 | Uvicorn, Python | No restrictions |
| ISC | 1 | Lucide React | Equivalent to MIT |
| Proprietary (Free) | 4 | Vercel, Railway, Supabase, Sentry | Free tier terms apply |
| Llama 3.1 Community | 1 | Llama 3.1 | Acceptable use policy applies |

### 18.2 Compliance Process

- **Pre-commit:** `license-checker` npm package scans for restricted licenses
- **Weekly:** Dependabot alerts for license changes
- **Quarterly:** Manual review of all dependency licenses
- **Policy:** No GPL/AGPL dependencies allowed (viral license risk)
- **Exception Process:** VP Engineering approval required for any non-standard license

---

## 19. Technology Exit Strategy Summary

| Technology | Risk Level | Migration Complexity | Estimated Migration Effort |
|---|---|---|---|
| Next.js | Medium | Medium | 1 week |
| Tailwind CSS | Low | Low | 2 days |
| FastAPI | Low | Low | 3 days |
| Supabase PostgreSQL | Low | Low | 1 day (`pg_dump`) |
| Supabase Auth | Medium | Medium | 3 days |
| Ollama | Low | Low | 1 day |
| Claude API | Low | Low | 1 day |
| Vercel | Medium | Medium | 2 days |
| Railway | Low | Low | 1 day |
| Sentry | Low | Low | 1 day |
| GitHub | Low | Low | 1 day |

---

## 20. Technology Decision Log

### ADR References

| ADR ID | Title | Decision | Date |
|---|---|---|---|
| ADR-001 | Use Next.js over Remix | Next.js 14 | 2026-01 |
| ADR-002 | Use FastAPI over Django | FastAPI 0.110 | 2026-01 |
| ADR-003 | Use Ollama as primary AI | Ollama + Llama 3.1 | 2026-01 |
| ADR-004 | Use Supabase as database | Supabase PostgreSQL | 2026-01 |
| ADR-005 | Use Zustand over Redux | Zustand v4 | 2026-02 |
| ADR-006 | Use Vercel for hosting | Vercel + Railway | 2026-02 |
| ADR-007 | Use Pydantic v2 | Pydantic v2 migration | 2026-03 |
| ADR-008 | Use Sentry for monitoring | Sentry (free tier) | 2026-03 |

---

## 21. Technology Review Cadence

| Review Type | Frequency | Participants | Agenda |
|---|---|---|---|
| **Radar Review** | Monthly | Tech Lead | Update adopt/trial/assess/hold |
| **Security Scan** | Weekly | Automated | CVE check, dependency audit |
| **Cost Review** | Monthly | Developer | Check free tier utilization |
| **Migration Plan** | Quarterly | Full Team | Evaluate major upgrades |
| **License Audit** | Quarterly | Developer | Check for license changes |
| **Tech Debt Review** | Bi-weekly | Engineering | TD tracking update |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-01-15 | Developer | Initial tech stack documentation |
| 1.1.0 | 2026-03-01 | Developer | Added alternatives considered, decision matrices |
| 2.0.0 | 2026-06-11 | Platform Engineering | Enterprise upgrade: 7 categories, comprehensive decision matrices, exit strategies, tech radar, deprecation timeline, cost analysis, vendor lock-in assessment |

---

*End of Document — ENG-TECHSTACK-001*
