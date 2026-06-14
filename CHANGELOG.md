# Changelog

All notable changes to Second Brain OS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/owner/secondbrain-os/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/owner/secondbrain-os/releases/tag/v0.1.0
