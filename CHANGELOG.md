# Changelog

All notable changes to Second Brain OS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-06-22

### Added (Phase 5: Enterprise Polish)
- Bundle size optimization: `sideEffects: false` in package.json for aggressive tree-shaking
- Named exports in root barrel (`components/index.ts`) replacing wildcard `export *`
- Response caching middleware with TTL and cache-control headers
- Batch query executor for parallel Supabase queries with error isolation
- Database index optimization migration (15 new composite/partial/full-text indexes)
- PurgeCSS audit script (`scripts/purgecss-check.sh`)
- OWASP Top 10 verification script (`scripts/owasp-check.sh`)
- SQL injection audit script (`scripts/sql-injection-audit.sh`)
- XSS sanitization utility with recursive object scanning
- Security disclosure file (`.well-known/security.txt`)
- Data retention policy documentation
- Component API documentation: 11 Storybook stories for root + UI components
- Release automation script (`scripts/release.sh`)
- `optimizePackageImports` extended to cover 8 heavy packages

### Changed
- Tailwind content paths extended to cover `hooks/` and `styles/` directories
- Safelist added for critical animation classes

### Infrastructure
- CI pipeline enhanced with Lighthouse CI, Trivy security scanning, a11y checks
- Automated deployment workflow for Vercel + Railway

### Tests
- 1450+ tests maintained with 97.57% coverage

## [1.0.0] - 2026-06-21

### Added (Phase 4: Enterprise Hardening)
- API key authentication system with SHA-256 hashing
- GDPR data export endpoint for all 18 user tables
- Data retention policy with automated cleanup
- Rate limiter with standard response headers (RFC 6585)
- Audit logging middleware for all data mutations
- CSRF protection middleware
- Input sanitization and XSS protection
- Graceful shutdown handler with connection draining
- GZip compression middleware for API responses
- Circuit breaker + exponential backoff retry for all AI calls
- Health probes (liveness + readiness) with dependency status
- OpenAPI summaries on all 118 API endpoints
- 15 new UI components (Avatar, Command, DataTable, etc.)
- 8 motion components (PageTransition, StaggerChildren, etc.)
- Storybook configuration with a11y addon
- AI Assistant and Agent Activity Feed components
- Comprehensive E2E tests for 5 critical flows
- Runbook documentation and deployment guide

### Changed
- 51 Supabase queries optimized from `select("*")` to explicit columns
- Frontend performance: React.memo on frequent components, dynamic imports
- Auth module: JWT refresh flow and API key rotation support

### Tests
- Test coverage increased from 68% to 98.99% (1450 tests)
- All 7 scheduler cron jobs fully tested
- All 26 database schema models validated
- All 10 agent modules tested with LLM fallback paths
- All shared utilities at 100% coverage

---

## [Unreleased]

### Added
- Enterprise documentation set (docs #00-#50)
  - Product docs: Project Vision, PRD, BRD, SRS, Features, User Stories, Acceptance Criteria
  - Engineering docs: Architecture, Tech Stack, System Architecture, Agent Architecture, Database, API, Events
  - Design docs: UI/UX, Design System, Design Tokens
  - AI docs: AI Instructions, Agent, Prompts, Memory Architecture, Knowledge Graph, Skills
  - Security docs: Security, Compliance, Data Privacy & GDPR
  - DevOps docs: Deployment, DevOps, Release Management
  - QA docs: Testing, QA
  - Operations docs: Analytics, Observability, Monitoring, Roadmap, Backlog, Runbooks, Incident Response
  - Enterprise extensions: Disaster Recovery, Risk Management, SLA, Developer Onboarding, Performance & Scalability, Cost Management, Documentation Standards, Change Management, Technical Debt
- Root-level enterprise files: LICENSE (MIT), CHANGELOG, CODE_OF_CONDUCT, SECURITY.md, .env.example
- GitHub community templates: Issue templates (bug report, feature request), PR template
- CI/CD pipeline: GitHub Actions workflow (lint, type-check, build, security audit)
- Docker Compose for local development
- Architecture Decision Records (ADR-001 through ADR-008)

### Changed
- Documentation architecture standardized with numbering convention
- IMPLEMENTATION_STATUS.md updated with full doc inventory

### Fixed
- Duplicate architecture doc (04) removed from engineering/

---

## [0.1.0] — 2026-06-01

### Added
- Initial project scaffolding and monorepo structure
- Next.js 14 frontend with App Router and Tailwind CSS
- FastAPI backend with 13 API routers (~50 endpoints)
- Supabase integration with 15+ database tables
- AI infrastructure: Ollama client + Claude API fallback
- APScheduler with 6 cron jobs
- 15 frontend modules: Dashboard, Tasks, Courses, Goals, Habits, Sleep, Income, Projects, Ideas, Resources, Opportunities, Academics, Time, Chat, Automation
- Core UI components: Button, Card, Input, Modal, Sidebar, Navbar
- State management: Zustand stores for tasks + users
- Three.js 3D background
- Framer Motion animations
- Google OAuth authentication via Supabase
- Rate limiting middleware (100 req/min)
- Structured JSON logging
- Base documentation framework

[Unreleased]: https://github.com/owner/secondbrain-os/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/owner/secondbrain-os/releases/tag/v1.0.0
[0.1.0]: https://github.com/owner/secondbrain-os/releases/tag/v0.1.0
