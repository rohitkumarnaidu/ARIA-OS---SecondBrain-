# Glossary — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-GLO-005 |
| Version | 1.0.0 |
| Status | Approved |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Executive Summary

This glossary defines all terminology used across Second Brain OS documentation, codebase, and communications. It covers product terms, technical terms, AI/agent concepts, business terms, metric definitions, and acronyms. Every term is defined with a clear, unambiguous definition relevant to this project.

---

## 2. Purpose

To establish a shared vocabulary across all project stakeholders, prevent ambiguity in documentation and communications, and serve as a quick reference for developers and contributors.

---

## 3. Scope

**In Scope:**
- All product module names and concepts
- AI agent terminology
- Technical architecture terms
- Database and infrastructure terms
- Business and metric terms
- Acronyms and abbreviations

**Out of Scope:**
- General programming terminology (API, JSON, HTTP)
- Third-party product names defined in their own documentation
- Industry-standard terms without project-specific meaning

---

## 4. Product Terms

| Term | Definition |
|---|---|
| **Active Builder Rate (ABR)** | Percentage of registered users who, within any 30-day window, completed >=15 tasks, studied >=3 courses, logged >=1 income entry, and shipped progress on >=1 project. North star metric. |
| **Active Push Intelligence** | Design paradigm where the system proactively delivers information (briefings, nudges, alerts) without user prompting. Contrasts with "pull" model (user opens app to check). |
| **ARIA** | Adaptive Reasoning and Intelligence Assistant — the AI orchestrator agent that coordinates 11 agents and manages all user interaction across 15 modules. |
| **Briefing** | AI-generated daily morning summary delivered at 7 AM, containing top-3 tasks, opportunity highlights, course targets, and sleep-adjusted recommendations. |
| **Build First** | Core principle that all system features funnel toward building real things: courses enable projects, ideas ship products, skills earn income. |
| **CIP** | Corporate Identity Program — collection of 50+ brand assets and guidelines for consistent visual identity. |
| **Compound Growth** | Design property where every action feeds every other action. Course completion improves skill profile -> better radar matches -> more income. |
| **Context Engine** | Pipeline that assembles user data (profile, goals, tasks, courses, skills, memory) into optimized system prompts for AI agents. |
| **Cron Job** | Scheduled background task executed by APScheduler at defined times (daily, weekly, every 15 minutes). 7 total. |
| **Dogfood Development** | Practice where the developer is also the primary user. Every feature is built because it was personally needed. |
| **Graceful Degradation** | System property where every AI-dependent feature has a deterministic, algorithm-driven fallback that works when AI is unavailable. |
| **Module** | One of 15 functional areas of the system (Tasks, Courses, Goals, Habits, Sleep, Income, Projects, Ideas, Resources, Opportunities, Academics, YouTube, Chat, Automation, Time). |
| **Nudge** | Gentle AI-generated reminder to take action on a course, habit, or task. Delivered at 6 PM daily by Nudge Agent. |
| **Opportunity Radar** | Daily 6 AM automated scan across 6 categories (internships, hackathons, fellowships, open-source, grants, freelance) matched to user skills. |
| **PromptLoader** | Python singleton class (`packages/ai/prompt_loader.py`) that loads, parses, validates, and serves all AI prompt files from `prompts/` directory with YAML frontmatter. |
| **Radar** | Short for Opportunity Radar. See Opportunity Radar. |
| **Resurface Engine** | Algorithm that identifies and re-presents saved content (resources, YouTube videos, ideas) at contextually relevant moments based on active goals and current tasks. |
| **Review** | AI-generated weekly narrative summary delivered Sunday 8 PM, covering task completion, course progress, income, opportunities, and behavioral patterns. |
| **Second Brain OS** | Full product name for the personal AI productivity system. Also referred to as ARIA OS. |
| **Sub-Agent** | Specialized AI module focused on a single domain (briefing, memory, learning, opportunity, sleep, nudge, roadmap, weekly review). 10 total. |
| **Wind-Down** | AI-generated bedtime reminder delivered at 9:30 PM, summarizing today's accomplishments and preparing tomorrow's first task. |
| **Zero-Cost Architecture** | Design constraint that the entire system must run on free-tier infrastructure: Vercel, Supabase (free tier), Ollama, Brave Search, Resend. Rs. 0/month. |
| **Zero-Miss Policy** | System property where every task, deadline, and commitment is either completed, rescheduled with notification, or explicitly dropped. No silent expirations. |

---

## 5. AI Agent Terms

| Term | Definition |
|---|---|
| **A00 — ARIA Orchestrator** | Central AI agent that receives user messages, classifies intent, dispatches to sub-agents, and synthesizes responses. |
| **A01 — Planner** | AI agent for task planning and schedule optimization. |
| **A02 — Memory Agent** | AI agent that extracts facts, preferences, and patterns from conversations and stores them in persistent memory. |
| **A03 — Learning Agent** | AI agent that detects productivity patterns, skill gaps, and learning opportunities from user data. |
| **A04 — Reminder** | Non-AI cron-based reminder system for tasks and deadlines. |
| **A05 — Career** | AI agent for career path optimization and skill gap analysis. |
| **A06 — Opportunity Agent** | AI agent that scans and matches external opportunities to user skills. |
| **A07 — Analytics** | Non-AI analytics engine for dashboard metrics and reporting. |
| **A08 — Roadmap Agent** | AI agent that optimizes skill development roadmaps and updates milestone relevance. |
| **A09 — Briefing Agent** | AI agent that generates the daily morning briefing with task prioritization. |
| **A10 — Weekly Review Agent** | AI agent that generates the Sunday weekly narrative review. |
| **A11 — Missed Task Checker** | Non-AI cron job that detects and reschedules overdue tasks every 15 minutes. |
| **A12 — Habit Miss Checker** | Non-AI cron job that detects missed habits at midnight. |
| **A13 — Sleep Agent** | AI agent that generates wind-down messages and analyzes sleep patterns. |
| **A14 — Nudge Agent** | AI agent that generates course and habit progress nudges. |
| **A15 — Opportunity Matching Agent** | AI agent that scores and ranks opportunity matches. |
| **LLMClient** | Python class (`packages/ai/client.py`) that manages AI provider calls with retry logic, circuit breaker, and provider failover. |
| **Circuit Breaker** | Resilience pattern that opens after 5 consecutive AI failures, triggering a 60-second cooldown before retrying. |
| **Provider Failover** | Automatic fallback from primary AI provider (Ollama) to secondary (Claude API) when primary is unavailable. |
| **Prompt Entry** | Data class representing a loaded prompt file with frontmatter and body properties. Managed by PromptLoader. |
| **Frontmatter** | YAML metadata block at the top of every prompt file containing version, status, model, max_tokens, temperature, tags. |

---

## 6. Technical Terms

| Term | Definition |
|---|---|
| **APScheduler** | Python library for scheduling cron jobs. Used for all 7 scheduled tasks. |
| **Circuit Breaker** | See AI Agent Terms. |
| **Edge Function** | Serverless function (Supabase) for running backend logic without maintaining a server. |
| **IndexedDB** | Browser-based NoSQL database used for PWA offline data storage. |
| **JWT** | JSON Web Token — authentication token format used by Supabase Auth. Format: header.payload.signature. |
| **Ollama** | Local LLM server that runs Mistral 7B and other models on consumer hardware. Default AI provider. |
| **PWA** | Progressive Web Application — installable web app with offline support via service worker and IndexedDB. |
| **RLS** | Row-Level Security — PostgreSQL security policy that ensures users can only access rows where user_id matches their auth.uid(). Applied to all 18+ tables. |
| **Service Worker** | Browser script that runs in background, enabling offline functionality, push notifications, and caching. |
| **Supabase** | Open-source Firebase alternative providing PostgreSQL database, authentication, storage, and realtime subscriptions. |
| **WXT** | Cross-browser extension framework for building Chrome and Firefox extensions from a single codebase. |
| **pgvector** | PostgreSQL extension for vector similarity search, used for semantic search across resources. |
| **Realtime** | Supabase feature enabling live data synchronization via WebSocket connections. |
| **Pydantic** | Python library for data validation using Python type annotations. Used for all API request/response schemas. |
| **Zustand** | Lightweight React state management library used for task and user stores. |

---

## 7. Business Terms

| Term | Definition |
|---|---|
| **BHAG** | Big Hairy Audacious Goal — 10-year aspirational target: 25,000+ students, 500,000+ courses, 100,000+ projects, Rs. 10 crore+ income. |
| **CAC** | Customer Acquisition Cost — cost to acquire one user. Rs. 0 for organic/word-of-mouth growth. |
| **Churn** | Percentage of users who stop using the product within a given period. |
| **DAU** | Daily Active Users — unique users who log in within a 24-hour period. |
| **DAU/MAU** | Engagement ratio — percentage of monthly users who use the product daily. |
| **GTM** | Go-To-Market strategy — plan for reaching target users and achieving adoption. |
| **LTV** | Lifetime Value — total value a user generates over their relationship with the product. |
| **MAU** | Monthly Active Users — unique users who log in within a 30-day period. |
| **NPS** | Net Promoter Score — user satisfaction metric (-100 to +100) based on likelihood to recommend. |
| **OKR** | Objectives and Key Results — goal-setting framework connecting high-level objectives to measurable results. |
| **PMF** | Product-Market Fit — state where a product satisfies strong market demand, evidenced by retention and engagement. |
| **SLA** | Service Level Agreement — commitment to uptime, response time, and reliability. Best-effort for free product. |
| **SMART** | Specific, Measurable, Achievable, Relevant, Time-bound — criteria for effective goal setting. |
| **SOM** | Serviceable Obtainable Market — realistic adoption target given constraints (100 users Year 1). |
| **TAM** | Total Addressable Market — total potential users (7.2 million for this product). |
| **SAM** | Serviceable Addressable Market — segment reachable with current product (600,000 users). |

---

## 8. Metric Terms

| Term | Definition |
|---|---|
| **Briefing read rate** | Percentage of briefings read within 1 hour of delivery. |
| **Course completion rate** | (Courses with progress = 100% / total courses) * 100. |
| **Deep work hours** | Hours of continuous focus >60 minutes on a single task. |
| **Effective hourly rate** | Total income / total hours worked for that income. |
| **Habit consistency** | (Habit completions / expected completions) * 100 over rolling 30 days. |
| **Match score** | 0-100 score representing relevance of an opportunity to a user's skills and interests. |
| **P95/P99** | 95th/99th percentile response time — 95%/99% of requests are faster than this value. |
| **Productivity score** | 0-100 score combining task completion (40%), study time (20%), sleep quality (20%), habit streaks (20%). |
| **Radar match relevance** | Percentage of opportunities with match_score >= 50 out of total found. |
| **Sleep score** | 0-100 score computed from sleep duration and self-rated quality. |
| **Streak recovery rate** | Number of days to resume a habit after a miss (lower is better). |
| **Task completion rate** | (Tasks completed / tasks created) * 100, measured per week. |

---

## 9. Acronyms

| Acronym | Full Form |
|---|---|
| ABR | Active Builder Rate |
| ADR | Architecture Decision Record |
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| ARIA | Adaptive Reasoning and Intelligence Assistant |
| BHAG | Big Hairy Audacious Goal |
| BRD | Business Requirements Document |
| CAC | Customer Acquisition Cost |
| CGPA | Cumulative Grade Point Average |
| CI/CD | Continuous Integration / Continuous Deployment |
| CORS | Cross-Origin Resource Sharing |
| CRUD | Create, Read, Update, Delete |
| CSR | Client-Side Rendering |
| DAU | Daily Active Users |
| DB | Database |
| DSA | Data Structures and Algorithms |
| ERP | Enterprise Resource Planning |
| FK | Foreign Key |
| GA | General Availability |
| GTM | Go-To-Market |
| HITL | Human-In-The-Loop |
| HTTP | Hypertext Transfer Protocol |
| HTTPS | HTTP Secure |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator |
| LLM | Large Language Model |
| LTV | Lifetime Value |
| MAU | Monthly Active Users |
| MCP | Model Context Protocol |
| MIT | Massachusetts Institute of Technology (license) |
| NLP | Natural Language Processing |
| NPS | Net Promoter Score |
| OCR | Optical Character Recognition |
| OKR | Objectives and Key Results |
| OS | Operating System |
| P0/P1/P2/P3 | Priority levels (Critical/High/Medium/Low) |
| PII | Personally Identifiable Information |
| PMF | Product-Market Fit |
| PRD | Product Requirements Document |
| PR | Pull Request |
| PWA | Progressive Web Application |
| RAG | Retrieval-Augmented Generation |
| RED | Rate, Errors, Duration (monitoring metrics) |
| RLS | Row-Level Security |
| ROI | Return on Investment |
| RTM | Requirements Traceability Matrix |
| SAM | Serviceable Addressable Market |
| SDK | Software Development Kit |
| SLA | Service Level Agreement |
| SMART | Specific, Measurable, Achievable, Relevant, Time-bound |
| SMS | Short Message Service |
| SOM | Serviceable Obtainable Market |
| SRS | Software Requirements Specification |
| SSL | Secure Sockets Layer |
| SSG | Static Site Generation |
| TAM | Total Addressable Market |
| TLS | Transport Layer Security |
| TTI | Time To Interactive |
| UI/UX | User Interface / User Experience |
| UVP | Unique Value Proposition |
| WCAG | Web Content Accessibility Guidelines |
| WIP | Work In Progress |

---

## 10. References

| Document | Location | Relationship |
|---|---|---|
| Product Vision | [00_ProjectVision.md](00_ProjectVision.md) | Broader context for terms |
| BRD Glossary | [03_BRD.md](03_BRD.md#16-glossary) | Expanded business term definitions |
| SRS Definitions | [04_SRS.md](04_SRS.md#13-definitions) | Technical term definitions |
| AGENTS.md | `AGENTS.md` | Architecture and system terms |

> **Duplicate note:** A governance-level glossary exists at [`docs/governance/glossary.md`](../governance/glossary.md) focused on project management, operations, and infrastructure terms. This product glossary covers product, feature, and domain terms. See the governance version for terms related to development process, compliance, and operations.
