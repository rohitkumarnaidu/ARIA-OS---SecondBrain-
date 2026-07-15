# Decision Log — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-DEC-008 |
| Version | 1.0.0 |
| Status | Approved |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Executive Summary

This document tracks all significant architectural and business decisions made during the Second Brain OS project. Each entry captures the context, decision, consequences, alternatives considered, and cross-references to related ADRs. The log provides a historical record of why decisions were made, enabling future developers to understand trade-offs and revisit decisions with full context.

---

## 2. Purpose

To maintain a permanent record of design rationale, enable informed decision-making by providing context from previous decisions, prevent repeated debate on settled questions, and support onboarding of new contributors.

---

## 3. Scope

**In Scope:**
- Architecture decisions affecting system design
- Technology stack choices
- Business model decisions
- Process and workflow decisions
- Priority and scope decisions
- Cross-references to all 15 existing ADRs

**Out of Scope:**
- Daily task prioritization
- Implementation-level details
- Ephemeral decisions reversed within a sprint

---

## 4. Business Context

All decisions are made for a solo-developed, zero-budget, open-source product targeting BTech CSE students. Primary constraints: 10-15 hrs/week capacity, zero infrastructure budget, single-user architecture, India-first focus. Decisions prioritize simplicity, maintainability, and free-tier compatibility.

---

## 5. Decision Log

### DEC-001: Monorepo over Multi-Repo
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Architecture

**Context:** Project includes frontend (Next.js), backend (FastAPI), scheduler (APScheduler), shared packages (AI, config, schemas). Options: separate repos or monorepo.

**Decision:** Use monorepo with pps/, packages/, services/, prompts/, 	ests/ directories.

**Consequences:** Positive: single clone, shared tooling, atomic cross-service changes. Negative: larger clone, all CI triggered on changes. Related ADR: ADR-001.

**Alternatives:** Multi-repo (cross-repo PRs). Single app (separation violated).

---

### DEC-002: Supabase over Custom Backend + DB
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Technology

**Decision:** Supabase for PostgreSQL + Auth (Google OAuth) + Realtime.

**Consequences:** Zero-cost managed DB with auth, RLS for security. Negative: 500MB limit, vendor dependency. Related ADR: ADR-002.

**Alternatives:** Firebase (NoSQL limits). Custom FastAPI + SQLite (no auth). Self-hosted PostgreSQL (maintenance).

---

### DEC-003: Ollama Primary + Claude API Fallback
**Date:** 2026-06-01 | **Status:** Approved | **Category:** AI Architecture

**Decision:** Ollama (Mistral 7B) as primary LLM. Claude API as fallback. Algorithmic fallback as safety net.

**Consequences:** Free, private, offline-capable. Negative: Mistral 7B quality lower; requires 8GB RAM. Related ADR: ADR-003.

**Alternatives:** Claude-only (cost). Ollama-only (quality). GPT-4o-mini (India API concerns).

---

### DEC-004: In-Process Agents over Microservices
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Architecture

**Decision:** 10 AI agents run as async functions within FastAPI process in packages/ai/agents/.

**Consequences:** No network overhead, simpler deployment. Negative: no horizontal scaling. Related ADR: ADR-004.

**Alternatives:** Microservices (deployment complexity). Serverless (cold starts, timeout limits).

---

### DEC-005: Zustand over Redux
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Frontend

**Decision:** Zustand for task + user stores. Other modules use local state.

**Consequences:** Minimal boilerplate, TypeScript-native, ~1KB bundle, persistence middleware. Related ADR: ADR-005.

**Alternatives:** Redux Toolkit (boilerplate). Context API (performance). Jotai (less mature).

---

### DEC-006: APScheduler over Celery
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Infrastructure

**Decision:** APScheduler in services/scheduler/ with 15 cron jobs.

**Consequences:** Simple Python API, no message broker needed. Negative: single point of failure. Related ADR: ADR-006.

**Alternatives:** Celery (requires Redis). System cron (platform-dependent). Supabase Edge Functions (10s timeout).

---

### DEC-007: PWA over Native Mobile
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Frontend

**Decision:** PWA first (Next.js + service worker + IndexedDB). React Native deferred to Year 2.

**Consequences:** Single codebase, installable, offline, push notifications. Negative: no native APIs. Related ADR: ADR-007.

---

### DEC-008: No Event Bus in Alpha
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Architecture

**Decision:** Direct function calls + Supabase Realtime. No event bus.

**Consequences:** Simplest architecture, no additional infra. Negative: tight coupling. Related ADR: ADR-008.

---

### DEC-009: Rs. 0 Forever for Core Product
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Business Model

**Decision:** Core product Rs. 0 forever. Revenue from optional premium AI credits (Year 2+), enterprise licensing (Year 3+), donations.

**Consequences:** No adoption barrier, aligns with mission. Negative: no revenue Year 1.

---

### DEC-010: Single-User Architecture
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Architecture

**Decision:** All design optimized for one person. No collaboration, sharing, or social features.

**Consequences:** Simpler architecture, faster development, stronger privacy. Negative: no network effects.

---

### DEC-011: Cyberpunk Dark Theme
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Design

**Decision:** Bold cyberpunk dark theme (#0A0B0F, #6366F1, #00FFA3). No light mode in v1.

**Consequences:** Distinctive brand, developer focus. Negative: accessibility concerns, outdoor usability.

---

### DEC-012: PromptLoader-Driven AI Architecture
**Date:** 2026-06-11 | **Status:** Approved | **Category:** AI Architecture

**Decision:** PromptLoader singleton reads prompts from prompts/ directory, parses YAML frontmatter.

**Consequences:** Version-controlled prompts, CI-validated, modular. Negative: filesystem dependency.

---

### DEC-013: India-First with English Interface
**Date:** 2026-06-11 | **Status:** Approved | **Category:** Product

**Decision:** English-only UI with India-specific content (CGPA, NPTEL). i18n deferred to Year 2.

---

### DEC-014: Python Backend over Node.js/Go
**Date:** 2026-06-01 | **Status:** Approved | **Category:** Technology

**Decision:** Python (FastAPI) for backend API + AI agents. Python AI ecosystem, developer's primary language.

---

### DEC-015: OpenAI-Compatible API over Direct Ollama SDK
**Date:** 2026-06-11 | **Status:** Approved | **Category:** Technology

**Decision:** Use Ollama's OpenAI-compatible API endpoint via unified httpx client.

**Consequences:** Unified API, easy to add GPT/Gemini. Negative: missing Ollama-specific features.

---

### DEC-016: In-Memory Cache over Redis
**Date:** 2026-06-11 | **Status:** Approved | **Category:** Infrastructure

**Decision:** In-memory TTL cache in packages/shared/utils/cache.py. Redis deferred until cache miss rate exceeds threshold.

**Consequences:** Zero infra, simple. Negative: cache lost on restart. Neutral: Redis can replace via same interface.

---

## 6. ADR Cross-Reference

| ADR | Title | Related Decisions |
|---|---|---|
| ADR-001 | Monorepo over Multi-Repo | DEC-001 |
| ADR-002 | Supabase over Custom Backend/DB | DEC-002, DEC-010 |
| ADR-003 | Ollama + Claude Fallback | DEC-003 |
| ADR-004 | In-Process Agents | DEC-004 |
| ADR-005 | Zustand over Redux | DEC-005 |
| ADR-006 | APScheduler over Celery | DEC-006 |
| ADR-007 | PWA over Native Mobile | DEC-007 |
| ADR-008 | No Event Bus | DEC-008 |

---

## 7. References

| Document | Location | Relationship |
|---|---|---|
| Product Strategy | ProductStrategy.md | Strategic decisions |
| Project Scope | ProjectScope.md | Scope decisions |
| Risks | Risks.md | Risk-informed decisions |
| Assumptions | Assumptions.md | Underlying assumptions |
| ADRs | docs/engineering/adr/ | Full ADR documents |
